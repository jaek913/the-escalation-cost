"""e9_suite.py - E9 validation suite. DESIGN Section 12 amendment 2026-07-16.

Seven legs, run before any real execution (two-stage handoff):
  LEG 1  VENDOR INTEGRITY - MD5-assert the 12 vendored modules E9 imports
         (the CIC-cleared bytes of amendment 2026-07-16d).
  LEG 2  UNIT MATH - our hysteresis formulas against hand-computed values:
         decay arithmetic, floor engagement, one-directionality, reduction
         of the response to pure elasticity at pool = 1.
  LEG 3  h=0 BIT-EQUIVALENCE (load-bearing) - OUR walk at intensity 0 must
         be BIT-IDENTICAL to the vendored elasticity-only pricing manager
         on planted streams that force real price changes. This PROVES the
         parity the source's dispatch wrapper merely argued.
  LEG 4  ENGAGEMENT + BASELINE INERTNESS - no_pricing at heavy intensity
         leaves the pool at exactly 1.0 with zero price changes (the h-axis
         cannot contaminate the comparator); a forced-raise stub policy
         erodes the pool monotonically and the floor holds at 0.10.
  LEG 5  PLANTED DECISION-RULE LOGIC - synthetic cells drive the frozen
         retain/downgrade rule to RETAIN, DOWNGRADE, and AS-FOUND.
  LEG 6  WIRING SMOKE + JSON ROUNDTRIP - the real run_e9(smoke=True) end to
         end through stockpyl; reparse the written JSON; assert schema and
         native types.
  LEG 7  FIDELITY-TARGET HASH - the registered artifact exists at its
         resolved path and matches the pinned SHA256.
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
sys.path.insert(0, str(_ANALYSIS / "vendor"))

import e9_hysteresis as e9  # noqa: E402
from e9_hysteresis_demand import (  # noqa: E402
    HysteresisSpec, POOL_FLOOR, apply_pricing_with_hysteresis,
    realized_demand, update_pool,
)

VENDOR = _ANALYSIS / "vendor"

# The CIC-cleared bytes (DESIGN E8 amendment 2026-07-16d). Any drift is a
# hard fail: the audit cleared THESE bytes.
VENDOR_MD5 = {
    "phase2_3_stage1_network.py": "9a59f2e2e432f967d73ecf2296e157c2",
    "phase2_3_stage2_demand.py": "605e9fb9ec40c62b8eabc2d497f9ed07",
    "phase2_3_stage3_policy_comparison.py": "508f080332ba3fe42559f0454fce5e25",
    "phase2_6_policy_scenarios.py": "ee52c2923aa97f190b13914c1461b4ff",
    "phase2_6_serial_network.py": "2eedff408e63d620045525f9667a9d1c",
    "phase2_6_spectral_radius.py": "e530ae06c57a15a6680419cbe245ec30",
    "phase2_6_sterman_policy.py": "98a2a10eaad392647d2cb861914c9fa4",
    "phase2_6_timevarying_demand.py": "e681e0c451457335ae66663b2a8b0e09",
    "phase2_7_demand_response.py": "013540f272d0574cf5bf7c489ade4593",
    "phase2_7_pricing_manager.py": "52945aeab2a55e452689d07cb436ed88",
    "phase2_7_pricing_policies.py": "b7a108875f3c257c99cc1508bd806f0f",
    "phase2_7_validation_runner.py": "2b3fc842139e33d9fab5952930477883",
}


def leg1_vendor_integrity() -> bool:
    ok = True
    for fname, want in sorted(VENDOR_MD5.items()):
        got = hashlib.md5((VENDOR / fname).read_bytes()).hexdigest()
        if got != want:
            print(f"  LEG1 FAIL {fname}: {got} != {want}")
            ok = False
    print(f"LEG 1 vendor integrity ({len(VENDOR_MD5)} files): "
          f"{'PASS' if ok else 'FAIL'}")
    return ok


def leg2_unit_math() -> bool:
    ok = True
    s3 = HysteresisSpec(intensity=0.30)
    # decay at ratio 1.2, h=0.3: 1 - 0.3*0.2 = 0.94
    v = update_pool(1.0, 1.2, s3)
    ok &= abs(v - 0.94) < 1e-12
    # one-directional: at/below reference the pool never moves
    ok &= update_pool(0.5, 1.0, s3) == 0.5
    ok &= update_pool(0.5, 0.8, s3) == 0.5
    # floor engagement: prev 0.12, h=0.6, ratio 1.5 -> decay 0.7 -> 0.084 -> 0.10
    s6 = HysteresisSpec(intensity=0.60)
    ok &= update_pool(0.12, 1.5, s6) == POOL_FLOOR
    # extreme elevation: decay clamps at 0 -> pool would be 0 -> floored
    ok &= update_pool(1.0, 3.0, s6) == POOL_FLOOR
    # response reduces to pure elasticity at pool = 1 (bit-exact)
    from phase2_7_demand_response import (
        DemandResponseConfig, apply_price_response)
    base_cfg = DemandResponseConfig(elasticity=1.5)
    spec0 = HysteresisSpec(elasticity=1.5, intensity=0.0)
    for b, p in [(100.0, 1.2), (37.5, 1.05), (2.0, 0.9), (250.0, 1.0)]:
        ours = realized_demand(b, p, 1.0, spec0)
        theirs = apply_price_response(b, p, base_cfg)
        ok &= (ours == theirs)
    # hand value: 100 * 1.2^-1.5 * 0.9 = 100 * 0.760726... * 0.9
    v = realized_demand(100.0, 1.2, 0.9, HysteresisSpec(elasticity=1.5))
    ok &= abs(v - 100.0 * (1.2 ** -1.5) * 0.9) < 1e-12
    print(f"LEG 2 unit math: {'PASS' if ok else 'FAIL'}")
    return ok


def _planted_streams(num_periods: int = 260) -> dict:
    """Three deterministic SKU streams with a +30% level shift at t=130,
    plus seeded noise - enough structure that phi_gated_asymmetric makes
    real price changes."""
    rng = np.random.default_rng(424242)
    streams = {}
    for i, base in enumerate([200.0, 100.0, 40.0]):
        x = np.full(num_periods, base)
        x[130:] *= 1.30
        x = x + rng.normal(0.0, base * 0.05, size=num_periods)
        streams[f"SKU{i}"] = np.maximum(x, 0.0)
    return streams


def leg3_h0_bit_equivalence() -> bool:
    from phase2_7_pricing_manager import (
        PricingScenarioConfig, apply_pricing_to_retailer_streams)
    from phase2_7_demand_response import DemandResponseConfig
    from phase2_7_pricing_policies import PricingPolicyConfig

    streams = _planted_streams()
    pol_cfg = PricingPolicyConfig(elasticity=1.5, review_interval=20)
    scen = PricingScenarioConfig(
        pricing_policy_name="phi_gated_asymmetric",
        policy_config=pol_cfg,
        demand_response_config=DemandResponseConfig(elasticity=1.5),
    )
    r_v, p_v, m_v = apply_pricing_to_retailer_streams(
        {k: v.copy() for k, v in streams.items()}, scen,
        transition_period=130)

    spec0 = HysteresisSpec(elasticity=1.5, intensity=0.0)
    r_o, p_o, m_o = apply_pricing_with_hysteresis(
        {k: v.copy() for k, v in streams.items()},
        pricing_policy_name="phi_gated_asymmetric",
        policy_config=PricingPolicyConfig(elasticity=1.5, review_interval=20),
        spec=spec0, transition_period=130, initial_price=1.0)

    ok = m_v["num_price_changes"] >= 1  # the leg is vacuous without changes
    ok &= (p_v == p_o)
    ok &= (m_v["revenue_per_period"] == m_o["revenue_per_period"])
    for k in streams:
        ok &= bool(np.array_equal(r_v[k], r_o[k]))
    ok &= m_o["final_customer_pool"] == 1.0
    print(f"LEG 3 h=0 bit-equivalence vs vendored manager "
          f"(price changes={m_v['num_price_changes']}): "
          f"{'PASS' if ok else 'FAIL'}")
    return ok


class _ForcedRaisePolicy:
    """Stub: always recommends a 20% raise. Suite-only."""
    def decide_price(self, period, demand_history, current_price):
        return 1.2


class _NoOpPolicy:
    def decide_price(self, period, demand_history, current_price):
        return current_price


def leg4_engagement_and_inertness() -> bool:
    streams = _planted_streams(num_periods=120)
    spec6 = HysteresisSpec(elasticity=1.5, intensity=0.60)
    from phase2_7_pricing_policies import PricingPolicyConfig
    cfg = PricingPolicyConfig(elasticity=1.5, review_interval=20)

    # Baseline inertness: constant price 1.0 -> pool exactly 1.0 forever.
    _, p_hist, meta = apply_pricing_with_hysteresis(
        {k: v.copy() for k, v in streams.items()},
        "no_pricing", cfg, spec6,
        policy_factory=lambda name, c: _NoOpPolicy())
    ok = all(p == 1.0 for p in p_hist)
    ok &= all(v == 1.0 for v in meta["pool_history"])
    ok &= meta["num_price_changes"] == 0

    # Engagement: forced raises erode the pool monotonically; floor holds.
    _, p_hist2, meta2 = apply_pricing_with_hysteresis(
        {k: v.copy() for k, v in streams.items()},
        "forced_raise", cfg, spec6,
        policy_factory=lambda name, c: _ForcedRaisePolicy())
    pools = meta2["pool_history"]
    ok &= meta2["num_price_changes"] == 1          # 1.0 -> 1.2 once, then flat
    ok &= pools[-1] < 1.0
    ok &= all(b <= a for a, b in zip(pools, pools[1:]))   # never regrows
    ok &= min(pools) >= POOL_FLOOR - 1e-15
    # Long-horizon decay at 20% elevation, h=0.6: decay 0.88/period -> floor
    spec_hard = HysteresisSpec(elasticity=1.5, intensity=0.60)
    pool = 1.0
    for _ in range(60):
        pool = update_pool(pool, 1.2, spec_hard)
    ok &= pool == POOL_FLOOR
    print(f"LEG 4 engagement + baseline inertness: {'PASS' if ok else 'FAIL'}")
    return ok


def leg5_decision_rule_logic() -> bool:
    def cells(m30, se30, m60, se60):
        hp = "level_shift_up_persistent"
        return {(hp, 0.30): {"benefit_mean": m30, "benefit_se": se30},
                (hp, 0.60): {"benefit_mean": m60, "benefit_se": se60}}
    ok = True
    r = e9.execute_decision_rule(cells(7800.0, 900.0, 5800.0, 950.0))
    ok &= r["verdict"] == "RETAIN-WITH-SPLIT-FRAMING"
    r = e9.execute_decision_rule(cells(-3000.0, 900.0, -5000.0, 950.0))
    ok &= r["verdict"] == "DOWNGRADE-FRAGILE-EVERYWHERE"
    r = e9.execute_decision_rule(cells(500.0, 900.0, 400.0, 950.0))
    ok &= r["verdict"] == "AS-FOUND-NEITHER-CONDITION-RESOLVED"
    # Downgrade precedence: resolved-negative at 0.30 wins even if 0.60
    # were positive (a pathological non-monotone input).
    r = e9.execute_decision_rule(cells(-3000.0, 900.0, 5800.0, 950.0))
    ok &= r["verdict"] == "DOWNGRADE-FRAGILE-EVERYWHERE"
    print(f"LEG 5 planted decision-rule logic: {'PASS' if ok else 'FAIL'}")
    return ok


def leg6_wiring_smoke_json() -> bool:
    res = e9.run_e9(smoke=True)
    out = _ANALYSIS / "outputs" / "e9_suite_smoke.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2))
    back = json.loads(out.read_text())
    ok = back["experiment"] == "E9"
    ok &= back["smoke"] is True
    ok &= back["n_trials"] == 8 and back["n_failures"] == 0
    ok &= isinstance(back["cells"], list) and len(back["cells"]) == 4
    for c in back["cells"]:
        ok &= isinstance(c["benefit_mean"], float)
        ok &= isinstance(c["pool_mean"], float)
        ok &= isinstance(c["status"], str)
    # engagement visible in the smoke: heavy-h pricing cells eroded the pool
    hp_cells = {(c["env"], c["h"]): c for c in back["cells"]}
    ok &= hp_cells[("level_shift_up_persistent", 0.6)]["pool_mean"] < 1.0
    print(f"LEG 6 wiring smoke + json roundtrip (8 trials): "
          f"{'PASS' if ok else 'FAIL'}")
    return ok


def leg7_fidelity_target_hash() -> bool:
    import os
    path = pathlib.Path(os.environ.get(
        "E9_FIDELITY_TARGET", str(e9.DEFAULT_FIDELITY_TARGET)))
    if not path.exists():
        print(f"LEG 7 fidelity target: FAIL (missing at {path})")
        return False
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    ok = sha == e9.FIDELITY_TARGET_SHA256
    print(f"LEG 7 fidelity-target hash: {'PASS' if ok else 'FAIL'} ({path})")
    return ok


def main() -> None:
    legs = [leg1_vendor_integrity(), leg2_unit_math(),
            leg3_h0_bit_equivalence(), leg4_engagement_and_inertness(),
            leg5_decision_rule_logic(), leg6_wiring_smoke_json(),
            leg7_fidelity_target_hash()]
    print(f"E9 SUITE ALL PASS: {all(legs)}")
    if not all(legs):
        sys.exit(1)


if __name__ == "__main__":
    main()
