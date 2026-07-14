"""e2_suite.py - E2 mechanism-validation suite (v1.9.5 experiment gate).

Planted-ground-truth validation of the WHOLE E2 pipeline at the real sample
size (n = 17 sectors, single cross-section), importing run_panel() from the
committed E2 script verbatim.

Legs:
  1. PLANTED EFFECT - 17 (D, realized) pairs where realized crisis damage is a
     genuine monotone function of D plus noise. Expect SUPPORT.
  2. PLANTED NULL   - realized independent of D. Expect WEAKENS, and the
     permutation-rule false-positive rate at alpha = 0.10 measured ~nominal
     over 2000 independent 17-sector nulls (accept 0.070 - 0.130).
  3. PLANTED FLIP   - realized a DECREASING function of D. Expect WEAKENS with
     negative Spearman - the rule flips when the truth flips.

Firewall: suite failures fix CODE only, never rules/thresholds.
Usage: python analysis\\suites\\e2_suite.py    (no external data touched)
"""

from __future__ import annotations

import pathlib
import sys

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
from e2_gfc_episode import ALPHA, boot_p, run_panel, spearman  # noqa: E402

N = 17
N_NULL_FP = 2000
FP_BAND = (0.070, 0.130)


def make_rows(rng, mode: str, noise=0.5):
    """mode: 'effect' | 'null' | 'flip'. Returns 17 (name, D, rho_c, dphi,
    realized) rows modeled on the real construction: D = (rho2/rho1)^tau
    depends on BOTH regime endpoints, so it is NOT a rank-copy of any single
    component. rho1 (calm) and rho2 (crisis) are drawn with independent
    scatter; rho_crisis = rho2 and |dphi| are correlated with D but imperfect
    proxies (the realistic case the rule's 'combined >= components' clause
    tests - D aggregates intensity AND duration, so it should rank realized
    damage at least as well as either piece alone)."""
    phi1 = rng.uniform(0.60, 0.90, N)          # calm persistence
    bump = rng.uniform(0.03, 0.22, N)          # crisis persistence jump
    phi2 = np.minimum(phi1 + bump, 0.995)
    # rho proxies (monotone in phi within this range) with independent noise
    rho1 = 0.7 + 0.5 * phi1 + 0.01 * rng.standard_normal(N)
    rho2 = 0.7 + 0.5 * phi2 + 0.01 * rng.standard_normal(N)
    D = (rho2 / rho1) ** 6.0
    rho_c = rho2
    dphi = phi2 - phi1
    # true crisis damage is driven by the COMPOUND (log D), i.e. intensity x
    # duration together - the thesis - plus idiosyncratic noise.
    z = (np.log(D) - np.log(D).mean()) / np.log(D).std()
    if mode == "effect":
        realized = 0.8 * z + noise * rng.standard_normal(N)
    elif mode == "flip":
        realized = -0.8 * z + noise * rng.standard_normal(N)
    else:  # null
        realized = noise * rng.standard_normal(N)
    order = np.argsort(D)
    return [(f"s{i:02d}", float(D[j]), float(rho_c[j]), float(dphi[j]),
             float(realized[j])) for i, j in enumerate(order)]


def leg1_effect() -> bool:
    rng = np.random.default_rng(1201)
    res = run_panel(make_rows(rng, "effect"), seed=1201)
    ok = res["verdict"] == "SUPPORT"
    print(f"LEG 1 planted effect: verdict={res['verdict']} "
          f"(S_D={res['spearman_D']:+.3f} p={res['p_one_sided']:.4f}, "
          f"combined>=comp={res['combined_ge_components']}) "
          f"-> {'PASS' if ok else 'FAIL'}")
    return ok


def leg2_null() -> bool:
    rng = np.random.default_rng(1202)
    res = run_panel(make_rows(rng, "null"), seed=1202)
    verdict_ok = res["verdict"] == "WEAKENS"
    print(f"LEG 2 planted null: verdict={res['verdict']} "
          f"(S_D={res['spearman_D']:+.3f} p={res['p_one_sided']:.4f}) "
          f"-> {'PASS' if verdict_ok else 'FAIL'}")
    rng_fp = np.random.default_rng(1302)
    hits = 0
    for _ in range(N_NULL_FP):
        D = np.sort(rng_fp.uniform(1.0, 3.0, N))
        realized = rng_fp.standard_normal(N)
        obs, p = boot_p(D, realized, rng_fp, b=1000)
        if obs > 0 and p < ALPHA:
            hits += 1
    fp = hits / N_NULL_FP
    fp_ok = FP_BAND[0] <= fp <= FP_BAND[1]
    print(f"LEG 2 FP rate: {hits}/{N_NULL_FP} = {fp:.4f} "
          f"(nominal {ALPHA}, band {FP_BAND}) -> {'PASS' if fp_ok else 'FAIL'}")
    return verdict_ok and fp_ok


def leg3_flip() -> bool:
    rng = np.random.default_rng(1203)
    res = run_panel(make_rows(rng, "flip"), seed=1203)
    ok = res["verdict"] == "WEAKENS" and res["spearman_D"] < 0
    print(f"LEG 3 planted flip: verdict={res['verdict']} "
          f"(S_D={res['spearman_D']:+.3f} p={res['p_one_sided']:.4f}) "
          f"-> {'PASS' if ok else 'FAIL'}")
    return ok


def main() -> int:
    print(f"E2 suite: n={N} sectors (real cross-section); permutation null "
          f"B=2000 (verdict), 1000 (FP leg), {N_NULL_FP} null panels")
    r1 = leg1_effect()
    r2 = leg2_null()
    r3 = leg3_flip()
    all_pass = r1 and r2 and r3
    print(f"\nALL PASS: {all_pass}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
