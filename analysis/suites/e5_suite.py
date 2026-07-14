"""e5_suite.py - E5 mechanism-validation suite (v1.9.5 experiment gate).

E5 is a DESCRIPTIVE ranking with a GRADED assertion rule (no random null). The
verdict logic that can silently break is the graded rule (rank vectors ->
ASSERTED/DOWNGRADED/DROPPED), so the suite tests that PURE rule deterministically
on exact planted rank configurations (imported verbatim from the E5 script),
and separately smoke-tests that the real series->rho-stats->ranking machinery
sorts correctly, computes the right top-quartile cut, and is deterministic.

Legs:
  1. GRADED RULE - exhaustive branch coverage on exact rank vectors:
       ASSERTED   : CHIPS at SPEC-R #1-#2, SPEC-M within top quartile.
       DOWNGRADED : CHIPS top-quartile in both specs but not #1-#2 in SPEC-R.
       DROPPED-a  : a CHIPS sector below the top quartile in SPEC-M.
       DROPPED-b  : CHIPS #1-#2 in SPEC-R but one drops out of SPEC-M top-q.
       DROPPED-c  : neither CHIPS sector in the SPEC-R top quartile.
     All five must map to the correct verdict.
  2. TOP-QUARTILE MATH - cut = ceil(17/4) = 5; boundary ranks (5 in, 6 out).
  3. RANKING SORT + ENGINE SMOKE - the real run_ranking() over synthetic member
     series sorts descending by % months rho > 1; the real sector_rho_stats()
     is deterministic under a fixed seed and returns finite stats in [0, 1].

Firewall: suite failures fix CODE only, never rules/thresholds.
Usage: python analysis\\suites\\e5_suite.py    (no external data touched)
"""

from __future__ import annotations

import math
import pathlib
import sys

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
import e5_instability_ranking as e5  # noqa: E402
from e5_instability_ranking import (CHIPS_MFG, CHIPS_WHOLESALE,  # noqa: E402
                                    ROLL_WIN, chips_graded_verdict,
                                    sector_rho_stats)

N_PERIODS = 410
A, B = CHIPS_MFG, CHIPS_WHOLESALE
CUT = math.ceil(17 / 4)   # top-quartile cut = 5


def leg1_graded_rule() -> bool:
    cases = [
        ("ASSERTED",   {A: 1, B: 2}, {A: 3, B: 5}, "ASSERTED"),
        ("DOWNGRADED", {A: 3, B: 4}, {A: 2, B: 5}, "DOWNGRADED"),
        ("DROPPED-a",  {A: 1, B: 2}, {A: 3, B: 6}, "DROPPED"),   # SPEC-M out
        ("DROPPED-b",  {A: 2, B: 1}, {A: 5, B: 7}, "DROPPED"),   # one SPEC-M out
        ("DROPPED-c",  {A: 6, B: 8}, {A: 6, B: 8}, "DROPPED"),   # SPEC-R out
    ]
    ok = True
    for label, rr, mr, expect in cases:
        got = chips_graded_verdict(rr, mr, CUT)["verdict"]
        hit = got == expect
        ok = ok and hit
        print(f"  {label:12s} R={rr} M={mr} -> {got} "
              f"(want {expect}) {'OK' if hit else 'FAIL'}")
    print(f"LEG 1 graded rule (5 branches) -> {'PASS' if ok else 'FAIL'}")
    return ok


def leg2_topquartile_math() -> bool:
    # rank 5 is in the top quartile, rank 6 is out (n=17, cut=ceil(17/4)=5)
    v_in = chips_graded_verdict({A: 4, B: 5}, {A: 4, B: 5}, CUT)["verdict"]
    v_out = chips_graded_verdict({A: 4, B: 6}, {A: 4, B: 5}, CUT)["verdict"]
    ok = CUT == 5 and v_in == "DOWNGRADED" and v_out == "DROPPED"
    print(f"LEG 2 top-quartile math: cut={CUT} (want 5), rank5-in={v_in=='DOWNGRADED'}, "
          f"rank6-out={v_out=='DROPPED'} -> {'PASS' if ok else 'FAIL'}")
    return ok


def gen_series(rng, instability: float, n=N_PERIODS, sig=0.03, mu=1.5,
               clamp=2.0):
    """I/S series with a controllable INSTABILITY level in [0, 1]: the target
    fraction of the sample running locally-explosive (phi = 1.02) spells in a
    contiguous central block, the rest calm (phi = 0.30). Monotone in
    instability -> monotone in % months rho > 1 (used only for the SORT smoke
    test, where relative order over a coarse spread is all that is checked)."""
    y = np.empty(n)
    x = 0.0
    n_hot = int(round(instability * (n - ROLL_WIN)))
    hot_start = ROLL_WIN + (n - ROLL_WIN - n_hot) // 2
    hot_end = hot_start + n_hot
    for t in range(n):
        phi = 1.02 if (hot_start <= t < hot_end) else 0.30
        x = phi * x + sig * rng.standard_normal()
        x = max(-clamp, min(clamp, x))
        y[t] = mu + x
    return y


def leg3_sort_and_smoke() -> bool:
    # real run_ranking over a coarse instability spread must sort descending
    rng = np.random.default_rng(54)
    levels = {f"S{i:02d}": lv for i, lv in enumerate(
        [0.9, 0.7, 0.5, 0.3, 0.1, 0.0])}
    cache = {sid: gen_series(rng, lv) for sid, lv in levels.items()}
    orig = e5.load_series
    try:
        e5.load_series = lambda sid: cache[sid]
        res = e5.run_ranking([(sid, sid) for sid in levels])
    finally:
        e5.load_series = orig
    pcts = [r["pct_months_above_1"] for r in res["ranking_R"]]
    sorted_ok = all(pcts[i] >= pcts[i + 1] for i in range(len(pcts) - 1))

    # engine smoke: real sector_rho_stats deterministic + valid range
    ya = gen_series(np.random.default_rng(9), 0.6)
    yb = gen_series(np.random.default_rng(9), 0.6)
    sa = sector_rho_stats(ya, 12, 3.0)
    sb = sector_rho_stats(yb, 12, 3.0)
    det = (abs(sa["pct_months_above_1"] - sb["pct_months_above_1"]) < 1e-12
           and math.isfinite(sa["peak_rho"]))
    rng_valid = 0.0 <= sa["pct_months_above_1"] <= 1.0
    ok = sorted_ok and det and rng_valid
    print(f"LEG 3 sort+smoke: descending-sort={sorted_ok}, det={det}, "
          f"pct in [0,1]={rng_valid} -> {'PASS' if ok else 'FAIL'}")
    return ok


def main() -> int:
    print(f"E5 suite: graded-rule branch coverage + ranking machinery "
          f"(n=17, roll_win={ROLL_WIN})")
    r1 = leg1_graded_rule()
    r2 = leg2_topquartile_math()
    r3 = leg3_sort_and_smoke()
    all_pass = r1 and r2 and r3
    print(f"\nALL PASS: {all_pass}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
