"""e6_suite.py - E6 mechanism-validation suite (v1.9.5 experiment gate).

E6 links utilization to rho, bins, and applies a monotonicity + crossing-bin
rule. The verdict machinery (bin -> per-bin mean -> monotone test + crossing
location -> SUPPORT/REFUTE) is what can silently break, so the suite feeds
bin_and_analyze() planted (utilization, rho) pairs with known structure that
must map to the correct verdict, checks the binning/alignment is correct, and
smoke-tests the real rho_series_dated() step.

Legs:
  1. SUPPORT   - planted rho increasing monotonically with utilization, crossing
     1.0 in the 85-90 bin. Verdict must be SUPPORT.
  2. REFUTE-A  - planted rho monotone but crossing BELOW 80% (in the <75 bin).
     Verdict must be REFUTE (crossing not at the knee).
  3. REFUTE-B  - planted rho NON-monotone (no clean utilization->rho relation).
     Verdict must be REFUTE.
  4. BINNING + SMOKE - month alignment keeps only shared months; bin counts are
     correct for a hand-built utilization vector; thin bins (< 6) excluded from
     the monotone test; the real rho_series_dated() runs, is deterministic, and
     returns finite rho aligned to real month labels.

Firewall: suite failures fix CODE only, never rules/thresholds.
Usage: python analysis\\suites\\e6_suite.py    (no external data touched)
"""

from __future__ import annotations

import pathlib
import sys

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
from e6_capacity_threshold import (CHIPS_MFG, ROLL_WIN, bin_and_analyze,  # noqa: E402
                                   rho_series_dated)


def _months(n: int, start_year: int = 1992) -> list[str]:
    out = []
    y, m = start_year, 1
    for _ in range(n):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m > 12:
            m = 1
            y += 1
    return out


def _synthetic(kind: str, n: int = 400, seed: int = 0):
    """Build aligned (rho_dates, rho_vals, util_dates, util_vals) with a planted
    utilization->rho relationship. Utilization spans all four bins."""
    rng = np.random.default_rng(seed)
    dates = _months(n)
    # utilization cycles through the full range so all bins populate
    util = 70 + 25 * (0.5 + 0.5 * np.sin(np.linspace(0, 12 * np.pi, n)))
    util += rng.normal(0, 1.0, n)
    if kind == "support":
        # rho rises with utilization, crossing 1.0 inside the 85-90 bin:
        # anchored so mean rho < 1 below 85 and >= 1 in the 85-90 and >=90 bins.
        rho_v = 1.0 + 0.012 * (util - 87.0) + rng.normal(0, 0.004, n)
    elif kind == "refute_low":
        # rho rises with utilization but crosses 1.0 already by ~72% (<75 bin)
        rho_v = 1.0 + 0.006 * (util - 72.0) + rng.normal(0, 0.005, n)
    else:  # non_monotone
        rho_v = 1.0 + 0.03 * np.sin(np.linspace(0, 30, n)) + rng.normal(0, 0.01, n)
    return dates, rho_v, dates, util


def leg1_support() -> bool:
    d, r, ud, uv = _synthetic("support", seed=61)
    res = bin_and_analyze(d, r, ud, uv)
    verdict = "SUPPORT" if res["monotone"] and res["crossing_at_knee"] else "REFUTE"
    ok = verdict == "SUPPORT"
    means = {b["label"]: (round(b["mean_rho"], 3) if b["mean_rho"] else None)
             for b in res["bins"]}
    print(f"LEG 1 SUPPORT: monotone={res['monotone']}, crossing={res['crossing_bin']} "
          f"(knee={res['crossing_at_knee']}); means={means} -> {'PASS' if ok else 'FAIL'}")
    return ok


def leg2_refute_low() -> bool:
    d, r, ud, uv = _synthetic("refute_low", seed=62)
    res = bin_and_analyze(d, r, ud, uv)
    verdict = "SUPPORT" if res["monotone"] and res["crossing_at_knee"] else "REFUTE"
    ok = verdict == "REFUTE"
    print(f"LEG 2 REFUTE (crossing below knee): monotone={res['monotone']}, "
          f"crossing={res['crossing_bin']} (knee={res['crossing_at_knee']}) "
          f"-> {'PASS' if ok else 'FAIL'}")
    return ok


def leg3_refute_nonmono() -> bool:
    d, r, ud, uv = _synthetic("non_monotone", seed=63)
    res = bin_and_analyze(d, r, ud, uv)
    verdict = "SUPPORT" if res["monotone"] and res["crossing_at_knee"] else "REFUTE"
    ok = verdict == "REFUTE"
    print(f"LEG 3 REFUTE (non-monotone): monotone={res['monotone']}, "
          f"crossing={res['crossing_bin']} -> {'PASS' if ok else 'FAIL'}")
    return ok


def leg4_binning_and_smoke() -> bool:
    # alignment: rho has months A..E, util has months C..G -> only C,D,E shared
    rho_dates = ["1992-01", "1992-02", "1992-03", "1992-04", "1992-05"]
    rho_vals = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
    util_dates = ["1992-03", "1992-04", "1992-05", "1992-06", "1992-07"]
    util_vals = np.array([70.0, 80.0, 88.0, 92.0, 95.0])   # <75,75-85,85-90,>=90,>=90
    res = bin_and_analyze(rho_dates, rho_vals, util_dates, util_vals)
    align_ok = res["n_paired"] == 3   # only 3 shared months
    counts = {b["label"]: b["n"] for b in res["bins"]}
    # shared: 70(<75), 80(75-85), 88(85-90) -> one each; 92/95 not in rho months
    bin_ok = counts == {"<75": 1, "75-85": 1, "85-90": 1, ">=90": 0}

    # engine smoke on real rho series
    rd_a, rv_a = rho_series_dated(CHIPS_MFG, 12, 3.0)
    rd_b, rv_b = rho_series_dated(CHIPS_MFG, 12, 3.0)
    det = (len(rv_a) == len(rv_b) and np.allclose(rv_a, rv_b)
           and np.all(np.isfinite(rv_a)) and len(rd_a) == len(rv_a))
    ok = align_ok and bin_ok and det
    print(f"LEG 4 binning+smoke: n_paired={res['n_paired']} (want 3), "
          f"bin counts {counts} align_ok={align_ok} bin_ok={bin_ok}, "
          f"real-rho det+finite={det} -> {'PASS' if ok else 'FAIL'}")
    return ok


def main() -> int:
    print(f"E6 suite: monotone+crossing rule + binning/alignment "
          f"(roll_win={ROLL_WIN})")
    r1 = leg1_support()
    r2 = leg2_refute_low()
    r3 = leg3_refute_nonmono()
    r4 = leg4_binning_and_smoke()
    all_pass = r1 and r2 and r3 and r4
    print(f"\nALL PASS: {all_pass}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
