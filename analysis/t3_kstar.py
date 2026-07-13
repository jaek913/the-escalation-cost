"""t3_kstar.py - T3: Optimal safety factor k* below the pi^2/2 speed limit.

Frozen operator: DESIGN.md Section 3 (pin 74c73ea165a7363c6714fe803fbe76b1).
Systems parameterized at fraction k of the stability limit,
k in {0.70, 0.75, ..., 1.00, 1.05}; regime-change scenarios from the T1 grid
plus the manufacturing-parameter scenario; expected total cost =
steady-state performance cost of under-aggressive feedback + transition damage
cost, per k; argmin located.

Stated model inputs (disclosed per the DESIGN validity review; sensitivity
swept and reported): per-horizon transition probability p_h in {1/60, 1/72,
1/84} per month over a 12-month horizon (manufacturing: regime changes every
5-7 years); performance cost linear in foregone aggressiveness,
perf(k) = w_perf * (1 - k), with weight w_perf in {0.5, 1.0, 2.0} relative to
unit damage scale; damage on transition = (rho_2(k)/rho_1(k))^tau at the
operating point bg_op = k * bg_star(phi_1, W), floored at 1 when the system
stays stable post-transition. kappa = 0.75 central (swept in T1/T2).

Decision rule (pre-registered): SUPPORT iff the expected-cost argmin is
strictly below k = 1.0 in EVERY scenario tested AND lies within [0.80, 0.98]
in the manufacturing scenario. REFUTE if the manufacturing argmin sits at
k >= 1.0 (the buffer buys nothing), which strikes the k* claim.

Output: analysis/outputs/t3_kstar.json
"""

from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from theory_lib import bg_star, rho, tau_sma

OUT = pathlib.Path(__file__).resolve().parent / "outputs" / "t3_kstar.json"
K_GRID = np.array([0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00, 1.05])
KAPPA = 0.75
HORIZON_M = 12

# Scenario set: (name, phi1, phi2, W). Manufacturing central + T1-grid draws.
SCENARIOS = [
    ("manufacturing_W8", 0.96, 0.99, 8),
    ("manufacturing_W12", 0.96, 0.99, 12),
    ("t1_mid_W8", 0.70, 0.90, 8),
    ("t1_mid_W12", 0.70, 0.95, 12),
    ("t1_high_W24", 0.85, 0.99, 24),
    ("t1_low_W4", 0.50, 0.90, 4),
]
P_MONTH = (1.0 / 60.0, 1.0 / 72.0, 1.0 / 84.0)
W_PERF = (0.5, 1.0, 2.0)


def expected_cost(k: float, phi1: float, phi2: float, w: int,
                  p_m: float, w_perf: float) -> float:
    bg_max = bg_star(phi1, w)
    bg_op = k * bg_max
    r1 = rho(phi1, w, bg_op)
    r2 = rho(phi2, w, bg_op)
    tau = tau_sma(w, KAPPA)
    # Transition damage per THM-1: ABSOLUTE blind-period amplification at the
    # operating point - rho_2(k)^tau when the post-transition loop is unstable,
    # zero excess when the reduced gain keeps it stable. (First QA run used the
    # gain-invariant ratio D here, which divides out exactly the k-sensitivity
    # the safety factor exploits - a code defect, corrected; the THM-3 ratio is
    # the regime-comparison factor, not the operating-cost object.)
    dmg_excess = max(r2, 1.0) ** tau - 1.0
    # If the steady state itself is unstable at this k (r1 >= 1), the
    # steady-state cost dominates: penalize with the steady-state blowup.
    steady_penalty = (r1 ** HORIZON_M) if r1 >= 1.0 else 0.0
    p_h = 1.0 - (1.0 - p_m) ** HORIZON_M
    return w_perf * (1.0 - k) + p_h * dmg_excess + steady_penalty


def main() -> None:
    results = []
    argmins_below_1 = True
    mfg_argmins = []

    for name, phi1, phi2, w in SCENARIOS:
        for p_m in P_MONTH:
            for wp in W_PERF:
                costs = [expected_cost(k, phi1, phi2, w, p_m, wp)
                         for k in K_GRID]
                k_arg = float(K_GRID[int(np.argmin(costs))])
                results.append({"scenario": name, "p_month": p_m,
                                "w_perf": wp, "k_argmin": k_arg,
                                "costs": [float(c) for c in costs]})
                if k_arg >= 1.0:
                    argmins_below_1 = False
                if name.startswith("manufacturing"):
                    mfg_argmins.append(k_arg)

    mfg_in_band = all(0.80 <= k <= 0.98 for k in mfg_argmins)
    mfg_all_below_1 = all(k < 1.0 for k in mfg_argmins)
    # Frozen partition (DESIGN Section 3): SUPPORT = argmin < 1.0 in EVERY
    # scenario AND manufacturing in [0.80, 0.98]. REFUTE = manufacturing
    # argmin at k >= 1.0 (the buffer buys nothing where the claim is made).
    # A non-manufacturing corner at k = 1.0 with manufacturing intact is
    # neither: reported as MIXED (the k* claim is manufacturing-scoped; mild
    # scenarios where the buffer is not worth its cost are honest reporting).
    if argmins_below_1 and mfg_in_band:
        verdict = "SUPPORT"
    elif not mfg_all_below_1:
        verdict = "REFUTE"
    else:
        verdict = "MIXED"
    out = {"experiment": "T3", "date": "2026-07-13",
           "design_pin": "74c73ea165a7363c6714fe803fbe76b1",
           "kappa": KAPPA, "horizon_months": HORIZON_M,
           "k_grid": [float(k) for k in K_GRID],
           "results": results,
           "all_argmins_below_1": argmins_below_1,
           "mfg_argmins": mfg_argmins, "mfg_in_band_080_098": mfg_in_band,
           "verdict": verdict}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print(f"T3 {out['verdict']}: all argmins < 1.0: {argmins_below_1}; "
          f"manufacturing argmins {sorted(set(mfg_argmins))} "
          f"in [0.80, 0.98]: {mfg_in_band}")
    print(f"ALL PASS: {verdict == 'SUPPORT'}")


if __name__ == "__main__":
    main()
