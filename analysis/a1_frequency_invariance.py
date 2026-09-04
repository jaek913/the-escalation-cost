"""a1_frequency_invariance.py - A1: does E1's reading survive quarterly sampling?

ROBUSTNESS APPENDIX to The Escalation Cost. Pre-registered in
A1_FREQUENCY_INVARIANCE.md, committed BEFORE this script existed
(commit c0da772). Nothing in this file may relax the rule fixed there.

WHY: every ESC experiment is monthly, and the frequency is structural - W is
a look-back in MONTHS, bg a share closed PER MONTH, rho the spectral radius
of a companion matrix whose period is the sampling interval. Public company
filings are QUARTERLY. If the reading survives coarser sampling the
firm-level path is open; if it does not, that path is closed and this file
records it.

METHOD (frozen in the pre-registration; restated here, not re-decided):
  * Input: the same hashed FRED store E1 reads. No new download.
  * Aggregation: I/S is a RATIO, not a flow, so quarters are the MEAN of the
    three monthly values, by real calendar quarter. Partial head/tail
    quarters dropped. End-of-quarter sampling is NOT run (avoiding a
    two-specification search).
  * Constants: every month-denominated constant divided by 3, preserving the
    same real time spans (BASE 60->20, RECENT 12->4, FWD 12->4, BLOCK 24->8).
  * W: 8/3 = 2.67 has no clean quarterly equivalent. Rule evaluated at W=3
    ONLY; W=2 and W=4 reported as a sensitivity strip so a reader can see
    whether the verdict hinges on the rounding.
  * Estimator: e1_rolling_validation.run_panel() is IMPORTED AND CALLED
    VERBATIM with module constants patched - never copied, never
    reimplemented - so the two runs differ only in input and window lengths.

DECISION RULE (fixed before any result):
  PASS    iff pooled quarterly Spearman > 0
          AND rank corr(S_monthly, S_quarterly) across all 17 sectors >= +0.50
          AND the quarterly run returns SUPPORT under E1's own RULE B.
  PARTIAL iff the first two hold and the third does not.
  FAIL    otherwise.
PARTIAL is the predicted outcome (n falls ~3x; averaging raises measured
persistence). A PARTIAL driven by lost power is NOT evidence against the
theory and is not to be reported as such.

Writes analysis/outputs/a1_frequency_invariance.json.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from collections import defaultdict

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "data"))

import e1_rolling_validation as e1  # noqa: E402  (the estimator, verbatim)
import pull  # noqa: E402

OUT = _HERE / "outputs" / "a1_frequency_invariance.json"
MONTHLY_JSON = _HERE / "outputs" / "e1_rolling_validation.json"

# Quarterly constants: month-denominated values / 3, same real spans.
Q_BASE_WIN, Q_RECENT_WIN, Q_FWD_WIN, Q_BLOCK = 20, 4, 4, 8
W_PRIMARY = 3            # 8/3 = 2.67 -> 3; rule evaluated HERE only
W_STRIP = (2, 3, 4)      # reported for transparency, not searched over
RANK_CORR_MIN = 0.50     # pre-registered threshold (component 2)


def load_dated_series(sid: str) -> tuple[list[str], np.ndarray]:
    """Read a FRED csv from the hashed store as (dates, values).

    E1's own loader drops the date column; quarterly aggregation needs real
    calendar quarters, so this reads both. Missing values ('.') are dropped
    with their dates, exactly as E1 drops them.
    """
    path = pull.RAW / f"fred_{sid}.csv"
    dates, vals = [], []
    with open(path) as f:
        next(f)
        for line in f:
            d, v = line.strip().split(",")
            if v != ".":
                dates.append(d)
                vals.append(float(v))
    return dates, np.asarray(vals)


def to_quarterly(dates: list[str], vals: np.ndarray) -> np.ndarray:
    """Calendar-quarter MEAN of a ratio series; partial quarters dropped.

    Frozen choice (pre-registration Section 4): I/S is a ratio, so quarters
    are averaged, not summed. Only quarters with all 3 months are kept, so a
    partial quarter at either end cannot distort the endpoint.
    """
    buckets: dict[tuple[int, int], list[float]] = defaultdict(list)
    for d, v in zip(dates, vals):
        y, m = int(d[:4]), int(d[5:7])
        buckets[(y, (m - 1) // 3 + 1)].append(v)
    keys = sorted(buckets)
    return np.asarray([float(np.mean(buckets[k])) for k in keys
                       if len(buckets[k]) == 3])


def store_hash(sids: list[str]) -> str:
    """One digest over every input file, so the JSON records what was read."""
    h = hashlib.md5()
    for sid in sorted(sids):
        h.update(pathlib.Path(pull.RAW / f"fred_{sid}.csv").read_bytes())
    return h.hexdigest()


def run_quarterly(panel_q: dict[str, np.ndarray], w: int) -> dict:
    """Call E1's run_panel VERBATIM with quarterly constants patched in.

    Patching module globals (rather than copying the function) is what makes
    this a frequency test and not a reimplementation: any change to E1's
    estimator propagates here automatically.
    """
    saved = (e1.BASE_WIN, e1.RECENT_WIN, e1.FWD_WIN, e1.BLOCK,
             e1.W_SPEC, e1.TAU)
    try:
        e1.BASE_WIN, e1.RECENT_WIN, e1.FWD_WIN = Q_BASE_WIN, Q_RECENT_WIN, Q_FWD_WIN
        e1.BLOCK = Q_BLOCK
        e1.W_SPEC = w
        e1.TAU = e1.KAPPA * w      # tau = kappa * W, as in E1
        return e1.run_panel(panel_q, seed=e1.SEED)
    finally:
        (e1.BASE_WIN, e1.RECENT_WIN, e1.FWD_WIN, e1.BLOCK,
         e1.W_SPEC, e1.TAU) = saved


def main() -> None:
    members = [(sid, title) for sid, role, title in pull.SECTOR_MAP
               if role.startswith("member")]
    assert len(members) == 17, f"expected 17 members, got {len(members)}"

    panel_q, n_monthly, n_quarterly = {}, {}, {}
    for sid, title in members:
        name = f"{sid} ({title})"
        dates, vals = load_dated_series(sid)
        q = to_quarterly(dates, vals)
        panel_q[name] = q
        n_monthly[name] = int(len(vals))
        n_quarterly[name] = int(len(q))

    # --- primary run (W = 3) + sensitivity strip -------------------------
    runs = {w: run_quarterly(panel_q, w) for w in W_STRIP}
    primary = runs[W_PRIMARY]

    # --- join to the published monthly result ----------------------------
    monthly = json.loads(MONTHLY_JSON.read_text())
    s_m = {s["sector"]: s["spearman"] for s in monthly["sectors"]}
    k_m = {s["sector"]: s["klass"] for s in monthly["sectors"]}
    s_q = {s["sector"]: s["spearman"] for s in primary["sectors"]}
    k_q = {s["sector"]: s["klass"] for s in primary["sectors"]}
    shared = [k for k in s_m if k in s_q]
    assert len(shared) == 17, f"sector join lost sectors: {len(shared)}/17"

    a = np.array([s_m[k] for k in shared])
    b = np.array([s_q[k] for k in shared])
    rank_corr = e1.spearman(a, b)          # E1's own Spearman, reused

    # --- decision rule ---------------------------------------------------
    c1 = bool(primary["pooled_mean_spearman"] > 0)
    c2 = bool(rank_corr >= RANK_CORR_MIN)
    c3 = bool(primary["verdict"] == "SUPPORT")
    result = "PASS" if (c1 and c2 and c3) else ("PARTIAL" if (c1 and c2) else "FAIL")

    out = dict(
        appendix="A1", of="E1 (rolling out-of-sample panel validation)",
        prereg="A1_FREQUENCY_INVARIANCE.md @ c0da772",
        design_pin=monthly.get("design_pin"),
        store_md5=store_hash([sid for sid, _ in members]),
        aggregation="calendar-quarter MEAN of the monthly I/S ratio; "
                    "partial head/tail quarters dropped",
        spec_quarterly=dict(W_primary=W_PRIMARY, W_strip=list(W_STRIP),
                            bg=e1.BG_SPEC, kappa=e1.KAPPA,
                            base_win=Q_BASE_WIN, recent_win=Q_RECENT_WIN,
                            fwd_win=Q_FWD_WIN, block=Q_BLOCK,
                            B=e1.B_BOOT, seed=e1.SEED),
        n_obs=dict(monthly=n_monthly, quarterly=n_quarterly),
        monthly_reference=dict(
            pooled_mean_spearman=monthly["pooled_mean_spearman"],
            p_panel=monthly["p_panel"], verdict=monthly["verdict"],
            n_oscillating=monthly["n_oscillating"]),
        quarterly_primary=dict(
            pooled_mean_spearman=primary["pooled_mean_spearman"],
            p_panel=primary["p_panel"], verdict=primary["verdict"],
            n_oscillating=primary["n_oscillating"],
            n_chronic=primary["n_chronic"]),
        sensitivity_strip={
            str(w): dict(pooled_mean_spearman=r["pooled_mean_spearman"],
                         p_panel=r["p_panel"], verdict=r["verdict"],
                         n_oscillating=r["n_oscillating"])
            for w, r in runs.items()},
        per_sector=[dict(sector=k, spearman_monthly=s_m[k],
                         spearman_quarterly=s_q[k],
                         klass_monthly=k_m[k], klass_quarterly=k_q[k])
                    for k in shared],
        decision=dict(
            c1_pooled_positive=c1,
            c2_rank_corr_ge_0_50=c2, rank_corr_monthly_vs_quarterly=rank_corr,
            c3_support_under_rule_B=c3, result=result),
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))

    m, q = out["monthly_reference"], out["quarterly_primary"]
    print(f"A1 {result}")
    print(f"  monthly   : pooled S={m['pooled_mean_spearman']:+.4f} "
          f"p={m['p_panel']:.4f} osc={m['n_oscillating']} {m['verdict']}")
    print(f"  quarterly : pooled S={q['pooled_mean_spearman']:+.4f} "
          f"p={q['p_panel']:.4f} osc={q['n_oscillating']} {q['verdict']}")
    print(f"  rank corr monthly vs quarterly (17 sectors) = {rank_corr:+.4f} "
          f"(need >= {RANK_CORR_MIN:+.2f})")
    print(f"  components: pooled>0 {c1} | rankcorr {c2} | SUPPORT {c3}")
    print("  W strip:", ", ".join(
        f"W={w}: S={r['pooled_mean_spearman']:+.3f} p={r['p_panel']:.4f} "
        f"{r['verdict']}" for w, r in runs.items()))
    for s in out["per_sector"]:
        print(f"    {s['sector'][:44]:44s} S_m={s['spearman_monthly']:+.3f} "
              f"S_q={s['spearman_quarterly']:+.3f}  "
              f"{s['klass_monthly'][:13]:13s} -> {s['klass_quarterly']}")


if __name__ == "__main__":
    main()
