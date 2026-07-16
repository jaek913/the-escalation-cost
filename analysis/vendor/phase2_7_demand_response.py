"""
Phase 2.7: Price-Elastic Demand Response Module
================================================

This module extends the Phase 2.6 demand generators with a price-response
layer. Phase 2.6 generates exogenous demand streams (iid_control, ar1_*,
drift_canonical, regime_change) where customer demand is independent of
retailer pricing. Phase 2.7 needs demand to respond to price so that
retailer pricing decisions actually affect what the chain sees, which is
the prerequisite for testing the formula's pricing-decision capability.

The mathematical model
----------------------

We use a constant-elasticity demand response, which is the standard model
in retail pricing literature. Mathematically:

    realized_demand(t) = baseline_demand(t) * (price(t) / reference_price) ^ (-elasticity)

The elasticity parameter is the percentage change in quantity demanded
per percentage change in price. For typical consumer goods, elasticity
ranges from about 0.5 (staples like flour) to 3.0 (discretionary luxury
goods). Default value is 1.5, which represents typical mid-market
consumer goods.

The reference price is the price level at which the realized demand
exactly equals the baseline demand. We default to 1.0 (a normalized unit
price), so pricing decisions are expressed as multiplicative adjustments:
a price of 1.1 means ten percent above reference, a price of 0.9 means
ten percent below reference.

Why constant elasticity rather than linear
-------------------------------------------

A linear model D = a - b*P would be simpler arithmetically, but it has
the problem that demand can go negative at high prices, which is
unphysical. The constant-elasticity model produces realistic demand
curves at both extremes of the price range and also has cleaner economic
interpretation because the elasticity parameter directly encodes the
price-sensitivity behavior we are trying to model.

Separation from preference dynamics
------------------------------------

The Phase 2.6 demand generators produce a baseline demand stream that
captures customer preference dynamics (the AR(1) persistence, regime
changes, drift schedules). The Phase 2.7 demand response layer applies
a price multiplier to this baseline. Keeping these two components
separate lets us reason about preference shifts and price responses
independently. The phi value the formula estimates from the realized
demand stream will pick up both effects, but the simulator's ground
truth keeps them separable for analysis purposes.

Author: JAE with Claude as research assistant
Date: April 29, 2026
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np


# =========================================================================
# CONFIGURATION
# =========================================================================

@dataclass
class DemandResponseConfig:
    """Configuration for the constant-elasticity demand response model.

    Three parameters control the model. Default values represent typical
    mid-market consumer goods at unit reference price.

    Attributes
    ----------
    elasticity : float
        Price elasticity of demand (a positive number). Higher values
        mean demand responds more strongly to price changes. Realistic
        range is 0.5 to 3.0. Default 1.5.
    reference_price : float
        The price at which realized demand equals baseline demand.
        Default 1.0 (normalized unit price).
    floor : float
        Minimum allowed realized demand. Set to 0.0 to allow demand to
        approach zero at very high prices. Set to a small positive
        number to prevent the simulator from seeing exactly-zero demand
        in pathological cases. Default 0.0.
    """
    elasticity: float = 1.5
    reference_price: float = 1.0
    floor: float = 0.0

    def __post_init__(self):
        # Validate inputs at construction time so we fail loudly rather
        # than producing silently-wrong results during a long fleet run.
        if self.elasticity < 0:
            raise ValueError(
                f"Elasticity must be non-negative, got {self.elasticity}. "
                f"Negative elasticity would mean demand rises with price, "
                f"which is the wrong sign for normal goods."
            )
        if self.reference_price <= 0:
            raise ValueError(
                f"Reference price must be positive, got {self.reference_price}."
            )
        if self.floor < 0:
            raise ValueError(
                f"Demand floor must be non-negative, got {self.floor}."
            )


# =========================================================================
# CORE FUNCTIONS
# =========================================================================

def apply_price_response(
    baseline_demand: float,
    price: float,
    config: DemandResponseConfig,
) -> float:
    """Apply the constant-elasticity demand response to a single period.

    Computes realized_demand = baseline * (price / reference) ^ (-elasticity)
    with a floor at config.floor.

    The mathematical structure means that at price equal to reference,
    realized_demand equals baseline_demand exactly. At price above
    reference, realized_demand is below baseline (customers buy less).
    At price below reference, realized_demand is above baseline (customers
    buy more).

    Parameters
    ----------
    baseline_demand : float
        The exogenous customer demand at reference price.
    price : float
        The current price the retailer is charging.
    config : DemandResponseConfig
        The elasticity model parameters.

    Returns
    -------
    float
        The realized demand at the given price. Always non-negative.
    """
    if price <= 0:
        # Defensive: the pricing policy should never produce a non-positive
        # price, but if it does we want to fail loudly rather than producing
        # NaN through the negative-power computation.
        raise ValueError(
            f"Price must be positive for elasticity model, got {price}. "
            f"This indicates a bug in the pricing decision policy."
        )

    # The price ratio is what enters the elasticity formula. A ratio of
    # 1.0 means price equals reference; greater than 1.0 means above
    # reference (and realized demand will be below baseline).
    price_ratio = price / config.reference_price

    # The elasticity formula. Note the negative sign: higher prices
    # reduce demand. Python handles fractional exponents on positive
    # numbers without issue.
    multiplier = price_ratio ** (-config.elasticity)

    realized = baseline_demand * multiplier
    return max(realized, config.floor)


def apply_price_response_array(
    baseline_demand: np.ndarray,
    prices: np.ndarray,
    config: DemandResponseConfig,
) -> np.ndarray:
    """Vectorized version of apply_price_response for whole-stream computation.

    When the price history is known up-front (for diagnostic purposes or
    for policies that pre-compute prices), this function applies the
    elasticity model to the entire baseline-demand array in one operation.

    The simulator's main loop will not normally use this version because
    pricing decisions depend on observed realized demand from previous
    periods, which means each period must be computed in sequence.
    However, this vectorized form is useful for unit tests, sanity checks,
    and any analysis that needs to recompute realized demand under
    counterfactual pricing.

    Parameters
    ----------
    baseline_demand : np.ndarray
        Array of baseline demand values, one per period.
    prices : np.ndarray
        Array of prices, one per period. Must be same length as
        baseline_demand and all positive.
    config : DemandResponseConfig
        The elasticity model parameters.

    Returns
    -------
    np.ndarray
        Array of realized demand values, same length as inputs.
    """
    if baseline_demand.shape != prices.shape:
        raise ValueError(
            f"baseline_demand shape {baseline_demand.shape} does not match "
            f"prices shape {prices.shape}"
        )
    if np.any(prices <= 0):
        # Find the first offending period for a useful error message.
        first_bad = int(np.argmax(prices <= 0))
        raise ValueError(
            f"All prices must be positive for elasticity model. "
            f"First non-positive price is at period {first_bad}: "
            f"{prices[first_bad]}"
        )

    price_ratios = prices / config.reference_price
    multipliers = np.power(price_ratios, -config.elasticity)
    realized = baseline_demand * multipliers
    return np.maximum(realized, config.floor)


def revenue_at_period(
    realized_demand: float,
    price: float,
    fulfilled_quantity: Optional[float] = None,
) -> float:
    """Compute revenue for a single period.

    Revenue is price times quantity sold. By default we assume the chain
    fulfills all realized demand, so quantity sold equals realized demand
    and revenue equals price times realized demand. If fulfilled_quantity
    is provided, it represents the actual quantity the chain was able to
    deliver (which may be less than realized demand under stockout
    conditions), and revenue is computed against that instead.

    The fulfilled_quantity path is important for capacity-constrained
    chains where the manufacturer might not be able to produce enough
    to satisfy realized demand. In those cases, revenue is bounded by
    what the chain physically delivered, not by what customers wanted
    to buy.

    Parameters
    ----------
    realized_demand : float
        Quantity the customer wanted to buy at the current price.
    price : float
        Current retailer price.
    fulfilled_quantity : float, optional
        Actual quantity delivered. Defaults to realized_demand, which
        assumes no stockout.

    Returns
    -------
    float
        Revenue for the period.
    """
    quantity_sold = realized_demand if fulfilled_quantity is None else fulfilled_quantity
    return price * quantity_sold


# =========================================================================
# SELF-TEST
# =========================================================================

def _self_test():
    """Verify the demand response model behaves correctly across regimes.

    Tests the model on three elasticity regimes (low, medium, high)
    against analytically known cases:
      1. Price equals reference -> realized demand equals baseline (any elasticity)
      2. Doubling price at elasticity 1.0 -> demand halves
      3. Halving price at elasticity 1.0 -> demand doubles
      4. Doubling price at elasticity 0.0 -> demand unchanged (perfectly inelastic)
      5. Vectorized version produces same results as scalar version
      6. Floor parameter prevents negative demand at extreme prices
    """
    print("=" * 60)
    print("Phase 2.7 demand response self-test")
    print("=" * 60)

    # --- Test 1: price at reference produces unchanged demand ---
    print("\nTest 1: price equals reference -> demand unchanged")
    for elasticity in [0.5, 1.0, 1.5, 2.0, 3.0]:
        cfg = DemandResponseConfig(elasticity=elasticity)
        d = apply_price_response(baseline_demand=10.0, price=1.0, config=cfg)
        print(f"  elasticity={elasticity:.1f}, baseline=10.0, price=1.0 -> {d:.4f}  "
              f"{'OK' if abs(d - 10.0) < 1e-9 else 'FAIL'}")
        assert abs(d - 10.0) < 1e-9

    # --- Test 2: doubling price at elasticity 1 halves demand ---
    print("\nTest 2: doubling price at elasticity=1.0 -> demand halves")
    cfg = DemandResponseConfig(elasticity=1.0)
    d = apply_price_response(baseline_demand=10.0, price=2.0, config=cfg)
    print(f"  baseline=10.0, price=2.0 -> {d:.4f}  "
          f"(expected 5.0)")
    assert abs(d - 5.0) < 1e-9

    # --- Test 3: halving price at elasticity 1 doubles demand ---
    print("\nTest 3: halving price at elasticity=1.0 -> demand doubles")
    cfg = DemandResponseConfig(elasticity=1.0)
    d = apply_price_response(baseline_demand=10.0, price=0.5, config=cfg)
    print(f"  baseline=10.0, price=0.5 -> {d:.4f}  "
          f"(expected 20.0)")
    assert abs(d - 20.0) < 1e-9

    # --- Test 4: zero elasticity is perfectly inelastic ---
    print("\nTest 4: zero elasticity -> demand unchanged regardless of price")
    cfg = DemandResponseConfig(elasticity=0.0)
    for price in [0.5, 1.0, 1.5, 2.0, 5.0]:
        d = apply_price_response(baseline_demand=10.0, price=price, config=cfg)
        print(f"  price={price:.1f} -> {d:.4f}  "
              f"{'OK' if abs(d - 10.0) < 1e-9 else 'FAIL'}")
        assert abs(d - 10.0) < 1e-9

    # --- Test 5: high elasticity produces aggressive response ---
    # At elasticity=3.0, doubling price should reduce demand by factor of 8
    print("\nTest 5: elasticity=3.0 -> doubling price reduces demand 8x")
    cfg = DemandResponseConfig(elasticity=3.0)
    d = apply_price_response(baseline_demand=80.0, price=2.0, config=cfg)
    print(f"  baseline=80.0, price=2.0 -> {d:.4f}  "
          f"(expected 10.0)")
    assert abs(d - 10.0) < 1e-9

    # --- Test 6: vectorized version matches scalar ---
    print("\nTest 6: vectorized matches scalar across elasticities")
    baseline = np.array([10.0, 12.0, 8.0, 15.0, 9.0])
    prices = np.array([1.0, 1.2, 0.8, 1.5, 0.9])
    for elasticity in [0.5, 1.5, 3.0]:
        cfg = DemandResponseConfig(elasticity=elasticity)
        realized_vec = apply_price_response_array(baseline, prices, cfg)
        realized_scalar = np.array([
            apply_price_response(baseline[i], prices[i], cfg)
            for i in range(len(baseline))
        ])
        max_diff = np.max(np.abs(realized_vec - realized_scalar))
        print(f"  elasticity={elasticity:.1f}, max_diff={max_diff:.2e}  "
              f"{'OK' if max_diff < 1e-12 else 'FAIL'}")
        assert max_diff < 1e-12

    # --- Test 7: floor parameter ---
    print("\nTest 7: floor parameter prevents demand from going below floor")
    cfg = DemandResponseConfig(elasticity=2.0, floor=0.5)
    # At very high price relative to reference, raw demand would be tiny.
    # Floor should kick in.
    d = apply_price_response(baseline_demand=10.0, price=100.0, config=cfg)
    print(f"  elasticity=2.0, floor=0.5, baseline=10.0, price=100.0 -> {d:.4f}")
    assert d >= 0.5
    assert d == 0.5  # at this extreme price, raw is 10 * 100^-2 = 0.001, so floor binds

    # --- Test 8: revenue computation ---
    print("\nTest 8: revenue computation")
    rev = revenue_at_period(realized_demand=10.0, price=1.5)
    print(f"  realized=10.0, price=1.5 -> revenue={rev:.4f}  (expected 15.0)")
    assert abs(rev - 15.0) < 1e-9

    rev_partial = revenue_at_period(realized_demand=10.0, price=1.5, fulfilled_quantity=8.0)
    print(f"  with fulfilled=8.0 -> revenue={rev_partial:.4f}  (expected 12.0)")
    assert abs(rev_partial - 12.0) < 1e-9

    # --- Test 9: validation errors fire correctly ---
    print("\nTest 9: validation errors")
    try:
        DemandResponseConfig(elasticity=-0.5)
        print("  FAIL: should have raised on negative elasticity")
        assert False
    except ValueError as e:
        print(f"  Negative elasticity rejected: {str(e)[:60]}...  OK")

    try:
        cfg = DemandResponseConfig(elasticity=1.5)
        apply_price_response(baseline_demand=10.0, price=-1.0, config=cfg)
        print("  FAIL: should have raised on negative price")
        assert False
    except ValueError as e:
        print(f"  Negative price rejected: {str(e)[:60]}...  OK")

    print("\nAll self-tests completed.")
    print("=" * 60)


if __name__ == '__main__':
    _self_test()
