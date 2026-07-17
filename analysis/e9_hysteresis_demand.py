"""e9_hysteresis_demand.py - E9: customer-hysteresis demand layer (OURS).

DESIGN.md Section 12, amendment 2026-07-16 (Option B, author-ratified).

PROVENANCE AND AUTHORSHIP (the honesty limits recorded in the amendment):
this module is WRITTEN FROM SPECIFICATION - the frozen operator in DESIGN
Section 12 plus the mathematical structure stated in the source module's
documentation - and is NOT copied or transcribed from the source's code
body. It is authorship-independent but NOT blind (the source's code was
read during the gate's verification, as the Standard requires). Its
faithfulness is PROVED, not assumed, by two pre-registered checks:
  (1) the suite's h=0 bit-equivalence leg against the vendored,
      CIC-cleared elasticity-only pricing manager; and
  (2) the fidelity comparison of our full run at the source's seeds
      (2000-2019) against the source's registered artifact
      (SHA256 e5875b0fac7f35e1b9ccc4b956c8f99f28355a5fa6787df6dd2624368202ef3b),
      per the amendment's TIER-EXACT / TIER-CLOSE / FAIL criterion.

THE FROZEN MATHEMATICS (DESIGN Section 12 amendment, "hysteresis"):
  pool(0) = 1.0. Each period, the pool is updated from the CURRENT price
  BEFORE demand realizes:
    ratio = price / reference_price
    if ratio <= 1.0 : pool unchanged             [one-directional]
    else            : pool *= max(0, 1 - intensity * (ratio - 1))
                      pool = max(pool, 0.10)     [floor]
  Realized demand per SKU:
    realized = baseline * ratio^(-elasticity) * pool
  The pricing policy's demand history is the POST-HYSTERESIS aggregate
  (the policy observes actual sales, eroded by its own past prices).
  At pool = 1.0 the arithmetic reduces exactly to the vendored
  elasticity-only model (x * 1.0 is IEEE-exact), which is why the h=0
  equivalence bar is bit-identity.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Floor on the customer pool (frozen from the operator: at most 90% of
# customers can be permanently lost; prevents zero-demand pathologies).
POOL_FLOOR = 0.10


@dataclass
class HysteresisSpec:
    """Frozen parameters of the hysteresis demand layer (DESIGN Sec 12)."""
    elasticity: float = 1.5
    reference_price: float = 1.0
    demand_floor: float = 0.0
    intensity: float = 0.0

    def __post_init__(self) -> None:
        if self.elasticity < 0:
            raise ValueError(f"elasticity must be >= 0, got {self.elasticity}")
        if self.reference_price <= 0:
            raise ValueError(
                f"reference_price must be > 0, got {self.reference_price}")
        if self.demand_floor < 0:
            raise ValueError(
                f"demand_floor must be >= 0, got {self.demand_floor}")
        if self.intensity < 0:
            raise ValueError(
                f"intensity must be >= 0, got {self.intensity} "
                f"(negative would mean customers join on price raises)")


def update_pool(previous_pool: float, price: float,
                spec: HysteresisSpec) -> float:
    """One-period pool update. One-directional: raises erode, cuts never
    regrow. Floored at POOL_FLOOR."""
    if price <= 0:
        raise ValueError(f"price must be > 0, got {price}")
    ratio = price / spec.reference_price
    if ratio <= 1.0:
        return previous_pool
    elevation = ratio - 1.0
    decay = max(0.0, 1.0 - spec.intensity * elevation)
    new_pool = previous_pool * decay
    return max(new_pool, POOL_FLOOR)


def realized_demand(baseline: float, price: float, pool: float,
                    spec: HysteresisSpec) -> float:
    """Constant-elasticity response times the surviving customer pool."""
    if price <= 0:
        raise ValueError(f"price must be > 0, got {price}")
    ratio = price / spec.reference_price
    factor = ratio ** (-spec.elasticity)
    realized = baseline * factor * pool
    return max(realized, spec.demand_floor)


def apply_pricing_with_hysteresis(
    sku_baseline_streams: Dict[Any, np.ndarray],
    pricing_policy_name: str,
    policy_config,
    spec: HysteresisSpec,
    transition_period: Optional[int] = None,
    initial_price: float = 1.0,
    policy_factory=None,
) -> Tuple[Dict[Any, np.ndarray], List[float], Dict[str, Any]]:
    """OUR pricing walk with the hysteresis pool threaded through it.

    Contract mirrors the vendored apply_pricing_to_retailer_streams (whose
    call-site look-ahead discipline cleared CIC-4): per period the pool is
    updated from the CURRENT price, per-SKU realized demand and revenue
    accrue at that price, the post-hysteresis aggregate is appended to the
    policy's demand history, and at review boundaries the policy decides
    the NEXT price from history covering periods 0..t only.

    policy_factory defaults to the vendored make_pricing_policy; it is a
    parameter so the suite can inject stub policies for engagement tests.
    """
    if not sku_baseline_streams:
        raise ValueError("sku_baseline_streams must contain at least one SKU")

    sku_ids = list(sku_baseline_streams.keys())
    num_periods = len(sku_baseline_streams[sku_ids[0]])
    for sku_id, stream in sku_baseline_streams.items():
        if len(stream) != num_periods:
            raise ValueError(
                f"stream length mismatch: SKU {sku_ids[0]} has "
                f"{num_periods}, SKU {sku_id} has {len(stream)}")

    if policy_factory is None:
        from phase2_7_pricing_policies import make_pricing_policy
        policy_factory = make_pricing_policy
    policy = policy_factory(pricing_policy_name, policy_config)
    review_interval = policy_config.review_interval

    current_price = float(initial_price)
    pool = 1.0
    price_history: List[float] = []
    pool_history: List[float] = []
    aggregated_demand_history: List[float] = []
    realized_streams: Dict[Any, List[float]] = {sid: [] for sid in sku_ids}
    revenue_per_period: List[float] = []

    num_price_changes = 0
    first_price_change_period: Optional[int] = None
    last_review_period = -1

    for t in range(num_periods):
        pool = update_pool(pool, current_price, spec)
        pool_history.append(pool)

        period_aggregate = 0.0
        period_revenue = 0.0
        for sku_id in sku_ids:
            baseline_t = float(sku_baseline_streams[sku_id][t])
            realized_t = realized_demand(baseline_t, current_price, pool, spec)
            realized_streams[sku_id].append(realized_t)
            period_aggregate += realized_t
            period_revenue += realized_t * current_price

        aggregated_demand_history.append(period_aggregate)
        price_history.append(current_price)
        revenue_per_period.append(period_revenue)

        is_review = (t + 1) % review_interval == 0
        if is_review and t > last_review_period:
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

    realized_arrays: Dict[Any, np.ndarray] = {
        sid: np.asarray(stream, dtype=float)
        for sid, stream in realized_streams.items()
    }

    lead_time = None
    if transition_period is not None and first_price_change_period is not None:
        if first_price_change_period >= transition_period:
            lead_time = first_price_change_period - transition_period

    metadata: Dict[str, Any] = {
        "pricing_policy_name": pricing_policy_name,
        "num_price_changes": num_price_changes,
        "first_price_change_period": first_price_change_period,
        "transition_period": transition_period,
        "lead_time_to_detection": lead_time,
        "revenue_per_period": revenue_per_period,
        "total_revenue": float(np.sum(revenue_per_period)),
        "mean_revenue_per_period": float(np.mean(revenue_per_period)),
        "final_price": current_price,
        "hysteresis_intensity": spec.intensity,
        "final_customer_pool": float(pool_history[-1]),
        "min_customer_pool": float(np.min(pool_history)),
        "pool_history": pool_history,
    }

    return realized_arrays, price_history, metadata
