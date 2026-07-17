"""e9_hysteresis.py - E9: customer-hysteresis sensitivity sweep (runner +
analysis). DESIGN.md Section 12, amendment 2026-07-16 (Option B).

OURS: this driver, the analysis, the decision-rule execution, the crossover
map, and the fidelity comparison. The hysteresis demand layer is OUR
spec-derived e9_hysteresis_demand. Everything inherited is the VENDORED,
CIC-cleared closure (E8 amendments 2026-07-16c/d) plus stockpyl 1.0.2.

The run executes the frozen grid at the SOURCE'S OWN SEEDS (2000-2019), so
one run is simultaneously (a) the fidelity cross-check against the
registered artifact (pre-registered TIER-EXACT / TIER-CLOSE / FAIL) and
(b) the E9 result (every decision-rule cell resolves at this n in the
source's data; severity measured at the gate).

Comparison is phi_gated_asymmetric vs no_pricing - the CLAIM-B family.
Nothing here may be attributed to the persistence formula (DISC-03 gate).

Writes analysis/outputs/e9_hysteresis.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import sys
import time
import traceback
from typing import Any, Dict, List, Optional

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE / "vendor"))

from e9_hysteresis_demand import (  # noqa: E402
    HysteresisSpec, apply_pricing_with_hysteresis,
)

from stockpyl.sim import simulation  # noqa: E402

from phase2_3_stage1_network import SKU_SPECS  # noqa: E402
from phase2_3_stage3_policy_comparison import apply_capacity_constraints  # noqa: E402
from phase2_6_serial_network import (  # noqa: E402
    SERIAL_NODE_SPECS, SERIAL_RETAILERS_FED, build_phase2_6_serial_network,
)
from phase2_6_timevarying_demand import constant_schedule  # noqa: E402
from phase2_6_policy_scenarios import apply_scenario_multiproduct  # noqa: E402
from phase2_7_pricing_policies import PricingPolicyConfig  # noqa: E402
from phase2_7_pricing_manager import (  # noqa: E402
    get_transition_period_for_environment,
)
from phase2_7_validation_runner import (  # noqa: E402
    assign_realized_streams_to_retailer,
    extract_chain_costs,
    generate_summed_baseline_streams,
)

OUT = _HERE / "outputs" / "e9_hysteresis.json"

# ---------------------------------------------------------------------------
# FROZEN CONFIGURATION (DESIGN Section 12 amendment 2026-07-16; from code)
# ---------------------------------------------------------------------------
NUM_PERIODS = 260
WARMUP_PERIODS = 52
CAPACITY_MULTIPLIER = 1.3
INVENTORY_SCENARIO = "all_sr"
ELASTICITY = 1.5
REVIEW_INTERVAL = 20
INTENSITIES = [0.0, 0.10, 0.30, 0.60]
SEED_START, SEED_END = 2000, 2019          # the source's own 20 seeds
SCENARIOS = ["no_pricing", "phi_gated_asymmetric"]
RETAILER_INDEX = 3
MANUFACTURER_INDEX = 0

DESIGN_PIN = "74c73ea165a7363c6714fe803fbe76b1"
FIDELITY_TARGET_SHA256 = (
    "e5875b0fac7f35e1b9ccc4b956c8f99f28355a5fa6787df6dd2624368202ef3b")

STORE = pathlib.Path(os.environ.get(
    "EC_STORE", r"C:\Users\jaek9\Documents\LaggingTruth\The-Escalation-Cost"))
DEFAULT_FIDELITY_TARGET = STORE / "raw" / "phase27" / \
    "phase2_7_hysteresis_results.json"


def sweep_environments() -> Dict[str, dict]:
    """Frozen verbatim from the source runner's get_sweep_environments()."""
    return {
        "level_shift_up_persistent": {
            "name": "level_shift_up_persistent",
            "generator_kind": "ar1",
            "schedule": constant_schedule(0.85),
            "level_shift_fraction": 0.20,
            "level_shift_period": 130,
            "level_shift_duration": None,
            "description": ("AR(1) phi=0.85 with persistent +20% level "
                            "shift at t=130"),
        },
        "low_phi_shift_up": {
            "name": "low_phi_shift_up",
            "generator_kind": "ar1",
            "schedule": constant_schedule(0.3),
            "level_shift_fraction": 0.20,
            "level_shift_period": 130,
            "level_shift_duration": None,
            "description": "AR(1) phi=0.3 with +20% level shift at t=130",
        },
    }


def run_trial(env_config: dict, scenario_name: str, intensity: float,
              trial_seed: int, num_periods: int = NUM_PERIODS,
              warmup_periods: int = WARMUP_PERIODS) -> Dict[str, Any]:
    """One (env, scenario, intensity, seed) trial with full chain dynamics,
    wired through the vendored CIC-cleared closure + OUR hysteresis walk."""
    try:
        net, nodes_by_index, products = build_phase2_6_serial_network()
        apply_capacity_constraints(
            nodes_by_index, products,
            capacity_multiplier=CAPACITY_MULTIPLIER,
        )

        baseline_streams = generate_summed_baseline_streams(
            env_config, trial_seed, num_periods,
        )
        transition_period = get_transition_period_for_environment(
            env_config["name"], env_config,
        )

        spec = HysteresisSpec(elasticity=ELASTICITY, reference_price=1.0,
                              demand_floor=0.0, intensity=intensity)
        policy_config = PricingPolicyConfig(
            elasticity=ELASTICITY, review_interval=REVIEW_INTERVAL,
        )
        realized_streams, price_history, meta = apply_pricing_with_hysteresis(
            sku_baseline_streams=baseline_streams,
            pricing_policy_name=scenario_name,
            policy_config=policy_config,
            spec=spec,
            transition_period=transition_period,
            initial_price=1.0,
        )

        assign_realized_streams_to_retailer(
            nodes_by_index, products, realized_streams,
        )

        arch_config = {
            "architecture": "serial",
            "demand_mode": "summed_at_retailer",
            "node_specs": SERIAL_NODE_SPECS,
            "retailers_fed": SERIAL_RETAILERS_FED,
            "retailer_indices": [RETAILER_INDEX],
            "manufacturer_index": MANUFACTURER_INDEX,
            "chain_length": 4,
        }
        apply_scenario_multiproduct(
            scenario_name=INVENTORY_SCENARIO,
            arch_config=arch_config,
            nodes_by_index=nodes_by_index,
            products_by_tier_and_sku=products,
            sku_specs=SKU_SPECS,
            oracle_phi_per_node=None,
        )

        simulation(net, num_periods=num_periods,
                   rand_seed=42, progress_bar=False)

        post_warmup_cost, per_tier_cost = extract_chain_costs(
            SERIAL_NODE_SPECS, nodes_by_index, num_periods, warmup_periods,
        )
        measured = num_periods - warmup_periods
        cost_per_period = post_warmup_cost / measured

        rev = meta["revenue_per_period"]
        post_warmup_revenue = float(np.sum(rev[warmup_periods:]))
        mean_rev = post_warmup_revenue / measured

        return {
            "trial_seed": trial_seed,
            "env": env_config["name"],
            "pricing_scenario": scenario_name,
            "hysteresis_intensity": intensity,
            "num_periods": num_periods,
            "warmup_periods": warmup_periods,
            "cost_per_period": float(cost_per_period),
            "mean_revenue_per_period": float(mean_rev),
            "net_per_period": float(mean_rev - cost_per_period),
            "num_price_changes": meta["num_price_changes"],
            "final_price": meta["final_price"],
            "final_customer_pool": meta["final_customer_pool"],
            "min_customer_pool": meta["min_customer_pool"],
            "success": True,
        }
    except Exception as e:
        return {
            "trial_seed": trial_seed,
            "env": env_config["name"],
            "pricing_scenario": scenario_name,
            "hysteresis_intensity": intensity,
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


def cell_status(mean: float, se: float) -> str:
    """Pre-registered resolution language (DESIGN Sec 12): within 1 SE of
    zero -> indeterminate; |mean| > 1.96 SE -> resolved; else unresolved."""
    if se <= 0:
        return "degenerate"
    if abs(mean) <= se:
        return "indeterminate"
    if abs(mean) > 1.96 * se:
        return "resolved"
    return "unresolved"


def execute_decision_rule(cells: Dict[tuple, dict]) -> Dict[str, Any]:
    """The frozen retain/downgrade rule, exactly as pre-registered.

    DOWNGRADE if the benefit is resolved-negative at h=0.30 in the
    high-persistence strained environment; RETAIN-WITH-SPLIT-FRAMING if the
    benefit is resolved-positive at h=0.60 in that environment; otherwise
    AS-FOUND (neither condition met at resolution)."""
    hp = "level_shift_up_persistent"
    c30, c60 = cells[(hp, 0.30)], cells[(hp, 0.60)]
    s30 = cell_status(c30["benefit_mean"], c30["benefit_se"])
    s60 = cell_status(c60["benefit_mean"], c60["benefit_se"])
    if c30["benefit_mean"] < 0 and s30 == "resolved":
        verdict = "DOWNGRADE-FRAGILE-EVERYWHERE"
    elif c60["benefit_mean"] > 0 and s60 == "resolved":
        verdict = "RETAIN-WITH-SPLIT-FRAMING"
    else:
        verdict = "AS-FOUND-NEITHER-CONDITION-RESOLVED"
    return {
        "verdict": verdict,
        "hp_h030": {"mean": c30["benefit_mean"], "se": c30["benefit_se"],
                    "status": s30},
        "hp_h060": {"mean": c60["benefit_mean"], "se": c60["benefit_se"],
                    "status": s60},
    }


def crossover_map(cells: Dict[tuple, dict], env: str,
                  intensities: List[float]) -> Dict[str, Any]:
    """Sign map along h with resolution; a boundary between two cells is a
    CROSSING only if both endpoints are resolved with opposite signs."""
    seq = []
    for h in intensities:
        c = cells[(env, h)]
        seq.append({"h": h, "mean": c["benefit_mean"], "se": c["benefit_se"],
                    "status": cell_status(c["benefit_mean"], c["benefit_se"])})
    crossing = None
    boundary = "none-in-range"
    for a, b in zip(seq, seq[1:]):
        if a["mean"] > 0 and b["mean"] < 0:
            if a["status"] == "resolved" and b["status"] == "resolved":
                crossing = [a["h"], b["h"]]
                boundary = "resolved"
            else:
                crossing = [a["h"], b["h"]]
                boundary = "unresolved"
            break
    return {"cells": seq, "crossing_bracket": crossing, "boundary": boundary}


def fidelity_check(trials: List[dict], target_path: pathlib.Path,
                   envs: List[str], intensities: List[float],
                   seeds: List[int]) -> Dict[str, Any]:
    """Pre-registered TIER-EXACT / TIER-CLOSE / FAIL comparison against the
    source's registered artifact, per trial on net value."""
    raw = target_path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != FIDELITY_TARGET_SHA256:
        return {"tier": "FAIL", "reason": f"target SHA256 mismatch: {sha}"}
    theirs = json.loads(raw)
    tidx = {}
    for t in theirs["trials"]:
        key = (t["env"], t["pricing_scenario"],
               round(t["hysteresis_intensity"], 6), t["trial_seed"])
        tidx[key] = t["mean_revenue_per_period"] - t["cost_per_period"]
    oidx = {}
    for t in trials:
        key = (t["env"], t["pricing_scenario"],
               round(t["hysteresis_intensity"], 6), t["trial_seed"])
        oidx[key] = t["net_per_period"]

    rels = []
    for key, theirs_net in tidx.items():
        if key not in oidx:
            return {"tier": "FAIL", "reason": f"missing trial {key}"}
        ours_net = oidx[key]
        rels.append(abs(ours_net - theirs_net) / max(1.0, abs(theirs_net)))
    max_rel = float(max(rels))
    if max_rel <= 1e-9:
        return {"tier": "TIER-EXACT", "max_rel_diff": max_rel,
                "n_compared": len(rels)}

    # TIER-CLOSE: every (env, h) paired-benefit mean within 0.1 x the
    # artifact's cell SE.
    def cell_benefit(idx, env, h):
        diffs = [idx[(env, "phi_gated_asymmetric", h, s)]
                 - idx[(env, "no_pricing", h, s)] for s in seeds]
        d = np.asarray(diffs)
        return float(d.mean()), float(d.std(ddof=1) / np.sqrt(len(d)))

    deltas = []
    close = True
    for env in envs:
        for h in intensities:
            m_t, se_t = cell_benefit(tidx, env, h)
            m_o, _ = cell_benefit(oidx, env, h)
            delta = abs(m_o - m_t)
            deltas.append({"env": env, "h": h, "ours": m_o, "theirs": m_t,
                           "abs_delta": delta, "bar": 0.1 * se_t})
            if delta > 0.1 * se_t:
                close = False
    tier = "TIER-CLOSE" if close else "FAIL"
    return {"tier": tier, "max_rel_diff": max_rel, "n_compared": len(rels),
            "cell_deltas": deltas}


def run_e9(smoke: bool = False,
           fidelity_target: Optional[str] = None) -> Dict[str, Any]:
    envs = sweep_environments()
    if smoke:
        # Reduced wiring check. The frozen envs shift at t=130, beyond a
        # short horizon - so the SMOKE-ONLY copies shift at t=60 instead
        # (detection is deterministic at the next review boundary, t=80,
        # leaving 40 periods of engagement). The real run uses the frozen
        # construction untouched.
        num_periods, warmup = 120, 20
        intensities = [0.0, 0.60]
        seeds = [SEED_START]
        for env_cfg in envs.values():
            env_cfg["level_shift_period"] = 60
    else:
        num_periods, warmup = NUM_PERIODS, WARMUP_PERIODS
        intensities = list(INTENSITIES)
        seeds = list(range(SEED_START, SEED_END + 1))

    t0 = time.time()
    trials: List[dict] = []
    for env_name, env_cfg in envs.items():
        for h in intensities:
            for s in seeds:
                for scen in SCENARIOS:
                    trials.append(run_trial(env_cfg, scen, h, s,
                                            num_periods, warmup))
    elapsed = time.time() - t0
    failures = [t for t in trials if not t.get("success")]

    cells: Dict[tuple, dict] = {}
    for env_name in envs:
        for h in intensities:
            diffs, pools = [], []
            for s in seeds:
                a = next(t for t in trials if t.get("success")
                         and t["env"] == env_name
                         and t["pricing_scenario"] == "phi_gated_asymmetric"
                         and t["hysteresis_intensity"] == h
                         and t["trial_seed"] == s)
                b = next(t for t in trials if t.get("success")
                         and t["env"] == env_name
                         and t["pricing_scenario"] == "no_pricing"
                         and t["hysteresis_intensity"] == h
                         and t["trial_seed"] == s)
                diffs.append(a["net_per_period"] - b["net_per_period"])
                pools.append(a["final_customer_pool"])
            d = np.asarray(diffs)
            se = float(d.std(ddof=1) / np.sqrt(len(d))) if len(d) > 1 else 0.0
            cells[(env_name, h)] = {
                "env": env_name, "h": h,
                "benefit_mean": float(d.mean()), "benefit_se": se,
                "sigma": float(d.mean() / se) if se > 0 else None,
                "status": cell_status(float(d.mean()), se),
                "pool_mean": float(np.mean(pools)),
                "n": len(d),
            }

    result: Dict[str, Any] = {
        "experiment": "E9", "date": "2026-07-16",
        "design_pin": DESIGN_PIN, "smoke": bool(smoke),
        "construction": {
            "num_periods": num_periods, "warmup_periods": warmup,
            "capacity_multiplier": CAPACITY_MULTIPLIER,
            "inventory_scenario": INVENTORY_SCENARIO,
            "elasticity": ELASTICITY, "review_interval": REVIEW_INTERVAL,
            "intensities": intensities,
            "seeds": [seeds[0], seeds[-1]],
            "scenarios": SCENARIOS,
            "comparison": "phi_gated_asymmetric vs no_pricing (Claim-B "
                          "family; not attributable to the formula)",
        },
        "n_trials": len(trials), "n_failures": len(failures),
        "elapsed_seconds": float(elapsed),
        "cells": [cells[k] for k in sorted(cells, key=lambda k: (k[0], k[1]))],
    }
    if failures:
        result["failures"] = failures[:5]

    if not smoke:
        result["decision"] = execute_decision_rule(cells)
        result["crossover"] = {
            env: crossover_map(cells, env, intensities) for env in envs}
        target = pathlib.Path(fidelity_target) if fidelity_target else (
            pathlib.Path(os.environ.get("E9_FIDELITY_TARGET",
                                        str(DEFAULT_FIDELITY_TARGET))))
        result["fidelity"] = fidelity_check(
            trials, target, list(envs), intensities, seeds)

    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true",
                    help="reduced wiring check (80 periods, 1 seed, 2 h)")
    ap.add_argument("--fidelity-target", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    res = run_e9(smoke=args.smoke, fidelity_target=args.fidelity_target)
    out = pathlib.Path(args.out) if args.out else (
        OUT if not args.smoke else OUT.with_name("e9_hysteresis_smoke.json"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2))

    print(f"E9 {'SMOKE' if res['smoke'] else 'RUN'}: trials={res['n_trials']} "
          f"failures={res['n_failures']} elapsed={res['elapsed_seconds']:.0f}s")
    for c in res["cells"]:
        print(f"  {c['env']:<28} h={c['h']:<4} benefit={c['benefit_mean']:>+10.2f} "
              f"se={c['benefit_se']:>8.2f} {c['status']:<13} "
              f"pool={c['pool_mean']:.3f}")
    if not res["smoke"]:
        print(f"  FIDELITY: {res['fidelity']['tier']} "
              f"(max_rel_diff={res['fidelity'].get('max_rel_diff')})")
        print(f"  DECISION: {res['decision']['verdict']}")


if __name__ == "__main__":
    main()
