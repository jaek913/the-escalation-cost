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
    # real run_ranking over a coarse instability spread must sort descending by
    # the AMENDED primary key (mean_exceedance)
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
    exc = [r["mean_exceedance"] for r in res["ranking_R"]]
    sorted_ok = all(exc[i] >= exc[i + 1] for i in range(len(exc) - 1))

    # engine smoke: real sector_rho_stats deterministic + valid range
    ya = gen_series(np.random.default_rng(9), 0.6)
    yb = gen_series(np.random.default_rng(9), 0.6)
    sa = sector_rho_stats(ya, 12, 3.0)
    sb = sector_rho_stats(yb, 12, 3.0)
    det = (abs(sa["mean_exceedance"] - sb["mean_exceedance"]) < 1e-12
           and math.isfinite(sa["peak_rho"]) and math.isfinite(sa["mean_exceedance"]))
    valid = sa["mean_exceedance"] >= 0.0 and 0.0 <= sa["pct_months_above_1"] <= 1.0
    ok = sorted_ok and det and valid
    print(f"LEG 3 sort+smoke: descending-sort(mean_exc)={sorted_ok}, det={det}, "
          f"valid={valid} -> {'PASS' if ok else 'FAIL'}")
    return ok


def _constant_phi_series(rng, phi_true: float, n=N_PERIODS, sig=0.03, mu=1.5,
                         clamp=2.5):
    """AR(1) series at a constant target persistence (no spells). A steady high
    phi keeps rolling rho above 1 for essentially the whole sample, so the old
    '% months rho > 1' key pegs to 1.0 (saturates) while mean_exceedance still
    varies with phi - the exact contrast the redesign fixes."""
    y = np.empty(n)
    x = 0.0
    for t in range(n):
        x = phi_true * x + sig * rng.standard_normal()
        x = max(-clamp, min(clamp, x))
        y[t] = mu + x
    return y


def leg4_non_saturation() -> bool:
    """Core purpose of the 2026-07-13 redesign: the primary key must NOT
    saturate where the old '% months rho > 1' key did. Build four sectors at
    steady high persistence (phi 0.995/0.99/0.985/0.98) that ALL peg the old
    binary key at exactly 1.0 (100% months above the boundary - reproducing the
    six-way-tie defect from the first real run), and confirm (a) the old key
    ties them at 100% while (b) mean_exceedance gives them DISTINCT, strictly
    ordered values - i.e. the ruler now has dynamic range at the top where the
    old one had none."""
    phis = [0.995, 0.99, 0.985, 0.98]   # descending instability, all saturating
    # average the statistic over several seeds per phi: the real test uses one
    # long 34-year series per sector (noise averages out), so the instrument
    # property (monotone in phi, non-saturating) is what must hold - a single
    # short synthetic draw carries enough sampling noise to reorder adjacent
    # near-identical phis, which is a generator artifact, not a key defect.
    def avg_stats(phi_true, seeds=8):
        pcts, excs = [], []
        for s in range(seeds):
            st = sector_rho_stats(
                _constant_phi_series(np.random.default_rng(100 + s), phi_true),
                12, 3.0)
            pcts.append(st["pct_months_above_1"])
            excs.append(st["mean_exceedance"])
        return float(np.mean(pcts)), float(np.mean(excs))
    agg = [avg_stats(p) for p in phis]
    pcts = [a[0] for a in agg]
    excs = [a[1] for a in agg]
    # (a) old binary key saturates: all tied at exactly 1.0
    old_key_saturates = (max(pcts) - min(pcts) < 1e-9) and min(pcts) > 0.999
    # (b) mean_exceedance strictly orders them (distinguishable, not float noise)
    new_key_orders = all(excs[i] > excs[i + 1] + 1e-5 for i in range(len(excs) - 1))
    new_key_spread = (max(excs) - min(excs)) > 1e-3
    ok = old_key_saturates and new_key_orders and new_key_spread
    print(f"LEG 4 non-saturation: old %>1 ties@100%={old_key_saturates} "
          f"(pcts={[round(p, 4) for p in pcts]}); mean_exc strictly-orders="
          f"{new_key_orders} + spread={new_key_spread} "
          f"(excs={[round(e, 4) for e in excs]}) -> {'PASS' if ok else 'FAIL'}")
    return ok


def main() -> int:
    print(f"E5 suite: graded-rule branch coverage + ranking machinery + "
          f"non-saturation (n=17, roll_win={ROLL_WIN})")
    r1 = leg1_graded_rule()
    r2 = leg2_topquartile_math()
    r3 = leg3_sort_and_smoke()
    r4 = leg4_non_saturation()
    all_pass = r1 and r2 and r3 and r4
    print(f"\nALL PASS: {all_pass}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
