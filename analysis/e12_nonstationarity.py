"""e12_nonstationarity.py - E12: recipe-level non-stationarity limitation
(pre-registered limitation documentation). DESIGN.md Section 13, E12 operator
+ amendment 2026-07-17. Standard v1.9.9.

E12 is an ANALYSIS - zero new simulation. Two evidence legs, both already in
hand and both hash-pinned:

LEG A (primary, 250 seeds): our own committed E7 rebuild artifact
  analysis/outputs/e7_chain_sweep.json - every cell carries the three-variant
  diagnostic (sr_paper9_ols / sr_oracle_local / sr_naive_damp, each paired
  within-seed against sr_disabled). Aggregates only; variant-vs-variant SEs are
  not recoverable from it, so ordering statements from LEG A use CI
  DISJOINTNESS (conservative).

LEG B (corroboration, 50 seeds): the source's raw 9,000-record sweep artifact
  (code CIC-cleared at E7/DISC-05). Raw per-trial records permit PROPERLY
  PAIRED per-seed variant-vs-variant contrasts with real SEs:
    d_s = (cost_A(s) - cost_B(s)) / cost_disabled(s) * 100
  Context-only extra: sr_numerical (the source's preserved pre-correction
  rule) vs baseline in the drift row - never claim-carrying.

The frozen decision rule (amendment 2026-07-17) is executed mechanically; this
experiment CANNOT support the thesis - it documents a limitation, or (if the
oracle wins) rewrites it as resolved.

Writes analysis/outputs/e12_nonstationarity.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent

DESIGN_PIN = "74c73ea165a7363c6714fe803fbe76b1"
LEGA_MD5 = "fdb79fd32566d4129226eea422c356cb"
LEGB_SHA256 = (
    "ea95218b2193b5ad0f174d380c13da358a9b365044cf2668fa243b34b0539e49")

DEFAULT_LEGA = _HERE / "outputs" / "e7_chain_sweep.json"
STORE = pathlib.Path(os.environ.get(
    "EC_STORE", r"C:\Users\jaek9\Documents\LaggingTruth\The-Escalation-Cost"))
DEFAULT_LEGB = STORE / "raw" / "phase26" / "aggregated_chain_length_sweep.json"

OUT = _HERE / "outputs" / "e12_nonstationarity.json"

DRIFT = "drift_canonical"
ENVS = ["drift_canonical", "ar1_high", "ar1_moderate", "iid_control"]
CHAIN_LENGTHS = [4, 6, 8]
CAPS = [1.3, 1.8, 2.4]
VARIANTS = ["sr_paper9_ols", "sr_oracle_local", "sr_naive_damp"]
BASELINE = "sr_disabled"
CONTEXT_VARIANT = "sr_numerical"   # pre-correction rule; context only
CLAIM_LOCUS = [(8, 1.8), (8, 2.4)]  # frozen: L=8 headroom cells
Z95 = 1.959963984540054


def ci_disjoint_below(a_ci: List[float], b_ci: List[float]) -> bool:
    """True iff interval a sits entirely below interval b (conservative
    ordering: a < b resolved without paired SEs)."""
    return a_ci[1] < b_ci[0]


def load_leg_a(path: pathlib.Path) -> Dict[str, Any]:
    raw = path.read_bytes()
    md5 = hashlib.md5(raw).hexdigest()
    if md5 != LEGA_MD5:
        raise RuntimeError(f"LEG A artifact MD5 mismatch: {md5} != {LEGA_MD5}")
    d = json.loads(raw)
    cells = {}
    for c in d["cells"]:
        cells[(c["env"], c["n_stages"], c["cap_mult"])] = c["diagnostic"]
    return {"md5": md5, "cells": cells, "spec": d["spec"]}


def load_leg_b(path: pathlib.Path) -> Dict[str, Any]:
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != LEGB_SHA256:
        raise RuntimeError(f"LEG B artifact SHA256 mismatch: {sha}")
    d = json.loads(raw)
    idx: Dict[Tuple, float] = {}
    for t in d["trials"]:
        if not t.get("success"):
            continue
        key = (t["env"], t["n_stages"], t["capacity_multiplier"],
               t["variant"], t["trial_seed"])
        idx[key] = t["cost_per_period"]
    return {"sha256": sha, "index": idx}


def paired_contrast(idx: Dict[Tuple, float], env: str, L: int, cap: float,
                    var_a: str, var_b: str) -> Dict[str, Any]:
    """Properly paired per-seed contrast (a - b) / baseline * 100 from raw
    records. Positive = var_a costs MORE than var_b."""
    seeds = sorted({k[4] for k in idx
                    if k[0] == env and k[1] == L and k[2] == cap
                    and k[3] == var_a})
    d = []
    for s in seeds:
        ka = (env, L, cap, var_a, s)
        kb = (env, L, cap, var_b, s)
        kbase = (env, L, cap, BASELINE, s)
        if ka in idx and kb in idx and kbase in idx:
            d.append((idx[ka] - idx[kb]) / idx[kbase] * 100.0)
    if len(d) < 2:
        return {"n": len(d), "mean": None, "se": None,
                "resolved": False, "sign": "n/a"}
    arr = np.asarray(d)
    mean = float(arr.mean())
    se = float(arr.std(ddof=1) / np.sqrt(len(arr)))
    resolved = bool(abs(mean) > Z95 * se)
    return {
        "n": len(arr), "mean": mean, "se": se,
        "ci": [mean - Z95 * se, mean + Z95 * se],
        "resolved": resolved,
        "sign": ("a_worse" if mean > 0 else "a_better") if resolved
                else "unresolved",
    }


def execute_decision_rule(leg_a_cells: Dict[Tuple, dict],
                          leg_b_contrasts: Dict[str, dict]) -> Dict[str, Any]:
    """The frozen rule of amendment 2026-07-17, executed mechanically."""
    # (i) oracle resolved-harm in all 9 drift cells
    oracle_harm_all = True
    oracle_cells = {}
    for L in CHAIN_LENGTHS:
        for cap in CAPS:
            v = leg_a_cells[(DRIFT, L, cap)]["sr_oracle_local"]
            key = f"L{L}x{cap}"
            oracle_cells[key] = {"mean": v["mean_pct_diff"], "se": v["se"],
                                 "sign": v["sign"]}
            if v["sign"] != "harm":
                oracle_harm_all = False

    # (ii) claim-locus fixed resolved-benefit with CI disjoint-below both
    locus_ok = True
    locus_detail = {}
    for (L, cap) in CLAIM_LOCUS:
        dg = leg_a_cells[(DRIFT, L, cap)]
        fx, orc, ols = (dg["sr_naive_damp"], dg["sr_oracle_local"],
                        dg["sr_paper9_ols"])
        cond = (fx["sign"] == "benefit"
                and ci_disjoint_below(fx["ci"], orc["ci"])
                and ci_disjoint_below(fx["ci"], ols["ci"]))
        locus_detail[f"L{L}x{cap}"] = {
            "fixed": {"mean": fx["mean_pct_diff"], "ci": fx["ci"],
                      "sign": fx["sign"]},
            "oracle_ci": orc["ci"], "ols_ci": ols["ci"],
            "condition_met": bool(cond),
        }
        if not cond:
            locus_ok = False

    # (iii) LEG B paired contrasts resolve negative at the claim locus
    legb_ok = True
    legb_detail = {}
    for (L, cap) in CLAIM_LOCUS:
        fo = leg_b_contrasts[f"drift_L{L}x{cap}_fixed_minus_oracle"]
        fl = leg_b_contrasts[f"drift_L{L}x{cap}_fixed_minus_ols"]
        cond = (fo["resolved"] and fo["mean"] < 0
                and fl["resolved"] and fl["mean"] < 0)
        legb_detail[f"L{L}x{cap}"] = {"fixed_minus_oracle": fo,
                                      "fixed_minus_ols": fl,
                                      "condition_met": bool(cond)}
        if not cond:
            legb_ok = False

    # ORACLE-WINS check (the pre-registered reversal)
    oracle_wins = True
    for (L, cap) in CLAIM_LOCUS:
        dg = leg_a_cells[(DRIFT, L, cap)]
        orc, fx, ols = (dg["sr_oracle_local"], dg["sr_naive_damp"],
                        dg["sr_paper9_ols"])
        if not (orc["sign"] == "benefit"
                and ci_disjoint_below(orc["ci"], fx["ci"])
                and ci_disjoint_below(orc["ci"], ols["ci"])):
            oracle_wins = False
            break

    if oracle_harm_all and locus_ok and legb_ok:
        verdict = "EXPECTED-CONFIRMED-RECIPE-LEVEL"
    elif oracle_wins:
        verdict = "ORACLE-WINS-LIMITATION-RESOLVED"
    else:
        verdict = "AS-FOUND-CHARACTERIZATION"

    return {
        "verdict": verdict,
        "i_oracle_harm_all_drift": bool(oracle_harm_all),
        "i_oracle_cells": oracle_cells,
        "ii_claim_locus": locus_detail,
        "iii_leg_b_paired": legb_detail,
        "oracle_wins_check": bool(oracle_wins),
    }


def run_e12(leg_a_path: Optional[str] = None,
            leg_b_path: Optional[str] = None) -> Dict[str, Any]:
    a_path = pathlib.Path(leg_a_path) if leg_a_path else DEFAULT_LEGA
    b_path = pathlib.Path(leg_b_path) if leg_b_path else pathlib.Path(
        os.environ.get("E12_SWEEP_TARGET", str(DEFAULT_LEGB)))

    leg_a = load_leg_a(a_path)
    leg_b = load_leg_b(b_path)

    # LEG A map: all 36 cells x 3 variants (drift claim-carrying; stationary
    # rows as controls).
    map_a = []
    for env in ENVS:
        for L in CHAIN_LENGTHS:
            for cap in CAPS:
                dg = leg_a["cells"][(env, L, cap)]
                row = {"env": env, "L": L, "cap": cap}
                for v in VARIANTS:
                    row[v] = {
                        "mean": dg[v]["mean_pct_diff"], "se": dg[v]["se"],
                        "ci": dg[v]["ci"], "sign": dg[v]["sign"],
                        "n": dg[v]["n_paired"],
                    }
                map_a.append(row)

    # LEG B: paired contrasts in the drift row (all 9 cells) + corroboration
    # of variant-vs-baseline means + sr_numerical context.
    contrasts: Dict[str, dict] = {}
    corrob = []
    context_numerical = []
    for L in CHAIN_LENGTHS:
        for cap in CAPS:
            key = f"drift_L{L}x{cap}"
            contrasts[f"{key}_oracle_minus_ols"] = paired_contrast(
                leg_b["index"], DRIFT, L, cap,
                "sr_oracle_local", "sr_paper9_ols")
            contrasts[f"{key}_fixed_minus_oracle"] = paired_contrast(
                leg_b["index"], DRIFT, L, cap,
                "sr_naive_damp", "sr_oracle_local")
            contrasts[f"{key}_fixed_minus_ols"] = paired_contrast(
                leg_b["index"], DRIFT, L, cap,
                "sr_naive_damp", "sr_paper9_ols")
            row = {"L": L, "cap": cap}
            for v in VARIANTS:
                row[v] = paired_contrast(
                    leg_b["index"], DRIFT, L, cap, v, BASELINE)
            corrob.append(row)
            context_numerical.append({
                "L": L, "cap": cap,
                "sr_numerical_vs_baseline": paired_contrast(
                    leg_b["index"], DRIFT, L, cap,
                    CONTEXT_VARIANT, BASELINE),
            })

    decision = execute_decision_rule(leg_a["cells"], contrasts)

    return {
        "experiment": "E12", "date": "2026-07-17",
        "design_pin": DESIGN_PIN,
        "classification": ("characterization - pre-registered limitation "
                           "documentation; CANNOT support the thesis"),
        "leg_a": {"path": "analysis/outputs/" + a_path.name, "md5": leg_a["md5"],
                  "n_seeds": 250, "map": map_a},
        "leg_b": {"path": "store:raw/phase26/" + b_path.name, "sha256": leg_b["sha256"],
                  "n_seeds": 50,
                  "drift_paired_contrasts": contrasts,
                  "drift_variant_vs_baseline_corroboration": corrob,
                  "context_sr_numerical_drift": context_numerical,
                  "context_note": ("sr_numerical is the source's preserved "
                                   "PRE-CORRECTION rule; context only, never "
                                   "claim-carrying")},
        "decision": decision,
        "scope_note": ("Only the tested trajectory shape (phi 0.30 -> 0.95 "
                       "-> 0.40) is claimed; drift, square-wave, and one-shot "
                       "shapes are future work per the operator."),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--leg-a", default=None)
    ap.add_argument("--leg-b", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    res = run_e12(args.leg_a, args.leg_b)
    out = pathlib.Path(args.out) if args.out else OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2))

    print(f"E12 ANALYSIS: decision={res['decision']['verdict']}")
    print("  drift oracle cells (LEG A, 250 seeds):")
    for k, v in res["decision"]["i_oracle_cells"].items():
        print(f"    {k:<10} {v['mean']:+.3f} se {v['se']:.3f} {v['sign']}")
    for k, v in res["decision"]["ii_claim_locus"].items():
        print(f"  locus {k}: fixed {v['fixed']['mean']:+.3f} "
              f"{v['fixed']['sign']} | condition_met={v['condition_met']}")
    for k, v in res["decision"]["iii_leg_b_paired"].items():
        fo, fl = v["fixed_minus_oracle"], v["fixed_minus_ols"]
        print(f"  legB {k}: fixed-oracle {fo['mean']:+.3f} (se {fo['se']:.3f},"
              f" {fo['sign']}) | fixed-ols {fl['mean']:+.3f} "
              f"(se {fl['se']:.3f}, {fl['sign']}) | met={v['condition_met']}")


if __name__ == "__main__":
    main()
