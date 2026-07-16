"""
Phase 2.7: Validation Runner for Pricing Mechanism
====================================================

This runner exercises the Phase 2.7 pricing mechanism on a small but
representative experimental matrix to verify that the implementation
produces sensible results before we commit fleet time to a full pricing
capacity sweep. The validation runner is deliberately simpler than the
main phase2_6_branching_toggle runner because we are testing the
implementation, not running the full publication-grade experiment.

The experimental matrix
-----------------------

The validation runs a four-stage serial chain with summed-at-retailer
demand at 1.3x capacity. Three demand environments are tested:

  ar1_high             - stationary high persistence (phi = 0.85)
                          Tests that the formula correctly engages on
                          persistent demand and reacts cleanly.

  regime_change        - upward regime change (phi steps 0.3 -> 0.85
                          at period 130)
                          Tests upward early-warning capability and
                          provides a clean lead-time-to-detection
                          measurement.

  downward_regime_change - downward regime change (phi steps 0.85 -> 0.3
                            at period 130)
                            Tests downward early-warning capability,
                            the operationally most important pricing
                            scenario for the dashboard product.

Four pricing strategies are compared in each environment:

  no_pricing             - static baseline (worst-case)
  naive_reactive         - reacts to demand without persistence test
  phi_gated_symmetric    - the proposed mechanism with symmetric thresholds
  phi_gated_asymmetric   - asymmetric variant (cuts more conservatively)

The inventory ordering policy is held fixed at 'all_sr' across all
trials so we are isolating the value of the pricing mechanism. The
extension to test pricing under different inventory scenarios is
straightforward but is deliberately deferred to keep the validation
focused.

Expected pattern
----------------

If the implementation is correct, the validation results should show:

  - no_pricing produces the lowest mean revenue per period
  - naive_reactive produces middle revenue with high variance and many
    price changes (reacting to noise as well as signal)
  - phi-gated produces the highest revenue with moderate variance and
    fewer price changes (acting only on signal)
  - In regime_change scenarios, phi-gated should have shorter lead-time
    -to-detection than naive_reactive
  - In ar1_high stationary, all policies that react should produce
    similar lead-time results because there is no transition to detect

If the validation does not match this pattern, the implementation has
a bug that needs investigation before we proceed to the full pricing
capacity sweep.

Author: JAE with Claude as research assistant
Date: April 29, 2026
"""

from typing import Optional
import argparse
import json
import time
import traceback
import numpy as np
from copy import deepcopy

# Phase 2.6 simulator infrastructure (unchanged)
from stockpyl.sim import simulation
from stockpyl.demand_source import DemandSource

from phase2_3_stage1_network import SKU_SPECS
from phase2_3_stage3_policy_comparison import apply_capacity_constraints
from phase2_3_stage2_demand import generate_compound_poisson_demand

from phase2_6_serial_network import (
    SERIAL_NODE_SPECS, SERIAL_RETAILERS_FED,
    build_phase2_6_serial_network,
)
from phase2_6_timevarying_demand import (
    constant_schedule,
    regime_change_schedule,
    generate_iid_normal_demand,
    generate_timevarying_ar1_demand,
)
from phase2_6_policy_scenarios import apply_scenario_multiproduct

# Phase 2.7 components
from phase2_7_demand_response import DemandResponseConfig
from phase2_7_pricing_policies import PricingPolicyConfig
from phase2_7_pricing_manager import (
    PricingScenarioConfig,
    apply_pricing_to_retailer_streams,
    get_transition_period_for_environment,
)


# =========================================================================
# LEVEL SHIFT POST-PROCESSING
# =========================================================================
# The Phase 2.6 demand environments change AR(1) persistence over time
# but hold the long-run mean constant. This is the right design for
# inventory experiments because what matters there is the persistence
# pattern that drives bullwhip dynamics. For pricing experiments,
# however, we need explicit level shifts because the pricing policy
# reacts to mean demand shifts, not to changes in autocorrelation.
#
# We post-process the AR(1) demand streams by adding a deterministic
# level shift schedule. The post-processing preserves the AR(1)
# autocorrelation structure (it is just a constant offset added to
# the entire stream after a given period), and it gives us clean
# control over both the magnitude and the timing of the shift.

def apply_level_shift(
    demand_stream: np.ndarray,
    shift_magnitude: float,
    shift_period: int,
    shift_duration: Optional[int] = None,
) -> np.ndarray:
    """Add a level shift to an AR(1) demand stream.

    Adds shift_magnitude (in absolute demand units, not a ratio) to
    every period from shift_period onward. If shift_duration is given,
    the shift only applies for that many periods, after which the
    stream returns to its original level (transient shift). If
    shift_duration is None, the shift is sustained for the rest of the
    simulation (persistent shift).

    Parameters
    ----------
    demand_stream : np.ndarray
        The original AR(1) demand stream.
    shift_magnitude : float
        Amount to add to each period during the shift. Positive for
        upward shifts, negative for downward.
    shift_period : int
        Period at which the shift begins (inclusive).
    shift_duration : int, optional
        Number of periods the shift lasts. None means sustained
        through end of simulation.

    Returns
    -------
    np.ndarray
        Demand stream with the level shift applied. Same length as
        the input. Clipped to non-negative values.
    """
    shifted = demand_stream.copy()
    if shift_duration is None:
        # Persistent shift: apply from shift_period to end.
        shifted[shift_period:] += shift_magnitude
    else:
        # Transient shift: apply for shift_duration periods only.
        end_period = min(shift_period + shift_duration, len(shifted))
        shifted[shift_period:end_period] += shift_magnitude
    return np.maximum(shifted, 0.0)


# =========================================================================
# CONFIGURATION
# =========================================================================

DEFAULT_NUM_PERIODS = 260
DEFAULT_WARMUP_PERIODS = 52
DEFAULT_CAPACITY_MULTIPLIER = 1.3
DEFAULT_INVENTORY_SCENARIO = 'all_sr'

# The serial chain has the retailer at node index 3.
RETAILER_INDEX = 3
MANUFACTURER_INDEX = 0

# Pricing scenario presets used in the validation. Each preset bundles
# the pricing policy choice with elasticity-matched configuration.
def make_pricing_scenarios(elasticity=1.5, review_interval=20):
    """Construct the standard pricing scenario set for validation.

    All four scenarios share the same elasticity and review interval
    so the comparison is clean (only the policy logic differs).
    """
    base_demand_cfg = DemandResponseConfig(elasticity=elasticity)
    base_policy_cfg = PricingPolicyConfig(
        elasticity=elasticity,
        review_interval=review_interval,
    )
    return {
        'no_pricing': PricingScenarioConfig(
            pricing_policy_name='no_pricing',
            policy_config=base_policy_cfg,
            demand_response_config=base_demand_cfg,
        ),
        'naive_reactive': PricingScenarioConfig(
            pricing_policy_name='naive_reactive',
            policy_config=base_policy_cfg,
            demand_response_config=base_demand_cfg,
        ),
        'phi_gated_symmetric': PricingScenarioConfig(
            pricing_policy_name='phi_gated_symmetric',
            policy_config=base_policy_cfg,
            demand_response_config=base_demand_cfg,
        ),
        'phi_gated_asymmetric': PricingScenarioConfig(
            pricing_policy_name='phi_gated_asymmetric',
            policy_config=base_policy_cfg,
            demand_response_config=base_demand_cfg,
        ),
    }


# Demand environment presets. We construct these directly here rather
# than importing from the runner because the validation needs the
# downward_regime_change environment which only lives inside the runner.
#
# The environments fall into two groups based on what they test:
#
# Group 1 - PERSISTENCE-ONLY ENVIRONMENTS (legacy from Phase 2.6 inventory
# experiments). These environments change the AR(1) persistence parameter
# phi over time but hold the long-run mean constant. They were designed
# for inventory experiments where bullwhip amplification depends on phi.
# For pricing experiments these environments rarely trigger policy
# reactions because there is no explicit demand level shift to detect.
# They are kept here for documentation and as negative controls.
#
# Group 2 - LEVEL-SHIFT ENVIRONMENTS (added April 29, 2026 for Phase 2.7
# pricing validation). These environments hold AR(1) persistence high
# (phi=0.85, in the engagement zone) and apply an explicit demand level
# shift at a known timestep. They directly test the pricing mechanism
# because the level shift is what pricing policies are designed to
# react to, and the high persistence ensures the phi gating allows
# reactions through.
#
# An environment dict with a 'level_shift_fraction' field specifies a
# multiplicative shift applied to the summed baseline demand at
# 'level_shift_period'. A value of 0.20 means demand is bumped up by
# 20 percent starting at that period. Negative values mean downward
# shifts. If 'level_shift_duration' is set the shift is transient;
# otherwise it persists through the end of simulation.
def get_validation_environments():
    """The demand environments for the Phase 2.7 validation.

    Six environments split between persistence-only legacy and
    level-shift environments designed specifically for pricing tests.
    """
    return {
        # ---- LEVEL-SHIFT ENVIRONMENTS (the meaningful pricing tests) ----
        'ar1_high_no_shift': {
            'name': 'ar1_high_no_shift',
            'generator_kind': 'ar1',
            'schedule': constant_schedule(0.85),
            'level_shift_fraction': 0.0,  # no shift = control
            'level_shift_period': 130,
            'level_shift_duration': None,
            'description': ('Stationary AR(1) phi=0.85 with NO level shift '
                              '(control: policies should NOT react)'),
        },
        'level_shift_up_persistent': {
            'name': 'level_shift_up_persistent',
            'generator_kind': 'ar1',
            'schedule': constant_schedule(0.85),
            'level_shift_fraction': 0.20,  # +20% shift
            'level_shift_period': 130,
            'level_shift_duration': None,  # sustained through end
            'description': ('AR(1) phi=0.85 with persistent +20% level '
                              'shift at t=130 (upward preference shift)'),
        },
        'level_shift_down_persistent': {
            'name': 'level_shift_down_persistent',
            'generator_kind': 'ar1',
            'schedule': constant_schedule(0.85),
            'level_shift_fraction': -0.20,  # -20% shift
            'level_shift_period': 130,
            'level_shift_duration': None,
            'description': ('AR(1) phi=0.85 with persistent -20% level '
                              'shift at t=130 (downward preference shift, '
                              'early-warning test)'),
        },
        # ---- DISCRIMINATION-TEST ENVIRONMENTS (added April 29, 2026 for
        # the phi-gating discrimination capability and asymmetric variant
        # value tests). These environments combine a level shift (to give
        # the policies something to react to) with a low or moderate
        # underlying persistence (so the phi gating has work to do).
        # The expected pattern is that naive_reactive reacts to the
        # level shift but phi-gated correctly identifies the persistence
        # as below the engagement threshold and holds price.
        'low_phi_shift_up': {
            'name': 'low_phi_shift_up',
            'generator_kind': 'ar1',
            'schedule': constant_schedule(0.3),
            'level_shift_fraction': 0.20,
            'level_shift_period': 130,
            'level_shift_duration': None,
            'description': ('AR(1) phi=0.3 (LOW persistence) with +20% '
                              'level shift at t=130. Tests phi-gating '
                              'discrimination: naive reacts but '
                              'phi-gated should not (phi below 0.6 '
                              'engagement threshold).'),
        },
        'low_phi_shift_down': {
            'name': 'low_phi_shift_down',
            'generator_kind': 'ar1',
            'schedule': constant_schedule(0.3),
            'level_shift_fraction': -0.20,
            'level_shift_period': 130,
            'level_shift_duration': None,
            'description': ('AR(1) phi=0.3 (LOW persistence) with -20% '
                              'level shift at t=130. Tests phi-gating '
                              'discrimination on downward direction: '
                              'naive cuts price but phi-gated should '
                              'not.'),
        },
        'mid_phi_shift_down': {
            'name': 'mid_phi_shift_down',
            'generator_kind': 'ar1',
            'schedule': constant_schedule(0.65),
            'level_shift_fraction': -0.20,
            'level_shift_period': 130,
            'level_shift_duration': None,
            'description': ('AR(1) phi=0.65 (between symmetric and '
                              'asymmetric down thresholds) with -20% '
                              'level shift at t=130. Tests asymmetric '
                              'variant: symmetric (threshold 0.6) cuts '
                              'price, asymmetric (threshold 0.75) does '
                              'not.'),
        },
        # ---- PERSISTENCE-ONLY ENVIRONMENTS (legacy, for reference) ----
        'ar1_high': {
            'name': 'ar1_high',
            'generator_kind': 'ar1',
            'schedule': constant_schedule(0.85),
            'description': 'Stationary AR(1) phi=0.85 (at engagement boundary)',
        },
        'regime_change': {
            'name': 'regime_change',
            'generator_kind': 'ar1',
            'schedule': regime_change_schedule(
                baseline_phi=0.3,
                new_regime_phi=0.85,
                transition_period=130,
            ),
            'description': ('Regime change: phi=0.3 baseline, '
                              'steps to 0.85 at t=130 (upward persistence '
                              'shift, NO explicit level shift)'),
        },
        'downward_regime_change': {
            'name': 'downward_regime_change',
            'generator_kind': 'ar1',
            'schedule': regime_change_schedule(
                baseline_phi=0.85,
                new_regime_phi=0.3,
                transition_period=130,
            ),
            'description': ('Downward regime change: phi=0.85 baseline, '
                              'steps to 0.3 at t=130 (downward persistence '
                              'shift, NO explicit level shift)'),
        },
    }


# =========================================================================
# DEMAND STREAM GENERATION
# =========================================================================

def generate_one_baseline_stream(sku, env_config, seed, num_periods):
    """Generate one baseline demand stream for a (sku, seed) combination.

    This is the same logic as the runner's _generate_one_demand_stream
    but copied here to keep the validation runner self-contained. We
    deliberately do NOT import from phase2_6_branching_toggle because
    that creates a circular import and obscures dependencies.
    """
    if sku.demand_type == 'ar1':
        if env_config['generator_kind'] == 'iid':
            return generate_iid_normal_demand(
                mean=sku.mean_demand,
                std=sku.mean_demand * sku.cv,
                num_periods=num_periods,
                seed=seed,
            )
        elif env_config['generator_kind'] == 'ar1':
            return generate_timevarying_ar1_demand(
                mean=sku.mean_demand,
                stationary_std=sku.mean_demand * sku.cv,
                schedule=env_config['schedule'],
                num_periods=num_periods,
                seed=seed,
            )
        else:
            raise ValueError(
                f"Unknown generator: {env_config['generator_kind']}"
            )
    elif sku.demand_type == 'compound_poisson':
        return generate_compound_poisson_demand(
            arrival_rate=sku.cp_arrival_rate,
            mean_size=sku.cp_mean_size,
            num_periods=num_periods,
            seed=seed,
        )
    else:
        raise ValueError(f"Unknown demand_type: {sku.demand_type}")


def generate_summed_baseline_streams(env_config, trial_seed, num_periods):
    """Generate the summed_at_retailer baseline streams for one trial.

    Returns a dict mapping SKU id to baseline demand array. Each stream
    is the sum of six hypothetical retailer streams, replicating the
    Phase 2.6 summed_at_retailer demand mode used in Direction 4.

    If the environment specifies a level_shift_fraction, the level
    shift is applied to the summed stream after the AR(1) generation.
    Adding a constant to the summed stream is mathematically equivalent
    to adding (constant / 6) to each individual stream before summing,
    so the AR(1) autocorrelation structure is preserved exactly.

    This dict is what the pricing manager consumes to produce realized
    streams. After pricing is applied, the realized streams are
    assigned to the serial retailer's demand sources for the
    inventory simulation.
    """
    gen_periods = num_periods + 20
    baseline_streams = {}
    for sku in SKU_SPECS:
        combined = np.zeros(gen_periods)
        for i in range(6):
            synthetic_retailer_idx = 6 + i
            seed = (trial_seed * 10000
                    + synthetic_retailer_idx * 100
                    + sku.sku_id)
            stream = generate_one_baseline_stream(
                sku, env_config, seed, gen_periods,
            )
            combined += stream
        combined = np.maximum(combined, 0.0)

        # Apply level shift if the environment specifies one.
        # The shift is multiplicative on the summed mean: a fraction
        # of 0.20 adds 0.20 times the summed-stream mean (6 * sku.mean_demand)
        # to every period from level_shift_period onward. Negative
        # fractions produce downward shifts. Duration controls whether
        # the shift is persistent (None) or transient (integer).
        shift_fraction = env_config.get('level_shift_fraction', 0.0)
        if shift_fraction != 0.0:
            shift_period = env_config.get('level_shift_period', 130)
            shift_duration = env_config.get('level_shift_duration', None)
            # Shift magnitude is fraction of the summed-stream mean,
            # which equals 6 times the per-retailer mean_demand.
            shift_magnitude = shift_fraction * 6.0 * sku.mean_demand
            combined = apply_level_shift(
                demand_stream=combined,
                shift_magnitude=shift_magnitude,
                shift_period=shift_period,
                shift_duration=shift_duration,
            )

        baseline_streams[sku.sku_id] = combined
    return baseline_streams


def assign_realized_streams_to_retailer(
    nodes_by_index, products_by_tier_and_sku, realized_streams,
):
    """Assign the realized demand streams to the retailer's demand sources.

    Mirrors what configure_demand_serial does in Phase 2.6 but takes
    pre-computed realized streams as input rather than generating them
    on the fly. This is the integration point where pricing-aware
    streams enter the inventory simulation.
    """
    retailer = nodes_by_index[RETAILER_INDEX]
    demand_sources = {}
    for sku in SKU_SPECS:
        ret_prod = products_by_tier_and_sku['retailer'][sku.sku_id]
        demand_sources[ret_prod.index] = DemandSource(
            type='D',
            demand_list=realized_streams[sku.sku_id].tolist(),
        )
    retailer.demand_source = demand_sources


# =========================================================================
# COST EXTRACTION
# =========================================================================

def extract_chain_costs(arch_node_specs, nodes_by_index,
                          num_periods, warmup_periods):
    """Extract chain-total and per-tier costs from the simulation result.

    Returns (post_warmup_cost, per_tier_cost dict). Uses the same
    accounting as phase2_6_branching_toggle: holding + stockout +
    optional in-transit cost summed over post-warmup periods at every
    node, with per-tier accounting for downstream analysis.
    """
    tier_lookup = {ns.index: ns.tier_level for ns in arch_node_specs}
    post_warmup_cost = 0.0
    per_tier_cost = {}

    for node_idx, node in nodes_by_index.items():
        tier = tier_lookup.get(node_idx)
        node_cost = 0.0
        for t in range(warmup_periods, num_periods):
            if t < len(node.state_vars):
                sv = node.state_vars[t]
                node_cost += sv.holding_cost_incurred
                node_cost += sv.stockout_cost_incurred
                if hasattr(sv, 'in_transit_holding_cost_incurred'):
                    node_cost += sv.in_transit_holding_cost_incurred
        post_warmup_cost += node_cost
        if tier is not None:
            per_tier_cost[tier] = per_tier_cost.get(tier, 0.0) + node_cost

    return post_warmup_cost, per_tier_cost


# =========================================================================
# SINGLE-TRIAL EXECUTION
# =========================================================================

def run_pricing_trial(
    env_config,
    inventory_scenario_name,
    pricing_scenario_name,
    pricing_scenario,
    trial_seed,
    num_periods=DEFAULT_NUM_PERIODS,
    warmup_periods=DEFAULT_WARMUP_PERIODS,
    capacity_multiplier=DEFAULT_CAPACITY_MULTIPLIER,
):
    """Run one pricing-enabled trial.

    Builds the four-stage serial chain, generates baseline demand
    streams, applies the pricing transformation to produce realized
    streams, runs the inventory simulation on the realized streams,
    and returns a result dict containing both pricing and inventory
    metrics.

    Parameters
    ----------
    env_config : dict
        Demand environment config (one of get_validation_environments()).
    inventory_scenario_name : str
        Inventory ordering scenario name (e.g., 'all_sr').
    pricing_scenario_name : str
        Identifier for the pricing scenario in the result record.
    pricing_scenario : PricingScenarioConfig
        The pricing configuration to apply.
    trial_seed : int
        Random seed for reproducibility. Same seed across pricing
        scenarios produces identical baseline demand, which is what
        enables the within-simulation counterfactual analysis.

    Returns
    -------
    dict
        Trial result with pricing and inventory metrics.
    """
    try:
        # Step 1: build network and apply capacity.
        net, nodes_by_index, products = build_phase2_6_serial_network()
        apply_capacity_constraints(
            nodes_by_index, products,
            capacity_multiplier=capacity_multiplier,
        )

        # Step 2: generate baseline demand streams (price-independent).
        # Same seed produces same baseline regardless of pricing scenario,
        # which is what enables paired-comparison statistical analysis.
        baseline_streams = generate_summed_baseline_streams(
            env_config, trial_seed, num_periods,
        )

        # Step 3: apply pricing transformation. The pricing manager walks
        # through periods sequentially, queries the pricing policy at
        # review intervals, and produces the realized demand streams.
        transition_period = get_transition_period_for_environment(
            env_config['name'], env_config,
        )
        realized_streams, price_history, pricing_metadata = (
            apply_pricing_to_retailer_streams(
                sku_baseline_streams=baseline_streams,
                pricing_scenario=pricing_scenario,
                transition_period=transition_period,
            )
        )

        # Step 4: assign realized streams to the retailer.
        assign_realized_streams_to_retailer(
            nodes_by_index, products, realized_streams,
        )

        # Step 5: configure inventory ordering policies via scenario.
        # We construct a minimal arch_config dict mirroring what
        # phase2_6_branching_toggle's make_architecture_config produces,
        # because apply_scenario_multiproduct expects this structure.
        arch_config = {
            'architecture': 'serial',
            'demand_mode': 'summed_at_retailer',
            'node_specs': SERIAL_NODE_SPECS,
            'retailers_fed': SERIAL_RETAILERS_FED,
            'retailer_indices': [RETAILER_INDEX],
            'manufacturer_index': MANUFACTURER_INDEX,
            'chain_length': 4,
        }
        apply_scenario_multiproduct(
            scenario_name=inventory_scenario_name,
            arch_config=arch_config,
            nodes_by_index=nodes_by_index,
            products_by_tier_and_sku=products,
            sku_specs=SKU_SPECS,
            oracle_phi_per_node=None,  # not needed for non-oracle scenarios
        )

        # Step 6: run the inventory simulation.
        total_cost = simulation(
            net, num_periods=num_periods,
            rand_seed=42, progress_bar=False,
        )

        # Step 7: extract cost outcomes.
        post_warmup_cost, per_tier_cost = extract_chain_costs(
            SERIAL_NODE_SPECS, nodes_by_index,
            num_periods, warmup_periods,
        )
        measured_periods = num_periods - warmup_periods
        cost_per_period = post_warmup_cost / measured_periods

        # Step 8: combine pricing and inventory metrics into result.
        # Revenue is restricted to post-warmup periods to match the
        # cost accounting and produce a clean revenue-vs-cost comparison.
        rev_per_period = pricing_metadata['revenue_per_period']
        post_warmup_revenue = float(np.sum(rev_per_period[warmup_periods:]))
        post_warmup_mean_rev = post_warmup_revenue / measured_periods

        result = {
            'trial_seed': trial_seed,
            'env': env_config['name'],
            'inventory_scenario': inventory_scenario_name,
            'pricing_scenario': pricing_scenario_name,
            'pricing_policy': pricing_scenario.pricing_policy_name,
            'elasticity': pricing_scenario.demand_response_config.elasticity,
            'capacity_multiplier': capacity_multiplier,
            'num_periods': num_periods,
            'warmup_periods': warmup_periods,
            # Inventory cost metrics (existing pattern from Phase 2.6).
            'total_cost_full': float(total_cost),
            'total_cost_post_warmup': float(post_warmup_cost),
            'cost_per_period': float(cost_per_period),
            'per_tier_cost': per_tier_cost,
            # Pricing metrics (new for Phase 2.7).
            'total_revenue_post_warmup': post_warmup_revenue,
            'mean_revenue_per_period': post_warmup_mean_rev,
            'num_price_changes': pricing_metadata['num_price_changes'],
            'first_price_change_period':
                pricing_metadata['first_price_change_period'],
            'lead_time_to_detection':
                pricing_metadata['lead_time_to_detection'],
            'transition_period': pricing_metadata['transition_period'],
            'final_price': pricing_metadata['final_price'],
            # Net value: revenue minus cost. This is the natural single-
            # number summary because it captures both the revenue uplift
            # from pricing and the inventory cost effect.
            'net_value_post_warmup': post_warmup_revenue - post_warmup_cost,
            'success': True,
        }

        return result

    except Exception as e:
        return {
            'trial_seed': trial_seed,
            'env': env_config['name'],
            'inventory_scenario': inventory_scenario_name,
            'pricing_scenario': pricing_scenario_name,
            'pricing_policy': pricing_scenario.pricing_policy_name,
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc(),
        }


# =========================================================================
# EXPERIMENT DRIVER
# =========================================================================

def run_validation(
    seed_start,
    seed_end,
    output_file,
    num_periods=DEFAULT_NUM_PERIODS,
    warmup_periods=DEFAULT_WARMUP_PERIODS,
    capacity_multiplier=DEFAULT_CAPACITY_MULTIPLIER,
    inventory_scenario=DEFAULT_INVENTORY_SCENARIO,
    elasticity=1.5,
    review_interval=20,
    environments_filter=None,
    pricing_scenarios_filter=None,
):
    """Run the full validation matrix and save results to JSON.

    The matrix is environments x pricing_scenarios x seeds. With the
    full default matrix that is 9 environments x 4 pricing scenarios
    times the number of seeds. The two filter arguments let callers
    select a subset of environments and pricing scenarios for cases
    where running the full matrix is unnecessary (for example, when
    a fleet shard wants to focus on a particular slice for diagnostic
    purposes).

    Parameters
    ----------
    seed_start, seed_end : int
        Inclusive seed range for this run.
    output_file : str
        Path for the result JSON file.
    environments_filter : list of str, optional
        If supplied, only environments whose names are in this list
        will be run. Pass None or an empty list to run all environments.
    pricing_scenarios_filter : list of str, optional
        Same idea but for pricing scenarios.
    """
    seeds = list(range(seed_start, seed_end + 1))
    n_seeds = len(seeds)
    all_environments = get_validation_environments()
    all_pricing_scenarios = make_pricing_scenarios(
        elasticity=elasticity, review_interval=review_interval,
    )

    # Apply the optional filters. The validation logic below works on
    # filtered dictionaries the same way it works on full ones, so we
    # only need to subset here at the top of the function.
    if environments_filter:
        environments = {k: v for k, v in all_environments.items()
                        if k in environments_filter}
        missing_envs = [e for e in environments_filter
                        if e not in all_environments]
        if missing_envs:
            raise ValueError(
                f"Unknown environments in filter: {missing_envs}. "
                f"Known: {sorted(all_environments.keys())}"
            )
    else:
        environments = all_environments

    if pricing_scenarios_filter:
        pricing_scenarios = {k: v for k, v in all_pricing_scenarios.items()
                              if k in pricing_scenarios_filter}
        missing_scens = [s for s in pricing_scenarios_filter
                          if s not in all_pricing_scenarios]
        if missing_scens:
            raise ValueError(
                f"Unknown pricing scenarios in filter: {missing_scens}. "
                f"Known: {sorted(all_pricing_scenarios.keys())}"
            )
    else:
        pricing_scenarios = all_pricing_scenarios

    print("=" * 70)
    print("PHASE 2.7 VALIDATION RUNNER")
    print("=" * 70)
    print(f"Architecture:         serial (4-stage)")
    print(f"Demand mode:          summed_at_retailer")
    print(f"Capacity multiplier:  {capacity_multiplier}")
    print(f"Inventory scenario:   {inventory_scenario}")
    print(f"Seed range:           [{seed_start}, {seed_end}] ({n_seeds} seeds)")
    print(f"Periods:              {num_periods} ({warmup_periods} warmup)")
    print(f"Elasticity:           {elasticity}")
    print(f"Review interval:      {review_interval} periods")
    print(f"Environments:         {list(environments.keys())}")
    print(f"Pricing scenarios:    {list(pricing_scenarios.keys())}")
    print(f"Total trials:         "
          f"{len(environments) * len(pricing_scenarios) * n_seeds}")
    print(f"Output:               {output_file}")
    print()

    overall_start = time.time()
    all_trials = []

    for env_name, env_config in environments.items():
        print()
        print("-" * 70)
        print(f"Environment: {env_name}")
        print(f"  {env_config['description']}")
        print("-" * 70)

        for pricing_name, pricing_scenario in pricing_scenarios.items():
            cell_start = time.time()
            for trial_seed in seeds:
                result = run_pricing_trial(
                    env_config=env_config,
                    inventory_scenario_name=inventory_scenario,
                    pricing_scenario_name=pricing_name,
                    pricing_scenario=pricing_scenario,
                    trial_seed=trial_seed,
                    num_periods=num_periods,
                    warmup_periods=warmup_periods,
                    capacity_multiplier=capacity_multiplier,
                )
                all_trials.append(result)

            cell_elapsed = time.time() - cell_start
            successes = sum(
                1 for t in all_trials[-n_seeds:] if t.get('success')
            )
            print(f"  {pricing_name:24s}: {successes}/{n_seeds} success, "
                  f"{cell_elapsed:.1f}s")

    overall_elapsed = time.time() - overall_start

    # Build output dict and save.
    n_success = sum(1 for r in all_trials if r.get('success'))
    n_fail = len(all_trials) - n_success
    output = {
        'config': {
            'experiment': 'phase2_7_validation',
            'architecture': 'serial',
            'demand_mode': 'summed_at_retailer',
            'inventory_scenario': inventory_scenario,
            'capacity_multiplier': capacity_multiplier,
            'num_periods': num_periods,
            'warmup_periods': warmup_periods,
            'seed_start': seed_start,
            'seed_end': seed_end,
            'elasticity': elasticity,
            'review_interval': review_interval,
            'environments': list(environments.keys()),
            'pricing_scenarios': list(pricing_scenarios.keys()),
            'total_trials': len(all_trials),
            'successes': n_success,
            'failures': n_fail,
            'elapsed_seconds': overall_elapsed,
        },
        'trials': all_trials,
    }
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print()
    print("=" * 70)
    print(f"VALIDATION COMPLETE in {overall_elapsed/60:.1f} min")
    print(f"Total trials: {len(all_trials)}")
    print(f"Successes: {n_success}, Failures: {n_fail}")
    if overall_elapsed > 0:
        print(f"Throughput: {len(all_trials) / overall_elapsed:.2f} trials/sec")
    print(f"Results saved to: {output_file}")
    print("=" * 70)

    return all_trials


# =========================================================================
# COMMAND-LINE INTERFACE
# =========================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Phase 2.7 pricing validation runner. Runs the '
                       'environments x pricing scenarios x seeds matrix '
                       'and saves results to a JSON file. When invoked as '
                       'a fleet worker, --environments and --pricing-scenarios '
                       'can subset the matrix.'
    )
    parser.add_argument('--seed-start', type=int, default=0)
    parser.add_argument('--seed-end', type=int, default=4,
                        help='Last seed (INCLUSIVE). Default 4 = 5 seeds.')
    parser.add_argument('--output', type=str, default='phase2_7_validation_results.json')
    parser.add_argument('--num-periods', type=int, default=DEFAULT_NUM_PERIODS)
    parser.add_argument('--warmup-periods', type=int,
                        default=DEFAULT_WARMUP_PERIODS)
    parser.add_argument('--capacity-multiplier', type=float,
                        default=DEFAULT_CAPACITY_MULTIPLIER)
    parser.add_argument('--inventory-scenario', type=str,
                        default=DEFAULT_INVENTORY_SCENARIO,
                        help='Inventory ordering scenario name.')
    parser.add_argument('--elasticity', type=float, default=1.5)
    parser.add_argument('--review-interval', type=int, default=20)
    # Filtering arguments for fleet shards. Each accepts a comma-separated
    # list of names, or the literal value 'all' (or empty) to mean no
    # filtering. The launcher passes specific subsets; ad-hoc local
    # invocations can omit these flags entirely to run the full matrix.
    parser.add_argument('--environments', type=str, default='all',
                        help="Comma-separated list of environment names to run, "
                              "or 'all' for the full set. Default 'all'.")
    parser.add_argument('--pricing-scenarios', type=str, default='all',
                        help="Comma-separated list of pricing scenario names "
                              "to run, or 'all' for the full set. Default 'all'.")
    return parser.parse_args()


def _parse_filter_arg(value):
    """Convert a comma-separated CLI argument into a list, or None for 'all'.

    The launcher passes either 'all' (meaning no filter) or a comma-
    separated list of names. We normalize this into a Python list, or
    None when no filtering should be applied.
    """
    if value is None:
        return None
    cleaned = value.strip()
    if cleaned == '' or cleaned.lower() == 'all':
        return None
    return [token.strip() for token in cleaned.split(',') if token.strip()]


if __name__ == '__main__':
    args = parse_args()
    run_validation(
        seed_start=args.seed_start,
        seed_end=args.seed_end,
        output_file=args.output,
        num_periods=args.num_periods,
        warmup_periods=args.warmup_periods,
        capacity_multiplier=args.capacity_multiplier,
        inventory_scenario=args.inventory_scenario,
        elasticity=args.elasticity,
        review_interval=args.review_interval,
        environments_filter=_parse_filter_arg(args.environments),
        pricing_scenarios_filter=_parse_filter_arg(args.pricing_scenarios),
    )
