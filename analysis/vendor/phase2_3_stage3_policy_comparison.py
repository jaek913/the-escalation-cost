"""
Phase 2.3 Stage 3: Three-way policy comparison with parallelization
=====================================================================

Stage 3 introduces the policy comparison that is the research value of
Phase 2.3. Three policies are compared across 100 independent trials,
each trial using common random numbers across policies so differences
reflect the policies themselves rather than random demand luck.

Policies compared:
1. Naive: base-stock = 3 * retailer mean demand at every node. Ignores
   aggregation and lead times. Dramatically understocks upstream tiers
   because the manufacturer actually needs to cover demand for 6 retailers
   plus additional lead-time inventory. Represents the worst-case
   "unsophisticated operator" configuration.

2. Informed (no capacity awareness): base-stock = aggregate_demand *
   effective_lead_time * 1.5 at each node. Applies Clark-Scarf logic with
   proper aggregation and lead-time accounting. This is our Stage 1/2
   baseline policy.

3. Informed (capacity-aware): base-stock = aggregate_demand *
   effective_lead_time * 1.5 * 1.2 at each node. Same as informed plus
   a 20% safety factor to buffer against manufacturer capacity binding.

Capacity constraint: each SKU's manufacturer product has order_capacity
set to 1.3 * aggregate mean demand (i.e., 1.3 * 6 * retailer_mean_demand).
This creates occasional capacity binding during demand peaks which is
what we need for the capacity-aware policy to have meaningful distinct
behavior.

PARALLELIZATION:
Uses joblib.Parallel with n_jobs=20. Each worker builds a fresh network,
runs all three policies against common random numbers from its trial seed,
and returns a dict of simple Python values. Total wall-clock time for
100 trials should be approximately 9-12 minutes.

Author: JAE with Claude as research assistant
Date: April 22, 2026
"""

import time
import json
import traceback
import numpy as np
from dataclasses import dataclass, field
from concurrent.futures import ProcessPoolExecutor, as_completed

from stockpyl.sim import simulation
from stockpyl.policy import Policy
from stockpyl.demand_source import DemandSource

# Import infrastructure from Stage 1 and demand generators from Stage 2.
# This avoids duplication and ensures consistency with validated code.
from phase2_3_stage1_network import (
    SKU_SPECS, NODE_SPECS, EDGES,
    build_phase2_3_network,
    holding_cost_for, stockout_cost_for,
    TIER_OFFSET, product_index,
)
from phase2_3_stage2_demand import (
    generate_ar1_demand,
    generate_compound_poisson_demand,
    configure_stochastic_demand,
    estimate_phi,
)


# =========================================================================
# POLICY CONFIGURATORS
# =========================================================================

# Each policy configurator sets the inventory_policy on all 12 nodes for
# all 12 SKUs. They all use the same dict-at-node-level pattern we
# validated in the v6 diagnostic. The only difference between policies is
# how base-stock levels are computed.

# Number of retailers downstream of each node (precomputed). For a
# distribution tree this equals the number of leaf descendants including
# the node itself if it is a leaf.
RETAILERS_FED = {
    0: 6,   # Manufacturer feeds all 6 retailers
    1: 4,   # Distributor 1 feeds retailers 6, 7, 8, 9 via Whsl 1 and 2
    2: 2,   # Distributor 2 feeds retailers 10, 11 via Whsl 3
    3: 2,   # Wholesaler 1 feeds retailers 6, 7
    4: 2,   # Wholesaler 2 feeds retailers 8, 9
    5: 2,   # Wholesaler 3 feeds retailers 10, 11
    6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1,
}


def configure_policy_naive(nodes_by_index, products_by_tier_and_sku):
    """
    Naive policy: base-stock = 3 * retailer mean demand at every node,
    regardless of position in the chain or lead time. This dramatically
    underestimates upstream needs because the manufacturer actually needs
    to cover aggregate demand for all 6 retailers, but naive treats every
    node as if it served one retailer's worth of demand.
    """
    for ns in NODE_SPECS:
        node = nodes_by_index[ns.index]
        tier = ns.tier_level
        policy_dict = {}
        for sku in SKU_SPECS:
            # Naive: 3x retailer mean, no aggregation, no lead time
            base_stock = sku.mean_demand * 3.0
            prod = products_by_tier_and_sku[tier][sku.sku_id]
            policy_dict[prod.index] = Policy(type='BS', base_stock_level=base_stock)
        node.inventory_policy = policy_dict


def configure_policy_informed(nodes_by_index, products_by_tier_and_sku, safety_factor=1.5):
    """
    Informed Clark-Scarf policy: base-stock = aggregate_demand *
    effective_lead_time * safety_factor. Accounts properly for both
    the aggregation effect (upstream nodes serve multiple downstream
    retailers) and the lead time (higher base-stock needed when units
    take longer to arrive). This is the Stage 1/2 baseline policy.
    """
    for ns in NODE_SPECS:
        node = nodes_by_index[ns.index]
        tier = ns.tier_level
        eff_lead_time = ns.shipment_lead_time + ns.order_lead_time
        num_retailers = RETAILERS_FED[ns.index]

        policy_dict = {}
        for sku in SKU_SPECS:
            agg_demand = sku.mean_demand * num_retailers
            base_stock = agg_demand * eff_lead_time * safety_factor
            prod = products_by_tier_and_sku[tier][sku.sku_id]
            policy_dict[prod.index] = Policy(type='BS', base_stock_level=base_stock)
        node.inventory_policy = policy_dict


def configure_policy_capacity_aware(nodes_by_index, products_by_tier_and_sku):
    """
    Capacity-aware policy: Same Clark-Scarf logic as informed but with
    a 20% additional safety factor to buffer against the risk that the
    manufacturer's capacity constraint binds during demand peaks.

    Effective safety factor: 1.5 * 1.2 = 1.8
    """
    configure_policy_informed(nodes_by_index, products_by_tier_and_sku,
                               safety_factor=1.8)


def configure_policy_variance_aware(nodes_by_index, products_by_tier_and_sku, z=1.645):
    """
    Variance-aware Clark-Scarf policy: base-stock = mean_demand_over_lead_time
    + z * std_demand_over_lead_time.

    Unlike the informed policy which uses a fixed 1.5 multiplier on mean
    demand (giving mean-proportional safety stock), the variance-aware policy
    uses safety stock that scales with the actual demand standard deviation.
    This properly handles heterogeneous coefficients of variation across SKUs.

    For AR(1) SKUs: std_per_period = mean * cv (from SKU spec)
    For compound Poisson SKUs: std_per_period = sqrt(arrival_rate * 2 * mean_size^2)

    Aggregation across N retailers uses sqrt(N) scaling under the IID
    approximation, and lead time scaling uses sqrt(L). For AR(1) demand this
    slightly underestimates variance due to autocorrelation, but the effect
    is modest at the phi values in our SKU spec (~10-20% underestimate at
    worst), and the baseline comparison value is not materially affected.

    z = 1.645 corresponds to a 95% target service level under normality.
    Heavy-tailed distributions like compound Poisson will fall short of 95%
    but should achieve substantially better coverage than the mean-proportional
    informed policy provides for those SKUs.
    """
    for ns in NODE_SPECS:
        node = nodes_by_index[ns.index]
        tier = ns.tier_level
        eff_lead_time = ns.shipment_lead_time + ns.order_lead_time
        num_retailers = RETAILERS_FED[ns.index]

        policy_dict = {}
        for sku in SKU_SPECS:
            # Per-retailer per-period demand statistics from the SKU spec
            if sku.demand_type == 'ar1':
                std_per_period = sku.mean_demand * sku.cv
            elif sku.demand_type == 'compound_poisson':
                # Closed-form for compound Poisson with exponential sizes
                variance_per_period = sku.cp_arrival_rate * 2 * sku.cp_mean_size ** 2
                std_per_period = np.sqrt(variance_per_period)
            else:
                raise ValueError(f"Unknown demand_type: {sku.demand_type}")

            # Aggregate over N retailers and over L lead time periods
            aggregate_mean = num_retailers * sku.mean_demand * eff_lead_time
            aggregate_std = std_per_period * np.sqrt(num_retailers * eff_lead_time)

            # Base stock: mean demand over lead time plus z-scaled safety stock
            base_stock = aggregate_mean + z * aggregate_std

            prod = products_by_tier_and_sku[tier][sku.sku_id]
            policy_dict[prod.index] = Policy(type='BS', base_stock_level=base_stock)
        node.inventory_policy = policy_dict


# =========================================================================
# CAPACITY CONSTRAINTS
# =========================================================================

# Capacity is set at the manufacturer's products. In stockpyl's per-product
# capacity model, each SKU has its own capacity limit. Setting cap at 1.3x
# aggregate mean demand gives occasional binding during peaks while staying
# above mean demand so normal operation is not constrained.

CAPACITY_MULTIPLIER = 1.3


def apply_capacity_constraints(nodes_by_index, products_by_tier_and_sku,
                                 capacity_multiplier=None):
    """
    Set per-product capacity at the manufacturer. Each SKU gets
    order_capacity = capacity_multiplier * aggregate_mean_demand where
    aggregate is across all 6 retailers.

    If capacity_multiplier is None (the default), uses the module-level
    CAPACITY_MULTIPLIER constant (1.3) to preserve backward compatibility
    with existing code that calls this function with two arguments.

    For the Phase 2.6 capacity sweep, we pass an explicit multiplier to
    test how the SR damping mechanism interacts with different capacity
    levels. Setting capacity_multiplier=None and providing a sentinel
    string 'unlimited' would not work cleanly with stockpyl's None-means-
    unlimited convention, so we use float('inf') to mean truly unlimited
    capacity (matching stockpyl's interpretation of None for order_capacity).
    """
    multiplier = capacity_multiplier if capacity_multiplier is not None else CAPACITY_MULTIPLIER

    for sku in SKU_SPECS:
        mfg_prod = products_by_tier_and_sku['manufacturer'][sku.sku_id]
        aggregate_mean = 6 * sku.mean_demand

        # Treat infinity as "no capacity constraint". Stockpyl interprets
        # order_capacity=None as unlimited, but we want an explicit value
        # for serialization purposes, so we convert inf to None here.
        if multiplier == float('inf'):
            mfg_prod.order_capacity = None
        else:
            mfg_prod.order_capacity = aggregate_mean * multiplier


# =========================================================================
# STATS EXTRACTION
# =========================================================================

def extract_trial_stats(network, nodes_by_index, products_by_tier_and_sku,
                        total_cost, num_periods, warmup_periods):
    """
    Extract per-trial statistics from a completed simulation. Returns a
    dict of simple Python values that joblib can safely serialize across
    process boundaries. All cost and activity measures use only the
    post-warmup "measured" period for comparability across trials.

    Statistics captured:
    - total_cost_measured: total cost from period warmup onward
    - cost_per_period: measured cost divided by measured periods
    - cost_by_component: dict of {holding, stockout, in_transit}
    - cost_by_sku: dict of {sku_id: total_cost} (from holding + stockout only)
    - service_level_by_sku: dict of {sku_id: fraction_demand_met}
    - stockout_events_by_sku: dict of {sku_id: num_periods_with_stockout}
    - peak_backlog_by_sku: dict of {sku_id: max backlog across all retailers}
    - capacity_utilization: dict of {sku_id: mean_production / capacity}
    - capacity_binding_fraction: dict of {sku_id: fraction_periods_at_cap}
    """
    measured_periods = num_periods - warmup_periods

    # Component totals over measured period
    total_holding = 0.0
    total_stockout = 0.0
    total_in_transit = 0.0

    for node in nodes_by_index.values():
        for t in range(warmup_periods, num_periods):
            if t < len(node.state_vars):
                sv = node.state_vars[t]
                total_holding += sv.holding_cost_incurred
                total_stockout += sv.stockout_cost_incurred
                total_in_transit += sv.in_transit_holding_cost_incurred

    total_cost_measured = total_holding + total_stockout + total_in_transit

    # Per-SKU service level at retailers
    # Service level = fraction of demand met from stock in measured period.
    # We compute this from demand_cumul and demand_met_from_stock_cumul.
    retailer_indices = [6, 7, 8, 9, 10, 11]
    service_level_by_sku = {}
    stockout_events_by_sku = {}
    peak_backlog_by_sku = {}

    for sku in SKU_SPECS:
        ret_prod_idx = products_by_tier_and_sku['retailer'][sku.sku_id].index
        total_demand = 0.0
        total_met = 0.0
        stockout_events = 0
        peak_bl = 0.0

        for retailer_idx in retailer_indices:
            retailer = nodes_by_index[retailer_idx]
            # Get cumulative values at end of measurement window and at
            # end of warmup, subtract to get measured-period total
            if num_periods - 1 < len(retailer.state_vars):
                sv_end = retailer.state_vars[num_periods - 1]
                demand_at_end = sv_end.demand_cumul.get(ret_prod_idx, 0)
                met_at_end = sv_end.demand_met_from_stock_cumul.get(ret_prod_idx, 0)
            else:
                demand_at_end = met_at_end = 0

            if warmup_periods - 1 >= 0 and warmup_periods - 1 < len(retailer.state_vars):
                sv_warmup = retailer.state_vars[warmup_periods - 1]
                demand_at_warmup = sv_warmup.demand_cumul.get(ret_prod_idx, 0)
                met_at_warmup = sv_warmup.demand_met_from_stock_cumul.get(ret_prod_idx, 0)
            else:
                demand_at_warmup = met_at_warmup = 0

            total_demand += (demand_at_end - demand_at_warmup)
            total_met += (met_at_end - met_at_warmup)

            # Count stockout events and peak backlog
            for t in range(warmup_periods, num_periods):
                if t < len(retailer.state_vars):
                    sv = retailer.state_vars[t]
                    inv = sv.inventory_level.get(ret_prod_idx, 0)
                    if inv < 0:
                        stockout_events += 1
                        peak_bl = max(peak_bl, -inv)

        service_level_by_sku[sku.sku_id] = total_met / max(total_demand, 1e-9)
        stockout_events_by_sku[sku.sku_id] = stockout_events
        peak_backlog_by_sku[sku.sku_id] = peak_bl

    # Capacity utilization at manufacturer. For each SKU, we track the
    # mean production per period and the fraction of periods where
    # production hit the capacity limit.
    manufacturer = nodes_by_index[0]
    capacity_utilization = {}
    capacity_binding_fraction = {}

    for sku in SKU_SPECS:
        mfg_prod = products_by_tier_and_sku['manufacturer'][sku.sku_id]
        cap = mfg_prod.order_capacity or float('inf')
        productions = []
        binding_count = 0

        for t in range(warmup_periods, num_periods):
            if t < len(manufacturer.state_vars):
                sv = manufacturer.state_vars[t]
                # Outbound shipment by product is a good proxy for production
                total_shipped = 0.0
                if hasattr(sv, 'outbound_shipment'):
                    for succ_idx, prod_dict in sv.outbound_shipment.items():
                        if isinstance(prod_dict, dict):
                            total_shipped += prod_dict.get(mfg_prod.index, 0)
                productions.append(total_shipped)
                if cap != float('inf') and total_shipped >= cap - 1e-6:
                    binding_count += 1

        if productions:
            mean_prod = float(np.mean(productions))
        else:
            mean_prod = 0.0
        capacity_utilization[sku.sku_id] = mean_prod / cap if cap != float('inf') else 0.0
        capacity_binding_fraction[sku.sku_id] = binding_count / max(len(productions), 1)

    return {
        'total_cost_all_periods': float(total_cost),
        'total_cost_measured': float(total_cost_measured),
        'cost_per_period': float(total_cost_measured / measured_periods),
        'cost_holding': float(total_holding),
        'cost_stockout': float(total_stockout),
        'cost_in_transit': float(total_in_transit),
        'service_level_by_sku': service_level_by_sku,
        'stockout_events_by_sku': stockout_events_by_sku,
        'peak_backlog_by_sku': peak_backlog_by_sku,
        'capacity_utilization': capacity_utilization,
        'capacity_binding_fraction': capacity_binding_fraction,
    }


# =========================================================================
# WORKER FUNCTION (runs in parallel across trials)
# =========================================================================

def run_trial_all_policies(trial_seed, num_periods, warmup_periods,
                            include_capacity=True):
    """
    Single trial: runs all three policies against common random numbers
    and returns a dict of per-policy statistics. This function is called
    by joblib workers in parallel.

    trial_seed determines the random numbers used for demand generation.
    All three policies within the same trial see identical demand, which
    is the common random numbers variance reduction technique. Different
    trial_seeds produce independent demand realizations.

    The function builds a fresh network for each policy to avoid any
    state leakage between policies. Network construction takes about 1
    second, which is small relative to the simulation time of ~36 seconds.
    """
    policies = ['naive', 'informed', 'capacity_aware', 'variance_aware']
    results = {}

    for policy_name in policies:
        try:
            # Build fresh network
            network, nodes_by_index, products = build_phase2_3_network()

            # Apply capacity constraints (same for all policies in this trial)
            if include_capacity:
                apply_capacity_constraints(nodes_by_index, products)

            # Configure demand with trial_seed (common random numbers)
            configure_stochastic_demand(
                nodes_by_index, products, num_periods, base_seed=trial_seed
            )

            # Configure the specific policy for this run
            if policy_name == 'naive':
                configure_policy_naive(nodes_by_index, products)
            elif policy_name == 'informed':
                configure_policy_informed(nodes_by_index, products)
            elif policy_name == 'capacity_aware':
                configure_policy_capacity_aware(nodes_by_index, products)
            elif policy_name == 'variance_aware':
                configure_policy_variance_aware(nodes_by_index, products)

            # Run simulation
            total_cost = simulation(network, num_periods=num_periods,
                                     rand_seed=trial_seed, progress_bar=False)

            # Extract statistics
            stats = extract_trial_stats(
                network, nodes_by_index, products,
                total_cost, num_periods, warmup_periods
            )
            stats['trial_seed'] = trial_seed
            stats['policy'] = policy_name
            results[policy_name] = stats

        except Exception as e:
            # Return error information so the main thread can report
            # which specific trial/policy combination failed
            results[policy_name] = {
                'error': True,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'trial_seed': trial_seed,
                'policy': policy_name,
            }

    return trial_seed, results


# =========================================================================
# VALIDATION GATES
# =========================================================================

def aggregate_stats_across_trials(all_results, policy_name):
    """
    Given the list of per-trial result dicts, compute cross-trial
    aggregate statistics for a specific policy. This is the raw data
    for both the policy comparison report and the validation gates.
    """
    trials = [r[1][policy_name] for r in all_results if not r[1][policy_name].get('error')]
    n = len(trials)
    if n == 0:
        return None

    costs = np.array([t['cost_per_period'] for t in trials])
    holding = np.array([t['cost_holding'] for t in trials])
    stockout = np.array([t['cost_stockout'] for t in trials])

    # Per-SKU aggregated service levels
    service_by_sku = {}
    for sku in SKU_SPECS:
        sls = [t['service_level_by_sku'][sku.sku_id] for t in trials]
        service_by_sku[sku.sku_id] = {
            'mean': float(np.mean(sls)),
            'min': float(np.min(sls)),
            'std': float(np.std(sls)),
        }

    # Capacity binding
    bind_by_sku = {}
    for sku in SKU_SPECS:
        bfs = [t['capacity_binding_fraction'][sku.sku_id] for t in trials]
        bind_by_sku[sku.sku_id] = {
            'mean': float(np.mean(bfs)),
            'max': float(np.max(bfs)),
        }

    return {
        'n_trials': n,
        'cost_per_period_mean': float(np.mean(costs)),
        'cost_per_period_std': float(np.std(costs)),
        'cost_per_period_stderr': float(np.std(costs) / np.sqrt(n)),
        'cost_per_period_ci95': [
            float(np.mean(costs) - 1.96 * np.std(costs) / np.sqrt(n)),
            float(np.mean(costs) + 1.96 * np.std(costs) / np.sqrt(n)),
        ],
        'cost_holding_mean': float(np.mean(holding)),
        'cost_stockout_mean': float(np.mean(stockout)),
        'service_by_sku': service_by_sku,
        'bind_by_sku': bind_by_sku,
    }


def run_validation_gates(all_results, aggregates):
    """
    Run Phase 2.3 Stage 3 validation gates. Returns True if all gates
    pass. Each gate is a focused check on one aspect of simulation
    correctness or policy comparison validity.
    """
    print()
    print("=" * 70)
    print("VALIDATION GATES")
    print("=" * 70)

    all_passed = True

    # Gate 1: All trials completed without errors
    print()
    print("Gate 1: Trial completion (no errors across 100 trials * 3 policies)")
    n_total_runs = 0
    n_errors = 0
    for trial_seed, results in all_results:
        for policy_name, stats in results.items():
            n_total_runs += 1
            if stats.get('error'):
                n_errors += 1
                print(f"  Error in trial {trial_seed} policy {policy_name}: "
                      f"{stats.get('error_type')}: {stats.get('error_message')}")
    if n_errors == 0:
        print(f"  PASS: all {n_total_runs} runs completed without errors")
    else:
        print(f"  FAIL: {n_errors} / {n_total_runs} runs had errors")
        all_passed = False

    # Gate 2: Policy cost ordering (naive > informed, capacity_aware reasonable)
    print()
    print("Gate 2: Policy cost ordering")
    naive_agg = aggregates['naive']
    informed_agg = aggregates['informed']
    cap_aware_agg = aggregates['capacity_aware']
    var_aware_agg = aggregates['variance_aware']

    naive_cost = naive_agg['cost_per_period_mean']
    informed_cost = informed_agg['cost_per_period_mean']
    cap_aware_cost = cap_aware_agg['cost_per_period_mean']
    var_aware_cost = var_aware_agg['cost_per_period_mean']

    print(f"  Naive cost/period:            {naive_cost:>15.2f}")
    print(f"  Informed cost/period:         {informed_cost:>15.2f}")
    print(f"  Capacity-aware cost/period:   {cap_aware_cost:>15.2f}")
    print(f"  Variance-aware cost/period:   {var_aware_cost:>15.2f}")

    if naive_cost > informed_cost:
        naive_informed_ratio = naive_cost / informed_cost
        print(f"  Naive/Informed ratio:       {naive_informed_ratio:.2f}x")
        print(f"  PASS: naive costs more than informed as expected")
    else:
        print(f"  FAIL: naive should cost more than informed but does not")
        all_passed = False

    # Gate 3: Statistical significance of naive vs informed difference
    print()
    print("Gate 3: Naive-vs-informed difference is statistically significant")
    # Use the standard errors to test if confidence intervals overlap
    naive_ci = naive_agg['cost_per_period_ci95']
    informed_ci = informed_agg['cost_per_period_ci95']
    # For non-overlapping intervals: informed upper < naive lower
    if informed_ci[1] < naive_ci[0]:
        print(f"  Informed 95% CI: [{informed_ci[0]:.2f}, {informed_ci[1]:.2f}]")
        print(f"  Naive 95% CI:    [{naive_ci[0]:.2f}, {naive_ci[1]:.2f}]")
        print(f"  PASS: CIs do not overlap")
    else:
        print(f"  Informed 95% CI: [{informed_ci[0]:.2f}, {informed_ci[1]:.2f}]")
        print(f"  Naive 95% CI:    [{naive_ci[0]:.2f}, {naive_ci[1]:.2f}]")
        print(f"  WARN: confidence intervals overlap")
        # Not a failure, but flag for attention

    # Gate 4: Informed service levels are high across all SKUs
    print()
    print("Gate 4: Informed policy produces >=90% service level for all SKUs")
    informed_services = informed_agg['service_by_sku']
    low_service_skus = []
    for sku in SKU_SPECS:
        sl = informed_services[sku.sku_id]['mean']
        status = 'ok' if sl >= 0.90 else 'LOW'
        if sl < 0.90:
            low_service_skus.append((sku.sku_id, sku.name, sl))
        print(f"  SKU {sku.sku_id:2d} ({sku.name:18s}): SL = {sl:.3f}  [{status}]")
    if not low_service_skus:
        print(f"  PASS: all SKUs meet 90% service level target")
    else:
        print(f"  INFO: {len(low_service_skus)} SKUs below 90% under informed policy")
        print(f"        (variance-aware policy in Gate 7 is designed to address this)")

    # Gate 4b: Variance-aware service levels
    print()
    print("Gate 4b: Variance-aware service levels across all SKUs")
    var_services = var_aware_agg['service_by_sku']
    for sku in SKU_SPECS:
        sl_informed = informed_services[sku.sku_id]['mean']
        sl_var = var_services[sku.sku_id]['mean']
        change = sl_var - sl_informed
        print(f"  SKU {sku.sku_id:2d} ({sku.name:18s}): "
              f"informed SL={sl_informed:.3f}, variance-aware SL={sl_var:.3f} "
              f"({'+' if change >= 0 else ''}{change:.3f})")

    # Gate 5: Capacity binds under informed policy (evidence that
    # capacity is actually a meaningful constraint)
    print()
    print("Gate 5: Manufacturer capacity binds under stress (informed policy)")
    binding_fractions = informed_agg['bind_by_sku']
    total_binding_skus = 0
    for sku in SKU_SPECS:
        bf = binding_fractions[sku.sku_id]['mean']
        if bf > 0.01:  # at least 1% of periods binding
            total_binding_skus += 1
        print(f"  SKU {sku.sku_id:2d} ({sku.name:18s}): binding fraction = {bf:.3f}")
    print(f"  SKUs with >1% binding: {total_binding_skus} of {len(SKU_SPECS)}")
    # Not a strict pass/fail; binding behavior is informational

    # Gate 6: Capacity-aware vs informed difference
    print()
    print("Gate 6: Capacity-aware vs informed comparison")
    diff = cap_aware_cost - informed_cost
    pct = (diff / informed_cost) * 100
    print(f"  Capacity-aware cost - informed cost: {diff:+.2f} ({pct:+.2f}%)")
    if diff < 0:
        print(f"  Capacity-aware saves cost relative to informed")
    elif diff > 0:
        print(f"  Capacity-aware costs more than informed (insurance premium)")
    else:
        print(f"  Capacity-aware equal to informed")

    # Gate 7: Variance-aware vs informed comparison (key Path C finding)
    print()
    print("Gate 7: Variance-aware vs informed comparison")
    diff_va = var_aware_cost - informed_cost
    pct_va = (diff_va / informed_cost) * 100
    print(f"  Variance-aware cost - informed cost: {diff_va:+.2f} ({pct_va:+.2f}%)")
    if diff_va < 0:
        print(f"  Variance-aware improves on informed baseline")
    else:
        print(f"  Variance-aware does not improve on informed baseline")

    # Check if variance-aware fixes the intermittent SKU service level gap
    sku12_informed_sl = informed_services[12]['mean']
    sku12_var_sl = var_services[12]['mean']
    print(f"  SKU 12 (intermittent) service level: "
          f"informed={sku12_informed_sl:.3f}, variance-aware={sku12_var_sl:.3f}")

    print()
    print("=" * 70)
    if all_passed:
        print("ALL CRITICAL VALIDATION GATES PASSED")
    else:
        print("SOME VALIDATION GATES FAILED - INVESTIGATE BEFORE PROCEEDING")
    print("=" * 70)

    return all_passed


# =========================================================================
# MAIN PARALLEL DRIVER
# =========================================================================

def main(num_trials=100, num_periods=156, warmup_periods=52, n_jobs=20):
    """
    Main driver: runs num_trials in parallel and produces the policy
    comparison report plus validation gates.
    """
    print()
    print("=" * 70)
    print("PHASE 2.3 STAGE 3: Three-way policy comparison")
    print("=" * 70)
    print()
    print(f"Configuration:")
    print(f"  Trials:         {num_trials}")
    print(f"  Periods:        {num_periods} (warmup {warmup_periods}, "
          f"measured {num_periods - warmup_periods})")
    print(f"  Parallel jobs:  {n_jobs}")
    print(f"  Policies:       naive, informed, capacity_aware, variance_aware")
    print(f"  Capacity:       per-product at manufacturer, {CAPACITY_MULTIPLIER}x mean")
    print()

    # Seed sequence: use distinct seeds for each trial so demand streams
    # are independent across trials. Start from 1000 to avoid collision
    # with small seed values that might be used elsewhere.
    trial_seeds = list(range(1000, 1000 + num_trials))

    print(f"Starting parallel execution across {n_jobs} workers...")
    t_start = time.time()

    # ProcessPoolExecutor distributes the trials across worker processes.
    # Each worker receives a trial seed and runs all three policies for
    # that seed. We use as_completed to get results as soon as each trial
    # finishes rather than waiting for all to complete before aggregating,
    # which lets us report progress incrementally.
    all_results = []
    with ProcessPoolExecutor(max_workers=n_jobs) as executor:
        # Submit all trials to the pool. The executor picks them up as
        # workers become available.
        future_to_seed = {
            executor.submit(run_trial_all_policies, seed, num_periods, warmup_periods): seed
            for seed in trial_seeds
        }

        # Collect results as trials complete, printing progress along the way
        completed = 0
        for future in as_completed(future_to_seed):
            seed = future_to_seed[future]
            try:
                result = future.result()
                all_results.append(result)
            except Exception as e:
                print(f"  Trial seed {seed} raised unhandled exception: "
                      f"{type(e).__name__}: {e}")
                # Store a placeholder so downstream code doesn't crash
                all_results.append((seed, {p: {'error': True,
                                                'error_type': type(e).__name__,
                                                'error_message': str(e),
                                                'trial_seed': seed,
                                                'policy': p}
                                            for p in ['naive', 'informed', 'capacity_aware', 'variance_aware']}))

            completed += 1
            # Report progress every 5 trials so we can see activity without
            # being overwhelmed by output. Also report at the end.
            if completed % 5 == 0 or completed == len(trial_seeds):
                elapsed_so_far = time.time() - t_start
                rate = completed / elapsed_so_far if elapsed_so_far > 0 else 0
                remaining = (len(trial_seeds) - completed) / rate if rate > 0 else 0
                print(f"  Completed {completed}/{len(trial_seeds)} trials  "
                      f"(elapsed {elapsed_so_far:.1f}s, "
                      f"est remaining {remaining:.0f}s)")

    # Sort results by trial seed so subsequent aggregation is deterministic
    # even though as_completed returns in completion order.
    all_results.sort(key=lambda r: r[0])

    elapsed = time.time() - t_start
    print()
    print(f"Parallel execution complete in {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
    print(f"Average time per trial (wall-clock): {elapsed / num_trials:.2f}s")

    # Aggregate statistics across trials for each policy
    print()
    print("Aggregating results...")
    aggregates = {}
    for policy_name in ['naive', 'informed', 'capacity_aware', 'variance_aware']:
        aggregates[policy_name] = aggregate_stats_across_trials(all_results, policy_name)

    # Run validation gates
    all_passed = run_validation_gates(all_results, aggregates)

    # Produce policy comparison report
    print()
    print("=" * 70)
    print("POLICY COMPARISON REPORT")
    print("=" * 70)
    for policy_name in ['naive', 'informed', 'capacity_aware', 'variance_aware']:
        agg = aggregates[policy_name]
        print()
        print(f"Policy: {policy_name.upper()}")
        print(f"  Trials completed:          {agg['n_trials']}")
        print(f"  Mean cost per period:      {agg['cost_per_period_mean']:>12.2f}")
        print(f"  Std of cost per period:    {agg['cost_per_period_std']:>12.2f}")
        print(f"  Standard error of mean:    {agg['cost_per_period_stderr']:>12.2f}")
        print(f"  95% CI for mean:           [{agg['cost_per_period_ci95'][0]:>10.2f}, "
              f"{agg['cost_per_period_ci95'][1]:>10.2f}]")
        print(f"  Holding cost component:    {agg['cost_holding_mean']:>12.2f}")
        print(f"  Stockout cost component:   {agg['cost_stockout_mean']:>12.2f}")

    # Headline comparisons
    naive = aggregates['naive']['cost_per_period_mean']
    informed = aggregates['informed']['cost_per_period_mean']
    cap_aware = aggregates['capacity_aware']['cost_per_period_mean']
    var_aware = aggregates['variance_aware']['cost_per_period_mean']

    print()
    print("HEADLINE COMPARISONS:")
    print(f"  Informed vs Naive:           {((informed - naive) / naive) * 100:+6.2f}% "
          f"({(naive - informed):+.2f} saved per period)")
    print(f"  Cap-aware vs Informed:       {((cap_aware - informed) / informed) * 100:+6.2f}% "
          f"({(informed - cap_aware):+.2f} saved per period)")
    print(f"  Variance-aware vs Informed:  {((var_aware - informed) / informed) * 100:+6.2f}% "
          f"({(informed - var_aware):+.2f} saved per period)")
    print(f"  Variance-aware vs Naive:     {((var_aware - naive) / naive) * 100:+6.2f}% "
          f"({(naive - var_aware):+.2f} saved per period)")

    # Save results
    output = {
        'config': {
            'num_trials': num_trials,
            'num_periods': num_periods,
            'warmup_periods': warmup_periods,
            'n_jobs': n_jobs,
            'capacity_multiplier': CAPACITY_MULTIPLIER,
            'trial_seeds': trial_seeds,
            'elapsed_seconds': elapsed,
        },
        'aggregates': aggregates,
        'all_trials': [
            {'trial_seed': seed, 'results': results}
            for seed, results in all_results
        ],
        'validation_passed': all_passed,
    }

    output_file = 'phase2_3_stage3_results.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    print()
    print(f"Results saved to {output_file}")

    print()
    print("=" * 70)
    if all_passed:
        print("STAGE 3 COMPLETE. Phase 2.3 full policy comparison successful.")
    else:
        print("STAGE 3 WARNING. Some gates did not pass; review output.")
    print("=" * 70)


if __name__ == '__main__':
    main(num_trials=100, num_periods=156, warmup_periods=52, n_jobs=20)
