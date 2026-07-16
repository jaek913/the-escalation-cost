"""
Phase 2.6: Serial Network Builder
==================================

Creates a 4-node serial chain (manufacturer -> distributor -> wholesaler ->
retailer) using the same SKU specifications, cost structure, and lead time
profile as the branched Phase 2.5 architecture. The single retailer is
configured to handle the equivalent demand of the 6 retailers in the
branched architecture, so the manufacturer sees the same total throughput
in both topologies.

WHY THIS EXISTS:
The capacity sweep proved that Paper 9's damping is harmful in Phase 2.5
regardless of capacity level. The next question is which architectural
feature causes the harm. The most likely candidates are branching
topology and demand aggregation. This module provides the network for
the serial-collapsed comparison condition. By comparing Paper 9's
behavior in this serial network against the branched Phase 2.5 (with
identical SKUs, costs, and total demand), we can isolate the topology
effect from the aggregation effect.

TOPOLOGY DESIGN:
- 4 nodes total (one per tier)
- Lead times match the typical retailer profile in branched: shipment=1, order=1
- Manufacturer keeps its 3+0 lead time for production
- Distributor and wholesaler match a "typical" intermediate node
- 12 SKUs identical to branched (SKU_SPECS imported from stage1)

DEMAND HANDLING:
The single retailer in this network represents the COMBINED demand of all
6 branched retailers. The runner that uses this network is responsible
for generating demand that totals 6x the per-retailer mean. This module
just builds the network skeleton; demand is configured externally.

CAPACITY AND POLICIES:
The manufacturer's capacity should still be 1.3x aggregate mean demand
(same formula as branched). Since aggregate mean = 6 * sku.mean_demand
in both architectures, the same apply_capacity_constraints function
works without modification.

For policies, the formula base_stock = mean_demand * num_retailers *
eff_lead_time * 1.5 needs num_retailers to reflect the equivalent number
of retailers worth of demand each node serves. In serial, every node
effectively serves 6 retailers worth of demand because that's how much
flows through the single chain.

Author: JAE with Claude as research assistant
Date: April 26, 2026
"""

from dataclasses import dataclass

from stockpyl.supply_chain_network import SupplyChainNetwork
from stockpyl.supply_chain_node import SupplyChainNode
from stockpyl.supply_chain_product import SupplyChainProduct

# Import SKU specs and helpers from the existing branched network builder.
# This guarantees both architectures use the same SKUs, costs, and tier
# offsets, which is essential for clean comparison.
from phase2_3_stage1_network import (
    SKU_SPECS,
    holding_cost_for, stockout_cost_for,
    TIER_OFFSET, product_index,
)


# =========================================================================
# SERIAL NODE SPECIFICATION
# =========================================================================
# Four nodes, one per tier. The manufacturer's lead time matches branched
# (3 production + 0 ordering). The intermediate tiers use the most common
# pattern in the branched architecture (1 shipment + 1 ordering each).
# The retailer uses the same pattern as a "typical" branched retailer.
# These choices keep effective lead times comparable between architectures.

@dataclass
class SerialNodeSpec:
    """Same fields as NodeSpec in stage1, but defined here so we don't
    accidentally couple to the branched-specific NODE_SPECS list."""
    index: int
    name: str
    tier_level: str
    shipment_lead_time: int
    order_lead_time: int


SERIAL_NODE_SPECS = [
    SerialNodeSpec(0, 'Manufacturer', 'manufacturer', shipment_lead_time=3, order_lead_time=0),
    SerialNodeSpec(1, 'Distributor',  'distributor',  shipment_lead_time=2, order_lead_time=1),
    SerialNodeSpec(2, 'Wholesaler',   'wholesaler',   shipment_lead_time=1, order_lead_time=1),
    SerialNodeSpec(3, 'Retailer',     'retailer',     shipment_lead_time=1, order_lead_time=1),
]

# Edges in serial chain are simple: each node feeds the next downstream node.
SERIAL_EDGES = [(0, 1), (1, 2), (2, 3)]

# Number of "equivalent retailers" each node serves. In serial, the single
# retailer represents 6 retailers worth of demand, so every node is
# effectively serving 6 retailers worth. This is what makes the policies
# size correctly for the same total demand as branched.
SERIAL_RETAILERS_FED = {0: 6, 1: 6, 2: 6, 3: 6}


# =========================================================================
# NETWORK BUILDER
# =========================================================================

def build_phase2_6_serial_network():
    """Build a 4-node serial chain compatible with the Phase 2.6 runner.

    Returns the same triple as build_phase2_3_network: (network,
    nodes_by_index, products_by_tier_and_sku). The structure of the
    second and third returns matches the branched builder exactly, so
    code that processes these can be shared between architectures.

    Network construction follows the same six-step pattern as the
    branched builder: create nodes, create products, attach products
    to nodes, set supply_type, declare BOMs, add edges. The only
    differences are the number of nodes (4 instead of 12) and the
    topology (linear instead of branched).
    """
    network = SupplyChainNetwork()

    # Step 1: Create the four nodes.
    nodes_by_index = {}
    for ns in SERIAL_NODE_SPECS:
        node = SupplyChainNode(
            index=ns.index,
            name=ns.name,
            shipment_lead_time=ns.shipment_lead_time,
            order_lead_time=ns.order_lead_time,
        )
        network.add_node(node)
        nodes_by_index[ns.index] = node

    # Step 2: Create products for each (tier, sku) combination. We use the
    # SAME product index scheme as the branched builder so any code that
    # looks up products by tier+sku works identically across architectures.
    products_by_tier_and_sku = {
        'manufacturer': {}, 'distributor': {}, 'wholesaler': {}, 'retailer': {},
    }
    for sku in SKU_SPECS:
        for tier in ['manufacturer', 'distributor', 'wholesaler', 'retailer']:
            p_index = product_index(tier, sku.sku_id)
            p_name = f"{sku.name}_at_{tier}_serial"
            holding = holding_cost_for(sku, tier)
            stockout = stockout_cost_for(sku) if tier == 'retailer' else 0.0

            kwargs = dict(
                index=p_index,
                name=p_name,
                local_holding_cost=holding,
                stockout_cost=stockout,
            )
            if tier == 'manufacturer':
                kwargs['supply_type'] = 'U'

            product = SupplyChainProduct(**kwargs)
            products_by_tier_and_sku[tier][sku.sku_id] = product

    # Step 3: Attach products to nodes. Each tier has exactly one node,
    # so the attachment is straightforward (no looping over multiple
    # nodes per tier as in branched).
    for sku in SKU_SPECS:
        nodes_by_index[0].add_product(products_by_tier_and_sku['manufacturer'][sku.sku_id])
        nodes_by_index[1].add_product(products_by_tier_and_sku['distributor'][sku.sku_id])
        nodes_by_index[2].add_product(products_by_tier_and_sku['wholesaler'][sku.sku_id])
        nodes_by_index[3].add_product(products_by_tier_and_sku['retailer'][sku.sku_id])

    # Step 4: Mark manufacturer as having external supply (raw materials).
    nodes_by_index[0].supply_type = 'U'

    # Step 5: Declare BOMs across tier boundaries. Same logic as branched:
    # each tier consumes one unit of the upstream tier's product per unit
    # produced. Pass-through transformation across all 12 SKUs.
    for sku in SKU_SPECS:
        mfg_prod  = products_by_tier_and_sku['manufacturer'][sku.sku_id]
        dist_prod = products_by_tier_and_sku['distributor'][sku.sku_id]
        whsl_prod = products_by_tier_and_sku['wholesaler'][sku.sku_id]
        ret_prod  = products_by_tier_and_sku['retailer'][sku.sku_id]
        ret_prod.set_bill_of_materials(raw_material=whsl_prod, num_needed=1.0)
        whsl_prod.set_bill_of_materials(raw_material=dist_prod, num_needed=1.0)
        dist_prod.set_bill_of_materials(raw_material=mfg_prod, num_needed=1.0)

    # Step 6: Add edges (3 edges in serial vs 11 in branched).
    for from_idx, to_idx in SERIAL_EDGES:
        network.add_edge(from_idx, to_idx)

    return network, nodes_by_index, products_by_tier_and_sku


# =========================================================================
# QUICK SANITY TEST (run if module invoked directly)
# =========================================================================

def _quick_test():
    """Build the network and verify basic structural properties."""
    print("Building serial Phase 2.6 network...")
    network, nodes, products = build_phase2_6_serial_network()
    print(f"  Nodes: {len(nodes)} (expected 4)")
    print(f"  Products by tier:")
    for tier, prod_dict in products.items():
        print(f"    {tier}: {len(prod_dict)} products")
    print(f"  Total products: {sum(len(d) for d in products.values())} (expected 48)")
    print(f"  Edges: {len(network.edges)} (expected 3)")

    # Check that nodes have the right tier products attached
    for node_idx, node in nodes.items():
        ns = next(s for s in SERIAL_NODE_SPECS if s.index == node_idx)
        # Each node should have 12 products (one per SKU)
        if hasattr(node, 'products'):
            n_products = len(node.products) if isinstance(node.products, (list, dict)) else 0
            print(f"  Node {node_idx} ({ns.name}, tier {ns.tier_level}): "
                  f"{n_products} products attached")

    print("Serial network structural sanity check complete.")


if __name__ == '__main__':
    _quick_test()
