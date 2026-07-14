"""e5_instability_ranking.py - E5: 17-sector structural-instability ranking
(the CHIPS observation). DESIGN.md Section 8 (pin 74c73ea165a7363c6714fe803fbe76b1).

Descriptive diagnostic (NOT a hypothesis test): rank the 17 sectors by the
fraction of months their rolling spectral radius rho exceeds 1, and test the
reproducibility + robustness of the observation that the CHIPS Act's two
dependent sectors rank at the top.

Operator (frozen):
  - rolling 60-month persistence per sector (trailing OLS AR(1));
  - rho computed under SPEC-R (W = 12, bg scale 3.0) - the primary spec;
  - per sector: peak rho, mean rho, % months rho > 1, over the full sample;
  - ranking by % months rho > 1;
  - robustness: recompute under SPEC-M (W = 8, bg 0.05); report BOTH.

Decision rule (frozen, graded assertion):
  (a) REPRODUCED if the ranking regenerates from the re-pulled hashed data
      (deterministic given the frozen store - asserted by this script running
      to completion on the hashed inputs and emitting the ranking).
  (b) CHIPS observation ("the two sectors the Act depends on are the two most
      structurally unstable"):
        ASSERTED       if computers/electronics manufacturing (NAICS 334 ->
                       A34SIS) AND wholesale machinery (R4238) rank #1-#2 under
                       SPEC-R AND both remain in the top quartile under SPEC-M;
        DOWNGRADED     to "among the most unstable" if both are top-quartile
                       but not #1-#2 (SPEC-R);
        DROPPED        if either falls below the top quartile in either spec.

Writes analysis/outputs/e5_instability_ranking.json.
"""

from __future__ import annotations

import json
import math
import pathlib
import sys

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "data"))
from theory_lib import rho  # noqa: E402
import pull  # noqa: E402
from e1_rolling_validation import load_series, ols_phi  # noqa: E402

OUT = _HERE / "outputs" / "e5_instability_ranking.json"

ROLL_WIN = 60
SPEC_R = dict(name="SPEC-R", W=12, bg=3.0)   # primary (bg scale 3.0)
SPEC_M = dict(name="SPEC-M", W=8, bg=0.05)   # robustness

# CHIPS-dependent sectors (frozen identification)
CHIPS_MFG = "A34SIS"      # NAICS 334 computers & electronic products (mfg)
CHIPS_WHOLESALE = "R4238IM163SCEN"  # wholesale machinery


def sector_rho_stats(y: np.ndarray, W: int, bg: float) -> dict:
    """Rolling 60-month persistence -> rho under (W, bg); returns peak/mean rho
    and % months rho > 1 over the full sample."""
    n = len(y)
    rhos = []
    for t in range(ROLL_WIN, n):
        phi = ols_phi(y[t - ROLL_WIN:t])
        rhos.append(rho(phi, W, bg))
    rr = np.asarray(rhos)
    return dict(peak_rho=float(rr.max()), mean_rho=float(rr.mean()),
                pct_months_above_1=float((rr > 1.0).mean()),
                n_months=int(len(rr)))


def rank_under(members: list[tuple[str, str]], spec: dict) -> list[dict]:
    """Return the sector ranking (desc by % months rho > 1) under a spec."""
    rows = []
    for sid, title in members:
        y = load_series(sid)
        st = sector_rho_stats(y, spec["W"], spec["bg"])
        rows.append(dict(sector=sid, title=title, **st))
    rows.sort(key=lambda r: r["pct_months_above_1"], reverse=True)
    for i, r in enumerate(rows):
        r["rank"] = i + 1
    return rows


def _rank_of(rows: list[dict], sid: str) -> int:
    for r in rows:
        if r["sector"] == sid:
            return r["rank"]
    return 10**9


def chips_graded_verdict(r_ranks: dict, m_ranks: dict,
                        top_quartile_cut: int) -> dict:
    """Pure graded-assertion rule (frozen, DESIGN Section 8). Given the CHIPS
    sectors' ranks under SPEC-R and SPEC-M and the top-quartile cut, return the
    verdict. ASSERTED iff both are #1-#2 under SPEC-R and both top-quartile
    under SPEC-M; DOWNGRADED iff both top-quartile under both specs but not
    #1-#2; DROPPED otherwise (either below the top quartile in either spec)."""
    both_top2_R = set(r_ranks.values()) == {1, 2}
    both_topq_R = all(v <= top_quartile_cut for v in r_ranks.values())
    both_topq_M = all(v <= top_quartile_cut for v in m_ranks.values())
    if both_top2_R and both_topq_M:
        verdict = "ASSERTED"
    elif both_topq_R and both_topq_M:
        verdict = "DOWNGRADED"
    else:
        verdict = "DROPPED"
    return dict(verdict=verdict, both_top2_R=bool(both_top2_R),
                both_topquartile_R=bool(both_topq_R),
                both_topquartile_M=bool(both_topq_M))


def run_ranking(members: list[tuple[str, str]]) -> dict:
    """Full E5 ranking under both specs + the graded CHIPS assertion.
    Used verbatim by the synthetic suite and the real run."""
    rank_r = rank_under(members, SPEC_R)
    rank_m = rank_under(members, SPEC_M)
    n = len(members)
    top_quartile_cut = math.ceil(n / 4)   # ranks 1..cut are the top quartile

    chips = [CHIPS_MFG, CHIPS_WHOLESALE]
    r_ranks = {s: _rank_of(rank_r, s) for s in chips}
    m_ranks = {s: _rank_of(rank_m, s) for s in chips}
    graded = chips_graded_verdict(r_ranks, m_ranks, top_quartile_cut)
    both_top2_R = graded["both_top2_R"]
    both_topq_R = graded["both_topquartile_R"]
    both_topq_M = graded["both_topquartile_M"]
    chips_verdict = graded["verdict"]

    return dict(
        spec_R=SPEC_R, spec_M=SPEC_M, roll_win=ROLL_WIN,
        top_quartile_cut=top_quartile_cut,
        ranking_R=rank_r, ranking_M=rank_m,
        chips_sectors=chips,
        chips_ranks_R=r_ranks, chips_ranks_M=m_ranks,
        chips_both_top2_R=bool(both_top2_R),
        chips_both_topquartile_R=bool(both_topq_R),
        chips_both_topquartile_M=bool(both_topq_M),
        chips_verdict=chips_verdict,
        reproduced=True)   # ran to completion on hashed inputs


def main() -> None:
    members = [(sid, title) for sid, role, title in pull.SECTOR_MAP
               if role.startswith("member")]
    assert len(members) == 17
    res = run_ranking(members)
    out = dict(experiment="E5", date="2026-07-13",
               design_pin="74c73ea165a7363c6714fe803fbe76b1", **res)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print(f"E5 reproduced={res['reproduced']}; CHIPS observation: "
          f"{res['chips_verdict']} "
          f"(SPEC-R ranks: 334->A34SIS #{res['chips_ranks_R'][CHIPS_MFG]}, "
          f"machinery R4238 #{res['chips_ranks_R'][CHIPS_WHOLESALE]}; "
          f"SPEC-M ranks #{res['chips_ranks_M'][CHIPS_MFG]}/"
          f"#{res['chips_ranks_M'][CHIPS_WHOLESALE]}; "
          f"top-quartile cut = {res['top_quartile_cut']})")
    print("SPEC-R ranking (top 6 by % months rho > 1):")
    for r in res["ranking_R"][:6]:
        print(f"  #{r['rank']:2d} {r['sector'][:16]:16s} "
              f"{r['title'][:34]:34s} %>1 {r['pct_months_above_1']:.1%} "
              f"peak {r['peak_rho']:.3f}")


if __name__ == "__main__":
    main()
