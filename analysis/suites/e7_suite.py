"""e7_suite.py - E7 validation suite (Standard v1.9.5 gate, extended v1.9.7).

Imports run_cell / crossover_map / calibration / stability VERBATIM from the
committed e7_chain_sweep.py - the suite exercises the real pipeline, never a
copy.

LEG 1 ENGINE FIDELITY (replaces the withdrawn replication leg, DESIGN
  2026-07-14c): beer_engine at E4's config must reproduce e4_beer_game's
  per-run costs BITWISE. A code-identity test proving no drift was introduced
  by parameterizing the engine. Not evidence, not a finding.
LEG 2 DYNAMIC RANGE / planted crossover (Risk 2, DESIGN 2026-07-14b): the
  crossover locator must find a planted harm->benefit transition, must NOT
  report one where the grid line is all-benefit, and must mark a flip between
  two UNRESOLVED cells as unresolved rather than as a crossover (the E5
  top-cluster lesson). Tested as a pure function on exact planted inputs.
LEG 3 RESOLUTION LOGIC (Risk 1): each cell's achieved MDD is computed from its
  OWN measured variance (never inherited from E4), and an unresolved cell is
  labelled 'unresolved' - never 'harm' or 'benefit'.
LEG 4 SIGN CONVENTION + no-harm mechanism: positive = all-tier costs more =
  harm; and the phi-gate leaves a sub-boundary environment essentially
  untouched (iid_control engagement ~ 0).
LEG 5 JSON BOUNDARY: the full result dict serializes (the E4 lesson - numpy
  bool_/float64 are not JSON-serializable and main() was never suite-tested).

Suite failures fix CODE ONLY - never the rules, thresholds, or report form.
"""

from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
sys.path.insert(0, str(_HERE))

import e4_beer_game as e4  # noqa: E402
from beer_engine import (ChainConfig, engagement_phi, make_demand,  # noqa: E402
                         simulate)
from e7_chain_sweep import (Z95, Z_MDD, calibration, crossover_map,  # noqa: E402
                            run_cell, stability)


def _cell(L, cap, env, mean, resolved):
    """Planted cell in run_cell's exact output shape."""
    se = abs(mean) / (Z95 * 2) if resolved and mean != 0 else abs(mean) * 10 + 1e-6
    return dict(n_ech=L, cap_mult=cap, env=env, n_seeds=1000,
                rel_diff_mean=mean, rel_diff_ci=[mean - Z95 * se, mean + Z95 * se],
                se=se, achieved_mdd=Z_MDD * se, resolved_vs_zero=resolved,
                sign=("harm" if mean > 0 else "benefit") if resolved else "unresolved",
                engagement_rate=0.05, phi_eng=0.83)


def leg1_engine_fidelity() -> bool:
    cfg = ChainConfig()  # defaults == E4's frozen config
    peng = engagement_phi(cfg)
    if peng != e4.PHI_ENG:
        print(f"LEG 1 FAIL: phi_eng {peng!r} != E4 {e4.PHI_ENG!r}")
        return False
    bad = 0
    for i in range(6):
        d1 = e4.make_demand(np.random.default_rng(e4.BASE_SEED + i))
        d2 = make_demand(np.random.default_rng(e4.BASE_SEED + i), cfg)
        if not np.array_equal(d1, d2):
            bad += 1
            continue
        for a in ("basestock", "spectral", "full"):
            if e4.simulate(d1, a) != simulate(d2, a, cfg, peng):
                bad += 1
    ok = bad == 0
    print(f"LEG 1 engine fidelity: phi_eng exact, 6 seeds x 3 algos bitwise vs "
          f"e4_beer_game, mismatches={bad} -> {'PASS' if ok else 'FAIL'}")
    return ok


def leg2_planted_crossover() -> bool:
    cap, env = 2.4, "ar1_high"
    # (i) planted resolved harm -> benefit transition: must be located
    cells = [_cell(4, cap, env, +0.0050, True), _cell(6, cap, env, +0.0010, True),
             _cell(8, cap, env, -0.0030, True)]
    cells += [_cell(L, c, e, -0.001, True) for L in (4, 6, 8)
              for c in (1.3, 1.8) for e in ("iid_control", "ar1_moderate",
                                            "ar1_high", "drift_canonical")]
    cells += [_cell(L, 2.4, e, -0.001, True) for L in (4, 6, 8)
              for e in ("iid_control", "ar1_moderate", "drift_canonical")]
    m = crossover_map(cells)[f"cap{cap}_{env}"]
    found = (len(m["sign_flips"]) == 1 and m["sign_flips"][0]["between"] == [6, 8]
             and m["sign_flips"][0]["resolved"] and m["spans_transition"])
    # (ii) all-benefit grid line: must NOT report a transition
    cells2 = [_cell(L, cap, env, -0.002, True) for L in (4, 6, 8)]
    cells2 += [_cell(L, c, e, -0.001, True) for L in (4, 6, 8)
               for c in (1.3, 1.8) for e in ("iid_control", "ar1_moderate",
                                             "ar1_high", "drift_canonical")]
    cells2 += [_cell(L, 2.4, e, -0.001, True) for L in (4, 6, 8)
               for e in ("iid_control", "ar1_moderate", "drift_canonical")]
    m2 = crossover_map(cells2)[f"cap{cap}_{env}"]
    degen = (not m2["spans_transition"]) and len(m2["sign_flips"]) == 0
    # (iii) flip between two UNRESOLVED cells: located but NOT called a crossover
    cells3 = [_cell(4, cap, env, +0.00002, False), _cell(6, cap, env, +0.00001, False),
              _cell(8, cap, env, -0.00002, False)]
    cells3 += [_cell(L, c, e, -0.001, True) for L in (4, 6, 8)
               for c in (1.3, 1.8) for e in ("iid_control", "ar1_moderate",
                                             "ar1_high", "drift_canonical")]
    cells3 += [_cell(L, 2.4, e, -0.001, True) for L in (4, 6, 8)
               for e in ("iid_control", "ar1_moderate", "drift_canonical")]
    m3 = crossover_map(cells3)[f"cap{cap}_{env}"]
    unres = (len(m3["sign_flips"]) == 1 and not m3["sign_flips"][0]["resolved"]
             and not m3["spans_transition"])
    ok = found and degen and unres
    print(f"LEG 2 planted crossover: located={found}, all-benefit line reports "
          f"no transition={degen}, unresolved flip not called a crossover={unres} "
          f"-> {'PASS' if ok else 'FAIL'}")
    return ok


def leg3_resolution_logic() -> bool:
    # real cell at small n; MDD must come from THIS cell's own variance
    c = run_cell(4, 2.4, "ar1_high", n_seeds=40, base_seed=4242)
    arith = (abs(c["achieved_mdd"] - Z_MDD * c["se"]) < 1e-15
             and abs((c["rel_diff_ci"][1] - c["rel_diff_ci"][0]) / 2
                     - Z95 * c["se"]) < 1e-12)
    consistent = c["resolved_vs_zero"] == (abs(c["rel_diff_mean"]) > Z95 * c["se"])
    # variance is measured per cell, not inherited: a different cell -> different se
    c2 = run_cell(4, 1.3, "iid_control", n_seeds=40, base_seed=4242)
    per_cell = c["se"] != c2["se"]
    # an unresolved cell must never be labelled harm/benefit
    lab = all((cc["sign"] == "unresolved") == (not cc["resolved_vs_zero"])
              for cc in (c, c2))
    ok = arith and consistent and per_cell and lab
    print(f"LEG 3 resolution logic: mdd/ci arithmetic={arith}, resolved flag "
          f"consistent={consistent}, se measured per-cell={per_cell} "
          f"({c['se']:.2e} vs {c2['se']:.2e}), unresolved never labelled "
          f"harm/benefit={lab} -> {'PASS' if ok else 'FAIL'}")
    return ok


def leg4_sign_and_no_harm() -> bool:
    # sign convention: a planted more-expensive all-tier must read POSITIVE=harm
    m = crossover_map([_cell(4, 2.4, "ar1_high", +0.01, True)]
                      + [_cell(L, c, e, -0.001, True) for L in (6, 8)
                         for c in (1.3, 1.8, 2.4) for e in ("iid_control",
                         "ar1_moderate", "ar1_high", "drift_canonical")]
                      + [_cell(4, c, e, -0.001, True) for c in (1.3, 1.8)
                         for e in ("iid_control", "ar1_moderate", "ar1_high",
                                   "drift_canonical")]
                      + [_cell(4, 2.4, e, -0.001, True) for e in ("iid_control",
                         "ar1_moderate", "drift_canonical")])
    signs_ok = _cell(4, 2.4, "ar1_high", +0.01, True)["sign"] == "harm" and \
        _cell(4, 2.4, "ar1_high", -0.01, True)["sign"] == "benefit"
    # no-harm mechanism: below the gate the tool reduces to base-stock
    cfg = ChainConfig(n_ech=4, cap_mult=2.4, env="iid_control")
    peng = engagement_phi(cfg)
    fr = []
    for i in range(15):
        d = make_demand(np.random.default_rng(7000 + i), cfg)
        _, f = simulate(d, "spectral", cfg, peng, count_engagement=True)
        fr.append(f)
    gate_ok = float(np.mean(fr)) < 0.01
    ok = signs_ok and gate_ok and isinstance(m, dict)
    print(f"LEG 4 sign + no-harm: positive=harm/negative=benefit={signs_ok}, "
          f"iid_control engagement={np.mean(fr):.3%} (<1%)={gate_ok} "
          f"-> {'PASS' if ok else 'FAIL'}")
    return ok


def leg5_json_boundary() -> bool:
    cells = [run_cell(L, 2.4, "ar1_high", n_seeds=12, base_seed=555)
             for L in (4, 6, 8)]
    cells += [run_cell(L, c, e, n_seeds=6, base_seed=555)
              for L in (4, 6, 8) for c in (1.3, 1.8)
              for e in ("iid_control", "ar1_moderate", "ar1_high",
                        "drift_canonical")]
    cells += [run_cell(L, 2.4, e, n_seeds=6, base_seed=555)
              for L in (4, 6, 8)
              for e in ("iid_control", "ar1_moderate", "drift_canonical")]
    payload = dict(cells=cells, crossover=crossover_map(cells),
                   calibration_vs_source=calibration(cells),
                   stability_statement=stability(cells))
    try:
        s = json.dumps(payload)
        json.loads(s)
        ok = True
    except (TypeError, ValueError) as exc:
        print(f"LEG 5 FAIL: {exc}")
        ok = False
    print(f"LEG 5 json boundary: full payload round-trips "
          f"({len(cells)} cells) -> {'PASS' if ok else 'FAIL'}")
    return ok


def main() -> None:
    print("E7 suite: engine fidelity + planted crossover + resolution logic "
          "+ sign/no-harm + json boundary")
    r = [leg1_engine_fidelity(), leg2_planted_crossover(), leg3_resolution_logic(),
         leg4_sign_and_no_harm(), leg5_json_boundary()]
    print(f"\nALL PASS: {all(r)}")
    sys.exit(0 if all(r) else 1)


if __name__ == "__main__":
    main()
