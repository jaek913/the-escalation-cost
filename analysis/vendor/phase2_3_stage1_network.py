"""
Phase 2.3 Stage 1: Multi-tier, multi-product network infrastructure
=====================================================================

This stage builds the full Phase 2.3 network topology with twelve SKUs
across four tiers, using the v6 multi-product pattern we validated in
the diagnostic sequence. Stage 1 uses deterministic unit demand to
verify the network infrastructure works at the four-tier twelve-product
scale before we add statistical demand generation in Stage 2.

Network topology (from Phase 2.1):
    Manufacturer (node 0)
        -> Distributor 1 (node 1), Distributor 2 (node 2)
            -> Wholesaler 1,2,3 (nodes 3,4,5)
                -> Retailer 1..6 (nodes 6..11)

Twelve SKUs across four cost tiers:
    Commodity Staples ($1):      SKUs 1, 2, 3
    Regular Consumer Goods ($5): SKUs 4, 5, 6
    Discretionary ($25):         SKUs 7, 8, 9
    Premium ($100):              SKUs 10, 11, 12 (SKU 12 is intermittent)

Product index scheme:
    Manufacturer tier: 1000 + sku   (1001..1012)
    Distributor tier:  2000 + sku   (2001..2012)
    Wholesaler tier:   3000 + sku   (3001..3012)
    Retailer tier:     4000 + sku   (4001..4012)

Total: 48 distinct product instances, 132 BOM declarations across 11 edges.

If Stage 1's sanity check passes, we proceed to Stage 2 which adds
AR(1) and compound Poisson demand generators.

Author: JAE with Claude as research assistant
Date: April 22, 2026
"""

import time
import traceback
from dataclasses import dataclass, field
import numpy as np

from stockpyl.supply_chain_network import SupplyChainNetwork
from stockpyl.supply_chain_node import SupplyChainNode
from stockpyl.supply_chain_product import SupplyChainProduct
from stockpyl.sim import simulation
from stockpyl.policy import Policy
from stockpyl.demand_source import DemandSource


# =========================================================================
# SKU SPECIFICATION
# =========================================================================

# Each SKU is characterized by its cost tier, mean demand, coefficient of
# variation, and persistence parameter. The cost tier determines unit cost
# and all cost-scaled quantities (holding and stockout). Mean demand,
# CV, and phi drive the demand generation process (phi for AR(1), separate
# parameters for the intermittent compound Poisson case).
#
# Using a dataclass gives us a clean single-source-of-truth for all twelve
# SKUs that we can iterate over during network construction and demand
# generation without hunting through scattered constants.

@dataclass
class SKUSpec:
    sku_id: int              # 1..12
    name: str
    cost_tier: str           # 'commodity', 'regular', 'discretionary', 'premium'
    unit_cost: float         # dollars per unit
    mean_demand: float       # units per period per retailer
    cv: float                # stationary coefficient of variation (std/mean)
    phi: float               # AR(1) persistence parameter (None for intermittent)
    demand_type: str = 'ar1'  # 'ar1' or 'compound_poisson'
    # Compound Poisson parameters, used only when demand_type == 'compound_poisson'
    cp_arrival_rate: float = 0.0   # events per period
    cp_mean_size: float = 0.0       # exponentially distributed size mean


# The twelve-SKU specification follows the design we agreed on. Commodity
# staples have low persistence because daily basics are relatively memoryless.
# Persistence increases with cost tier because discretionary and premium
# purchases track ongoing household or economic trends. The premium tier
# includes one AR(1) item (high-end but steady) and one compound Poisson
# item (the intermittent archetype representing slow-moving specialty goods).

SKU_SPECS = [
    # Commodity Staples tier: $1 unit cost, mean demand 200
    SKUSpec(sku_id=1,  name='staple_A',        cost_tier='commodity',    unit_cost=1.0,   mean_demand=200, cv=0.15,  phi=0.30),
    SKUSpec(sku_id=2,  name='staple_B',        cost_tier='commodity',    unit_cost=1.0,   mean_demand=200, cv=0.175, phi=0.35),
    SKUSpec(sku_id=3,  name='staple_C',        cost_tier='commodity',    unit_cost=1.0,   mean_demand=200, cv=0.20,  phi=0.40),
    # Regular Consumer Goods tier: $5 unit cost, mean demand 100
    SKUSpec(sku_id=4,  name='regular_A',       cost_tier='regular',      unit_cost=5.0,   mean_demand=100, cv=0.20,  phi=0.40),
    SKUSpec(sku_id=5,  name='regular_B',       cost_tier='regular',      unit_cost=5.0,   mean_demand=100, cv=0.225, phi=0.45),
    SKUSpec(sku_id=6,  name='regular_C',       cost_tier='regular',      unit_cost=5.0,   mean_demand=100, cv=0.25,  phi=0.50),
    # Discretionary tier: $25 unit cost, mean demand 40
    SKUSpec(sku_id=7,  name='discretionary_A', cost_tier='discretionary', unit_cost=25.0,  mean_demand=40,  cv=0.30,  phi=0.55),
    SKUSpec(sku_id=8,  name='discretionary_B', cost_tier='discretionary', unit_cost=25.0,  mean_demand=40,  cv=0.325, phi=0.60),
    SKUSpec(sku_id=9,  name='discretionary_C', cost_tier='discretionary', unit_cost=25.0,  mean_demand=40,  cv=0.35,  phi=0.65),
    # Premium tier: $100 unit cost
    SKUSpec(sku_id=10, name='premium_A',       cost_tier='premium',      unit_cost=100.0, mean_demand=10,  cv=0.40,  phi=0.65),
    SKUSpec(sku_id=11, name='premium_B',       cost_tier='premium',      unit_cost=100.0, mean_demand=10,  cv=0.45,  phi=0.70),
    # SKU 12: the intermittent archetype. Uses compound Poisson demand
    # with arrival rate 0.4 (about 40% of periods see any demand) and
    # exponentially distributed order sizes averaging 5 units per event.
    # Overall average demand is ~2 units per period.
    SKUSpec(sku_id=12, name='intermittent',    cost_tier='premium',      unit_cost=100.0, mean_demand=2.0, cv=1.5,   phi=None,
            demand_type='compound_poisson', cp_arrival_rate=0.4, cp_mean_size=5.0),
]


# =========================================================================
# COST STRUCTURE
# =========================================================================

# Holding costs scale with both the SKU's unit cost and the tier level
# (echelon). Upstream nodes have lower holding costs because they hold
# inventory at cost price, while retailers hold it at retail price. The
# multiplier structure matches the 1:2:4:6 ratio we used in Phase 2.1.5,
# scaled to per-unit-cost-dollar at the base.

# Base holding cost per unit per period, expressed as fraction of unit cost.
# Manufacturer has the lowest cost per unit, retailer has the highest.
HOLDING_COST_FRACTION_BY_TIER_LEVEL = {
    'manufacturer': 0.005,   # 0.5% of unit cost per period
    'distributor':  0.010,
    'wholesaler':   0.020,
    'retailer':     0.030,
}

# Stockout cost at retailer is approximately 80% of unit cost, representing
# lost margin on the sale that does not occur. Upstream nodes have no
# stockout cost because their "demand" is internal orders from downstream.
STOCKOUT_COST_FRACTION = 0.80


def holding_cost_for(sku_spec: SKUSpec, tier_level: str) -> float:
    """Holding cost per unit per period for a given SKU at a given tier."""
    return sku_spec.unit_cost * HOLDING_COST_FRACTION_BY_TIER_LEVEL[tier_level]


def stockout_cost_for(sku_spec: SKUSpec) -> float:
    """Stockout cost per unit per period. Only applies at retailer tier."""
    return sku_spec.unit_cost * STOCKOUT_COST_FRACTION


# =========================================================================
# NETWORK TOPOLOGY
# =========================================================================

# Distribution tree from Phase 2.1, with asymmetric lead times from
# Phase 2.1-Realism. Each node gets a tuple of (index, name, tier_level,
# shipment_lead_time, order_lead_time) so we can build nodes and edges
# programmatically.

@dataclass
class NodeSpec:
    index: int
    name: str
    tier_level: str   # 'manufacturer' | 'distributor' | 'wholesaler' | 'retailer'
    shipment_lead_time: int
    order_lead_time: int


# Asymmetric lead times from Phase 2.1-Realism: manufacturer has long
# production lead time (3 weeks), distributor and wholesaler have moderate
# transit times, retailers vary individually by geographic distance.
NODE_SPECS = [
    NodeSpec(0,  'Manufacturer',    'manufacturer', shipment_lead_time=3, order_lead_time=0),
    NodeSpec(1,  'Distributor_1',   'distributor',  shipment_lead_time=2, order_lead_time=1),
    NodeSpec(2,  'Distributor_2',   'distributor',  shipment_lead_time=2, order_lead_time=1),
    NodeSpec(3,  'Wholesaler_1',    'wholesaler',   shipment_lead_time=1, order_lead_time=1),
    NodeSpec(4,  'Wholesaler_2',    'wholesaler',   shipment_lead_time=1, order_lead_time=1),
    NodeSpec(5,  'Wholesaler_3',    'wholesaler',   shipment_lead_time=1, order_lead_time=1),
    NodeSpec(6,  'Retailer_1',      'retailer',     shipment_lead_time=1, order_lead_time=1),
    NodeSpec(7,  'Retailer_2',      'retailer',     shipment_lead_time=1, order_lead_time=2),
    NodeSpec(8,  'Retailer_3',      'retailer',     shipment_lead_time=1, order_lead_time=1),
    NodeSpec(9,  'Retailer_4',      'retailer',     shipment_lead_time=2, order_lead_time=2),
    NodeSpec(10, 'Retailer_5',      'retailer',     shipment_lead_time=1, order_lead_time=2),
    NodeSpec(11, 'Retailer_6',      'retailer',     shipment_lead_time=1, order_lead_time=1),
]

# Edges in the distribution tree. Each tuple is (from_index, to_index).
# Total edges: 2 + 3 + 6 = 11.
EDGES = [
    # Manufacturer to distributors
    (0, 1), (0, 2),
    # Distributors to wholesalers
    (1, 3), (1, 4),
    (2, 5),
    # Wholesalers to retailers
    (3, 6), (3, 7),
    (4, 8), (4, 9),
    (5, 10), (5, 11),
]

# Tier level for each node index, derived from NODE_SPECS for fast lookup
TIER_LEVEL_BY_NODE_INDEX = {ns.index: ns.tier_level for ns in NODE_SPECS}

# Product index convention: product index = tier_offset + sku_id where
# tier_offset is 1000 for manufacturer, 2000 for distributor, etc.
TIER_OFFSET = {
    'manufacturer': 1000,
    'distributor':  2000,
    'wholesaler':   3000,
    'retailer':     4000,
}


def product_index(tier_level: str, sku_id: int) -> int:
    """Generate the product index for a given (tier_level, sku_id) pair."""
    return TIER_OFFSET[tier_level] + sku_id


# =========================================================================
# NETWORK BUILDER
# =========================================================================

def build_phase2_3_network():
    """
    Build the complete Phase 2.3 network: 12 nodes across 4 tiers with
    12 SKUs per tier (48 products total), 11 edges, and 132 BOM declarations.

    Returns a tuple of (network, nodes_by_index, products_by_tier_and_sku)
    where nodes_by_index maps node indices to SupplyChainNode instances
    and products_by_tier_and_sku is a nested dict:
        products_by_tier_and_sku[tier_level][sku_id] = SupplyChainProduct
    """
    network = SupplyChainNetwork()

    # Step 1: Create all 12 nodes and add them to the network. We create
    # nodes first so products can later be attached to them. The node's
    # shipment_lead_time is set at the node level; it will be inherited
    # by all products at the node unless a product-specific value is set.
    nodes_by_index = {}
    for ns in NODE_SPECS:
        node = SupplyChainNode(
            index=ns.index,
            name=ns.name,
            shipment_lead_time=ns.shipment_lead_time,
            order_lead_time=ns.order_lead_time,
        )
        network.add_node(node)
        nodes_by_index[ns.index] = node

    # Step 2: Create all 48 products. Each SKU has four distinct product
    # instances, one at each tier. The product's holding cost is set at
    # the product level because it varies by tier and SKU. Stockout cost
    # is only set on retailer-tier products since upstream tiers do not
    # face external demand.
    #
    # supply_type='U' is set on manufacturer-tier products. This tells
    # stockpyl that the manufacturer is fed by an unlimited external
    # supplier (representing raw materials or imports that arrive without
    # constraint at this level of modeling).
    products_by_tier_and_sku = {
        'manufacturer': {}, 'distributor': {}, 'wholesaler': {}, 'retailer': {},
    }
    for sku in SKU_SPECS:
        for tier in ['manufacturer', 'distributor', 'wholesaler', 'retailer']:
            p_index = product_index(tier, sku.sku_id)
            p_name = f"{sku.name}_at_{tier}"
            holding = holding_cost_for(sku, tier)
            stockout = stockout_cost_for(sku) if tier == 'retailer' else 0.0

            kwargs = dict(
                index=p_index,
                name=p_name,
                local_holding_cost=holding,
                stockout_cost=stockout,
            )
            # Manufacturer-tier products need supply_type='U' so stockpyl
            # treats them as having an implicit external supplier (the
            # discovery that resolved our v5 diagnostic).
            if tier == 'manufacturer':
                kwargs['supply_type'] = 'U'

            product = SupplyChainProduct(**kwargs)
            products_by_tier_and_sku[tier][sku.sku_id] = product

    # Step 3: Attach each product to its corresponding node. Products
    # belong to specific nodes; the SKU's manufacturer-tier instance goes
    # on the manufacturer node, each distributor node gets its own copies
    # of the distributor-tier instances (they share the same product index
    # conceptually but each node gets its own attachment), and so on down
    # the chain.
    for sku in SKU_SPECS:
        # Manufacturer (one node)
        nodes_by_index[0].add_product(products_by_tier_and_sku['manufacturer'][sku.sku_id])
        # Distributors (two nodes, both handle all distributor-tier products)
        for node_idx in (1, 2):
            nodes_by_index[node_idx].add_product(products_by_tier_and_sku['distributor'][sku.sku_id])
        # Wholesalers (three nodes)
        for node_idx in (3, 4, 5):
            nodes_by_index[node_idx].add_product(products_by_tier_and_sku['wholesaler'][sku.sku_id])
        # Retailers (six nodes)
        for node_idx in (6, 7, 8, 9, 10, 11):
            nodes_by_index[node_idx].add_product(products_by_tier_and_sku['retailer'][sku.sku_id])

    # Step 4: Set supply_type on the manufacturer node as well, for
    # safety. The get_attribute lookup logic falls back from product to
    # node, so having it at both levels ensures stockpyl correctly
    # identifies the manufacturer as having an external supplier.
    nodes_by_index[0].supply_type = 'U'

    # Step 5: Declare Bill of Materials relationships across each tier
    # boundary. For each SKU, the retailer's product consumes one unit
    # of the wholesaler's product, the wholesaler's product consumes one
    # unit of the distributor's product, and the distributor's product
    # consumes one unit of the manufacturer's product. The transformation
    # is pass-through (num_needed=1.0) because no real production happens.
    # This is 12 SKUs times 3 tier boundaries = 36 BOM declarations. The
    # earlier claim of 132 was counting edges times SKUs, but BOMs are
    # declared once per (product, raw_material) pair, not once per edge.
    for sku in SKU_SPECS:
        mfg_prod   = products_by_tier_and_sku['manufacturer'][sku.sku_id]
        dist_prod  = products_by_tier_and_sku['distributor'][sku.sku_id]
        whsl_prod  = products_by_tier_and_sku['wholesaler'][sku.sku_id]
        ret_prod   = products_by_tier_and_sku['retailer'][sku.sku_id]
        # Retailer product consumes wholesaler product
        ret_prod.set_bill_of_materials(raw_material=whsl_prod, num_needed=1.0)
        # Wholesaler product consumes distributor product
        whsl_prod.set_bill_of_materials(raw_material=dist_prod, num_needed=1.0)
        # Distributor product consumes manufacturer product
        dist_prod.set_bill_of_materials(raw_material=mfg_prod, num_needed=1.0)

    # Step 6: Add edges between nodes. The edges define the graph
    # topology; the BOMs above define which products flow across these
    # edges.
    for from_idx, to_idx in EDGES:
        network.add_edge(from_idx, to_idx)

    return network, nodes_by_index, products_by_tier_and_sku


# =========================================================================
# DETERMINISTIC DEMAND (Stage 1 only)
# =========================================================================

def configure_deterministic_demand(nodes_by_index, products_by_tier_and_sku, num_periods):
    """
    For Stage 1 we use simple deterministic demand: each SKU produces
    a fixed number of units per period at each retailer. The quantity
    matches the SKU's mean demand so steady-state inventory levels should
    be computable from basic Clark-Scarf theory and verifiable in the
    sanity check.

    In Stage 2 this function is replaced with the AR(1) and compound
    Poisson generators that drive realistic variable demand.

    Sets demand_source as a dict at the node level (the v6 pattern we
    validated). Assigning demand_source on individual products does not
    work because the node's default DemandSource() shadows the assignment.
    """
    retailer_indices = [6, 7, 8, 9, 10, 11]
    for retailer_idx in retailer_indices:
        retailer = nodes_by_index[retailer_idx]
        # Build a dict keyed by retailer-tier product index, with a
        # DemandSource for each SKU.
        demand_sources = {}
        for sku in SKU_SPECS:
            ret_prod = products_by_tier_and_sku['retailer'][sku.sku_id]
            demand_list = [float(sku.mean_demand)] * num_periods
            demand_sources[ret_prod.index] = DemandSource(
                type='D', demand_list=demand_list
            )
        retailer.demand_source = demand_sources


# =========================================================================
# POLICY CONFIGURATION (Stage 1 simple base-stock)
# =========================================================================

def configure_policies(nodes_by_index, products_by_tier_and_sku):
    """
    Set per-product base-stock policies at every node. For Stage 1 we use
    simple Clark-Scarf-informed base-stock levels based on the node's
    effective lead time and the aggregate demand that flows through it.

    Effective lead time at a node equals its own shipment lead time plus
    any order lead time, which captures the delay between placing an
    order and the ordered units becoming available. The number of
    retailers downstream from each node determines the aggregate demand
    flowing through that node for a given SKU.

    For Stage 1 we use a simple safety factor of 1.5x effective lead time
    demand. In Stage 3 we will introduce capacity-aware policies, AR(1)
    adjustments, and alternative policy comparisons.
    """
    # Precompute how many retailers each node feeds. For a distribution
    # tree this is equivalent to the number of leaf descendants of the node.
    retailers_fed = {
        0:  6,  # Manufacturer feeds all 6 retailers
        1:  4,  # Distributor 1 feeds retailers 6, 7, 8, 9 via Whsl 1 and 2
        2:  2,  # Distributor 2 feeds retailers 10, 11 via Whsl 3
        3:  2,  # Wholesaler 1 feeds retailers 6, 7
        4:  2,  # Wholesaler 2 feeds retailers 8, 9
        5:  2,  # Wholesaler 3 feeds retailers 10, 11
        6:  1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1,  # Each retailer feeds only itself
    }

    for ns in NODE_SPECS:
        node = nodes_by_index[ns.index]
        eff_lead_time = ns.shipment_lead_time + ns.order_lead_time
        num_retailers = retailers_fed[ns.index]

        # Build the per-SKU policy dict for this node
        policy_dict = {}
        tier = ns.tier_level
        for sku in SKU_SPECS:
            # Aggregate demand flowing through this node for this SKU:
            # mean demand per retailer times number of retailers downstream
            # (including this node itself if it is a retailer).
            agg_demand = sku.mean_demand * num_retailers
            # Safety factor of 1.5x effective lead time demand. Stage 3
            # will refine this with demand-variance-aware calibration.
            base_stock = agg_demand * eff_lead_time * 1.5
            prod = products_by_tier_and_sku[tier][sku.sku_id]
            policy_dict[prod.index] = Policy(
                type='BS', base_stock_level=base_stock,
            )
        node.inventory_policy = policy_dict


# =========================================================================
# SANITY CHECK
# =========================================================================

def sanity_check(network, nodes_by_index, products_by_tier_and_sku, num_periods=30):
    """
    Run a short simulation and verify that the four-tier network behaves
    as expected. The sanity check answers several questions at once:

    1. Does the simulation run to completion without errors?
    2. Does demand propagate all the way up from retailer to manufacturer?
    3. Do the per-SKU inventory levels look reasonable at each tier?
    4. Do aggregated flows make sense relative to the demand we specified?

    Each retailer demands the full SKU mean per period (200 for commodity,
    100 for regular, 40 for discretionary, 10 or 2 for premium). With
    six retailers, the manufacturer should see aggregate demand of
    1200 per period for commodity SKUs, 600 for regular, 240 for
    discretionary, 60 for premium AR(1) SKUs, and 12 for the intermittent
    SKU. These numbers are what we check against.
    """
    print("-" * 70)
    print(f"Running sanity check simulation for {num_periods} periods...")
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

    # Gate 1: Did the simulation produce activity? Check that at least
    # one retailer has seen inventory changes across periods. If inventory
    # is stuck at initial levels, demand is not flowing.
    print()
    print("Gate 1: Activity detection (inventory levels changing)")
    retailer_6 = nodes_by_index[6]
    ret_prod_staple_a = products_by_tier_and_sku['retailer'][1]
    initial_inv = retailer_6.state_vars[0].inventory_level.get(ret_prod_staple_a.index)
    final_inv = retailer_6.state_vars[-1].inventory_level.get(ret_prod_staple_a.index)
    print(f"  Retailer 1, SKU 1 (staple_A): initial={initial_inv}, final={final_inv}")
    if initial_inv == final_inv:
        print(f"  FAIL: inventory not changing; demand not flowing")
        return False
    print(f"  PASS")

    # Gate 2: Manufacturer sees aggregated demand. Sum the manufacturer's
    # outbound shipments across all periods for SKU 1 and verify it is
    # approximately 6 retailers * 200 units/period * num_periods
    # (minus the first couple periods of lead-time warmup).
    print()
    print("Gate 2: Demand propagates to manufacturer tier")
    manufacturer = nodes_by_index[0]
    mfg_prod_staple_a = products_by_tier_and_sku['manufacturer'][1]

    # Sum outbound shipments from manufacturer for SKU 1 across all periods.
    # outbound_shipment is nested as {successor_idx: {product_idx: qty}}.
    total_mfg_shipped = 0.0
    for sv in manufacturer.state_vars:
        if hasattr(sv, 'outbound_shipment'):
            for succ_idx, prod_dict in sv.outbound_shipment.items():
                if isinstance(prod_dict, dict):
                    total_mfg_shipped += prod_dict.get(mfg_prod_staple_a.index, 0)

    # Expected: 6 retailers * 200 units * num_periods, with some reduction
    # for warmup periods when demand is still propagating up.
    expected = 6 * 200 * num_periods
    warmup_tolerance = 0.5  # accept any value between 50% and 150% of expected
    if expected * (1 - warmup_tolerance) < total_mfg_shipped < expected * (1 + warmup_tolerance):
        print(f"  Manufacturer shipped {total_mfg_shipped:.0f} units of SKU 1")
        print(f"  Expected roughly {expected:.0f} (6 retailers * 200 units * {num_periods} periods)")
        print(f"  PASS")
    else:
        print(f"  Manufacturer shipped {total_mfg_shipped:.0f}, expected ~{expected:.0f}")
        print(f"  FAIL: demand not propagating correctly")
        return False

    # Gate 3: All twelve SKUs show activity. Verify that each of the
    # twelve SKUs produced some flow at the manufacturer tier, which
    # confirms all twelve product chains are wired correctly.
    print()
    print("Gate 3: All 12 SKUs show activity at manufacturer")
    all_ok = True
    for sku in SKU_SPECS:
        mfg_prod = products_by_tier_and_sku['manufacturer'][sku.sku_id]
        total_sku = 0.0
        for sv in manufacturer.state_vars:
            if hasattr(sv, 'outbound_shipment'):
                for succ_idx, prod_dict in sv.outbound_shipment.items():
                    if isinstance(prod_dict, dict):
                        total_sku += prod_dict.get(mfg_prod.index, 0)
        expected_sku = 6 * sku.mean_demand * num_periods
        reasonable = expected_sku * 0.5 < total_sku < expected_sku * 1.5
        status = 'ok' if reasonable else 'PROBLEM'
        print(f"  SKU {sku.sku_id:2d} ({sku.name:18s}): shipped {total_sku:>8.1f}, expected ~{expected_sku:>8.1f}  [{status}]")
        if not reasonable:
            all_ok = False
    if not all_ok:
        print(f"  FAIL: at least one SKU did not propagate correctly")
        return False
    print(f"  PASS")

    # Gate 4: Total cost reconciliation. Verify that total cost matches
    # the sum of per-node per-period holding and stockout costs, within
    # numerical tolerance.
    print()
    print("Gate 4: Total cost reconciliation")
    reconciled_cost = 0.0
    for node in nodes_by_index.values():
        for sv in node.state_vars[:num_periods]:
            reconciled_cost += (sv.holding_cost_incurred + sv.stockout_cost_incurred
                                + sv.in_transit_holding_cost_incurred)
    rel_error = abs(reconciled_cost - total_cost) / max(abs(total_cost), 1e-9)
    print(f"  Reported total cost:    {total_cost:.2f}")
    print(f"  Sum of per-period costs: {reconciled_cost:.2f}")
    print(f"  Relative error:         {rel_error:.6f}")
    if rel_error > 0.01:
        print(f"  FAIL: cost reconciliation off by more than 1%")
        return False
    print(f"  PASS")

    return True


# =========================================================================
# MAIN
# =========================================================================

def main():
    print()
    print("=" * 70)
    print("PHASE 2.3 STAGE 1: Four-tier multi-product network scaling test")
    print("=" * 70)
    print()
    print(f"Building network with {len(NODE_SPECS)} nodes across 4 tiers,")
    print(f"{len(SKU_SPECS)} SKUs, and {len(SKU_SPECS) * 4} total product instances.")
    print()

    print("Building network...")
    t0 = time.time()
    network, nodes_by_index, products_by_tier_and_sku = build_phase2_3_network()
    print(f"  Network built in {time.time() - t0:.2f}s")
    print(f"  Nodes: {len(nodes_by_index)}")
    total_products = sum(len(v) for v in products_by_tier_and_sku.values())
    print(f"  Products: {total_products}")
    print(f"  BOM declarations: {len(SKU_SPECS) * 3} (12 SKUs * 3 tier boundaries)")
    print(f"  Edges: {len(EDGES)}")
    print()

    num_periods = 30
    print(f"Configuring deterministic demand for {num_periods} periods...")
    configure_deterministic_demand(nodes_by_index, products_by_tier_and_sku, num_periods)

    print("Configuring base-stock policies...")
    configure_policies(nodes_by_index, products_by_tier_and_sku)
    print()

    ok = sanity_check(network, nodes_by_index, products_by_tier_and_sku, num_periods)

    print()
    print("=" * 70)
    if ok:
        print("STAGE 1 COMPLETE. Four-tier multi-product scaling validated.")
        print("Ready to proceed to Stage 2 (AR(1) + compound Poisson demand).")
    else:
        print("STAGE 1 FAILED. Debug the sanity check gate that did not pass.")
    print("=" * 70)


if __name__ == '__main__':
    main()
