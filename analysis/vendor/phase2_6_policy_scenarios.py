"""
Phase 2.6: Policy Scenario Registry and Factory
================================================

This module defines the "scenario" abstraction that lets a single Phase 2.6
experiment specify which policy each tier of the chain uses. A scenario is
just a dictionary that maps tier names (retailer, wholesaler, distributor,
manufacturer) to policy names (sterman, sr_paper9_ols, sr_disabled, etc.).
The runner consumes the scenario at simulation-setup time and attaches the
appropriate policy class to each node.

Why we need this
----------------

The original phase2_6_branching_toggle runner assumes every node uses the
same SR variant chosen at the command line. That assumption produced the
inadvertent all-rational test we were running all week, where every node
used SR-disabled (functionally base-stock) and there was nothing for the
SR formula to fix. Phase 2.6 should be testing the formula against both
rational and irrational co-players, but the per-tier-policy dimension was
not exposed in the runner so it never got tested.

The scenario registry restores the dimension that was lost. By introducing
a registry of named scenarios, each of which specifies a per-tier policy
mapping, we can run experiments like "SR at retailer with Sterman at all
upstream tiers" without modifying the runner each time. The named scenarios
match the position experiment from beergame_validation.py April 21, which
established that retailer-only SR deployment captures 48 to 58 percent of
the total possible savings.

Cross-architecture support
--------------------------

All three architectures used in Phase 2.6 (4-stage serial, N-stage
long_serial, 12-node branched) use the SAME canonical tier names
(manufacturer, distributor, wholesaler, retailer) on their node specs.
Long-serial collapses N-3 intermediate nodes into the wholesaler tier;
branched assigns multiple nodes to retailer (six retailers), wholesaler
(three), and distributor (two) tiers. Because each architecture's
node_specs already carries the tier_level field, the scenario applier
simply reads that field for each node and attaches the tier's specified
policy. A single scenario like sr_retailer_only thus works correctly
across all three architectures without architecture-specific scenario
definitions: in the 4-stage chain it places SR at one retailer node,
in the 12-node branched architecture it places SR at six retailer nodes,
and in the 8-stage long_serial chain it places SR at one retailer node
plus Sterman at five wholesaler nodes plus the distributor and manufacturer.

Author: JAE with Claude as research assistant
Date: April 27, 2026
"""

from typing import Callable, Dict, Optional, Any
from stockpyl.policy import Policy

from phase2_6_sterman_policy import (
    StermanConfig,
    StermanPolicy,
)
from phase2_6_spectral_radius import (
    SpectralRadiusConfig,
    SpectralRadiusPolicy,
    DAMPING_PAPER9, DAMPING_NUMERICAL, DAMPING_FIXED, DAMPING_DISABLED,
    ESTIMATOR_OLS, ESTIMATOR_ORACLE,
    make_sr_paper9_ols,
    make_sr_disabled,
    make_naive_damp,
)


# =========================================================================
# CANONICAL TIER NAMES
# =========================================================================
# Every architecture in Phase 2.6 (4-stage serial, N-stage long_serial,
# 12-node branched) annotates each node with one of these four canonical
# tier names. The scenario applier reads ns.tier_level for each node and
# attaches the policy that the scenario specifies for that tier.

TIER_NAMES = ('retailer', 'wholesaler', 'distributor', 'manufacturer')


# =========================================================================
# POLICY FACTORY REGISTRY
# =========================================================================
# Each entry produces a stockpyl Policy subclass instance configured for
# production use. The callable signature is:
#
#   factory(product_idx, node_idx, initial_target, oracle_phi=None, **kwargs)
#       -> Policy
#
# The initial_target parameter is a unified base-stock-style anchor that
# different policy types interpret differently. For SR variants it becomes
# initial_base_stock. For Sterman it becomes the initial target inventory
# level (target_IL), with the supply-line target derived from it via the
# lead-time scaling factor. This unification lets the runner compute one
# anchor per (node, SKU) and pass it to whatever policy the scenario
# selects, instead of computing different anchors for different policy
# types.
#
# The oracle_phi parameter is consumed only by sr_oracle_local; other
# factories ignore it.

def _make_sterman_for_node(
    product_idx: int,
    node_idx: int,
    initial_target: float,
    oracle_phi: Optional[Any] = None,
    eff_lead_time: int = 4,
    **kwargs,
) -> StermanPolicy:
    """Sterman policy configured for production experiments.

    Uses literature-standard alpha_S=0.5, alpha_SL=0.2, theta=0.2 and
    enables self-calibrating targets after fifteen observations. The
    self-calibration is important for production because fixed targets
    produce empty-start dormancy in stockpyl (see verify_sterman_policy.py
    and the MemPalace drawer titled "STERMAN POLICY PORT VERIFICATION").
    With self-calibration, targets scale to the observed demand level at
    each tier, which avoids the panic-order overshoot that fixed targets
    produce.

    The initial_target parameter sets the inventory-level anchor used
    before self-calibration kicks in. The supply-line anchor is derived
    by scaling initial_target by the effective lead time ratio so the
    target_OO captures the volume in transit at steady state.
    """
    # Sterman's target_OO should reflect expected demand × lead time at
    # steady state. The runner passes initial_target = expected_demand ×
    # num_retailers × eff_lead_time × 1.5, which is a base-stock-style
    # safety-stock-inflated anchor. We split this into target_IL (the
    # safety stock portion) and target_OO (the in-transit portion) using
    # a heuristic split that gives target_OO roughly equal to initial_
    # target × (eff_lead_time / (eff_lead_time + 1)). The exact split
    # matters less than it sounds because self-calibration replaces both
    # values within fifteen periods of warmup.
    target_IL = initial_target / 1.5  # remove the safety stock inflation
    target_OO = target_IL * eff_lead_time / max(eff_lead_time + 1, 1)

    config = StermanConfig(
        alpha_S=0.5,
        alpha_SL=0.2,
        d_hat_ewma=0.2,
    )
    return StermanPolicy(
        config=config,
        product_idx=product_idx,
        node_idx=node_idx,
        initial_target_IL=target_IL,
        initial_target_OO=target_OO,
    )


def _make_sr_paper9_ols_for_node(
    product_idx: int,
    node_idx: int,
    initial_target: float,
    oracle_phi: Optional[Any] = None,
    **kwargs,
) -> SpectralRadiusPolicy:
    """SR-Paper9-OLS deployable variant.

    Uses the Paper 7 Section 2.1 pi-squared-over-two formula with the
    OLS persistence estimator. This is the deployable form of the
    Spectral Radius policy that a real practitioner would use. The
    oracle_phi parameter is ignored because OLS estimates phi from
    observed demand rather than receiving it externally.
    """
    config = SpectralRadiusConfig(
        damping_mode=DAMPING_PAPER9,
        estimator_mode=ESTIMATOR_OLS,
    )
    return SpectralRadiusPolicy(
        config=config,
        product_idx=product_idx,
        node_idx=node_idx,
        initial_base_stock=initial_target,
    )


def _make_sr_oracle_local_for_node(
    product_idx: int,
    node_idx: int,
    initial_target: float,
    oracle_phi: Optional[Any] = None,
    **kwargs,
) -> SpectralRadiusPolicy:
    """SR-Oracle variant: Paper 7 formula with externally-provided phi.

    Receives the true demand persistence (or a per-period phi schedule)
    from the runner via oracle_phi. Used as a diagnostic to separate
    estimator error from formula error: if SR-Paper9-OLS underperforms
    SR-Oracle, the estimator is the bottleneck; if both perform similarly,
    the formula itself is the bottleneck.
    """
    config = SpectralRadiusConfig(
        damping_mode=DAMPING_PAPER9,
        estimator_mode=ESTIMATOR_ORACLE,
        oracle_phi=oracle_phi if oracle_phi is not None else 0.5,
    )
    return SpectralRadiusPolicy(
        config=config,
        product_idx=product_idx,
        node_idx=node_idx,
        initial_base_stock=initial_target,
    )


def _make_sr_disabled_for_node(
    product_idx: int,
    node_idx: int,
    initial_target: float,
    oracle_phi: Optional[Any] = None,
    **kwargs,
) -> SpectralRadiusPolicy:
    """SR-disabled ablation baseline (functionally self-calibrating base-stock).

    Damping pinned at alpha=1.0 means no damping is applied; the policy
    reduces to pure self-calibrating base-stock with newsvendor target
    sizing. This is the "rational base-stock" co-player benchmark that
    SR-Paper9-OLS is compared against in stable chains.
    """
    config = SpectralRadiusConfig(
        damping_mode=DAMPING_DISABLED,
        estimator_mode=ESTIMATOR_OLS,
    )
    return SpectralRadiusPolicy(
        config=config,
        product_idx=product_idx,
        node_idx=node_idx,
        initial_base_stock=initial_target,
    )


def _make_sr_naive_damp_for_node(
    product_idx: int,
    node_idx: int,
    initial_target: float,
    oracle_phi: Optional[Any] = None,
    **kwargs,
) -> SpectralRadiusPolicy:
    """Naive damping baseline with alpha pinned at 0.6.

    Tests whether the specific Paper 7 damping rule matters or whether
    "any moderate damping" produces similar results. If SR-Paper9-OLS
    significantly outperforms naive-damp-0.6, the theoretical formula
    contributes more than just generic damping.
    """
    config = SpectralRadiusConfig(
        damping_mode=DAMPING_FIXED,
        estimator_mode=ESTIMATOR_OLS,
        fixed_alpha=0.6,
    )
    return SpectralRadiusPolicy(
        config=config,
        product_idx=product_idx,
        node_idx=node_idx,
        initial_base_stock=initial_target,
    )


def _make_sr_numerical_for_node(
    product_idx: int,
    node_idx: int,
    initial_target: float,
    oracle_phi: Optional[Any] = None,
    **kwargs,
) -> SpectralRadiusPolicy:
    """SR-Numerical variant: direct numerical alpha computation.

    Uses the numerical damping mode from the SR policy module, which
    computes alpha by directly evaluating the spectral radius condition
    rather than using the closed-form pi-squared-over-two approximation.
    Provides a sanity check that the closed-form formula is not introducing
    approximation error relative to direct numerical evaluation.
    """
    config = SpectralRadiusConfig(
        damping_mode=DAMPING_NUMERICAL,
        estimator_mode=ESTIMATOR_OLS,
    )
    return SpectralRadiusPolicy(
        config=config,
        product_idx=product_idx,
        node_idx=node_idx,
        initial_base_stock=initial_target,
    )


# Registry mapping policy name (string used in scenarios) to factory.
# The keys are the names that appear in scenario specifications.
POLICY_FACTORY_REGISTRY: Dict[str, Callable[..., Policy]] = {
    'sterman':         _make_sterman_for_node,
    'sr_paper9_ols':   _make_sr_paper9_ols_for_node,
    'sr_oracle_local': _make_sr_oracle_local_for_node,
    'sr_disabled':     _make_sr_disabled_for_node,
    'sr_naive_damp':   _make_sr_naive_damp_for_node,
    'sr_numerical':    _make_sr_numerical_for_node,
}


# Short aliases the runner can pass through directly. These are the
# names that --variants accepts in the original variants-mode runner.
SR_VARIANT_NAMES = (
    'sr_paper9_ols',
    'sr_oracle_local',
    'sr_disabled',
    'sr_naive_damp',
    'sr_numerical',
)


# =========================================================================
# SCENARIO REGISTRY
# =========================================================================
# Each scenario is a dict mapping tier name to policy name. The named
# scenarios below correspond to the position experiment from
# beergame_validation.py April 21, plus the all-rational and all-irrational
# extremes that anchor the regime axis described in the master project plan.
#
# NAMING CONVENTION FOR SCENARIOS:
# - all_<policy>: every tier runs <policy>
# - sr_<positions>: SR at the specified positions, Sterman elsewhere
# The "sr" in scenario names refers to sr_paper9_ols specifically (the
# deployable variant). To test position experiments with other SR variants,
# add a new scenario like sr_oracle_retailer_only that specifies
# sr_oracle_local at the retailer.

# All four tiers run rational base-stock. This is the "rational ceiling"
# benchmark.
SCENARIO_ALL_BASESTOCK: Dict[str, str] = {
    'retailer':     'sr_disabled',
    'wholesaler':   'sr_disabled',
    'distributor':  'sr_disabled',
    'manufacturer': 'sr_disabled',
}

# All four tiers run the deployable SR formula.
SCENARIO_ALL_SR: Dict[str, str] = {
    'retailer':     'sr_paper9_ols',
    'wholesaler':   'sr_paper9_ols',
    'distributor':  'sr_paper9_ols',
    'manufacturer': 'sr_paper9_ols',
}

# All four tiers run Sterman behavioral ordering. This is the "irrational
# floor" benchmark representing untrained human ordering.
SCENARIO_ALL_STERMAN: Dict[str, str] = {
    'retailer':     'sterman',
    'wholesaler':   'sterman',
    'distributor':  'sterman',
    'manufacturer': 'sterman',
}

# Position experiment: SR deployed at retailer only, Sterman elsewhere.
SCENARIO_SR_RETAILER_ONLY: Dict[str, str] = {
    'retailer':     'sr_paper9_ols',
    'wholesaler':   'sterman',
    'distributor':  'sterman',
    'manufacturer': 'sterman',
}

# Position experiment: SR deployed at retailer and wholesaler.
SCENARIO_SR_RETAILER_WHOLESALER: Dict[str, str] = {
    'retailer':     'sr_paper9_ols',
    'wholesaler':   'sr_paper9_ols',
    'distributor':  'sterman',
    'manufacturer': 'sterman',
}

# Position experiment: SR deployed at three downstream tiers, Sterman
# at manufacturer.
SCENARIO_SR_TOP3: Dict[str, str] = {
    'retailer':     'sr_paper9_ols',
    'wholesaler':   'sr_paper9_ols',
    'distributor':  'sr_paper9_ols',
    'manufacturer': 'sterman',
}

# Position experiment control: SR deployed at manufacturer only, Sterman
# elsewhere. April 21 results showed this is harmful in literature setup;
# our smoke test showed it is helpful but much worse than retailer-only
# in the production stockpyl setup with self-calibrating targets.
SCENARIO_SR_MANUFACTURER_ONLY: Dict[str, str] = {
    'retailer':     'sterman',
    'wholesaler':   'sterman',
    'distributor':  'sterman',
    'manufacturer': 'sr_paper9_ols',
}


SCENARIO_REGISTRY: Dict[str, Dict[str, str]] = {
    'all_basestock':            SCENARIO_ALL_BASESTOCK,
    'all_sr':                   SCENARIO_ALL_SR,
    'all_sterman':              SCENARIO_ALL_STERMAN,
    'sr_retailer_only':         SCENARIO_SR_RETAILER_ONLY,
    'sr_retailer_wholesaler':   SCENARIO_SR_RETAILER_WHOLESALER,
    'sr_top3':                  SCENARIO_SR_TOP3,
    'sr_manufacturer_only':     SCENARIO_SR_MANUFACTURER_ONLY,
}


# =========================================================================
# SCENARIO APPLIER (single-product) - kept for smoke test compatibility
# =========================================================================
# This is the simple single-SKU applier the smoke test uses. The runner
# uses apply_scenario_multiproduct below, which handles the multi-SKU
# multi-architecture case.

NODE_INDEX_TO_TIER_4STAGE = {
    0: 'manufacturer',
    1: 'distributor',
    2: 'wholesaler',
    3: 'retailer',
}


def apply_scenario(
    scenario_name: str,
    nodes_by_index: Dict[int, object],
    product_by_node: Dict[int, object],
    node_index_to_tier: Optional[Dict[int, str]] = None,
) -> None:
    """Attach per-tier policies in a single-SKU 4-stage chain.

    Used by phase2_6_sterman_smoke_test.py. For multi-SKU multi-architecture
    chains used by the production runner, use apply_scenario_multiproduct
    instead.
    """
    if scenario_name not in SCENARIO_REGISTRY:
        raise KeyError(
            f"Scenario '{scenario_name}' not in registry. "
            f"Known: {sorted(SCENARIO_REGISTRY.keys())}"
        )

    scenario = SCENARIO_REGISTRY[scenario_name]
    if node_index_to_tier is None:
        node_index_to_tier = NODE_INDEX_TO_TIER_4STAGE

    for node_idx, node in nodes_by_index.items():
        tier_name = node_index_to_tier[node_idx]
        policy_name = scenario[tier_name]
        factory = POLICY_FACTORY_REGISTRY[policy_name]
        product = product_by_node[node_idx]

        # For single-SKU smoke test, use a fixed default initial target
        # of 12 (matching the verification harness configuration).
        policy = factory(
            product_idx=product.index,
            node_idx=node_idx,
            initial_target=12.0,
            oracle_phi=None,
            eff_lead_time=4,
        )
        node.inventory_policy = {product.index: policy}


# =========================================================================
# SCENARIO APPLIER (multi-product, multi-architecture)
# =========================================================================
# This is the production applier the branching_toggle runner uses. It
# handles arbitrary architectures (4-stage serial, N-stage long_serial,
# 12-node branched) and arbitrary numbers of SKUs per node, plus optional
# oracle_phi values for the SR-Oracle variant.
#
# The applier reads ns.tier_level from each node spec to identify which
# tier each node belongs to, looks up that tier's specified policy in
# the scenario, and constructs a Policy instance per (node, SKU) using
# the factory registered under that policy name. Initial base-stock-style
# anchors are computed using the same formula the existing
# configure_sr_policies uses, so SR variants receive equivalent anchors
# whether attached via the variants-mode or the scenarios-mode pathway.

def apply_scenario_multiproduct(
    scenario_name: str,
    arch_config: Dict[str, Any],
    nodes_by_index: Dict[int, object],
    products_by_tier_and_sku: Dict[str, Dict[int, object]],
    sku_specs: list,
    oracle_phi_per_node: Optional[Dict[int, Any]] = None,
) -> None:
    """Attach per-tier policies for multi-SKU multi-architecture networks.

    Iterates over arch_config['node_specs'], reading ns.tier_level for
    each node to determine which tier it belongs to. Looks up the
    scenario's policy for that tier and constructs an instance of the
    appropriate policy class for each SKU at that node, mirroring the
    existing configure_sr_policies pattern but with per-tier policy
    selection driven by the scenario.

    Parameters
    ----------
    scenario_name : str
        Key into SCENARIO_REGISTRY.
    arch_config : dict
        Architecture configuration dict produced by
        phase2_6_branching_toggle.make_architecture_config. Must contain
        'node_specs' and 'retailers_fed' keys.
    nodes_by_index : dict
        Maps node integer index to stockpyl SupplyChainNode.
    products_by_tier_and_sku : dict
        Maps tier name to dict mapping SKU id to SupplyChainProduct.
        As returned by network builders.
    sku_specs : list
        List of SKU spec dataclasses with mean_demand, sku_id fields.
    oracle_phi_per_node : dict, optional
        Per-node oracle phi value (scalar or callable schedule). Consumed
        only by the sr_oracle_local factory; ignored by other factories.

    Raises
    ------
    KeyError
        If scenario_name is not registered, if a tier referenced by the
        scenario is not in the architecture, or if a policy name in the
        scenario is not in POLICY_FACTORY_REGISTRY.
    """
    if scenario_name not in SCENARIO_REGISTRY:
        raise KeyError(
            f"Scenario '{scenario_name}' not in registry. "
            f"Known: {sorted(SCENARIO_REGISTRY.keys())}"
        )
    scenario = SCENARIO_REGISTRY[scenario_name]

    node_specs = arch_config['node_specs']
    retailers_fed = arch_config['retailers_fed']

    for ns in node_specs:
        node = nodes_by_index[ns.index]
        tier = ns.tier_level
        eff_lead_time = ns.shipment_lead_time + ns.order_lead_time
        num_retailers = retailers_fed[ns.index]

        # Look up which policy this tier should run for this scenario.
        if tier not in scenario:
            raise KeyError(
                f"Scenario '{scenario_name}' has no entry for tier "
                f"'{tier}' (node {ns.index}). Scenario tiers: "
                f"{sorted(scenario.keys())}"
            )
        policy_name = scenario[tier]

        if policy_name not in POLICY_FACTORY_REGISTRY:
            raise KeyError(
                f"Policy '{policy_name}' (referenced by tier '{tier}' "
                f"in scenario '{scenario_name}') is not in factory "
                f"registry. Known: {sorted(POLICY_FACTORY_REGISTRY.keys())}"
            )
        factory = POLICY_FACTORY_REGISTRY[policy_name]

        # Determine oracle_phi for this node (only matters for sr_oracle_local).
        this_oracle_phi = None
        if policy_name == 'sr_oracle_local' and oracle_phi_per_node is not None:
            this_oracle_phi = oracle_phi_per_node.get(ns.index, 0.5)

        # Build a policy instance per SKU at this node. This mirrors the
        # pattern in configure_sr_policies: each SKU gets its own policy
        # with anchor sized to that SKU's expected demand × the node's
        # effective lead time × the safety stock multiplier.
        policy_dict = {}
        for sku in sku_specs:
            prod = products_by_tier_and_sku[tier][sku.sku_id]
            initial_target = sku.mean_demand * num_retailers * eff_lead_time * 1.5

            policy = factory(
                product_idx=prod.index,
                node_idx=ns.index,
                initial_target=initial_target,
                oracle_phi=this_oracle_phi,
                eff_lead_time=eff_lead_time,
            )
            # Some policies use the .node attribute to access node state.
            policy.node = node
            policy_dict[prod.index] = policy

        node.inventory_policy = policy_dict


# =========================================================================
# UTILITY FUNCTIONS
# =========================================================================

def list_scenarios() -> list:
    """Return the list of registered scenario names in stable order."""
    return list(SCENARIO_REGISTRY.keys())


def list_policies() -> list:
    """Return the list of registered policy names in stable order."""
    return list(POLICY_FACTORY_REGISTRY.keys())


def get_scenario_spec(scenario_name: str) -> Dict[str, str]:
    """Return a copy of the scenario's tier-to-policy mapping."""
    if scenario_name not in SCENARIO_REGISTRY:
        raise KeyError(
            f"Scenario '{scenario_name}' not in registry. "
            f"Known: {sorted(SCENARIO_REGISTRY.keys())}"
        )
    return dict(SCENARIO_REGISTRY[scenario_name])


def variant_to_scenario_label(variant_name: str) -> str:
    """Map a variant name (used in variants-mode) to a scenario label.

    Used by the runner to produce a 'scenario' field in result records
    when running in variants mode, so downstream tooling can treat
    variant-mode and scenario-mode results uniformly. The label has
    the form 'all_<variant>' to indicate that the variant is applied
    uniformly across all tiers, distinguishing it from the named
    scenario 'all_sr' (which always uses sr_paper9_ols specifically).
    """
    return f"all_{variant_name}"


# =========================================================================
# SELF-TEST
# =========================================================================

def _self_test():
    """Verify that the registry is internally consistent."""
    print("=" * 60)
    print("Phase 2.6 Policy Scenarios self-test")
    print("=" * 60)

    print(f"\nRegistered policies: {sorted(POLICY_FACTORY_REGISTRY.keys())}")
    print(f"Registered scenarios: {list_scenarios()}")

    # Check 1: every scenario covers all tiers.
    print("\nChecking scenario completeness...")
    for scen_name, scen_spec in SCENARIO_REGISTRY.items():
        missing = set(TIER_NAMES) - set(scen_spec.keys())
        extra = set(scen_spec.keys()) - set(TIER_NAMES)
        assert not missing, f"Scenario '{scen_name}' missing tiers: {missing}"
        assert not extra, f"Scenario '{scen_name}' has unrecognized tiers: {extra}"
        print(f"  {scen_name}: OK ({sorted(scen_spec.keys())})")

    # Check 2: every policy name referenced by any scenario is registered.
    print("\nChecking policy reference consistency...")
    referenced_policies = set()
    for scen_spec in SCENARIO_REGISTRY.values():
        referenced_policies.update(scen_spec.values())
    unregistered = referenced_policies - set(POLICY_FACTORY_REGISTRY.keys())
    assert not unregistered, (
        f"Scenarios reference unregistered policies: {unregistered}"
    )
    print(f"  All {len(referenced_policies)} referenced policies are registered.")

    # Check 3: each factory can be called with the unified signature.
    print("\nChecking factory callability with unified signature...")
    for policy_name, factory in POLICY_FACTORY_REGISTRY.items():
        try:
            instance = factory(
                product_idx=999,
                node_idx=0,
                initial_target=24.0,
                oracle_phi=0.7,
                eff_lead_time=3,
            )
            print(f"  {policy_name:20s} -> {type(instance).__name__}  OK")
        except Exception as exc:
            print(f"  {policy_name:20s} -> FAILED: {exc}")
            raise

    # Check 4: variant_to_scenario_label produces expected output.
    print("\nChecking variant-to-scenario label mapping...")
    for v in SR_VARIANT_NAMES:
        label = variant_to_scenario_label(v)
        print(f"  {v:20s} -> {label}")

    print("\nAll self-tests completed.")
    print("=" * 60)


if __name__ == '__main__':
    _self_test()
