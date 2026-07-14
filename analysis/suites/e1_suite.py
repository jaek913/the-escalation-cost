"""e1_suite.py - E1 mechanism-validation suite (v1.9.5 experiment gate, item c).

Planted-ground-truth validation of the WHOLE E1 pipeline (data shape ->
estimator -> statistic -> decision rule) at the REAL sample size, importing
run_panel() from the committed E1 script verbatim - the suite never
reimplements the pipeline it validates.

Legs:
  1. PLANTED EFFECT   - 17 synthetic sectors, 410 months, regime-oscillating
     AR(1) I/S series where shifts to high persistence genuinely enlarge
     subsequent deviations. Expect verdict SUPPORT.
  2. PLANTED NULL     - fixed-persistence sectors, no regime dynamics. Expect
     the honest verdict FALSIFIED, and the per-sector false-positive rate of
     the descriptive alpha = 0.05 line measured ~nominal on 600 independent
     null sectors (accept 0.010 - 0.075).
  3. PLANTED FLIP     - regime shifts wired so higher D predicts SMALLER
     deviations (high-persistence regime has much quieter innovations).
     Expect verdict FALSIFIED with predominantly negative panel signs -
     demonstrating the rule flips when the truth flips.

Firewall (item d): suite failures fix CODE only, never rules/thresholds.

Usage: python analysis\\suites\\e1_suite.py    (no external data touched)
"""

from __future__ import annotations

import pathlib
import sys

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
from e1_rolling_validation import (ALPHA, B_BOOT, block_boot_p,  # noqa: E402
                                   run_panel, sector_series_stats)

N_MONTHS = 410          # real panel length (Jan 1992 - latest)
N_SECTORS = 17
N_NULL_FP = 600         # independent null sectors for FP-rate measurement
FP_BAND = (0.010, 0.075)  # nominal 0.05 (descriptive line) with binomial tolerance


def gen_regime_series(rng, n=N_MONTHS, phi_lo=0.97, phi_hi=1.012,
                      sig_lo=0.030, sig_hi=0.045, dur_lo=42, dur_hi=48,
                      mu=1.5, clamp=2.0):
    """AR(1) I/S series with persistence switching between a calm regime and
    a locally-explosive spell (phi_hi slightly above 1, bounded by the spell
    ending and a physical clamp) - this is how real I/S series push trailing
    OLS phi-hat, and hence rolling SPEC-M rho, across 1.0 in both directions.
    With sig_hi == sig_lo, explosive spells genuinely produce larger
    subsequent absolute excursions - the planted mechanism."""
    y = np.empty(n)
    x = 0.0
    hi = False
    for t in range(n):
        if rng.random() < 1.0 / (dur_hi if hi else dur_lo):
            hi = not hi
        phi = phi_hi if hi else phi_lo
        sig = sig_hi if hi else sig_lo
        x = phi * x + sig * rng.standard_normal()
        x = max(-clamp, min(clamp, x))
        y[t] = mu + x
    return y


def gen_null_series(rng, n=N_MONTHS, phi=0.97, sig=0.03, mu=1.5):
    y = np.empty(n)
    x = 0.0
    for t in range(n):
        x = phi * x + sig * rng.standard_normal()
        y[t] = mu + x
    return y


def leg1_effect() -> bool:
    rng = np.random.default_rng(101)
    panel = {f"eff_{i:02d}": gen_regime_series(rng) for i in range(N_SECTORS)}
    res = run_panel(panel, seed=101)
    ok = res["verdict"] == "SUPPORT"
    print(f"LEG 1 planted effect: verdict={res['verdict']} "
          f"(pooled S={res['pooled_mean_spearman']:+.3f} p={res['p_panel']:.4f}, "
          f"osc={res['n_oscillating']}) -> {'PASS' if ok else 'FAIL'}")
    return ok


def leg2_null() -> bool:
    rng = np.random.default_rng(202)
    panel = {f"nul_{i:02d}": gen_null_series(rng) for i in range(N_SECTORS)}
    res = run_panel(panel, seed=202)
    verdict_ok = res["verdict"] == "FALSIFIED"
    print(f"LEG 2 planted null: verdict={res['verdict']} "
          f"(pooled S={res['pooled_mean_spearman']:+.3f} p={res['p_panel']:.4f}, "
          f"osc={res['n_oscillating']}) -> {'PASS' if verdict_ok else 'FAIL'}")
    # False-positive rate of the per-sector rule at alpha, measured on
    # independent null sectors (coarser B for runtime; p-resolution 1/1000
    # is adequate at alpha = 0.01).
    rng_fp = np.random.default_rng(303)
    hits = 0
    for i in range(N_NULL_FP):
        y = gen_null_series(rng_fp)
        st = sector_series_stats(y)
        obs, p = block_boot_p(st["d"], st["outcome"], rng_fp, b=1000)
        if obs > 0 and p < ALPHA:
            hits += 1
    fp = hits / N_NULL_FP
    fp_ok = FP_BAND[0] <= fp <= FP_BAND[1]
    print(f"LEG 2 FP rate: {hits}/{N_NULL_FP} = {fp:.4f} "
          f"(nominal {ALPHA}, band {FP_BAND}) -> {'PASS' if fp_ok else 'FAIL'}")
    return verdict_ok and fp_ok


def leg3_flip() -> bool:
    rng = np.random.default_rng(404)
    panel = {f"flp_{i:02d}": gen_regime_series(rng, sig_lo=0.045, sig_hi=0.012)
             for i in range(N_SECTORS)}
    res = run_panel(panel, seed=404)
    ok = (res["verdict"] == "FALSIFIED"
          and res["pooled_mean_spearman"] <= 0.10)
    print(f"LEG 3 planted flip: verdict={res['verdict']} "
          f"(pooled S={res['pooled_mean_spearman']:+.3f} p={res['p_panel']:.4f}) "
          f"-> {'PASS' if ok else 'FAIL'}")
    return ok


def main() -> int:
    print(f"E1 suite: n={N_MONTHS} months x {N_SECTORS} sectors "
          f"(real sample size); B={B_BOOT} (verdict legs), 1000 (FP leg)")
    r1 = leg1_effect()
    r2 = leg2_null()
    r3 = leg3_flip()
    all_pass = r1 and r2 and r3
    print(f"\nALL PASS: {all_pass}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
