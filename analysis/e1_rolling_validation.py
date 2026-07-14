"""e1_rolling_validation.py - E1: rolling out-of-sample panel validation.
THE PRIMARY FALSIFIER (DESIGN.md Section 4; pin 74c73ea165a7363c6714fe803fbe76b1).

FROZEN SCRIPT-LEVEL SPECIFICS (design-freeze commit precedes the suite's first
official run; per the v1.9.5 gate and the alignment review's FLAG-1):

1. kappa = 0.75, so tau = kappa * W = 6.0 under SPEC-M (W = 8). Invariance
   note: W is constant across sectors and months, so tau is a single constant
   exponent; Spearman is rank-based, hence E1's statistic is provably
   invariant to the kappa choice. The pin exists for reproducibility, not
   because the result depends on it.
2. Exact outcome (deviation) definition: with mu12_t = mean of the trailing
   12 months at t,
     fwd_dev_t  = mean over h=1..12 of |IS_{t+h} - mu12_t|
     base_dev_t = mean over the trailing 12 months of |IS - mu12_t|
     outcome_t  = fwd_dev_t - base_dev_t   (EXCESS absolute deviation)
   The trailing-12 anchor (rather than trailing-60) keeps the outcome's
   serial dependence within the DESIGN-frozen 24-month bootstrap blocks so
   the pre-registered correction is actually calibrated - verified by the
   suite's measured false-positive rate.
3. Regime detection (source construction): phi_baseline = OLS AR(1) on the
   trailing 60 months; phi_recent = OLS AR(1) on the trailing 12 months.
   D_t = (rho(phi_recent, W, bg) / rho(phi_baseline, W, bg))^tau, SPEC-M
   (W = 8, bg = 0.05), the THM-3 identity form.
4. p-values: one-sided (positive-association) circular block bootstrap NULL -
   the outcome series is resampled in 24-month circular blocks independently
   of D (preserving its autocorrelation, breaking the pairing), B = 2000;
   p = fraction of null Spearman >= observed. This is the pre-registered
   effective-sample-size correction.
5. Sector classification precedence (per the decision rule): chronic
   (rolling SPEC-M rho > 1 in > 40% of months) is classified FIRST and
   reported separately as a boundary-condition case; else oscillating if the
   rolling rho crosses 1.0 in both directions at least once; else
   never-crossing (reported, outside the majority denominator).

Decision rule (as amended 2026-07-13, DESIGN Section 4 dated amendment -
RULE B, panel-level falsifier): SUPPORT iff >= 2 regime-oscillating sectors
AND pooled mean Spearman across them > 0 AND one-sided p < 0.01 under the
JOINT circular block bootstrap null (one 24-month block index set applied to
every oscillating sector's outcome simultaneously, D fixed, B = 2000).
FALSIFIED otherwise. Per-sector p-values (alpha 0.05 reference) are
descriptive only.

Reads hashed data from the project-local store; writes
analysis/outputs/e1_rolling_validation.json.
"""

from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "data"))
from theory_lib import rho  # noqa: E402
import pull  # noqa: E402  (frozen SECTOR_MAP + store paths; no network at import)

OUT = _HERE / "outputs" / "e1_rolling_validation.json"

# SPEC-M (DESIGN Section 0) + frozen pins
W_SPEC, BG_SPEC = 8, 0.05
KAPPA = 0.75
TAU = KAPPA * W_SPEC
BASE_WIN, RECENT_WIN, FWD_WIN = 60, 12, 12
BLOCK, B_BOOT = 24, 2000
ALPHA = 0.05        # per-sector DESCRIPTIVE reference line
ALPHA_PANEL = 0.01  # verdict-level threshold (rule B)
MIN_OSC = 2
CHRONIC_FRAC = 0.40
SEED = 20260713


def load_series(sid: str) -> np.ndarray:
    path = pull.RAW / f"fred_{sid}.csv"
    vals = []
    with open(path) as f:
        next(f)
        for line in f:
            _, v = line.strip().split(",")
            if v != ".":
                vals.append(float(v))
    return np.asarray(vals)


def ols_phi(y: np.ndarray) -> float:
    x, z = y[:-1], y[1:]
    xm, zm = x.mean(), z.mean()
    den = ((x - xm) ** 2).sum()
    return float(((x - xm) * (z - zm)).sum() / den) if den > 0 else 0.0


def _rank(a: np.ndarray) -> np.ndarray:
    r = np.empty(len(a))
    r[np.argsort(a, kind="mergesort")] = np.arange(len(a))
    return r


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra, rb = _rank(a), _rank(b)
    ra -= ra.mean(); rb -= rb.mean()
    den = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra * rb).sum() / den) if den > 0 else 0.0


def block_boot_p(d: np.ndarray, outcome: np.ndarray, rng: np.random.Generator,
                 block: int = BLOCK, b: int = B_BOOT) -> tuple[float, float]:
    """One-sided positive-association p via circular block bootstrap of the
    outcome series against fixed D (frozen item 4)."""
    obs = spearman(d, outcome)
    n = len(outcome)
    n_blocks = int(np.ceil(n / block))
    count = 0
    rd = _rank(d); rd -= rd.mean()
    rd_den = np.sqrt((rd ** 2).sum())
    for _ in range(b):
        starts = rng.integers(0, n, n_blocks)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel()[:n] % n
        ro = _rank(outcome[idx]); ro -= ro.mean()
        den = rd_den * np.sqrt((ro ** 2).sum())
        s = float((rd * ro).sum() / den) if den > 0 else 0.0
        if s >= obs:
            count += 1
    return obs, (count + 1) / (b + 1)


def sector_series_stats(y: np.ndarray) -> dict:
    """Full per-sector E1 pipeline on one I/S series (frozen items 2-3, 5)."""
    n = len(y)
    d_vals, out_vals, rho_roll = [], [], []
    for t in range(BASE_WIN, n):
        base = y[t - BASE_WIN:t]
        recent = y[t - RECENT_WIN:t]
        mu12 = recent.mean()
        phi_b = ols_phi(base)
        r_b = rho(phi_b, W_SPEC, BG_SPEC)
        rho_roll.append(r_b)
        if t + FWD_WIN > n:
            continue
        phi_r = ols_phi(y[t - RECENT_WIN:t])
        r_r = rho(phi_r, W_SPEC, BG_SPEC)
        d_vals.append((r_r / r_b) ** TAU if r_b > 0 else np.nan)
        fwd_dev = np.abs(y[t + 1:t + 1 + FWD_WIN] - mu12).mean()
        base_dev = np.abs(recent - mu12).mean()
        out_vals.append(fwd_dev - base_dev)
    d = np.asarray(d_vals); o = np.asarray(out_vals)
    ok = np.isfinite(d) & np.isfinite(o)
    rr = np.asarray(rho_roll)
    frac_above = float((rr > 1.0).mean())
    above = rr > 1.0
    crossings_up = int(((~above[:-1]) & above[1:]).sum())
    crossings_dn = int((above[:-1] & (~above[1:])).sum())
    if frac_above > CHRONIC_FRAC:
        klass = "chronic-boundary"
    elif crossings_up >= 1 and crossings_dn >= 1:
        klass = "oscillating"
    else:
        klass = "never-crossing"
    return dict(d=d[ok], outcome=o[ok], n_obs=int(ok.sum()),
                frac_months_above_1=frac_above,
                crossings_up=crossings_up, crossings_dn=crossings_dn,
                klass=klass)


def run_panel(panel: dict[str, np.ndarray], seed: int = SEED) -> dict:
    """panel: sector name -> I/S series. Returns full E1 result + verdict
    under RULE B. Used verbatim by both the synthetic suite and the real run."""
    rng = np.random.default_rng(seed)
    stats = {k: sector_series_stats(y) for k, y in panel.items()}
    n_min = min(len(st["outcome"]) for st in stats.values())
    ranked, sectors = {}, []
    for name, st in stats.items():
        rd = _rank(st["d"][:n_min]); rd = rd - rd.mean()
        ranked[name] = (rd, float(np.sqrt((rd ** 2).sum())),
                        st["outcome"][:n_min])
        obs, p = block_boot_p(st["d"][:n_min], st["outcome"][:n_min], rng)
        sectors.append(dict(sector=name, klass=st["klass"],
                            n_obs=int(n_min), spearman=obs,
                            p_one_sided_descriptive=p,
                            frac_months_above_1=st["frac_months_above_1"]))
    osc = [s["sector"] for s in sectors if s["klass"] == "oscillating"]
    obs_by = {s["sector"]: s["spearman"] for s in sectors}
    pooled = float(np.mean([obs_by[k] for k in osc])) if osc else 0.0
    # Joint block-bootstrap null: one index set across all oscillating sectors.
    n_blocks = int(np.ceil(n_min / BLOCK))
    count = 0
    for _ in range(B_BOOT):
        starts = rng.integers(0, n_min, n_blocks)
        idx = (starts[:, None] + np.arange(BLOCK)[None, :]).ravel()[:n_min] % n_min
        vals = []
        for k in osc:
            rd, rdd, o = ranked[k]
            ro = _rank(o[idx]); ro = ro - ro.mean()
            den = rdd * np.sqrt((ro ** 2).sum())
            vals.append(float((rd * ro).sum() / den) if den > 0 else 0.0)
        if osc and float(np.mean(vals)) >= pooled:
            count += 1
    p_pool = (count + 1) / (B_BOOT + 1)
    verdict = ("SUPPORT" if len(osc) >= MIN_OSC and pooled > 0
               and p_pool < ALPHA_PANEL else "FALSIFIED")
    return dict(sectors=sectors, n_oscillating=len(osc),
                n_chronic=sum(1 for s in sectors
                              if s["klass"] == "chronic-boundary"),
                pooled_mean_spearman=pooled, p_panel=p_pool,
                verdict=verdict)


def main() -> None:
    members = [(sid, title) for sid, role, title in pull.SECTOR_MAP
               if role.startswith("member")]
    assert len(members) == 17
    panel = {f"{sid} ({title})": load_series(sid) for sid, title in members}
    res = run_panel(panel)
    out = dict(experiment="E1", date="2026-07-13",
               design_pin="74c73ea165a7363c6714fe803fbe76b1",
               spec=dict(W=W_SPEC, bg=BG_SPEC, kappa=KAPPA, tau=TAU,
                         base_win=BASE_WIN, recent_win=RECENT_WIN,
                         fwd_win=FWD_WIN, block=BLOCK, B=B_BOOT, alpha=ALPHA,
                         chronic_frac=CHRONIC_FRAC, seed=SEED),
               **res)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print(f"E1 {res['verdict']}: pooled S={res['pooled_mean_spearman']:+.4f} "
          f"p_panel={res['p_panel']:.4f} over {res['n_oscillating']} oscillating "
          f"sectors; chronic boundary cases: {res['n_chronic']}")
    for s in res["sectors"]:
        print(f"  {s['sector'][:52]:52s} {s['klass']:16s} "
              f"rho>1 {s['frac_months_above_1']:.1%}  "
              f"S={s['spearman']:+.3f} p={s['p_one_sided_descriptive']:.4f}")


if __name__ == "__main__":
    main()
