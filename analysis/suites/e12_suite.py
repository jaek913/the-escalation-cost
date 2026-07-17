"""e12_suite.py - E12 validation suite. DESIGN Section 13 amendment 2026-07-17.

Six legs, run before the analysis (two-stage handoff):
  LEG 1  INPUT HASHES - LEG A artifact MD5 (our committed E7 rebuild output)
         and LEG B artifact SHA256 (the source's raw 9,000-record sweep).
  LEG 2  REGRESSION - LEG B machinery recomputes the E7-verified headline
         triple (sr_paper9_ols vs sr_disabled, ar1_high x 2.4x) from the raw
         records: +0.439 (L=4), +0.137 (L=6), -0.141 (L=8), within 1e-3.
  LEG 3  PAIRED-CONTRAST MACHINERY - planted synthetic records with known
         exact contrasts; the function must return them.
  LEG 4  CI-DISJOINTNESS UNIT - ordering helper on planted intervals.
  LEG 5  PLANTED DECISION-RULE LOGIC - synthetic maps drive the frozen rule
         to EXPECTED-CONFIRMED, ORACLE-WINS, and AS-FOUND.
  LEG 6  FULL RUN + JSON ROUNDTRIP - run_e12 end to end on the real inputs;
         reparse; schema and native types.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
_ANALYSIS = _HERE.parent
sys.path.insert(0, str(_ANALYSIS))

import e12_nonstationarity as e12  # noqa: E402


def _leg_b_path() -> pathlib.Path:
    import os
    return pathlib.Path(os.environ.get(
        "E12_SWEEP_TARGET", str(e12.DEFAULT_LEGB)))


def leg1_input_hashes() -> bool:
    ok = True
    a = e12.DEFAULT_LEGA
    if not a.exists():
        print(f"  LEG1 FAIL: LEG A missing at {a}")
        ok = False
    else:
        md5 = hashlib.md5(a.read_bytes()).hexdigest()
        if md5 != e12.LEGA_MD5:
            print(f"  LEG1 FAIL: LEG A MD5 {md5} != {e12.LEGA_MD5}")
            ok = False
    b = _leg_b_path()
    if not b.exists():
        print(f"  LEG1 FAIL: LEG B missing at {b}")
        ok = False
    else:
        sha = hashlib.sha256(b.read_bytes()).hexdigest()
        if sha != e12.LEGB_SHA256:
            print(f"  LEG1 FAIL: LEG B SHA256 mismatch")
            ok = False
    print(f"LEG 1 input hashes: {'PASS' if ok else 'FAIL'}")
    return ok


def leg2_regression_e7_headline() -> bool:
    leg_b = e12.load_leg_b(_leg_b_path())
    want = {4: 0.439, 6: 0.137, 8: -0.141}
    ok = True
    for L, target in want.items():
        r = e12.paired_contrast(leg_b["index"], "ar1_high", L, 2.4,
                                "sr_paper9_ols", "sr_disabled")
        if r["mean"] is None or abs(r["mean"] - target) > 1e-3:
            print(f"  LEG2 FAIL L={L}: got {r['mean']} want {target}")
            ok = False
    print(f"LEG 2 regression (E7-verified headline triple from raw): "
          f"{'PASS' if ok else 'FAIL'}")
    return ok


def leg3_paired_contrast_machinery() -> bool:
    # Planted: baseline 100 for all seeds; variant A = 103, variant B = 101
    # -> (A-B)/base*100 = +2.000 exactly, sd 0 across seeds -> se 0, but we
    # plant a small spread to exercise the se path: A alternates 103/105.
    idx = {}
    for s in range(4):
        idx[("envX", 4, 1.3, "sr_disabled", s)] = 100.0
        idx[("envX", 4, 1.3, "A", s)] = 103.0 + (2.0 if s % 2 else 0.0)
        idx[("envX", 4, 1.3, "B", s)] = 101.0
    r = e12.paired_contrast(idx, "envX", 4, 1.3, "A", "B")
    ok = (r["n"] == 4 and abs(r["mean"] - 3.0) < 1e-12)
    # exact-mean check: contrasts are (2,4,2,4)/100*100 -> mean 3.0
    # one-sided planted negative
    for s in range(4):
        idx[("envX", 4, 1.3, "C", s)] = 96.0
    r2 = e12.paired_contrast(idx, "envX", 4, 1.3, "C", "B")
    ok &= (abs(r2["mean"] - (-5.0)) < 1e-12 and r2["resolved"]
           and r2["sign"] == "a_better")
    # missing-arm safety
    r3 = e12.paired_contrast(idx, "envX", 4, 1.3, "A", "NOPE")
    ok &= (r3["n"] == 0 and r3["mean"] is None)
    print(f"LEG 3 paired-contrast machinery: {'PASS' if ok else 'FAIL'}")
    return ok


def leg4_ci_disjoint_unit() -> bool:
    ok = e12.ci_disjoint_below([-2.0, -1.0], [-0.5, 0.5]) is True
    ok &= e12.ci_disjoint_below([-2.0, -0.4], [-0.5, 0.5]) is False
    ok &= e12.ci_disjoint_below([0.1, 0.2], [0.2, 0.3]) is False  # touching
    print(f"LEG 4 CI-disjointness unit: {'PASS' if ok else 'FAIL'}")
    return ok


def _planted_cells(oracle_sign, fixed_sign, fixed_ci, oracle_ci, ols_ci):
    """Build a full 9-cell drift map + the two locus cells' variant dicts."""
    cells = {}
    for L in e12.CHAIN_LENGTHS:
        for cap in e12.CAPS:
            cells[(e12.DRIFT, L, cap)] = {
                "sr_oracle_local": {"mean_pct_diff": 0.3, "se": 0.03,
                                    "ci": list(oracle_ci),
                                    "sign": oracle_sign, "n_paired": 250},
                "sr_paper9_ols": {"mean_pct_diff": 0.1, "se": 0.02,
                                  "ci": list(ols_ci), "sign": "harm",
                                  "n_paired": 250},
                "sr_naive_damp": {"mean_pct_diff": fixed_ci[0] / 2
                                  + fixed_ci[1] / 2, "se": 0.08,
                                  "ci": list(fixed_ci), "sign": fixed_sign,
                                  "n_paired": 250},
            }
    return cells


def _planted_legb(met: bool):
    out = {}
    for (L, cap) in e12.CLAIM_LOCUS:
        key = f"drift_L{L}x{cap}"
        val = {"n": 50, "mean": -1.0 if met else +0.1, "se": 0.1,
               "ci": [-1.2, -0.8] if met else [-0.1, 0.3],
               "resolved": met, "sign": "a_better" if met else "unresolved"}
        out[f"{key}_fixed_minus_oracle"] = dict(val)
        out[f"{key}_fixed_minus_ols"] = dict(val)
        out[f"{key}_oracle_minus_ols"] = dict(val)
    return out


def leg5_decision_rule_logic() -> bool:
    ok = True
    # EXPECTED-CONFIRMED: oracle harm everywhere; fixed resolved-benefit,
    # CI disjoint below both; LEG B met.
    cells = _planted_cells("harm", "benefit", (-1.3, -0.9),
                          (0.2, 0.4), (0.05, 0.15))
    r = e12.execute_decision_rule(cells, _planted_legb(True))
    ok &= r["verdict"] == "EXPECTED-CONFIRMED-RECIPE-LEVEL"
    # AS-FOUND: fixed unresolved at the locus
    cells2 = _planted_cells("harm", "unresolved", (-0.2, 0.3),
                           (0.2, 0.4), (0.05, 0.15))
    r2 = e12.execute_decision_rule(cells2, _planted_legb(False))
    ok &= r2["verdict"] == "AS-FOUND-CHARACTERIZATION"
    # ORACLE-WINS: oracle resolved-benefit disjoint below fixed and ols
    cells3 = _planted_cells("benefit", "harm", (0.2, 0.5),
                           (-1.0, -0.7), (0.05, 0.15))
    r3 = e12.execute_decision_rule(cells3, _planted_legb(False))
    ok &= r3["verdict"] == "ORACLE-WINS-LIMITATION-RESOLVED"
    print(f"LEG 5 planted decision-rule logic: {'PASS' if ok else 'FAIL'}")
    return ok


def leg6_full_run_roundtrip() -> bool:
    res = e12.run_e12(leg_b_path=str(_leg_b_path()))
    out = _ANALYSIS / "outputs" / "e12_suite_check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2))
    back = json.loads(out.read_text())
    ok = back["experiment"] == "E12"
    ok &= back["decision"]["verdict"] in (
        "EXPECTED-CONFIRMED-RECIPE-LEVEL",
        "ORACLE-WINS-LIMITATION-RESOLVED",
        "AS-FOUND-CHARACTERIZATION")
    ok &= len(back["leg_a"]["map"]) == 36
    ok &= len(back["leg_b"]["drift_variant_vs_baseline_corroboration"]) == 9
    ok &= isinstance(
        back["decision"]["i_oracle_harm_all_drift"], bool)
    print(f"LEG 6 full run + json roundtrip: {'PASS' if ok else 'FAIL'}")
    return ok


def main() -> None:
    legs = [leg1_input_hashes(), leg2_regression_e7_headline(),
            leg3_paired_contrast_machinery(), leg4_ci_disjoint_unit(),
            leg5_decision_rule_logic(), leg6_full_run_roundtrip()]
    print(f"E12 SUITE ALL PASS: {all(legs)}")
    if not all(legs):
        sys.exit(1)


if __name__ == "__main__":
    main()
