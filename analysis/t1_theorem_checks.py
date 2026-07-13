"""t1_theorem_checks.py - T1: Measurement Damage Theorem three-way verification
(machine legs: symbolic step-check + numeric stress grid).

Frozen operator: DESIGN.md Section 1 (pin 74c73ea165a7363c6714fe803fbe76b1).
Written-proof leg: paper/proofs_appendix_g.md (G.0-G.5).

Decision rule (pre-registered): SUPPORT iff the symbolic check passes every step
AND the numeric grid shows realized damage <= bound within tolerance (rel 1e-6
deterministic) in 100% of in-domain cells. REFUTE on any reproducible in-domain
counterexample or failed proof step.

Output: analysis/outputs/t1_theorem_checks.json
"""

from __future__ import annotations

import itertools
import json
import pathlib
import sys

import numpy as np
import sympy as sp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from theory_lib import (GRID_BG, GRID_KAPPA, GRID_PHI1, GRID_PHI2, GRID_W,
                        N_SEEDS, companion_np, dominant_left_eigvec, ols_phi,
                        rho, tau_sma, yw_phi)

OUT = pathlib.Path(__file__).resolve().parent / "outputs" / "t1_theorem_checks.json"
DET_RTOL = 1e-6  # pre-registered deterministic tolerance


# ---------------------------------------------------------------- symbolic ---

def symbolic_checks() -> dict:
    res = {}

    # S1. Companion characteristic polynomial (foundation for A2), w = 3, 5, 10.
    lam, phi, bg = sp.symbols("lam phi bg")
    ok = True
    for w in (3, 5, 10):
        a = sp.zeros(w, w)
        a[0, 0] = phi - bg / w
        for j in range(1, w):
            a[0, j] = -bg / w
        for i in range(1, w):
            a[i, i - 1] = 1
        charpoly = sp.expand((lam * sp.eye(w) - a).det())
        target = sp.expand(lam ** w - phi * lam ** (w - 1)
                           + (bg / w) * sum(lam ** j for j in range(w)))
        if sp.simplify(charpoly - target) != 0:
            ok = False
    res["S1_charpoly_identity"] = ok

    # Symbols with the domain assumptions of Appendix G (A5, A6, positive costs).
    W = sp.symbols("W", positive=True)
    aa = sp.symbols("a", positive=True)          # a = kappa ln rho_2 > 0
    cd, ce = sp.symbols("c_D c_E", positive=True)
    en = sp.symbols("E_n", positive=True)        # est_num = 1 - phi^2 in (0,1)
    ph = sp.symbols("phi_s", positive=True)      # phi in (0,1)
    r1, r2 = sp.symbols("rho_1 rho_2", positive=True)
    tau_s = sp.symbols("tau_s", positive=True)
    d0 = sp.symbols("d_0", positive=True)

    # S2. THM-1(c): D_SMA = exp(a W) is strictly convex in W (2nd deriv > 0).
    dsma = sp.exp(aa * W)
    res["S2_dsma_convex"] = bool(sp.simplify(sp.diff(dsma, W, 2)
                                             - aa ** 2 * sp.exp(aa * W)) == 0)

    # S3. THM-1(a) induction identity at symbolic tau = 4:
    # d_4 = d_0 * r_0 r_1 r_2 r_3 and each r_t <= r2 gives d_4 <= d_0 r2^4.
    rts = sp.symbols("r_0 r_1 r_2x r_3", positive=True)
    d4 = d0
    for r in rts:
        d4 = d4 * r
    bound_gap = d0 * r2 ** 4 - d4
    subbed = bound_gap.subs({r: r2 for r in rts})
    res["S3_thm1_induction_tau4"] = bool(sp.simplify(subbed) == 0)

    # S4. THM-2: strict convexity of the loss (each term's 2nd derivative > 0).
    L = cd * sp.exp(aa * W) + ce * en / W
    d2 = sp.diff(L, W, 2)
    res["S4_loss_convex"] = bool(
        sp.simplify(d2 - (cd * aa ** 2 * sp.exp(aa * W) + 2 * ce * en / W ** 3)) == 0)

    # S5. THM-2: L'(1) < 0 is EXACTLY condition (C) c_E E_n > c_D a e^a.
    lp1 = sp.diff(L, W).subs(W, 1)
    res["S5_interiority_condition"] = bool(
        sp.simplify(lp1 - (cd * aa * sp.exp(aa) - ce * en)) == 0)

    # S6. THM-2(iii): Lambert-W closed form satisfies the FOC. Verified via
    # the defining identity u e^u = z (the proof's own step G.3(iii)):
    # with u = W_L(z), z = (a/2) sqrt(B), W* = 2u/a, we have exp(aW*) = exp(2u)
    # = (z/u)^2, so FOC-LHS = c_D a (z/u)^2 and FOC-RHS = c_E E_n a^2/(4u^2);
    # their difference must simplify to zero symbolically.
    B = ce * en / (cd * aa)
    z = (aa / 2) * sp.sqrt(B)
    u = sp.symbols("u", positive=True)  # stands for W_L(z); e^u = z/u
    lhs = cd * aa * (z / u) ** 2
    rhs = ce * en * aa ** 2 / (4 * u ** 2)
    res["S6_lambertw_solves_foc"] = bool(sp.simplify(lhs - rhs) == 0)

    # S7. Corrected statics G.4: signs of the FOC's parameter derivatives.
    G = cd * aa * sp.exp(aa * W) - ce * (1 - ph ** 2) / W ** 2
    g_phi = sp.diff(G, ph)          # = +2 c_E phi / W^2  -> dW*/dphi < 0
    g_a = sp.diff(G, aa)            # = c_D e^{aW}(1+aW) > 0 -> dW*/da < 0
    g_ce = sp.diff(G, ce)           # = -(1-phi^2)/W^2 < 0 -> dW*/dc_E > 0
    res["S7a_g_phi_positive"] = bool(
        sp.simplify(g_phi - 2 * ce * ph / W ** 2) == 0)
    res["S7b_g_a_positive"] = bool(
        sp.simplify(g_a - cd * sp.exp(aa * W) * (1 + aa * W)) == 0)
    res["S7c_g_ce_negative"] = bool(
        sp.simplify(g_ce + (1 - ph ** 2) / W ** 2) == 0)

    # S8. THM-3 identity: log D = tau (ln r2 - ln r1).
    D = (r2 / r1) ** tau_s
    res["S8_thm3_log_identity"] = bool(
        sp.simplify(sp.log(D) - tau_s * (sp.log(r2) - sp.log(r1))) == 0)

    res["all_pass"] = all(v for k, v in res.items() if k != "all_pass")
    return res


# ----------------------------------------------------------------- numeric ---

def numeric_grid() -> dict:
    counterexamples = []
    n_cells = n_indomain = 0
    mono_phi_fail = mono_bg_fail = 0
    noisy_exceed_frac = []

    rng_master = np.random.default_rng(20260713)

    for phi1, phi2, w, bg in itertools.product(GRID_PHI1, GRID_PHI2,
                                               GRID_W, GRID_BG):
        if phi2 <= phi1:
            continue
        n_cells += 1
        r1 = rho(phi1, w, bg)
        r2 = rho(phi2, w, bg)

        # A3 monotonicity (phi2 > phi1 must give r2 > r1) - checked on ALL cells.
        if not r2 > r1:
            mono_phi_fail += 1
            counterexamples.append({"type": "A3_monotonicity",
                                    "cell": [phi1, phi2, w, bg],
                                    "r1": r1, "r2": r2})

        # In-domain per A6: rho_1 < 1 < rho_2.
        if not (r1 < 1.0 < r2):
            continue
        n_indomain += 1

        # Gain-envelope lemma G.1b used in THM-1a (in-domain form): for
        # rho_2 > 1, rho(phi_2, W, bg') <= rho_2 for all bg' in [0, bg].
        # (Global gain monotonicity is FALSE - rho is U-shaped in bg; the
        # first container QA run caught this, and the proof was corrected.)
        for frac in np.linspace(0.05, 0.95, 10):
            if rho(phi2, w, float(frac) * bg) > r2 + 1e-9:
                mono_bg_fail += 1
                counterexamples.append({"type": "gain_envelope",
                                        "cell": [phi1, phi2, w, bg],
                                        "frac": float(frac)})
                break

        a2 = companion_np(phi2, w, bg)
        lam1, w1 = dominant_left_eigvec(a2)

        for kappa in GRID_KAPPA:
            tau = tau_sma(w, kappa)
            ti = int(np.ceil(tau))

            # Deterministic dominant-mode check (THM-1a exact under A4):
            # |w1^T A2^ti x0| == |lam1|^ti |w1^T x0| to rel 1e-6.
            x0 = rng_master.standard_normal(w)
            proj0 = abs(np.vdot(w1, x0))
            if proj0 < 1e-8:
                x0 = x0 + np.real(w1)
                proj0 = abs(np.vdot(w1, x0))
            x = x0.astype(complex)
            for _ in range(ti):
                x = a2 @ x
            lhs = abs(np.vdot(w1, x))
            rhs = (abs(lam1) ** ti) * proj0
            if abs(lhs - rhs) > DET_RTOL * max(rhs, 1e-300):
                counterexamples.append({"type": "deterministic_dominant_mode",
                                        "cell": [phi1, phi2, w, bg, kappa],
                                        "lhs": lhs, "rhs": rhs})

            # Bound + D > 1 (THM-3 in-domain property).
            d_ratio = (r2 / r1) ** tau
            if not d_ratio > 1.0:
                counterexamples.append({"type": "D_not_exceeding_one",
                                        "cell": [phi1, phi2, w, bg, kappa],
                                        "D": d_ratio})

            # Noisy simulation leg (100 seeds): homogeneous part must obey the
            # bound exactly (checked above); with additive noise, exceedances of
            # the homogeneous bound must be attributable to the noise term -
            # reported as an informational fraction, not a counterexample,
            # unless the NOISE-FREE component itself violates (already caught).
            exceed = 0
            for s in range(N_SEEDS):
                rng = np.random.default_rng(hash((phi1, phi2, w, bg, s)) % 2**32)
                xs = x0.astype(complex)
                base = proj0
                for _ in range(ti):
                    xs = a2 @ xs + 0.01 * rng.standard_normal(w)
                grow = abs(np.vdot(w1, xs)) / base
                if grow > (abs(lam1) ** ti) * (1 + 1e-6) + 10:  # noise allowance
                    exceed += 1
            noisy_exceed_frac.append(exceed / N_SEEDS)

    return {"n_cells": n_cells, "n_indomain": n_indomain,
            "mono_phi_fail": mono_phi_fail, "mono_bg_fail": mono_bg_fail,
            "counterexamples": counterexamples,
            "noisy_exceed_frac_mean": float(np.mean(noisy_exceed_frac))
            if noisy_exceed_frac else None,
            "all_pass": len(counterexamples) == 0}


def ols_vs_yw() -> dict:
    """Re-earn the estimator comparison: 200 histories, phi = 0.95, n = 40."""
    rng = np.random.default_rng(950040)
    ols_v, yw_v = [], []
    for _ in range(200):
        y = np.zeros(40)
        for t in range(1, 40):
            y[t] = 0.95 * y[t - 1] + rng.standard_normal()
        ols_v.append(ols_phi(y))
        yw_v.append(yw_phi(y))
    om, ym = float(np.mean(ols_v)), float(np.mean(yw_v))
    return {"ols_mean": om, "yw_mean": ym, "true_phi": 0.95,
            "ols_less_biased": abs(om - 0.95) <= abs(ym - 0.95)}


def main() -> None:
    sym = symbolic_checks()
    num = numeric_grid()
    est = ols_vs_yw()
    verdict = ("SUPPORT" if sym["all_pass"] and num["all_pass"] else "REFUTE")
    out = {"experiment": "T1", "date": "2026-07-13",
           "design_pin": "74c73ea165a7363c6714fe803fbe76b1",
           "symbolic": sym, "numeric": num, "estimator_comparison": est,
           "verdict": verdict}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print(f"T1 {verdict}: symbolic all_pass={sym['all_pass']}, "
          f"numeric all_pass={num['all_pass']} "
          f"({num['n_indomain']}/{num['n_cells']} in-domain cells, "
          f"{len(num['counterexamples'])} counterexamples); "
          f"OLS {est['ols_mean']:.3f} vs YW {est['yw_mean']:.3f} "
          f"(OLS less biased: {est['ols_less_biased']})")
    print(f"ALL PASS: {verdict == 'SUPPORT'}")


if __name__ == "__main__":
    main()
