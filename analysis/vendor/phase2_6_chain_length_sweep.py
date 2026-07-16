"""
Phase 2.6: Chain-Length Sweep Runner
======================================

PURPOSE:
This runner extends the Phase 2.6 capacity sweep to a third dimension:
chain length. The Direction 4 capacity sweep established the
manufacturer-harm phi curve at 4-stage serial-summed-at-retailer
architecture across capacities 1.3x, 1.8x, 2.4x, 3.0x. This runner
asks how that curve scales with chain length, sweeping across
4-stage, 6-stage, and 8-stage serial chains at 1.3x, 1.8x, 2.4x.

The hypothesis being tested is that chain-length amplifies bullwhip
and increases the operational value of the SR formula. If the
formula's distinctive value (alpha at high phi) grows monotonically
with chain length, that supports the spectral radius interpretation
because longer chains compound amplification per echelon.

EXPERIMENTAL DESIGN:
Three chain lengths (4, 6, 8) times three capacities (1.3x, 1.8x, 2.4x)
times five SR variants times four demand environments times fifty seeds.
Total cells: 3*3 = 9 (chain_length, capacity) cells. Total simulations
per cell: 5 variants * 4 envs * 50 seeds = 1000. Grand total: 9000
simulations. Each cell is a separate worker invocation coordinated by
the launcher.

ARCHITECTURE CHOICE:
Uses stockpyl's serial_system constructor for clean N-stage chain
construction. This is the same constructor used in the original
Phase 2.6 overnight sweep that produced the lt3_len8_nocap result
showing -0.965% benefit. Single-SKU semantics (one product per node,
single demand stream at the retailer) keeps the architecture simple
and the chain-length comparison clean: only chain length and capacity
vary across cells, every other dimension is held constant.

SR VARIANT DESIGN:
The five variants match the capacity sweep design exactly:
  - sr_paper9_ols: SR with OLS estimator (formula-on, real-world
    data feed)
  - sr_oracle_local: SR with oracle phi from the demand schedule
    (formula-on, ground-truth data feed)
  - sr_disabled: All base-stock, no SR damping (formula-off baseline)
  - sr_naive_damp: SR with fixed alpha=0.6 (formula-off comparison
    with brute-force damping)
  - sr_numerical: SR with numerical damping mode (alternative
    estimator implementation)

Note: Unlike the Direction 4 capacity sweep on the tree architecture,
serial chains have a uniform tier structure so we do NOT need to vary
WHERE the SR is placed (the "scenarios" dimension from Direction 4
becomes redundant). Every variant places SR at every node in the chain.

DISTRIBUTED EXECUTION:
Same pattern as phase2_6_capacity_sweep.py. Accepts --n-stages,
--capacity-multiplier, --capacity-label, --seed-start, --seed-end,
--output. The launcher coordinates running all 9 cells across the
active fleet.

Author: JAE with Claude as research assistant
Date: April 30, 2026
"""

import argparse
import json
import time
import traceback
import numpy as np

from stockpyl.supply_chain_network import serial_system
from stockpyl.sim import simulation
from stockpyl.demand_source import DemandSource

from phase2_6_spectral_radius import (
    SpectralRadiusPolicy,
    SpectralRadiusConfig,
    DAMPING_PAPER9, DAMPING_NUMERICAL, DAMPING_FIXED, DAMPING_DISABLED,
    ESTIMATOR_OLS, ESTIMATOR_ORACLE,
)
from phase2_6_timevarying_demand import (
    constant_schedule,
    piecewise_linear_schedule,
    generate_timevarying_ar1_demand,
    generate_iid_normal_demand,
)


# =========================================================================
# CONFIGURATION
# =========================================================================

# Simulation horizon. Same as Direction 4 (260 periods, 52 warmup)
# for direct comparability.
DEFAULT_NUM_PERIODS = 260
DEFAULT_WARMUP_PERIODS = 52

# Chain construction parameters. The serial chain uses a single SKU
# with these characteristics. Mean and std match the overnight sweep
# pattern (mean=10, std=2). Holding/stockout costs are also matched
# to overnight sweep so chain-cost magnitudes are comparable to the
# Phase 2.6 reference results.
DEMAND_MEAN = 10.0
DEMAND_STD = 2.0
HOLDING_COST = 1.0
STOCKOUT_COST = 10.0

# Lead time per stage. Direction 4 used effective lead time 3 (1 ship
# + 2 order) at each tier. We use shipment_lead_time=1 with the
# default stockpyl order lead time, giving effective LT close to that.
SHIPMENT_LEAD_TIME = 2

# Initial inventory level scales with mean demand. 1.5x mean per stage
# is roughly the conservative newsvendor level used in Direction 4.
INITIAL_BS_MULTIPLIER = 1.5


def make_phase2_6_drift_schedule(num_periods):
    """The drift schedule. Same shape as Direction 4."""
    seg = num_periods / 5.0
    breakpoints = [
        (0,                  0.30),
        (int(1 * seg),       0.30),
        (int(2 * seg),       0.95),
        (int(3 * seg),       0.95),
        (int(4 * seg),       0.40),
        (num_periods - 1,    0.40),
    ]
    return piecewise_linear_schedule(
        breakpoints=breakpoints,
        name=f"drift_0.3_0.95_0.4_{num_periods}p",
        description="Drift schedule (engages mechanism).",
    )


def get_demand_environments(num_periods):
    """Same four environments as Direction 4 capacity sweep."""
    return {
        'iid_control': {
            'name': 'iid_control',
            'generator_kind': 'iid',
            'schedule': None,
            'description': 'IID normal demand (no persistence)',
        },
        'ar1_moderate': {
            'name': 'ar1_moderate',
            'generator_kind': 'ar1',
            'schedule': constant_schedule(0.6),
            'description': 'Stationary AR(1) phi=0.6 (below engagement)',
        },
        'ar1_high': {
            'name': 'ar1_high',
            'generator_kind': 'ar1',
            'schedule': constant_schedule(0.85),
            'description': 'Stationary AR(1) phi=0.85 (at engagement boundary)',
        },
        'drift_canonical': {
            'name': 'drift_canonical',
            'generator_kind': 'ar1',
            'schedule': make_phase2_6_drift_schedule(num_periods),
            'description': 'Time-varying phi 0.3->0.95->0.4 (crosses threshold)',
        },
    }


# =========================================================================
# CHAIN CONSTRUCTION
# =========================================================================

def build_chain(n_stages, capacity_multiplier, demand_array):
    """Construct a serial chain of n_stages nodes.

    The chain is built via stockpyl's serial_system constructor.
    Capacity is applied uniformly to all nodes via the order_capacity
    kwarg. When capacity_multiplier is float('inf') we omit the kwarg
    entirely so stockpyl uses its default unlimited capacity.

    The chain is indexed from 0 (manufacturer) to n_stages-1 (retailer).
    Demand is fed at the retailer (last node) via the demand_list
    parameter. Each node has the same per-stage holding cost and the
    retailer alone has stockout cost (per stockpyl convention for
    serial chains).
    """
    initial_bs = DEMAND_MEAN * SHIPMENT_LEAD_TIME * INITIAL_BS_MULTIPLIER

    kwargs = {
        'num_nodes': n_stages,
        'local_holding_cost': HOLDING_COST,
        'stockout_cost': STOCKOUT_COST,
        'shipment_lead_time': SHIPMENT_LEAD_TIME,
        'demand_type': 'D',
        'demand_list': list(demand_array),
        'initial_inventory_level': initial_bs,
    }

    # Apply capacity if it is finite. The capacity multiplier is
    # applied to the mean demand to get an absolute capacity value.
    # When capacity_multiplier is float('inf') we leave order_capacity
    # unset so stockpyl uses unlimited capacity.
    if capacity_multiplier != float('inf'):
        kwargs['order_capacity'] = DEMAND_MEAN * capacity_multiplier

    return serial_system(**kwargs)


# =========================================================================
# SR POLICY ATTACHMENT
# =========================================================================

def make_sr_config(variant_name, oracle_phi=None):
    """Build a SpectralRadiusConfig for the named variant.

    Mirrors the variant-to-config mapping used in
    phase2_6_capacity_sweep.py so the comparison with Direction 4 is
    apples-to-apples on the variant dimension.
    """
    if variant_name == 'sr_paper9_ols':
        return SpectralRadiusConfig(
            damping_mode=DAMPING_PAPER9,
            estimator_mode=ESTIMATOR_OLS,
        )
    elif variant_name == 'sr_oracle_local':
        return SpectralRadiusConfig(
            damping_mode=DAMPING_PAPER9,
            estimator_mode=ESTIMATOR_ORACLE,
            oracle_phi=oracle_phi if oracle_phi is not None else 0.5,
        )
    elif variant_name == 'sr_disabled':
        return SpectralRadiusConfig(
            damping_mode=DAMPING_DISABLED,
            estimator_mode=ESTIMATOR_OLS,
        )
    elif variant_name == 'sr_naive_damp':
        return SpectralRadiusConfig(
            damping_mode=DAMPING_FIXED,
            estimator_mode=ESTIMATOR_OLS,
            fixed_alpha=0.6,
        )
    elif variant_name == 'sr_numerical':
        return SpectralRadiusConfig(
            damping_mode=DAMPING_NUMERICAL,
            estimator_mode=ESTIMATOR_OLS,
        )
    else:
        raise ValueError(f"Unknown variant: {variant_name}")


def attach_sr_policies(network, variant_name, oracle_phi=None):
    """Attach an SR policy to every node in the chain.

    Each node gets its own fresh policy instance so diagnostic state
    does not collide across nodes. The product_idx defaults to zero
    for serial chains because there is exactly one product per node;
    we set it more precisely to the node's first product index after
    construction so the policy reads the right product's data during
    simulation.
    """
    initial_bs = DEMAND_MEAN * SHIPMENT_LEAD_TIME * INITIAL_BS_MULTIPLIER

    for node in network.nodes:
        config = make_sr_config(variant_name, oracle_phi=oracle_phi)
        policy = SpectralRadiusPolicy(
            config=config,
            product_idx=0,  # Will be overridden below if products exist
            node_idx=node.index,
            initial_base_stock=initial_bs,
        )
        policy.node = node
        if node.products:
            policy.product_idx = node.products[0].index
        node.inventory_policy = policy


# =========================================================================
# CALIBRATION
# =========================================================================

def calibrate_oracle_phi(env_name, env_config):
    """Return oracle phi for each node based on the demand schedule.

    Same approach as phase2_6_capacity_sweep.py post-fix: oracle gets
    the TRUE phi from the demand schedule rather than OLS-estimated
    plateau values. For stationary environments we return a scalar;
    for drift_canonical we return the schedule callable. The
    SpectralRadiusPolicy handles both transparently.
    """
    if env_config['generator_kind'] == 'iid':
        return 0.0

    schedule = env_config.get('schedule')
    if schedule is None:
        return 0.0

    if env_name == 'ar1_moderate':
        return 0.6
    elif env_name == 'ar1_high':
        return 0.85
    elif env_name == 'drift_canonical':
        return schedule
    else:
        return schedule


# =========================================================================
# SINGLE-TRIAL EXECUTION
# =========================================================================

def configure_demand(network, env_config, trial_seed, num_periods):
    """Generate a demand stream and feed it to the retailer.

    The retailer is the last node in the chain (highest index). For
    serial_system, demand is configured via the retailer's
    demand_source attribute as a single DemandSource of type 'D'
    with an explicit demand_list.
    """
    # Find the retailer (in stockpyl serial_system, the retailer is
    # always at the highest tier index)
    retailer = max(network.nodes, key=lambda n: n.index)

    gen_periods = num_periods + 20

    if env_config['generator_kind'] == 'iid':
        demand_arr = generate_iid_normal_demand(
            mean=DEMAND_MEAN,
            std=DEMAND_STD,
            num_periods=gen_periods,
            seed=trial_seed,
        )
    elif env_config['generator_kind'] == 'ar1':
        demand_arr = generate_timevarying_ar1_demand(
            mean=DEMAND_MEAN,
            stationary_std=DEMAND_STD,
            schedule=env_config['schedule'],
            num_periods=gen_periods,
            seed=trial_seed,
        )
    else:
        raise ValueError(f"Unknown generator: {env_config['generator_kind']}")

    retailer.demand_source = DemandSource(
        type='D',
        demand_list=demand_arr.tolist(),
    )


def run_single_trial(env_config, variant_name, trial_seed,
                       num_periods, warmup_periods,
                       n_stages, capacity_multiplier,
                       oracle_phi=None):
    """Run one (variant, env, seed, n_stages, capacity) combination."""
    try:
        # Generate demand first so we can pass it to build_chain
        gen_periods = num_periods + 20
        if env_config['generator_kind'] == 'iid':
            demand_arr = generate_iid_normal_demand(
                mean=DEMAND_MEAN, std=DEMAND_STD,
                num_periods=gen_periods, seed=trial_seed,
            )
        elif env_config['generator_kind'] == 'ar1':
            demand_arr = generate_timevarying_ar1_demand(
                mean=DEMAND_MEAN, stationary_std=DEMAND_STD,
                schedule=env_config['schedule'],
                num_periods=gen_periods, seed=trial_seed,
            )
        else:
            raise ValueError(f"Unknown generator: {env_config['generator_kind']}")

        net = build_chain(n_stages, capacity_multiplier, demand_arr)
        attach_sr_policies(net, variant_name, oracle_phi=oracle_phi)

        total_cost = simulation(net, num_periods=num_periods,
                                  rand_seed=42, progress_bar=False)

        # Post-warmup cost
        post_warmup_cost = 0.0
        for node in net.nodes:
            for t in range(warmup_periods, num_periods):
                if t < len(node.state_vars):
                    sv = node.state_vars[t]
                    post_warmup_cost += sv.holding_cost_incurred
                    post_warmup_cost += sv.stockout_cost_incurred
                    if hasattr(sv, 'in_transit_holding_cost_incurred'):
                        post_warmup_cost += sv.in_transit_holding_cost_incurred

        measured_periods = num_periods - warmup_periods
        cost_per_period = post_warmup_cost / measured_periods

        return {
            'trial_seed': trial_seed,
            'variant': variant_name,
            'env': env_config['name'],
            'n_stages': n_stages,
            'capacity_multiplier': (capacity_multiplier
                                       if capacity_multiplier != float('inf')
                                       else 'inf'),
            'total_cost_full': float(total_cost),
            'total_cost_post_warmup': float(post_warmup_cost),
            'cost_per_period': float(cost_per_period),
            'success': True,
        }

    except Exception as e:
        return {
            'trial_seed': trial_seed,
            'variant': variant_name,
            'env': env_config['name'],
            'n_stages': n_stages,
            'capacity_multiplier': (capacity_multiplier
                                       if capacity_multiplier != float('inf')
                                       else 'inf'),
            'total_cost_full': float('nan'),
            'total_cost_post_warmup': float('nan'),
            'cost_per_period': float('nan'),
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc(),
        }


def run_one_seed_all_variants(env_config, trial_seed,
                                  num_periods, warmup_periods,
                                  n_stages, capacity_multiplier,
                                  oracle_phi):
    """Run all five variants on one seed at one (n_stages, capacity) cell."""
    variants = [
        'sr_paper9_ols',
        'sr_oracle_local',
        'sr_disabled',
        'sr_naive_damp',
        'sr_numerical',
    ]
    return [
        run_single_trial(
            env_config, v, trial_seed,
            num_periods, warmup_periods,
            n_stages, capacity_multiplier,
            oracle_phi=oracle_phi,
        )
        for v in variants
    ]


# =========================================================================
# MAIN EXPERIMENT DRIVER
# =========================================================================

def run_experiment(seed_start, seed_end, output_file,
                       num_periods, warmup_periods,
                       n_stages, capacity_multiplier, capacity_label):
    """Run one (n_stages, capacity) cell across all envs, variants, seeds."""
    seeds = list(range(seed_start, seed_end + 1))
    n_seeds = len(seeds)

    print("=" * 70)
    print("PHASE 2.6 CHAIN-LENGTH SWEEP")
    print("=" * 70)
    print(f"Chain length:         {n_stages} stages")
    print(f"Capacity:             {capacity_label} (multiplier {capacity_multiplier})")
    print(f"Seed range:           [{seed_start}, {seed_end}] inclusive ({n_seeds} seeds)")
    print(f"Periods:              {num_periods} ({warmup_periods} warmup)")
    print(f"Output:               {output_file}")
    print()

    overall_start = time.time()
    environments = get_demand_environments(num_periods)
    all_trials = []
    oracle_phi_cache = {}

    # Early-abort guard: same pattern as capacity_sweep
    EARLY_ABORT_THRESHOLD_TRIALS = 10
    early_abort_seen_errors = []

    for env_name, env_config in environments.items():
        print()
        print("-" * 70)
        print(f"Environment: {env_name}")
        print(f"  {env_config['description']}")
        print("-" * 70)

        if env_name not in oracle_phi_cache:
            oracle_phi_cache[env_name] = calibrate_oracle_phi(
                env_name, env_config
            )
            phi_repr = oracle_phi_cache[env_name]
            if callable(phi_repr):
                phi_str = "<schedule>"
            else:
                phi_str = f"{phi_repr:.3f}"
            print(f"  Oracle phi: {phi_str}")

        oracle_phi = oracle_phi_cache[env_name]

        env_start = time.time()
        for i, trial_seed in enumerate(seeds):
            trial_results = run_one_seed_all_variants(
                env_config, trial_seed,
                num_periods, warmup_periods,
                n_stages, capacity_multiplier,
                oracle_phi,
            )
            all_trials.extend(trial_results)

            # Early-abort check
            if len(all_trials) <= EARLY_ABORT_THRESHOLD_TRIALS:
                for tr in trial_results:
                    if not tr.get('success'):
                        early_abort_seen_errors.append(tr.get('error', 'unknown'))
            if len(all_trials) == EARLY_ABORT_THRESHOLD_TRIALS:
                if (len(early_abort_seen_errors) == EARLY_ABORT_THRESHOLD_TRIALS
                    and len(set(early_abort_seen_errors)) <= 2):
                    print()
                    print("!" * 70)
                    print("EARLY ABORT: All first "
                          f"{EARLY_ABORT_THRESHOLD_TRIALS} simulations failed.")
                    print(f"Most common error: {early_abort_seen_errors[0]}")
                    print("!" * 70)
                    raise RuntimeError(
                        f"Systematic failure in first "
                        f"{EARLY_ABORT_THRESHOLD_TRIALS} trials: "
                        f"{early_abort_seen_errors[0]}"
                    )

            if (i + 1) % 5 == 0 or (i + 1) == n_seeds:
                elapsed = time.time() - env_start
                rate = (i + 1) / elapsed if elapsed > 0 else 0
                eta = (n_seeds - (i + 1)) / rate if rate > 0 else 0
                print(f"    Seed {trial_seed} done ({i+1}/{n_seeds}, "
                      f"elapsed {elapsed:.0f}s, ETA {eta:.0f}s)")

        env_elapsed = time.time() - env_start
        print(f"  Environment {env_name} complete in {env_elapsed/60:.1f} min")

        # Save partial results after each environment
        elapsed_so_far = time.time() - overall_start
        partial_output = {
            'config': {
                'seed_start': seed_start,
                'seed_end': seed_end,
                'num_periods': num_periods,
                'warmup_periods': warmup_periods,
                'n_stages': n_stages,
                'capacity_multiplier': (capacity_multiplier
                                           if capacity_multiplier != float('inf')
                                           else 'inf'),
                'capacity_label': capacity_label,
                'environments_completed': list(oracle_phi_cache.keys()),
                'elapsed_seconds': elapsed_so_far,
            },
            'trials': all_trials,
        }
        with open(output_file, 'w') as f:
            json.dump(partial_output, f, indent=2)

    overall_elapsed = time.time() - overall_start

    final_output = {
        'config': {
            'seed_start': seed_start,
            'seed_end': seed_end,
            'num_periods': num_periods,
            'warmup_periods': warmup_periods,
            'n_stages': n_stages,
            'capacity_multiplier': (capacity_multiplier
                                       if capacity_multiplier != float('inf')
                                       else 'inf'),
            'capacity_label': capacity_label,
            'environments_completed': list(oracle_phi_cache.keys()),
            'elapsed_seconds': overall_elapsed,
        },
        'trials': all_trials,
    }
    with open(output_file, 'w') as f:
        json.dump(final_output, f, indent=2)

    print()
    print("=" * 70)
    print(f"CELL COMPLETE in {overall_elapsed/60:.1f} min")
    print(f"  Chain length:   {n_stages}")
    print(f"  Capacity:       {capacity_label}")
    print(f"Trial entries:    {len(all_trials)}")
    n_success = sum(1 for r in all_trials if r.get('success'))
    n_fail = len(all_trials) - n_success
    print(f"Successes: {n_success}, Failures: {n_fail}")
    print("=" * 70)

    return all_trials


# =========================================================================
# COMMAND-LINE INTERFACE
# =========================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Phase 2.6 chain-length sweep runner. Tests one '
                       '(n_stages, capacity) cell at a time; the launcher '
                       'coordinates all 9 cells across the fleet.'
    )
    parser.add_argument('--n-stages', type=int, required=True,
                        help='Number of stages in the serial chain (e.g. 4, 6, 8).')
    parser.add_argument('--seed-start', type=int, required=True,
                        help='First seed (inclusive).')
    parser.add_argument('--seed-end', type=int, required=True,
                        help='Last seed (INCLUSIVE).')
    parser.add_argument('--output', type=str, required=True,
                        help='Output JSON file path.')
    parser.add_argument('--num-periods', type=int, default=DEFAULT_NUM_PERIODS,
                        help=f'Simulation horizon (default {DEFAULT_NUM_PERIODS}).')
    parser.add_argument('--warmup-periods', type=int, default=DEFAULT_WARMUP_PERIODS,
                        help=f'Warmup periods (default {DEFAULT_WARMUP_PERIODS}).')
    parser.add_argument('--capacity-multiplier', type=str, required=True,
                        help='Capacity multiplier as a number, OR "inf" for unlimited.')
    parser.add_argument('--capacity-label', type=str, required=True,
                        help='Human-readable label (e.g. "default_1.3x", "loose_1.8x").')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    if args.capacity_multiplier.lower() == 'inf':
        cap_mult = float('inf')
    else:
        cap_mult = float(args.capacity_multiplier)

    if args.n_stages < 2:
        raise SystemExit(f"--n-stages must be >= 2, got {args.n_stages}")

    run_experiment(
        seed_start=args.seed_start,
        seed_end=args.seed_end,
        output_file=args.output,
        num_periods=args.num_periods,
        warmup_periods=args.warmup_periods,
        n_stages=args.n_stages,
        capacity_multiplier=cap_mult,
        capacity_label=args.capacity_label,
    )
