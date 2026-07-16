"""
Phase 2.7: Pricing Decision Policies
=====================================

This module defines the pricing policies that operate at the retailer
position in Phase 2.7 experiments. A pricing policy decides whether to
change the retail price at each pricing review interval based on
observed demand history. The price decision then feeds back into the
demand response model in phase2_7_demand_response.py to produce the
realized demand the chain sees.

The three policies implemented here form the comparison set described
in the Phase 2.7 design document. They share a common interface so the
simulator can swap them in and out without architecture changes.

The three policies
------------------

NoPricingPolicy: never changes price regardless of observed demand.
This is the worst-case baseline. The retailer is operating with a
fixed price and any persistence-driven pricing opportunity is missed.
Useful for measuring whether dynamic pricing in general adds value
relative to static pricing.

NaiveReactivePolicy: changes price proportionally to observed demand
shifts without distinguishing persistent shifts from transient noise.
Each pricing review compares a recent short window of demand against
a longer baseline window; if the shift exceeds a minimum threshold the
policy adjusts price proportionally. This represents a typical
operations manager who reacts to whatever the trailing data shows
without sophisticated signal processing. Comparing against this
baseline isolates the value of the formula's persistence-discrimination
capability beyond the value of dynamic pricing in general.

PhiGatedPolicy: uses an OLS persistence estimator to decide whether
observed demand changes reflect genuine preference shifts or transient
noise. Only adjusts price when both (a) the demand shift exceeds a
minimum threshold and (b) the persistence estimate exceeds an engagement
threshold. The bidirectional symmetry of phi is what gives this policy
the early-warning capability for both upward and downward demand shifts.
The asymmetric variant uses different engagement thresholds for upward
versus downward decisions, reflecting the operational reality that
price cuts are harder to reverse than price increases.

The price adjustment formula
----------------------------

When a pricing policy decides to act, all three pricing policies use
the same adjustment formula:

    new_price = current_price * (demand_shift_factor) ^ (1 / elasticity)

This is the constant-volume pricing rule. It adjusts price so that
realized demand returns to the baseline level after the shift, which
means the retailer captures the entire preference shift in price
changes while keeping volume stable. The mathematical derivation is:

    realized_demand = baseline * f * (price/p_ref)^(-elasticity)

Setting realized_demand equal to baseline (volume stays at baseline
level) and solving for new_price yields the formula above.

For the upward case (f > 1) this means raising price; for the downward
case (f < 1) this means cutting price; the formula handles both
directions symmetrically. This is the bidirectional mechanism that
makes the formula an early-warning system for demand collapse rather
than just a pricing-up tool.

The OLS persistence estimator
-----------------------------

The phi-gated policy estimates persistence using a lag-1 OLS regression
on the demand history. Concretely, given a window of recent demand
observations, we compute the coefficient of D[t-1] when regressing
D[t] against D[t-1]. This is a standard estimator for AR(1) persistence
with known finite-sample bias (Hurwicz) but is the same estimator the
inventory-side SR formula uses, so we get consistency between the
inventory and pricing decisions.

Author: JAE with Claude as research assistant
Date: April 29, 2026
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional
import numpy as np


# =========================================================================
# CONFIGURATION
# =========================================================================

@dataclass
class PricingPolicyConfig:
    """Common configuration for the pricing policies.

    These parameters are shared across all three policies even though
    not all policies use all parameters. Keeping them in one config
    object simplifies the runner-side configuration and makes it easy
    to compare policies with identical thresholds.

    Attributes
    ----------
    elasticity : float
        Price elasticity assumed by the policy when computing price
        adjustments. Should match the elasticity in the demand response
        model for consistency. Default 1.5.
    review_interval : int
        Number of periods between pricing reviews. Default 20 periods,
        which represents biweekly pricing for daily-period simulations
        or monthly pricing for weekly-period simulations.
    recent_window : int
        Number of recent periods used to estimate the current demand
        level. Default 20 periods.
    baseline_window : int
        Number of periods used to estimate the baseline demand level.
        The baseline is the recent_window-to-(recent_window+baseline_window)
        period range, so it does not overlap with the recent window.
        Default 60 periods (giving a total lookback of 80 periods for
        baseline-to-recent comparison).
    min_change_threshold : float
        Minimum fractional shift in demand required to trigger a price
        change. Default 0.05 (five percent). Below this threshold the
        policy holds price even if other conditions are met.
    phi_estimation_window : int
        Number of periods used by the phi-gated policy for OLS
        persistence estimation. Default 40 periods. Should be at least
        as large as the recent_window to give the OLS estimator enough
        data.
    phi_threshold_up : float
        Engagement threshold for upward price decisions in phi-gated
        policies. The policy raises price only if estimated phi exceeds
        this value. Default 0.6.
    phi_threshold_down : float
        Engagement threshold for downward price decisions in phi-gated
        policies. The asymmetric variant uses 0.75 (more conservative);
        the symmetric variant uses the same value as phi_threshold_up.
        Default 0.6 (symmetric).
    max_price_change : float
        Maximum fractional change in price per pricing review. Caps
        runaway price moves that could result from extreme observed
        shifts. Default 0.25 (twenty-five percent per review).
    """
    elasticity: float = 1.5
    review_interval: int = 20
    recent_window: int = 20
    baseline_window: int = 60
    min_change_threshold: float = 0.05
    phi_estimation_window: int = 40
    phi_threshold_up: float = 0.6
    phi_threshold_down: float = 0.6
    max_price_change: float = 0.25

    def __post_init__(self):
        # Validation. Same pattern as DemandResponseConfig: catch errors
        # at construction time so we fail loudly rather than producing
        # silently-wrong results during a long fleet run.
        if self.elasticity <= 0:
            raise ValueError(
                f"Elasticity must be positive, got {self.elasticity}."
            )
        if self.review_interval < 1:
            raise ValueError(
                f"Review interval must be at least 1 period, got "
                f"{self.review_interval}."
            )
        if self.recent_window < 1:
            raise ValueError(
                f"Recent window must be at least 1 period, got "
                f"{self.recent_window}."
            )
        if self.baseline_window < 1:
            raise ValueError(
                f"Baseline window must be at least 1 period, got "
                f"{self.baseline_window}."
            )
        if self.min_change_threshold < 0:
            raise ValueError(
                f"Min change threshold must be non-negative, got "
                f"{self.min_change_threshold}."
            )
        if not (0 <= self.phi_threshold_up <= 1):
            raise ValueError(
                f"phi_threshold_up must be in [0, 1], got "
                f"{self.phi_threshold_up}."
            )
        if not (0 <= self.phi_threshold_down <= 1):
            raise ValueError(
                f"phi_threshold_down must be in [0, 1], got "
                f"{self.phi_threshold_down}."
            )
        if self.max_price_change <= 0:
            raise ValueError(
                f"Max price change must be positive, got "
                f"{self.max_price_change}."
            )


# =========================================================================
# OLS PERSISTENCE ESTIMATOR
# =========================================================================

def estimate_phi_ols(demand_history: List[float]) -> float:
    """Estimate AR(1) persistence parameter from a demand history window.

    Computes the lag-1 OLS regression coefficient of D[t] on D[t-1],
    which is the maximum-likelihood estimator for the AR(1) phi parameter
    under normality assumptions. Has known downward bias (Hurwicz bias)
    in finite samples but is the same estimator the inventory-side SR
    policy uses, so we get consistency between inventory and pricing
    decisions.

    The estimator subtracts the mean from the demand series before
    regressing, which is the standard demeaned form and avoids
    confounding the slope estimate with the demand level. If the
    series has near-zero variance (numerical-precision issue), returns
    0.0 to indicate no detectable persistence.

    Parameters
    ----------
    demand_history : list of float
        Recent demand observations, in chronological order. Length
        should be at least 3 for a meaningful estimate.

    Returns
    -------
    float
        Estimated AR(1) phi value, clipped to [-1, 1]. Returns 0.0 if
        the series is too short or numerically degenerate.
    """
    if len(demand_history) < 3:
        return 0.0

    arr = np.asarray(demand_history, dtype=float)
    arr_centered = arr - arr.mean()

    # Lag-1 covariance / lag-0 variance is the standard OLS slope.
    numerator = np.sum(arr_centered[1:] * arr_centered[:-1])
    denominator = np.sum(arr_centered[:-1] ** 2)

    if denominator < 1e-12:
        # Degenerate case: demand is essentially constant. No persistence
        # is detectable in this regime, so return 0.0 rather than
        # producing a divide-by-zero or random extreme estimate.
        return 0.0

    phi = float(numerator / denominator)
    # Clip to the AR(1) stationarity range. Beyond [-1, 1] the demand
    # process is non-stationary, which is outside our model assumptions.
    return float(np.clip(phi, -1.0, 1.0))


# =========================================================================
# PRICING POLICY BASE CLASS
# =========================================================================

class PricingPolicy:
    """Abstract base class for pricing decision policies.

    Subclasses implement the decide_price method, which is called at
    each pricing review interval. The policy receives the current price
    and the full demand history observed so far (as a Python list of
    floats) and returns the new price for the next interval.

    The policy is stateless across calls; any state it needs (such as
    when the last price change happened) is reconstructed from the
    inputs each time. This keeps the interface simple and makes the
    policy easy to test in isolation.

    Attributes
    ----------
    config : PricingPolicyConfig
        The shared configuration object.
    name : str
        Human-readable policy name for logging and result records.
    """

    def __init__(self, config: PricingPolicyConfig, name: str):
        self.config = config
        self.name = name

    def decide_price(
        self,
        period: int,
        demand_history: List[float],
        current_price: float,
    ) -> float:
        """Return the new price for the next pricing interval.

        Parameters
        ----------
        period : int
            The current simulation period. Used by some policies that
            care about elapsed time.
        demand_history : list of float
            All realized demand observations from period 0 up to (but
            not including) the current period. The most recent entry
            is at index -1.
        current_price : float
            The price currently in effect.

        Returns
        -------
        float
            The new price. Returning current_price means no change.
        """
        raise NotImplementedError("Subclass must implement decide_price")

    def _compute_demand_shift(
        self,
        demand_history: List[float],
    ) -> Optional[float]:
        """Compute the recent-vs-baseline demand shift factor.

        Returns the ratio of mean demand in the recent_window to mean
        demand in the baseline_window. Returns None if there is not
        enough history to compute the comparison or if the baseline
        is too small to give a meaningful ratio.

        The recent window is the last recent_window observations. The
        baseline window is the recent_window-to-(recent_window+baseline_window)
        observations counting back from the present, so the two windows
        do not overlap.
        """
        cfg = self.config
        total_needed = cfg.recent_window + cfg.baseline_window
        if len(demand_history) < total_needed:
            return None

        recent = np.asarray(demand_history[-cfg.recent_window:], dtype=float)
        baseline = np.asarray(
            demand_history[-total_needed:-cfg.recent_window],
            dtype=float,
        )

        recent_mean = float(recent.mean())
        baseline_mean = float(baseline.mean())

        if baseline_mean < 1e-9:
            # Baseline demand is essentially zero. Ratio is undefined;
            # signal "no decision possible" by returning None.
            return None

        return recent_mean / baseline_mean

    def _apply_price_adjustment(
        self,
        current_price: float,
        shift_factor: float,
    ) -> float:
        """Apply the constant-volume price adjustment formula.

        Returns the new price obtained by raising the shift_factor to
        the power of one over elasticity and multiplying by the current
        price. Caps the price change at max_price_change to prevent
        runaway moves from extreme observed shifts.

        For shift_factor > 1 (demand up), the new price is above the
        current price. For shift_factor < 1 (demand down), the new
        price is below the current price. For shift_factor == 1 the
        price is unchanged.
        """
        # Constant-volume pricing: adjust price so that realized demand
        # returns to baseline level under the elasticity model.
        raw_new_price = current_price * (shift_factor ** (1.0 / self.config.elasticity))

        # Cap the change at max_price_change in either direction.
        max_factor = 1.0 + self.config.max_price_change
        min_factor = 1.0 - self.config.max_price_change

        capped_factor = max(min_factor, min(max_factor,
                                              raw_new_price / current_price))
        return current_price * capped_factor


# =========================================================================
# CONCRETE POLICY: NO PRICING (STATIC BASELINE)
# =========================================================================

class NoPricingPolicy(PricingPolicy):
    """The static-pricing baseline. Never changes price.

    This policy ignores demand observations entirely and always returns
    the current price unchanged. Useful as the worst-case baseline that
    isolates the value of dynamic pricing in general (relative to no
    pricing at all). Comparing more sophisticated policies against this
    baseline tells us whether ANY pricing mechanism beats holding price
    constant.

    The policy still receives the same arguments as the others to keep
    the simulator-facing interface uniform.
    """

    def __init__(self, config: PricingPolicyConfig):
        super().__init__(config=config, name="no_pricing")

    def decide_price(
        self,
        period: int,
        demand_history: List[float],
        current_price: float,
    ) -> float:
        # The static-pricing policy never adjusts price.
        return current_price


# =========================================================================
# CONCRETE POLICY: NAIVE REACTIVE
# =========================================================================

class NaiveReactivePolicy(PricingPolicy):
    """Reactive pricing without persistence discrimination.

    This policy compares recent demand against a baseline window and
    adjusts price proportionally to the observed shift, regardless of
    whether the shift is persistent or transient. It represents a
    typical operations manager who reacts to whatever the trailing data
    shows without sophisticated signal processing.

    Comparing against this baseline isolates the value of the formula's
    persistence-discrimination capability beyond the value of dynamic
    pricing in general. If phi-gated outperforms naive reactive, the
    persistence-discrimination is providing value beyond what reactive
    pricing alone provides. If they perform similarly, persistence
    discrimination is not adding value beyond reactive pricing.
    """

    def __init__(self, config: PricingPolicyConfig):
        super().__init__(config=config, name="naive_reactive")

    def decide_price(
        self,
        period: int,
        demand_history: List[float],
        current_price: float,
    ) -> float:
        shift_factor = self._compute_demand_shift(demand_history)
        if shift_factor is None:
            return current_price

        # If the shift is below the minimum threshold, hold price.
        # This prevents the policy from constantly fiddling with price
        # in response to small period-to-period noise.
        if abs(shift_factor - 1.0) < self.config.min_change_threshold:
            return current_price

        # Apply the constant-volume price adjustment. Note that this
        # naive policy uses the SAME formula as phi-gated for the
        # adjustment; the only difference between the policies is the
        # decision of WHEN to act, not the adjustment magnitude.
        return self._apply_price_adjustment(current_price, shift_factor)


# =========================================================================
# CONCRETE POLICY: PHI-GATED (THE PROPOSED MECHANISM)
# =========================================================================

class PhiGatedPolicy(PricingPolicy):
    """The persistence-discriminating pricing policy.

    Uses the OLS estimator to compute the AR(1) persistence parameter
    from recent demand history. Adjusts price only if both (a) the
    demand shift exceeds the minimum threshold and (b) the persistence
    estimate exceeds the engagement threshold. The persistence test
    ensures the policy reacts only to genuinely persistent demand
    shifts and ignores transient noise.

    This is the bidirectional early-warning policy. The same algorithm
    raises prices when demand persists upward and cuts prices when
    demand persists downward, because phi measures persistence
    regardless of direction. The downward case is operationally most
    important because it acts as an early warning for demand collapse,
    letting the retailer act before competitors using reactive systems
    can detect the decline.

    The asymmetric variant (phi_threshold_up != phi_threshold_down)
    reflects the operational reality that price cuts are harder to
    reverse than price increases. The default symmetric variant uses
    the same threshold for both directions.
    """

    def __init__(self, config: PricingPolicyConfig, name: str = "phi_gated"):
        super().__init__(config=config, name=name)

    def decide_price(
        self,
        period: int,
        demand_history: List[float],
        current_price: float,
    ) -> float:
        shift_factor = self._compute_demand_shift(demand_history)
        if shift_factor is None:
            return current_price

        # Magnitude check. If the demand shift is below the minimum
        # threshold, hold price even if the persistence is high. This
        # prevents the policy from making price changes based on tiny
        # persistent shifts that do not justify the operational cost.
        if abs(shift_factor - 1.0) < self.config.min_change_threshold:
            return current_price

        # Persistence check. Compute phi from the recent demand window
        # and compare against the appropriate threshold. The threshold
        # depends on the direction of the shift: shifts up use
        # phi_threshold_up; shifts down use phi_threshold_down. For the
        # symmetric variant these thresholds are equal; for the
        # asymmetric variant phi_threshold_down is more stringent.
        cfg = self.config
        phi_window = demand_history[-cfg.phi_estimation_window:]
        if len(phi_window) < 3:
            return current_price
        phi = estimate_phi_ols(phi_window)

        is_upward = shift_factor > 1.0
        threshold = cfg.phi_threshold_up if is_upward else cfg.phi_threshold_down

        if phi < threshold:
            # Persistence is too low; the observed shift is more likely
            # transient than persistent. Hold price.
            return current_price

        # Both checks passed. Apply the price adjustment.
        return self._apply_price_adjustment(current_price, shift_factor)


# =========================================================================
# POLICY FACTORY REGISTRY
# =========================================================================
# Same factory-and-registry pattern as phase2_6_policy_scenarios for
# consistency. The runner can look up a policy by name and instantiate
# it with the appropriate config.

def make_no_pricing(config: PricingPolicyConfig) -> NoPricingPolicy:
    """Factory for the static-pricing baseline."""
    return NoPricingPolicy(config=config)


def make_naive_reactive(config: PricingPolicyConfig) -> NaiveReactivePolicy:
    """Factory for the naive reactive baseline."""
    return NaiveReactivePolicy(config=config)


def make_phi_gated_symmetric(config: PricingPolicyConfig) -> PhiGatedPolicy:
    """Factory for the symmetric phi-gated policy.

    Uses the same phi threshold for both upward and downward decisions.
    The symmetric variant is the cleanest test of the bidirectional
    mechanism because asymmetry between directions is purely an
    operational consideration that the simulator does not capture.
    """
    # Force symmetric thresholds by overriding phi_threshold_down to
    # match phi_threshold_up. This is a defensive copy that does not
    # mutate the caller's config.
    sym_config = PricingPolicyConfig(
        elasticity=config.elasticity,
        review_interval=config.review_interval,
        recent_window=config.recent_window,
        baseline_window=config.baseline_window,
        min_change_threshold=config.min_change_threshold,
        phi_estimation_window=config.phi_estimation_window,
        phi_threshold_up=config.phi_threshold_up,
        phi_threshold_down=config.phi_threshold_up,  # forced match
        max_price_change=config.max_price_change,
    )
    return PhiGatedPolicy(config=sym_config, name="phi_gated_symmetric")


def make_phi_gated_asymmetric(config: PricingPolicyConfig) -> PhiGatedPolicy:
    """Factory for the asymmetric phi-gated policy.

    Uses different phi thresholds for upward versus downward decisions.
    The asymmetric variant reflects the operational reality that price
    cuts are harder to reverse than price increases. By default upward
    decisions use phi_threshold_up=0.6 and downward decisions use
    phi_threshold_down=0.75 (more conservative).

    If the caller's config already has different up/down thresholds,
    those are preserved. If the caller's config has equal thresholds
    (symmetric default), this factory bumps the down threshold to 0.75
    to enforce the asymmetric behavior.
    """
    if config.phi_threshold_up == config.phi_threshold_down:
        # Default asymmetric values: 0.6 for raises, 0.75 for cuts.
        asym_config = PricingPolicyConfig(
            elasticity=config.elasticity,
            review_interval=config.review_interval,
            recent_window=config.recent_window,
            baseline_window=config.baseline_window,
            min_change_threshold=config.min_change_threshold,
            phi_estimation_window=config.phi_estimation_window,
            phi_threshold_up=0.6,
            phi_threshold_down=0.75,
            max_price_change=config.max_price_change,
        )
    else:
        # Caller has already configured asymmetric thresholds; honor them.
        asym_config = config
    return PhiGatedPolicy(config=asym_config, name="phi_gated_asymmetric")


# Registry mapping policy name (string used in scenarios) to factory.
PRICING_POLICY_REGISTRY: Dict[str, Callable[..., PricingPolicy]] = {
    "no_pricing":            make_no_pricing,
    "naive_reactive":        make_naive_reactive,
    "phi_gated_symmetric":   make_phi_gated_symmetric,
    "phi_gated_asymmetric":  make_phi_gated_asymmetric,
}


PRICING_POLICY_NAMES = tuple(PRICING_POLICY_REGISTRY.keys())


def list_pricing_policies() -> list:
    """Return the list of registered pricing policy names."""
    return list(PRICING_POLICY_REGISTRY.keys())


def make_pricing_policy(
    name: str,
    config: Optional[PricingPolicyConfig] = None,
) -> PricingPolicy:
    """Construct a pricing policy by name from the registry.

    Parameters
    ----------
    name : str
        One of the names in PRICING_POLICY_NAMES.
    config : PricingPolicyConfig, optional
        The configuration to use. If None, a default config is created.

    Returns
    -------
    PricingPolicy
        An instantiated pricing policy.
    """
    if name not in PRICING_POLICY_REGISTRY:
        raise KeyError(
            f"Pricing policy '{name}' not in registry. "
            f"Known: {sorted(PRICING_POLICY_REGISTRY.keys())}"
        )
    if config is None:
        config = PricingPolicyConfig()
    return PRICING_POLICY_REGISTRY[name](config)


# =========================================================================
# SELF-TEST
# =========================================================================

def _self_test():
    """Verify the pricing policies behave correctly across regimes.

    Tests cover:
      1. OLS estimator on known AR(1) processes recovers the true phi
      2. NoPricingPolicy never changes price
      3. NaiveReactivePolicy responds to shifts but ignores small noise
      4. PhiGatedPolicy holds price when shift is small
      5. PhiGatedPolicy holds price when phi is below threshold
      6. PhiGatedPolicy adjusts price when both conditions met
      7. PhiGatedPolicy responds bidirectionally (up and down)
      8. Asymmetric variant uses different thresholds for up vs down
      9. Max price change cap prevents runaway moves
    """
    print("=" * 60)
    print("Phase 2.7 pricing policies self-test")
    print("=" * 60)

    # --- Test 1: OLS estimator on known AR(1) processes ---
    print("\nTest 1: OLS estimator recovers known phi")
    rng = np.random.default_rng(42)
    for true_phi in [0.0, 0.3, 0.6, 0.85]:
        # Generate a long AR(1) series with stationary variance 1.0.
        sigma_eps = np.sqrt(1.0 - true_phi ** 2)
        n = 2000
        d = np.zeros(n)
        d[0] = rng.normal(0.0, 1.0)
        for t in range(1, n):
            d[t] = true_phi * d[t-1] + rng.normal(0.0, sigma_eps)
        # Add a positive mean so the test mimics realistic demand.
        d = d + 10.0
        est_phi = estimate_phi_ols(d.tolist())
        print(f"  true_phi={true_phi:.2f} -> estimated={est_phi:+.3f}  "
              f"{'OK' if abs(est_phi - true_phi) < 0.05 else 'wide'}")

    # --- Test 2: NoPricingPolicy never changes price ---
    print("\nTest 2: NoPricingPolicy never changes price")
    cfg = PricingPolicyConfig()
    policy = NoPricingPolicy(cfg)
    # Even with massive demand swings, price should not change.
    fake_history = [10.0] * 100 + [50.0] * 100  # huge upward shift
    new_price = policy.decide_price(period=200, demand_history=fake_history,
                                       current_price=1.0)
    print(f"  baseline price=1.0 with huge demand shift -> new={new_price:.4f}  "
          f"{'OK' if new_price == 1.0 else 'FAIL'}")
    assert new_price == 1.0

    # --- Test 3: NaiveReactivePolicy responds to shifts ---
    print("\nTest 3: NaiveReactivePolicy responds to shifts")
    cfg = PricingPolicyConfig(elasticity=1.5, recent_window=20, baseline_window=60)
    policy = NaiveReactivePolicy(cfg)

    # Setup: baseline of 80 periods at demand=10, then 20 periods at demand=12
    # (20% upward shift). Naive policy should raise price.
    history_up = [10.0] * 60 + [12.0] * 20
    new_price = policy.decide_price(period=80, demand_history=history_up,
                                       current_price=1.0)
    expected = 1.0 * (12.0 / 10.0) ** (1.0 / 1.5)
    print(f"  20% up shift, e=1.5 -> price={new_price:.4f} "
          f"(expected ~{expected:.4f})  "
          f"{'OK' if abs(new_price - expected) < 0.001 else 'FAIL'}")
    assert abs(new_price - expected) < 0.001

    # Symmetric: 20% downward shift should drop price.
    history_dn = [10.0] * 60 + [8.0] * 20
    new_price_dn = policy.decide_price(period=80, demand_history=history_dn,
                                          current_price=1.0)
    expected_dn = 1.0 * (8.0 / 10.0) ** (1.0 / 1.5)
    print(f"  20% down shift, e=1.5 -> price={new_price_dn:.4f} "
          f"(expected ~{expected_dn:.4f})  "
          f"{'OK' if abs(new_price_dn - expected_dn) < 0.001 else 'FAIL'}")
    assert abs(new_price_dn - expected_dn) < 0.001

    # Small shift below threshold should not change price.
    history_small = [10.0] * 60 + [10.2] * 20  # 2% shift
    new_price_small = policy.decide_price(period=80, demand_history=history_small,
                                             current_price=1.0)
    print(f"  2% shift (below 5% threshold) -> price={new_price_small:.4f}  "
          f"{'OK' if new_price_small == 1.0 else 'FAIL'}")
    assert new_price_small == 1.0

    # --- Test 4: PhiGatedPolicy holds price when phi is low ---
    print("\nTest 4: PhiGatedPolicy holds price when phi is low (transient noise)")
    cfg = PricingPolicyConfig(elasticity=1.5)
    policy = PhiGatedPolicy(cfg)

    # Build a history with low persistence (essentially IID) but with
    # a recent upward shift. The shift exists but phi is low, so the
    # policy should hold price.
    rng = np.random.default_rng(42)
    iid_baseline = list(rng.normal(10.0, 2.0, size=60))
    iid_recent = list(rng.normal(12.0, 2.0, size=20))  # shift in mean only
    history_iid = iid_baseline + iid_recent
    new_price = policy.decide_price(period=80, demand_history=history_iid,
                                       current_price=1.0)
    print(f"  20% mean shift in IID stream (low phi) -> price={new_price:.4f}  "
          f"{'OK' if new_price == 1.0 else 'price moved (phi may be > threshold)'}")
    # Note: this test is probabilistic. With very long IID streams phi is
    # essentially 0, but with 80 samples there is sample variation. We
    # expect price to NOT change but it is not strictly guaranteed.

    # --- Test 5: PhiGatedPolicy adjusts price when phi is high ---
    print("\nTest 5: PhiGatedPolicy adjusts price when phi is high (real shift)")
    # Build a high-persistence AR(1) series with a clear upward shift.
    true_phi = 0.85
    sigma_eps = np.sqrt(1.0 - true_phi ** 2)
    rng = np.random.default_rng(123)
    series = np.zeros(80)
    series[0] = rng.normal(0.0, 1.0)
    for t in range(1, 60):
        series[t] = true_phi * series[t-1] + rng.normal(0.0, sigma_eps)
    series[:60] += 10.0  # baseline level
    # Now generate the 'recent' window at a higher level
    series[60] = true_phi * (series[59] - 10.0) + rng.normal(0.0, sigma_eps) + 12.0
    for t in range(61, 80):
        series[t] = true_phi * (series[t-1] - 12.0) + rng.normal(0.0, sigma_eps) + 12.0

    history_high_phi = series.tolist()
    new_price = policy.decide_price(period=80, demand_history=history_high_phi,
                                       current_price=1.0)
    moved = new_price != 1.0
    print(f"  AR(1) phi=0.85 with 20% level shift -> price={new_price:.4f}  "
          f"{'OK (price moved)' if moved else 'price unchanged'}")

    # --- Test 6: bidirectional response (downward case) ---
    print("\nTest 6: PhiGatedPolicy responds in downward direction too")
    # Mirror of test 5 but with a downward level shift.
    rng = np.random.default_rng(123)
    series_dn = np.zeros(80)
    series_dn[0] = rng.normal(0.0, 1.0)
    for t in range(1, 60):
        series_dn[t] = true_phi * series_dn[t-1] + rng.normal(0.0, sigma_eps)
    series_dn[:60] += 10.0
    series_dn[60] = true_phi * (series_dn[59] - 10.0) + rng.normal(0.0, sigma_eps) + 8.0
    for t in range(61, 80):
        series_dn[t] = true_phi * (series_dn[t-1] - 8.0) + rng.normal(0.0, sigma_eps) + 8.0

    history_dn_phi = series_dn.tolist()
    new_price_dn = policy.decide_price(period=80, demand_history=history_dn_phi,
                                          current_price=1.0)
    moved_dn = new_price_dn != 1.0
    direction_correct = new_price_dn < 1.0 if moved_dn else None
    print(f"  AR(1) phi=0.85 with 20% downward shift -> price={new_price_dn:.4f}  "
          f"{'OK (price cut)' if (moved_dn and direction_correct) else 'unchanged or wrong direction'}")

    # --- Test 7: Asymmetric variant uses different thresholds ---
    print("\nTest 7: Asymmetric variant has different thresholds for up vs down")
    cfg_asym = PricingPolicyConfig(elasticity=1.5)
    policy_asym = make_phi_gated_asymmetric(cfg_asym)
    print(f"  policy.config.phi_threshold_up   = {policy_asym.config.phi_threshold_up}")
    print(f"  policy.config.phi_threshold_down = {policy_asym.config.phi_threshold_down}")
    assert policy_asym.config.phi_threshold_up == 0.6
    assert policy_asym.config.phi_threshold_down == 0.75
    print(f"  asymmetric thresholds correctly set OK")

    # --- Test 8: Symmetric variant has equal thresholds ---
    print("\nTest 8: Symmetric variant has equal thresholds")
    policy_sym = make_phi_gated_symmetric(cfg_asym)
    print(f"  policy.config.phi_threshold_up   = {policy_sym.config.phi_threshold_up}")
    print(f"  policy.config.phi_threshold_down = {policy_sym.config.phi_threshold_down}")
    assert policy_sym.config.phi_threshold_up == policy_sym.config.phi_threshold_down
    print(f"  symmetric thresholds correctly set OK")

    # --- Test 9: Max price change cap ---
    print("\nTest 9: Max price change cap prevents runaway moves")
    cfg_cap = PricingPolicyConfig(elasticity=1.5, max_price_change=0.10)
    policy_cap = NaiveReactivePolicy(cfg_cap)
    # 50% upward shift would normally produce a 30%+ price increase but
    # the cap limits it to 10%.
    history_huge = [10.0] * 60 + [15.0] * 20
    new_price_cap = policy_cap.decide_price(period=80, demand_history=history_huge,
                                                current_price=1.0)
    print(f"  50% up shift with 10% cap -> price={new_price_cap:.4f} "
          f"(expected 1.10)  "
          f"{'OK' if abs(new_price_cap - 1.10) < 0.001 else 'FAIL'}")
    assert abs(new_price_cap - 1.10) < 0.001

    # --- Test 10: Registry lookup ---
    print("\nTest 10: Registry lookup produces all policies")
    for name in PRICING_POLICY_NAMES:
        policy = make_pricing_policy(name)
        print(f"  '{name}' -> {type(policy).__name__} (name={policy.name})  OK")

    # --- Test 11: Validation errors ---
    print("\nTest 11: Validation errors fire correctly")
    try:
        PricingPolicyConfig(elasticity=-0.5)
        print("  FAIL: should have raised on negative elasticity")
        assert False
    except ValueError as e:
        print(f"  Negative elasticity rejected: {str(e)[:60]}...  OK")

    try:
        PricingPolicyConfig(phi_threshold_up=1.5)
        print("  FAIL: should have raised on phi threshold > 1")
        assert False
    except ValueError as e:
        print(f"  Out-of-range phi threshold rejected: {str(e)[:60]}...  OK")

    print("\nAll self-tests completed.")
    print("=" * 60)


if __name__ == '__main__':
    _self_test()
