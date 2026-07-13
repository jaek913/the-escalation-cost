"""t2_wstar.py - T2: Optimal window W* - Lambert-W closed form vs brute force.

Frozen operator: DESIGN.md Section 2 (pin 74c73ea165a7363c6714fe803fbe76b1).
Cost model per DESIGN + Appendix G.3: L(W) = c_D rho_2^{kappa W} + c_E (1-phi^2)/W,
computed over integer W in [2, 120] across the T1 in-domain grid.

Model-reading notes (documented, not searched): rho_2 is the cell's parameter,
held fixed while W is swept (the theorem's cost model treats rho_2 as the
regime-intensity parameter); the estimation-cost phi is the calm-regime phi_1
(the persistence being estimated in steady state); c_D = c_E = 1 (the DESIGN
states proportionality; equal unit constants are the canonical frozen reading,
with condition (C) then classifying each cell as interior or boundary).

Decision rule (pre-registered): SUPPORT iff closed-form W* matches the numeric
argmin within +/-1 grid step in >= 99% of in-domain interior cells AND every
cell's cost curve is unimodal. REFUTE on systematic mismatch or non-unique /
boundary minima where the theorem asserts a unique interior optimum.

Output: analysis/outputs/t2_wstar.json
"""

from __future__ import annotations

import itertools
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from theory_lib import (GRID_BG, GRID_KAPPA, GRID_PHI1, GRID_PHI2, GRID_W,
                        interiority_c, loss, rho, wstar_closed)

OUT = pathlib.Path(__file__).resolve().parent / "outputs" / "t2_wstar.json"
W_SWEEP = np.arange(2, 121)


def unimodal(vals: np.ndarray) -> bool:
    d = np.sign(np.diff(vals))
    d = d[d != 0]
    if len(d) == 0:
        return True
    flips = int(np.sum(np.abs(np.diff(d)) > 0))
    return flips <= 1 and (len(d) == 0 or d[-1] >= 0 or flips == 0)


def main() -> None:
    interior_total = interior_match = 0
    boundary_cells = unimodal_fail = 0
    mismatches = []

    for phi1, phi2, w, bg, kappa in itertools.product(
            GRID_PHI1, GRID_PHI2, GRID_W, GRID_BG, GRID_KAPPA):
        if phi2 <= phi1:
            continue
        r1 = rho(phi1, w, bg)
        r2 = rho(phi2, w, bg)
        if not (r1 < 1.0 < r2):
            continue

        a = kappa * np.log(r2)
        est_num = 1.0 - phi1 ** 2
        curve = np.array([loss(wv, a, est_num) for wv in W_SWEEP])
        arg = int(W_SWEEP[int(np.argmin(curve))])

        if not unimodal(curve):
            unimodal_fail += 1
            mismatches.append({"type": "unimodality",
                               "cell": [phi1, phi2, w, bg, kappa]})

        ws = wstar_closed(a, est_num)
        if ws < 2.0 or not interiority_c(a, est_num):
            # Boundary regime per G.3(ii): expect the swept argmin at the left
            # edge; consistency check, excluded from the interior +/-1 statistic.
            boundary_cells += 1
            if arg > 3:
                mismatches.append({"type": "boundary_inconsistency",
                                   "cell": [phi1, phi2, w, bg, kappa],
                                   "wstar": ws, "argmin": arg})
            continue

        interior_total += 1
        if abs(round(ws) - arg) <= 1:
            interior_match += 1
        else:
            mismatches.append({"type": "interior_mismatch",
                               "cell": [phi1, phi2, w, bg, kappa],
                               "wstar": ws, "argmin": arg})

    match_rate = (interior_match / interior_total) if interior_total else 1.0
    support = (match_rate >= 0.99 and unimodal_fail == 0
               and not any(m["type"] == "boundary_inconsistency"
                           for m in mismatches))
    out = {"experiment": "T2", "date": "2026-07-13",
           "design_pin": "74c73ea165a7363c6714fe803fbe76b1",
           "interior_cells": interior_total, "interior_match": interior_match,
           "match_rate": match_rate, "boundary_cells": boundary_cells,
           "unimodal_failures": unimodal_fail,
           "mismatches": mismatches[:50],
           "verdict": "SUPPORT" if support else "REFUTE"}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print(f"T2 {out['verdict']}: interior match {interior_match}/{interior_total} "
          f"({match_rate:.1%}), boundary cells {boundary_cells}, "
          f"unimodal failures {unimodal_fail}")
    print(f"ALL PASS: {support}")


if __name__ == "__main__":
    main()
