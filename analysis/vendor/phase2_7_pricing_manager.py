"""
Phase 2.7: Pricing Manager - Integration Layer
================================================

This module provides the integration layer that bridges the pricing
policy decisions (phase2_7_pricing_policies.py) with the demand response
model (phase2_7_demand_response.py). It takes baseline customer demand
streams, applies pricing decisions made at review intervals, and produces
the realized demand streams that the chain sees.

The architectural insight
-------------------------

Pricing decisions are made at discrete review intervals (e.g., every 20
periods), and within each interval the price is held constant. This
discrete-review structure means that the entire realized demand stream
can be pre-computed BEFORE running the inventory simulation, by walking
through periods sequentially and making pricing decisions whenever a
review interval is reached. The pricing layer therefore lives entirely
upstream of the inventory simulation and does not require any
modification to the existing simulation loop.

The flow is:
  baseline customer demand (from AR(1) generator)
    ->  apply pricing transformation (this module)
      ->  realized demand stream (what the chain sees)
        ->  feed to existing inventory simulator
          ->  cost outcomes

This clean separation lets inventory-only experiments continue to work
unchanged (just skip the pricing transformation) and adds pricing as a
new optional dimension without modifying the core simulation logic.

Aggregation across SKUs
-----------------------

In multi-SKU chains, the retailer makes one pricing decision per review
interval that applies to all SKUs at that retailer. The pricing policy's
decision is informed by the aggregated demand across all SKUs at the
retailer, which mimics the realistic case where retailers do
category-level or brand-level pricing rather than per-SKU pricing. This
also makes the policy more robust because it observes more demand signal
than any individual SKU would provide.

Multi-retailer chains
---------------------

In branched chains with multiple retailers, each retailer makes its own
independent pricing decisions based on its own observed demand. Each
retailer instantiates its own pricing policy (with the same configuration)
and operates independently. This mimics the realistic case where retailers
in a hub-and-spoke distribution structure operate as independent
businesses making their own pricing decisions.

Lead-time-to-detection metric
-----------------------------

For experiments with a known regime change (regime_change and
downward_regime_change environments), this module computes the lead-time
metric as the difference between the regime change period and the first
period at which any pricing policy makes a price change after the
transition. This is a direct measurement of the early-warning capability
of each policy.

Author: JAE with Claude as research assistant
Date: April 29, 2026
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from phase2_7_demand_response import (
    DemandResponseConfig,
    apply_price_response,
    revenue_at_period,
)
from phase2_7_pricing_policies import (
    PricingPolicy,
    PricingPolicyConfig,
    make_pricing_policy,
    PRICING_POLICY_REGISTRY,
)


# =========================================================================
# CONFIGURATION
# =========================================================================

@dataclass
class PricingScenarioConfig:
    """Complete configuration for a pricing scenario.

    Bundles together the pricing policy choice, the demand response
    model parameters, and the operational parameters (initial price,
    review schedule). The runner instantiates one of these per
    experimental cell that involves pricing.

    Attributes
    ----------
    pricing_policy_name : str
        Which pricing policy to use, from PRICING_POLICY_REGISTRY.
        Examples: 'no_pricing', 'naive_reactive', 'phi_gated_symmetric',
        'phi_gated_asymmetric'.
    policy_config : PricingPolicyConfig
        Configuration passed to the pricing policy constructor.
    demand_response_config : DemandResponseConfig
        Configuration for the constant-elasticity demand response.
        The elasticity here should typically match the elasticity in
        policy_config so the pricing policy's price adjustments are
        consistent with the actual demand response.
    initial_price : float
        Starting price at simulation period 0. Default 1.0 matches the
        default reference_price in the demand response config, which
        means initial demand equals baseline demand.
    """
    pricing_policy_name: str
    policy_config: PricingPolicyConfig = field(default_factory=PricingPolicyConfig)
    demand_response_config: DemandResponseConfig = field(default_factory=DemandResponseConfig)
    initial_price: float = 1.0

    def __post_init__(self):
        if self.pricing_policy_name not in PRICING_POLICY_REGISTRY:
            raise ValueError(
                f"Unknown pricing policy '{self.pricing_policy_name}'. "
                f"Known: {sorted(PRICING_POLICY_REGISTRY.keys())}"
            )
        if self.initial_price <= 0:
            raise ValueError(
                f"Initial price must be positive, got {self.initial_price}."
            )


# =========================================================================
# CORE TRANSFORMATION
# =========================================================================

def apply_pricing_to_retailer_streams(
    sku_baseline_streams: Dict[Any, np.ndarray],
    pricing_scenario: PricingScenarioConfig,
    transition_period: Optional[int] = None,
) -> Tuple[Dict[Any, np.ndarray], List[float], Dict[str, Any]]:
    """Apply pricing decisions to a single retailer's per-SKU baseline streams.

    Walks through periods sequentially, applying the elasticity model to
    each SKU's baseline demand using the current retailer-level price.
    At each review interval, calls the pricing policy with the aggregated
    demand history (summed across SKUs) to decide the next interval's
    price. Returns the per-SKU realized demand streams along with the
    price history and metadata for analysis.

    Parameters
    ----------
    sku_baseline_streams : dict
        Maps SKU identifier to baseline demand array. All arrays must
        have the same length.
    pricing_scenario : PricingScenarioConfig
        The pricing scenario to apply.
    transition_period : int, optional
        Known regime change period for lead-time-to-detection metric.
        If supplied, the metadata records the first period after this
        timestep at which the policy made a price change.

    Returns
    -------
    realized_streams : dict
        Maps SKU identifier to realized demand array, same shape as
        baseline streams.
    price_history : list of float
        Length-num_periods list of the price in effect at each period.
    metadata : dict
        Contains:
          - num_price_changes: count of distinct price changes
          - first_price_change_period: when the first change occurred
          - lead_time_to_detection: periods between transition_period
            and first_price_change_period (if both are defined)
          - revenue_per_period: list of revenue at each period
          - pricing_policy_name: for traceability
    """
    if not sku_baseline_streams:
        raise ValueError("sku_baseline_streams must contain at least one SKU")

    # Validate that all streams have the same length.
    sku_ids = list(sku_baseline_streams.keys())
    num_periods = len(sku_baseline_streams[sku_ids[0]])
    for sku_id, stream in sku_baseline_streams.items():
        if len(stream) != num_periods:
            raise ValueError(
                f"All SKU streams must have the same length. "
                f"SKU {sku_ids[0]} has length {num_periods} but "
                f"SKU {sku_id} has length {len(stream)}."
            )

    # Instantiate the pricing policy.
    policy = make_pricing_policy(
        pricing_scenario.pricing_policy_name,
        pricing_scenario.policy_config,
    )
    review_interval = pricing_scenario.policy_config.review_interval

    # Initialize state.
    current_price = pricing_scenario.initial_price
    price_history = []
    aggregated_demand_history: List[float] = []
    realized_streams: Dict[Any, List[float]] = {sku_id: [] for sku_id in sku_ids}
    revenue_per_period: List[float] = []

    # Track price-change events for the metrics.
    num_price_changes = 0
    first_price_change_period: Optional[int] = None
    last_review_period = -1

    # Walk through periods sequentially.
    for t in range(num_periods):
        # Step 1: compute realized demand for each SKU at the current price.
        period_aggregate = 0.0
        period_revenue = 0.0
        for sku_id in sku_ids:
            baseline_t = float(sku_baseline_streams[sku_id][t])
            realized_t = apply_price_response(
                baseline_demand=baseline_t,
                price=current_price,
                config=pricing_scenario.demand_response_config,
            )
            realized_streams[sku_id].append(realized_t)
            period_aggregate += realized_t
            period_revenue += revenue_at_period(realized_t, current_price)

        # Step 2: record observations.
        aggregated_demand_history.append(period_aggregate)
        price_history.append(current_price)
        revenue_per_period.append(period_revenue)

        # Step 3: at review intervals, query the policy for the next price.
        # The first review happens at period (review_interval - 1) so the
        # policy has review_interval periods of demand history to work with.
        # The exact alignment matters less than that we are consistent.
        is_review_period = (t + 1) % review_interval == 0
        if is_review_period and t > last_review_period:
            new_price = policy.decide_price(
                period=t + 1,
                demand_history=aggregated_demand_history,
                current_price=current_price,
            )
            last_review_period = t

            if abs(new_price - current_price) > 1e-9:
                num_price_changes += 1
                if first_price_change_period is None:
                    first_price_change_period = t + 1
                current_price = new_price

    # Convert lists back to numpy arrays for downstream consumers.
    realized_arrays: Dict[Any, np.ndarray] = {
        sku_id: np.asarray(stream, dtype=float)
        for sku_id, stream in realized_streams.items()
    }

    # Compute lead-time-to-detection if applicable.
    lead_time = None
    if transition_period is not None and first_price_change_period is not None:
        if first_price_change_period >= transition_period:
            lead_time = first_price_change_period - transition_period

    metadata = {
        "pricing_policy_name": pricing_scenario.pricing_policy_name,
        "num_price_changes": num_price_changes,
        "first_price_change_period": first_price_change_period,
        "transition_period": transition_period,
        "lead_time_to_detection": lead_time,
        "revenue_per_period": revenue_per_period,
        "total_revenue": float(np.sum(revenue_per_period)),
        "mean_revenue_per_period": float(np.mean(revenue_per_period)),
        "revenue_std": float(np.std(revenue_per_period, ddof=1))
                        if len(revenue_per_period) > 1 else 0.0,
        "final_price": current_price,
    }

    return realized_arrays, price_history, metadata


def apply_pricing_to_chain(
    chain_baseline_streams: Dict[Tuple[int, Any], np.ndarray],
    pricing_scenario: PricingScenarioConfig,
    transition_period: Optional[int] = None,
) -> Tuple[Dict[Tuple[int, Any], np.ndarray], Dict[int, Any]]:
    """Apply pricing across a multi-retailer chain.

    Each retailer operates its own independent pricing policy on its own
    SKUs. The retailers do not coordinate or share information; each one
    makes pricing decisions based on its own observed demand. This mimics
    the realistic case where retailers in a distribution structure
    operate as independent businesses.

    Parameters
    ----------
    chain_baseline_streams : dict
        Maps (retailer_idx, sku_id) tuples to baseline demand arrays.
        All arrays must have the same length. The retailer indices can
        be any hashable values (typically node integer indices).
    pricing_scenario : PricingScenarioConfig
        The pricing scenario to apply. The same policy class and
        configuration is used at every retailer, but each retailer's
        instance is independent.
    transition_period : int, optional
        Known regime change period for lead-time-to-detection metric.

    Returns
    -------
    realized_streams : dict
        Same shape as input but with elasticity applied.
    per_retailer_metadata : dict
        Maps retailer_idx to that retailer's metadata dict from
        apply_pricing_to_retailer_streams.
    """
    # Group baseline streams by retailer.
    retailers_to_skus: Dict[int, Dict[Any, np.ndarray]] = {}
    for (retailer_idx, sku_id), stream in chain_baseline_streams.items():
        if retailer_idx not in retailers_to_skus:
            retailers_to_skus[retailer_idx] = {}
        retailers_to_skus[retailer_idx][sku_id] = stream

    # Apply pricing independently at each retailer.
    realized_streams: Dict[Tuple[int, Any], np.ndarray] = {}
    per_retailer_metadata: Dict[int, Any] = {}
    for retailer_idx, sku_streams in retailers_to_skus.items():
        retailer_realized, retailer_prices, retailer_meta = (
            apply_pricing_to_retailer_streams(
                sku_baseline_streams=sku_streams,
                pricing_scenario=pricing_scenario,
                transition_period=transition_period,
            )
        )
        # Re-key the realized streams back into the (retailer, sku) format.
        for sku_id, realized in retailer_realized.items():
            realized_streams[(retailer_idx, sku_id)] = realized
        # Include the price history in the metadata.
        retailer_meta["price_history"] = retailer_prices
        per_retailer_metadata[retailer_idx] = retailer_meta

    return realized_streams, per_retailer_metadata


# =========================================================================
# REGIME-CHANGE TRANSITION DETECTION
# =========================================================================

def get_transition_period_for_environment(
    env_name: str,
    env_config: Optional[dict] = None,
) -> Optional[int]:
    """Return the known regime-change or level-shift period for an env.

    The runner uses this helper to look up the transition period when
    setting up pricing experiments that need lead-time-to-detection.
    Returns None for environments without a defined transition.

    Two sources of transition info are checked. First, if env_config is
    supplied and has a non-zero 'level_shift_fraction', the function
    returns the env's 'level_shift_period' field. This handles the
    Phase 2.7 level-shift environments which carry their transition
    timestep in their config. Second, the helper falls back to a
    hardcoded list of legacy persistence-only environments
    ('regime_change', 'downward_regime_change') which by convention
    have their transition at period 130.

    The two-source design lets new environments work automatically
    without requiring this helper to be updated, while preserving
    backward compatibility with the legacy environments that do not
    carry their transition period in their config.

    Parameters
    ----------
    env_name : str
        The environment name (used for the legacy fallback).
    env_config : dict, optional
        The full environment config dict. If supplied and the env has
        a level_shift_fraction set, this is the preferred source.

    Returns
    -------
    int or None
        The transition period, or None if no transition is defined.
    """
    # First source: explicit level_shift_period in env_config.
    if env_config is not None:
        shift_fraction = env_config.get('level_shift_fraction', 0.0)
        if shift_fraction != 0.0:
            return env_config.get('level_shift_period', 130)

    # Second source: legacy persistence-only envs (hardcoded).
    if env_name in ("regime_change", "downward_regime_change"):
        return 130

    return None


# =========================================================================
# AGGREGATION HELPERS FOR ANALYSIS
# =========================================================================

def aggregate_chain_pricing_metrics(
    per_retailer_metadata: Dict[int, Any],
) -> Dict[str, Any]:
    """Aggregate per-retailer pricing metadata into chain-level summary.

    For multi-retailer chains, this produces a single-row summary that
    can be stored alongside the existing inventory metrics. The chain-
    level revenue is the sum across retailers; the lead-time-to-detection
    is the minimum across retailers (whichever retailer reacted first
    sets the chain's effective lead time).

    Parameters
    ----------
    per_retailer_metadata : dict
        Output from apply_pricing_to_chain.

    Returns
    -------
    dict
        Chain-level aggregated metrics suitable for inclusion in a
        trial result record.
    """
    if not per_retailer_metadata:
        return {
            "total_chain_revenue": 0.0,
            "mean_revenue_per_period": 0.0,
            "total_price_changes": 0,
            "min_lead_time_to_detection": None,
            "first_price_change_period": None,
        }

    total_revenue = 0.0
    total_price_changes = 0
    lead_times: List[int] = []
    first_changes: List[int] = []
    revenue_per_period_sum = None  # accumulate as np.ndarray

    for retailer_meta in per_retailer_metadata.values():
        total_revenue += retailer_meta["total_revenue"]
        total_price_changes += retailer_meta["num_price_changes"]
        if retailer_meta["lead_time_to_detection"] is not None:
            lead_times.append(retailer_meta["lead_time_to_detection"])
        if retailer_meta["first_price_change_period"] is not None:
            first_changes.append(retailer_meta["first_price_change_period"])

        rpp = np.asarray(retailer_meta["revenue_per_period"], dtype=float)
        if revenue_per_period_sum is None:
            revenue_per_period_sum = rpp.copy()
        else:
            revenue_per_period_sum = revenue_per_period_sum + rpp

    mean_per_period = (float(revenue_per_period_sum.mean())
                       if revenue_per_period_sum is not None and
                       len(revenue_per_period_sum) > 0 else 0.0)

    return {
        "total_chain_revenue": total_revenue,
        "mean_revenue_per_period": mean_per_period,
        "total_price_changes": total_price_changes,
        "min_lead_time_to_detection": min(lead_times) if lead_times else None,
        "first_price_change_period": min(first_changes) if first_changes else None,
        "num_retailers_with_changes": len(first_changes),
    }


# =========================================================================
# SELF-TEST
# =========================================================================

def _self_test():
    """Verify the pricing manager produces consistent results.

    Tests:
      1. With no_pricing policy, realized demand equals baseline demand
         (because price stays at reference and elasticity has no effect)
      2. With elasticity, naive policy on rising demand reduces demand
         from what it would be at baseline price
      3. Multi-retailer chain produces independent decisions per retailer
      4. Lead-time-to-detection is computed correctly when policy reacts
         after a known transition
      5. Aggregation across retailers sums correctly
    """
    print("=" * 60)
    print("Phase 2.7 pricing manager self-test")
    print("=" * 60)

    # --- Test 1: no_pricing policy preserves baseline demand ---
    print("\nTest 1: no_pricing leaves demand unchanged")
    baseline = {
        "sku_a": np.array([10.0] * 100),
        "sku_b": np.array([15.0] * 100),
    }
    scenario = PricingScenarioConfig(
        pricing_policy_name="no_pricing",
    )
    realized, prices, meta = apply_pricing_to_retailer_streams(
        baseline, scenario,
    )
    print(f"  realized matches baseline: "
          f"{all(np.allclose(realized[k], baseline[k]) for k in baseline)}")
    print(f"  num_price_changes: {meta['num_price_changes']}  "
          f"(expected 0)")
    assert meta['num_price_changes'] == 0
    assert all(p == 1.0 for p in prices)

    # --- Test 2: elasticity reduces demand at high price ---
    print("\nTest 2: elasticity transforms baseline demand correctly")
    # Force a single price change by using a baseline with a clear shift
    # and a naive_reactive policy.
    baseline_shift = {
        "sku_a": np.concatenate([
            np.array([10.0] * 60),
            np.array([12.0] * 40),  # 20% upward shift starting period 60
        ]),
    }
    scenario = PricingScenarioConfig(
        pricing_policy_name="naive_reactive",
        policy_config=PricingPolicyConfig(
            elasticity=1.5,
            review_interval=20,
            recent_window=20,
            baseline_window=60,
        ),
        demand_response_config=DemandResponseConfig(elasticity=1.5),
        initial_price=1.0,
    )
    realized, prices, meta = apply_pricing_to_retailer_streams(
        baseline_shift, scenario,
    )
    # In the first 60 periods, price stays at 1.0 so realized = baseline.
    # After the shift becomes detectable (around period 80 with our
    # window settings), price should rise.
    print(f"  num_price_changes: {meta['num_price_changes']}  "
          f"(expected >= 1)")
    print(f"  first_price_change: {meta['first_price_change_period']}  "
          f"(expected ~80)")
    print(f"  final_price: {meta['final_price']:.4f}  "
          f"(expected > 1.0 because demand rose)")
    assert meta['num_price_changes'] >= 1
    assert meta['final_price'] > 1.0

    # --- Test 3: multi-retailer chain with independent decisions ---
    print("\nTest 3: multi-retailer chain runs independent pricing")
    # Two retailers with different baseline patterns.
    chain_baseline = {
        (1, "sku_a"): np.array([10.0] * 100),  # retailer 1: stable
        (1, "sku_b"): np.array([15.0] * 100),
        (2, "sku_a"): np.concatenate([  # retailer 2: shifts up
            np.array([10.0] * 60),
            np.array([13.0] * 40),
        ]),
        (2, "sku_b"): np.concatenate([
            np.array([15.0] * 60),
            np.array([19.5] * 40),  # also 30% up at retailer 2
        ]),
    }
    scenario = PricingScenarioConfig(
        pricing_policy_name="naive_reactive",
        policy_config=PricingPolicyConfig(elasticity=1.5),
        demand_response_config=DemandResponseConfig(elasticity=1.5),
    )
    chain_realized, chain_meta = apply_pricing_to_chain(
        chain_baseline, scenario,
    )
    print(f"  retailers covered: {sorted(chain_meta.keys())}")
    print(f"  retailer 1 price changes: "
          f"{chain_meta[1]['num_price_changes']}  (expected 0, no shift)")
    print(f"  retailer 2 price changes: "
          f"{chain_meta[2]['num_price_changes']}  (expected >= 1, shift)")
    assert chain_meta[1]['num_price_changes'] == 0
    assert chain_meta[2]['num_price_changes'] >= 1

    # --- Test 4: lead-time-to-detection ---
    print("\nTest 4: lead-time-to-detection metric")
    # Use transition_period=60 to match the shift in baseline_shift.
    realized, prices, meta = apply_pricing_to_retailer_streams(
        baseline_shift, scenario, transition_period=60,
    )
    print(f"  transition at period 60")
    print(f"  first price change at period: "
          f"{meta['first_price_change_period']}")
    print(f"  lead_time_to_detection: "
          f"{meta['lead_time_to_detection']} periods")
    assert meta['lead_time_to_detection'] is not None
    assert meta['lead_time_to_detection'] >= 0

    # --- Test 5: aggregation across retailers ---
    print("\nTest 5: chain-level aggregation")
    chain_summary = aggregate_chain_pricing_metrics(chain_meta)
    expected_total_revenue = sum(
        m["total_revenue"] for m in chain_meta.values()
    )
    print(f"  total_chain_revenue: {chain_summary['total_chain_revenue']:.2f}")
    print(f"  expected total: {expected_total_revenue:.2f}  "
          f"{'OK' if abs(chain_summary['total_chain_revenue'] - expected_total_revenue) < 0.01 else 'FAIL'}")
    print(f"  total_price_changes: {chain_summary['total_price_changes']}")
    assert abs(chain_summary['total_chain_revenue'] - expected_total_revenue) < 0.01

    # --- Test 6: phi_gated produces fewer changes than naive on noise ---
    print("\nTest 6: phi-gated produces fewer changes than naive on IID noise")
    rng = np.random.default_rng(42)
    iid_baseline = {
        "sku_a": np.maximum(rng.normal(10.0, 2.0, size=200), 0.1),
    }
    scenario_naive = PricingScenarioConfig(
        pricing_policy_name="naive_reactive",
        policy_config=PricingPolicyConfig(elasticity=1.5),
        demand_response_config=DemandResponseConfig(elasticity=1.5),
    )
    scenario_phi = PricingScenarioConfig(
        pricing_policy_name="phi_gated_symmetric",
        policy_config=PricingPolicyConfig(elasticity=1.5),
        demand_response_config=DemandResponseConfig(elasticity=1.5),
    )
    _, _, meta_naive = apply_pricing_to_retailer_streams(
        iid_baseline, scenario_naive,
    )
    _, _, meta_phi = apply_pricing_to_retailer_streams(
        iid_baseline, scenario_phi,
    )
    print(f"  naive_reactive on IID: {meta_naive['num_price_changes']} price changes")
    print(f"  phi_gated_symmetric on IID: {meta_phi['num_price_changes']} price changes")
    print(f"  {'OK (phi_gated produced fewer or equal)' if meta_phi['num_price_changes'] <= meta_naive['num_price_changes'] else 'unexpected: phi_gated produced more changes'}")

    # --- Test 7: get_transition_period_for_environment ---
    print("\nTest 7: get_transition_period_for_environment lookup")
    print(f"  regime_change: {get_transition_period_for_environment('regime_change')}  "
          f"(expected 130)")
    print(f"  downward_regime_change: {get_transition_period_for_environment('downward_regime_change')}  "
          f"(expected 130)")
    print(f"  ar1_high: {get_transition_period_for_environment('ar1_high')}  "
          f"(expected None)")
    assert get_transition_period_for_environment("regime_change") == 130
    assert get_transition_period_for_environment("downward_regime_change") == 130
    assert get_transition_period_for_environment("ar1_high") is None

    print("\nAll self-tests completed.")
    print("=" * 60)


if __name__ == '__main__':
    _self_test()
