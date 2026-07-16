"""
Phase 2.3 Stage 2: AR(1) and compound Poisson demand generators
================================================================

Stage 1 validated that the four-tier twelve-product network infrastructure
works correctly with deterministic unit demand. Stage 2 replaces that
simple demand pattern with realistic archetype-specific generators that
make the twelve SKUs genuinely distinct from each other.

Eleven SKUs use AR(1) persistent demand, following the pattern validated
in Phase 2.2 with per-SKU persistence parameters ranging from 0.30
(commodity staples) to 0.70 (premium items). Each SKU has its own
coefficient of variation based on its cost tier, with more expensive
items showing higher relative variability as buyers make more deliberate
discretionary decisions.

The twelfth SKU uses compound Poisson demand representing the intermittent
archetype of slow-moving specialty items. An arrival process with rate
0.4 per period generates demand events, and when an event occurs, the
size is drawn from an exponential distribution with mean 5 units. This
produces roughly 40 percent of periods with some demand and 60 percent
with zero demand, giving an overall average of 2 units per period while
maintaining the irregular purchase pattern characteristic of this archetype.

Stage 2 sanity checks verify:
1. Each AR(1) SKU produces demand with correct mean, std, and phi
2. The intermittent SKU produces demand with correct arrival rate and mean size
3. Cross-retailer demand streams are statistically independent
4. Persistence estimation recovers true phi values across multiple seeds
5. Aggregate manufacturer demand scales correctly with six retailers

If Stage 2's sanity checks pass, we have a fully working simulation with
realistic demand that is ready for the policy comparison in Stage 3.

Author: JAE with Claude as research assistant
Date: April 22, 2026
"""

import time
import traceback
import numpy as np
from collections import defaultdict

from stockpyl.sim import simulation
from stockpyl.policy import Policy
from stockpyl.demand_source import DemandSource

# Import the network infrastructure from Stage 1. This avoids duplicating
# seven hundred lines of network construction code and keeps the data
# model consistent between stages. If Stage 1's code changes, Stage 2
# picks up those changes automatically.
from phase2_3_stage1_network import (
    SKU_SPECS, NODE_SPECS, EDGES,
    build_phase2_3_network,
    configure_policies,
    holding_cost_for, stockout_cost_for,
    TIER_OFFSET, product_index,
)


# =========================================================================
# AR(1) DEMAND GENERATOR (from Phase 2.2, extended for per-SKU phi)
# =========================================================================

def generate_ar1_demand(mean, stationary_std, phi, num_periods, seed):
    """
    Generate an AR(1) demand sequence with specified mean, stationary
    standard deviation, and persistence parameter phi.

    The AR(1) process is: D[t] = mean + phi * (D[t-1] - mean) + epsilon[t]
    where epsilon[t] is drawn from Normal(0, sigma_eps). For the stationary
    standard deviation to equal stationary_std, sigma_eps must equal
    stationary_std * sqrt(1 - phi^2). We initialize D[0] from the stationary
    distribution directly, which eliminates the burn-in transient that
    would otherwise appear in the first several periods.

    This is the same generator we validated in Phase 2.2. Gate 16 of that
    phase confirmed the persistence estimator recovers the true phi with
    bias -0.0009 across twenty seeds.

    Negative values are clipped to zero because negative demand is
    physically meaningless. This occurs with probability far less than
    one percent for our parameters and the clipping has minimal effect
    on the sequence statistics.
    """
    rng = np.random.default_rng(seed)
    sigma_eps = stationary_std * np.sqrt(1 - phi ** 2)

    # Initialize from stationary distribution
    demand = np.zeros(num_periods)
    demand[0] = rng.normal(mean, stationary_std)
    for t in range(1, num_periods):
        epsilon = rng.normal(0, sigma_eps)
        demand[t] = mean + phi * (demand[t - 1] - mean) + epsilon

    # Clip negatives to zero (rare events that violate physical meaning)
    demand = np.maximum(demand, 0.0)
    return demand


# =========================================================================
# COMPOUND POISSON DEMAND GENERATOR (new for Phase 2.3)
# =========================================================================

def generate_compound_poisson_demand(arrival_rate, mean_size, num_periods, seed):
    """
    Generate compound Poisson demand for the intermittent SKU archetype.

    At each period, a Poisson-distributed number of arrivals occurs with
    rate equal to arrival_rate. For each arrival, an order size is drawn
    from an exponential distribution with mean equal to mean_size. The
    total demand in the period is the sum of all arrival sizes, which is
    zero when no arrivals occur.

    With arrival_rate = 0.4, approximately 67 percent of periods have
    zero arrivals (exp(-0.4) ~= 0.67), 27 percent have exactly one
    arrival, and 6 percent have two or more arrivals. This produces the
    characteristic zero-inflation pattern of intermittent demand.

    With exponentially distributed sizes averaging 5 units, individual
    demand events range from very small to occasionally very large,
    matching the realistic pattern where specialty-item orders can be
    either a single replacement part or a larger business restocking.

    Expected overall mean demand = arrival_rate * mean_size = 0.4 * 5 = 2.0
    Expected overall variance has a closed-form expression for compound
    Poisson: Var = arrival_rate * (mean_size^2 + size_variance). For
    exponential sizes with mean m, variance equals m^2, so
    Var = arrival_rate * 2 * m^2 = 0.4 * 50 = 20, giving std ~ 4.47.

    Demand values are rounded to integers because we are modeling unit
    sales of discrete items, which is the natural interpretation of a
    slow-moving specialty item where each unit is a distinct physical good.
    """
    rng = np.random.default_rng(seed)
    demand = np.zeros(num_periods)

    for t in range(num_periods):
        num_arrivals = rng.poisson(arrival_rate)
        if num_arrivals > 0:
            # Draw arrival sizes from exponential distribution
            sizes = rng.exponential(mean_size, size=num_arrivals)
            demand[t] = int(round(sizes.sum()))

    return demand


# =========================================================================
# DEMAND CONFIGURATION (replaces Stage 1's deterministic version)
# =========================================================================

def configure_stochastic_demand(nodes_by_index, products_by_tier_and_sku,
                                 num_periods, base_seed=42):
    """
    Configure realistic archetype-specific demand at each of the six
    retailers for each of the twelve SKUs. Eleven SKUs use AR(1) and
    the twelfth uses compound Poisson as specified in SKU_SPECS.

    Each (retailer, SKU) combination gets its own random seed to ensure
    demand streams are independent across retailers. Using a base seed
    plus per-retailer and per-SKU offsets makes the simulation fully
    reproducible while keeping the streams uncorrelated.

    The demand arrays are stored in a return dict so that validation
    can check their statistics without re-generating them. This is the
    same pattern we used in Phase 2.2.
    """
    retailer_indices = [6, 7, 8, 9, 10, 11]
    # demand_arrays[retailer_idx][sku_id] = numpy array of demand per period
    demand_arrays = {r: {} for r in retailer_indices}

    for retailer_idx in retailer_indices:
        retailer = nodes_by_index[retailer_idx]
        demand_sources = {}

        for sku in SKU_SPECS:
            # Unique seed for this (retailer, SKU) combination
            seed = base_seed + 1000 * retailer_idx + sku.sku_id

            if sku.demand_type == 'ar1':
                stationary_std = sku.mean_demand * sku.cv
                demand_arr = generate_ar1_demand(
                    mean=sku.mean_demand,
                    stationary_std=stationary_std,
                    phi=sku.phi,
                    num_periods=num_periods,
                    seed=seed,
                )
            elif sku.demand_type == 'compound_poisson':
                demand_arr = generate_compound_poisson_demand(
                    arrival_rate=sku.cp_arrival_rate,
                    mean_size=sku.cp_mean_size,
                    num_periods=num_periods,
                    seed=seed,
                )
            else:
                raise ValueError(f"Unknown demand_type: {sku.demand_type}")

            demand_arrays[retailer_idx][sku.sku_id] = demand_arr

            ret_prod = products_by_tier_and_sku['retailer'][sku.sku_id]
            demand_sources[ret_prod.index] = DemandSource(
                type='D',
                demand_list=demand_arr.tolist(),
            )

        # The v6 pattern: set demand_source as a dict at the node level
        retailer.demand_source = demand_sources

    return demand_arrays


# =========================================================================
# PERSISTENCE ESTIMATOR (from Phase 2.2)
# =========================================================================

def estimate_phi(demand_series):
    """
    Estimate the AR(1) persistence parameter phi from a demand series
    using lag-1 autocorrelation. This is the estimator the Spectral
    Radius algorithm relies on, and Phase 2.2 Gate 16 confirmed it
    recovers the true phi with very small bias.

    Returns lag-1 autocorrelation computed as the ratio of lag-1
    autocovariance to total variance.
    """
    d = np.asarray(demand_series, dtype=float)
    d_mean = d.mean()
    d_centered = d - d_mean
    autocov_1 = np.mean(d_centered[:-1] * d_centered[1:])
    variance = np.mean(d_centered ** 2)
    if variance == 0:
        return 0.0
    return autocov_1 / variance


# =========================================================================
# SANITY CHECKS
# =========================================================================

def sanity_check_demand_properties(demand_arrays, num_periods):
    """
    Verify the demand generators produce output matching their specifications.
    Returns True if all checks pass.
    """
    print("-" * 70)
    print("Sanity check: demand generator properties")
    print("-" * 70)

    all_ok = True

    # Gate 1: Per-SKU marginal statistics across retailers
    print()
    print("Gate 1: Per-SKU marginal statistics (averaged across 6 retailers)")
    for sku in SKU_SPECS:
        # Average statistics across retailers for more stable estimates
        means = []
        stds = []
        for retailer_idx in [6, 7, 8, 9, 10, 11]:
            d = demand_arrays[retailer_idx][sku.sku_id]
            means.append(d.mean())
            stds.append(d.std())
        avg_mean = np.mean(means)
        avg_std = np.mean(stds)

        if sku.demand_type == 'ar1':
            expected_mean = sku.mean_demand
            expected_std = sku.mean_demand * sku.cv
            mean_err = abs(avg_mean - expected_mean) / expected_mean
            std_err = abs(avg_std - expected_std) / expected_std
            tier = sku.cost_tier
            status = 'ok' if mean_err < 0.05 and std_err < 0.15 else 'PROBLEM'
            print(f"  SKU {sku.sku_id:2d} ({sku.name:18s}, {tier:13s}): "
                  f"mean={avg_mean:>7.2f} (exp {expected_mean:>6.1f}, err {mean_err:>5.1%}), "
                  f"std={avg_std:>6.2f} (exp {expected_std:>5.1f}, err {std_err:>5.1%})  [{status}]")
            if status == 'PROBLEM':
                all_ok = False
        elif sku.demand_type == 'compound_poisson':
            # Compound Poisson expected mean = rate * mean_size
            # Compound Poisson expected var = rate * 2 * mean_size^2 (for exp size)
            expected_mean = sku.cp_arrival_rate * sku.cp_mean_size
            expected_var = sku.cp_arrival_rate * 2 * sku.cp_mean_size ** 2
            expected_std = np.sqrt(expected_var)
            # For rounded integer demand, slight bias can occur; allow
            # larger tolerance for the intermittent SKU
            mean_err = abs(avg_mean - expected_mean) / max(expected_mean, 0.1)
            std_err = abs(avg_std - expected_std) / max(expected_std, 0.1)
            tier = sku.cost_tier
            status = 'ok' if mean_err < 0.25 and std_err < 0.30 else 'PROBLEM'
            print(f"  SKU {sku.sku_id:2d} ({sku.name:18s}, {tier:13s}): "
                  f"mean={avg_mean:>7.2f} (exp {expected_mean:>6.2f}, err {mean_err:>5.1%}), "
                  f"std={avg_std:>6.2f} (exp {expected_std:>5.2f}, err {std_err:>5.1%})  [{status}]")
            if status == 'PROBLEM':
                all_ok = False

    # Gate 2: Persistence recovery for AR(1) SKUs
    print()
    print("Gate 2: Persistence estimation across 6 retailers")
    for sku in SKU_SPECS:
        if sku.demand_type != 'ar1':
            continue
        phi_estimates = []
        for retailer_idx in [6, 7, 8, 9, 10, 11]:
            d = demand_arrays[retailer_idx][sku.sku_id]
            phi_estimates.append(estimate_phi(d))
        mean_phi = np.mean(phi_estimates)
        std_phi = np.std(phi_estimates)
        phi_err = abs(mean_phi - sku.phi)
        status = 'ok' if phi_err < 0.20 else 'PROBLEM'
        print(f"  SKU {sku.sku_id:2d} ({sku.name:18s}): "
              f"true phi={sku.phi:.2f}, "
              f"estimated phi={mean_phi:.3f} +/- {std_phi:.3f}, "
              f"err {phi_err:.3f}  [{status}]")
        if status == 'PROBLEM':
            all_ok = False

    # Gate 3: Intermittent SKU zero-inflation
    print()
    print("Gate 3: Intermittent SKU shows expected zero-inflation")
    sku12 = [s for s in SKU_SPECS if s.demand_type == 'compound_poisson'][0]
    zero_fractions = []
    for retailer_idx in [6, 7, 8, 9, 10, 11]:
        d = demand_arrays[retailer_idx][sku12.sku_id]
        zero_frac = np.mean(d == 0)
        zero_fractions.append(zero_frac)
    mean_zero_frac = np.mean(zero_fractions)
    # Expected fraction of zero-demand periods = exp(-arrival_rate)
    expected_zero_frac = np.exp(-sku12.cp_arrival_rate)
    zero_err = abs(mean_zero_frac - expected_zero_frac)
    status = 'PASS' if zero_err < 0.05 else 'FAIL'
    print(f"  Expected fraction of zero periods: {expected_zero_frac:.3f} (exp(-{sku12.cp_arrival_rate}))")
    print(f"  Observed fraction (avg across retailers): {mean_zero_frac:.3f}")
    print(f"  Error: {zero_err:.3f}  [{status}]")
    if status == 'FAIL':
        all_ok = False

    # Gate 4: Cross-retailer independence for a representative AR(1) SKU
    print()
    print("Gate 4: Cross-retailer independence for SKU 5 (moderate phi)")
    sku5_arrays = np.array([demand_arrays[r][5] for r in [6, 7, 8, 9, 10, 11]])
    corr_matrix = np.corrcoef(sku5_arrays)
    # Extract off-diagonal absolute values (15 pairs)
    n = corr_matrix.shape[0]
    off_diag = [abs(corr_matrix[i, j]) for i in range(n) for j in range(i + 1, n)]
    max_corr = max(off_diag)
    # Use the same Phase 2.2 threshold of 0.35 calibrated for AR(1) with
    # our sample size and pairwise test count
    threshold = 0.35
    status = 'PASS' if max_corr < threshold else 'FAIL'
    print(f"  Max absolute cross-retailer correlation: {max_corr:.3f} (threshold {threshold})")
    print(f"  Status: {status}")
    if status == 'FAIL':
        all_ok = False

    return all_ok


def sanity_check_simulation(network, nodes_by_index, products_by_tier_and_sku,
                             num_periods):
    """
    Run the simulation with stochastic demand and verify that activity
    flows through the network as expected. This is similar to Stage 1's
    gate structure but adapted for stochastic demand.
    """
    print()
    print("-" * 70)
    print(f"Sanity check: running simulation for {num_periods} periods")
    print("-" * 70)

    start = time.time()
    try:
        total_cost = simulation(network, num_periods=num_periods,
                                rand_seed=42, progress_bar=False)
    except Exception as e:
        print(f"  SIMULATION FAILED: {type(e).__name__}: {e}")
        tb = traceback.format_exc().split('\n')
        for line in tb[-15:-1]:
            print(f"    {line}")
        return False
    elapsed = time.time() - start
    print(f"  Simulation completed in {elapsed:.2f}s. Total cost: {total_cost:.2f}")

    # Gate 5: All twelve SKUs still show activity at manufacturer under
    # stochastic demand. This is the same check as Stage 1 Gate 3 but
    # with the stochastic demand arrays feeding the system.
    print()
    print("Gate 5: All 12 SKUs propagate to manufacturer under stochastic demand")
    manufacturer = nodes_by_index[0]
    all_ok = True
    for sku in SKU_SPECS:
        mfg_prod = products_by_tier_and_sku['manufacturer'][sku.sku_id]
        total_shipped = 0.0
        for sv in manufacturer.state_vars:
            if hasattr(sv, 'outbound_shipment'):
                for succ_idx, prod_dict in sv.outbound_shipment.items():
                    if isinstance(prod_dict, dict):
                        total_shipped += prod_dict.get(mfg_prod.index, 0)
        expected = 6 * sku.mean_demand * num_periods
        # Tolerance accounts for warmup and random variation
        reasonable = 0.4 * expected < total_shipped < 1.3 * expected
        status = 'ok' if reasonable else 'PROBLEM'
        print(f"  SKU {sku.sku_id:2d} ({sku.name:18s}): shipped {total_shipped:>9.1f}, "
              f"expected ~{expected:>9.1f}  [{status}]")
        if status == 'PROBLEM':
            all_ok = False
    if not all_ok:
        return False

    # Gate 6: Cost reconciliation under stochastic demand
    print()
    print("Gate 6: Cost reconciliation")
    reconciled_cost = 0.0
    for node in nodes_by_index.values():
        for sv in node.state_vars[:num_periods]:
            reconciled_cost += (sv.holding_cost_incurred
                                + sv.stockout_cost_incurred
                                + sv.in_transit_holding_cost_incurred)
    rel_error = abs(reconciled_cost - total_cost) / max(abs(total_cost), 1e-9)
    print(f"  Reported total cost: {total_cost:.2f}")
    print(f"  Reconciled cost:     {reconciled_cost:.2f}")
    print(f"  Relative error:      {rel_error:.6f}")
    passed = rel_error < 0.01
    print(f"  Status: {'PASS' if passed else 'FAIL'}")
    if not passed:
        return False

    return True


# =========================================================================
# MAIN
# =========================================================================

def main():
    print()
    print("=" * 70)
    print("PHASE 2.3 STAGE 2: AR(1) + compound Poisson demand generators")
    print("=" * 70)
    print()

    print("Building network (from Stage 1)...")
    network, nodes_by_index, products_by_tier_and_sku = build_phase2_3_network()
    print(f"  {len(nodes_by_index)} nodes, "
          f"{sum(len(v) for v in products_by_tier_and_sku.values())} products")

    # Use 156 periods to match Phase 2.2's horizon (52 warmup + 104 measured)
    num_periods = 156
    print(f"\nGenerating stochastic demand for {num_periods} periods across 6 retailers and 12 SKUs...")
    t0 = time.time()
    demand_arrays = configure_stochastic_demand(
        nodes_by_index, products_by_tier_and_sku, num_periods, base_seed=42
    )
    print(f"  Demand arrays generated in {time.time() - t0:.2f}s")
    total_demand_series = sum(len(demand_arrays[r]) for r in demand_arrays)
    print(f"  Total demand series: {total_demand_series} (6 retailers * 12 SKUs)")

    print("\nConfiguring policies...")
    configure_policies(nodes_by_index, products_by_tier_and_sku)

    # First validate the demand generators themselves before running simulation
    demand_ok = sanity_check_demand_properties(demand_arrays, num_periods)

    if not demand_ok:
        print()
        print("=" * 70)
        print("Demand generators have problems. Fix before running simulation.")
        print("=" * 70)
        return

    # Then run simulation and verify end-to-end propagation
    sim_ok = sanity_check_simulation(
        network, nodes_by_index, products_by_tier_and_sku, num_periods
    )

    print()
    print("=" * 70)
    if demand_ok and sim_ok:
        print("STAGE 2 COMPLETE.")
        print("Realistic demand generation verified at four-tier twelve-SKU scale.")
        print("Ready to proceed to Stage 3 (policy comparison and validation gates).")
    else:
        print("STAGE 2 FAILED. Debug the gate that did not pass.")
    print("=" * 70)


if __name__ == '__main__':
    main()
