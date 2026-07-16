"""
Phase 2.6: Spectral Radius Ordering Policy
==========================================

Implements Paper 9's spectral-radius-constrained ordering policy as a stockpyl
Policy subclass, integrated with the Phase 2.5 multi-echelon architecture.

This file contains five algorithm variants that share a single base class:

  1. SR-Paper9-OLS   : Paper 7 Section 2.1 pi-squared-over-two formula + OLS
                        persistence estimator. This is the deployable version.
  2. SR-oracle-phi   : Same formula but receives true phi from the simulator
                        ground truth rather than estimating. Diagnostic tool
                        that separates formula validity from estimator bias.
  3. SR-disabled     : Alpha pinned at 1.0 (no damping). Pure self-calibrating
                        base-stock. Ablation baseline.
  4. naive-damp-0.6  : Alpha pinned at 0.6 (fixed moderate damping). Tests
                        whether the specific rule matters versus any damping.
  5. SR-numerical    : Uses the less-conservative numerical threshold that
                        characterized the pre-April-22 implementation. Tests
                        whether the threshold correction matters.

Paper 7 Section 2.1 formula:
    S          = (1 - phi^W) / (1 - phi)        [cumulative persistence memory]
    alpha_max  = pi^2 / (2 * S)                  [maximum safe aggressiveness]
    alpha_op   = alpha_max * k_star              [operational alpha with margin]

The constant pi^2/2 (approximately 4.9348) arises from a Neimark-Sacker
bifurcation analysis tied to half-wavelength resonance in the ordering
dynamics. The safety factor k_star (typically 0.85 to 0.95, default 0.90)
accounts for estimation uncertainty during regime transitions.

Damping acts on the gap (BS - inventory_position), NOT on the incoming demand.
The ordering rule preserves demand-replacement at alpha equal to 1.0:
    order = demand + alpha * (BS - inventory_position_before_demand)
          = demand + alpha * (BS - inventory_position_passed - demand)
          = demand * (1 - alpha) + alpha * (BS - inventory_position_passed)

At alpha equal to 1.0 this collapses to pure base-stock (BS - IP). At
alpha less than 1.0 demand is always replaced but only a fraction of the
inventory deficit is corrected per period.

Author: JAE with Claude as research assistant
Date: April 24, 2026
"""

from dataclasses import dataclass, field
from typing import Callable, Optional, Union, Dict, List
import numpy as np

from stockpyl.policy import Policy


# =========================================================================
# MODULE-LEVEL HELPER FUNCTIONS
# =========================================================================
# These functions implement the core mathematical operations as module-level
# helpers (rather than class methods) so they can be independently tested
# and reused. This matches the pattern from beergame_validation.py.

PI_SQUARED_OVER_TWO = (np.pi ** 2) / 2.0  # approximately 4.9348
PI_SQUARED = np.pi ** 2                    # approximately 9.8696


def estimate_ar1_persistence(
    demand_history: np.ndarray,
    min_observations: int = 10,
) -> float:
    """Estimate AR(1) persistence parameter phi from observed demand.

    Computes phi as the OLS regression coefficient of x_t on x_{t-1} after
    centering the series. Clipped to [0, 0.999] to avoid numerical issues
    at the stability boundary.

    Special case: if the series has near-zero variance (constant or
    near-constant demand), the OLS denominator becomes near-zero and
    the estimate is numerically unreliable. We return 0.95 in that case
    to reflect that constant demand is maximally persistent. This matches
    the convention from beergame_validation.py Section 4.

    The OLS estimator is known to underreport AR(1) persistence on finite
    samples (Hurwicz bias). For true phi equal to 0.95, OLS typically
    returns mean estimates around 0.67. The Phase 2.6 SR-oracle-phi variant
    bypasses this bias by receiving true phi from the simulator.

    Parameters
    ----------
    demand_history : np.ndarray
        Array of per-period demand observations. Most recent observation
        should be the last element.
    min_observations : int
        Minimum length required; shorter series return 0.5 as a neutral
        prior.

    Returns
    -------
    phi : float
        Estimated AR(1) persistence in [0, 0.999].
    """
    if len(demand_history) < min_observations:
        return 0.5  # neutral prior when data is insufficient

    x = np.asarray(demand_history, dtype=float)
    x_centered = x - x.mean()

    denominator = np.sum(x_centered[:-1] ** 2)
    if denominator < 1e-6:
        # Near-constant series: variance is effectively zero.
        # Return high persistence as the convention for stable signals.
        return 0.95

    numerator = np.sum(x_centered[1:] * x_centered[:-1])
    return float(np.clip(numerator / denominator, 0.0, 0.999))


def cumulative_persistence_memory(phi: float, window: int) -> float:
    """Compute S = (1 - phi^W) / (1 - phi) from Paper 7 Section 2.1.

    S represents how much memory the window captures given the persistence.
    As phi approaches 1.0, S approaches W (the full window length). As phi
    approaches 0, S approaches 1 (only the current observation matters).

    Parameters
    ----------
    phi : float
        AR(1) persistence in [0, 1].
    window : int
        Measurement window length W in periods.

    Returns
    -------
    S : float
        Cumulative persistence memory.
    """
    if abs(1.0 - phi) < 1e-12:
        # Limit as phi approaches 1: S approaches W.
        return float(window)
    return (1.0 - phi ** window) / (1.0 - phi)


def compute_alpha_pi_squared_over_two(
    phi: float,
    window: int,
    k_star: float = 0.90,
) -> float:
    """Paper 7 Section 2.1 closed-form maximum safe ordering aggressiveness.

    Formula:
        S          = (1 - phi^W) / (1 - phi)
        alpha_max  = pi^2 / (2 * S)
        alpha_op   = alpha_max * k_star

    The constant pi^2/2 arises from a Neimark-Sacker bifurcation analysis
    tied to half-wavelength resonance. This is the EXACT analytical result
    from the Measurement Damage Theorem, asymptotically exact for phi near
    1.0 and meaningful guidance for all phi above 0.

    Parameters
    ----------
    phi : float
        AR(1) persistence.
    window : int
        Measurement window length.
    k_star : float
        Safety factor in [0.85, 0.95], default 0.90.

    Returns
    -------
    alpha : float
        Operational ordering aggressiveness. Not yet clipped to [floor, 1.0];
        caller is responsible for clipping.
    """
    S = cumulative_persistence_memory(phi, window)
    if S < 1e-12:
        return 2.0  # effectively unconstrained; caller will clip
    alpha_max = PI_SQUARED_OVER_TWO / S
    return alpha_max * k_star


def compute_alpha_numerical(
    phi: float,
    window: int,
    k_star: float = 1.00,
) -> float:
    """Pre-correction numerical threshold used before the April 22 fix.

    The pre-correction code used the numerical stability threshold
    rho <= 1.0 rather than Paper 7's pi^2/2 closed-form bound. The
    numerical rule is less conservative because it finds alpha at the
    stability boundary WITHOUT margin. This implementation approximates
    that behavior using alpha_max = pi^2 / S (without the /2), which
    produces alpha values roughly double those of the closed-form rule.

    The SR-numerical variant exists specifically to document that the
    threshold change matters. We expect this variant to rarely engage
    damping at typical persistence levels, matching the April 21
    diagnostic finding that alpha stayed at 1.0 for most periods.

    Parameters
    ----------
    phi : float
        AR(1) persistence.
    window : int
        Measurement window length.
    k_star : float
        Safety factor. Default 1.0 (no margin) to match the pre-correction
        behavior.

    Returns
    -------
    alpha : float
        Operational aggressiveness under the numerical threshold.
    """
    S = cumulative_persistence_memory(phi, window)
    if S < 1e-12:
        return 2.0
    alpha_max = PI_SQUARED / S  # NB: without the factor of 2
    return alpha_max * k_star


# =========================================================================
# SPECTRAL RADIUS POLICY CONFIGURATION
# =========================================================================

# Damping mode strings. Each mode corresponds to one of the five variants
# in the Phase 2.6 factorial design.
DAMPING_PAPER9   = 'paper9_pi2'   # Paper 7 Section 2.1 formula (SR-Paper9, SR-oracle-phi)
DAMPING_NUMERICAL = 'numerical'    # Pre-correction numerical rule (SR-numerical)
DAMPING_FIXED    = 'fixed'         # Constant alpha (naive-damp-0.6)
DAMPING_DISABLED = 'disabled'      # Alpha pinned at 1.0 (SR-disabled)

# Estimator mode strings.
ESTIMATOR_OLS    = 'ols'           # OLS regression, realistic deployment
ESTIMATOR_ORACLE = 'oracle'        # Simulator ground truth, diagnostic only


@dataclass
class SpectralRadiusConfig:
    """Configuration parameters for the SpectralRadiusPolicy.

    The five Phase 2.6 variants correspond to five different configurations
    of this dataclass. Factory functions below construct them.
    """

    # ----- Core formula parameters -----
    window: int = 8
    """Measurement window length W in periods. Paper 7 default is 8."""

    k_star: float = 0.90
    """Safety factor in [0.85, 0.95] for the pi^2/2 formula."""

    # ----- Mode selection -----
    damping_mode: str = DAMPING_PAPER9
    """Which alpha computation to use. See DAMPING_* constants."""

    estimator_mode: str = ESTIMATOR_OLS
    """How to obtain persistence phi. See ESTIMATOR_* constants."""

    # ----- Mode-specific parameters -----
    fixed_alpha: float = 0.6
    """Used when damping_mode == DAMPING_FIXED (naive-damp-0.6)."""

    oracle_phi: Union[float, Callable[[int], float], None] = None
    """
    Used when estimator_mode == ESTIMATOR_ORACLE.
    Can be a scalar (constant true phi for whole simulation) or a callable
    that takes the current period and returns the true phi at that period
    (for time-varying persistence experiments).
    """

    # ----- Damping bounds -----
    alpha_floor: float = 0.02
    """Minimum alpha to prevent total ordering paralysis."""

    alpha_ceiling: float = 1.0
    """Maximum alpha; 1.0 corresponds to full base-stock behavior."""

    # ----- Self-calibration parameters -----
    safety_factor_z: float = 1.645
    """Newsvendor safety factor; 1.645 corresponds to 95 percent service."""

    min_obs_for_calibration: int = 15
    """Minimum history length before self-calibration activates."""

    lookback_window: int = 20
    """How far back to look when estimating phi and demand statistics."""


# =========================================================================
# SPECTRAL RADIUS POLICY CLASS
# =========================================================================

class SpectralRadiusPolicy(Policy):
    """Paper 9 spectral-radius-constrained ordering policy.

    This policy subclasses stockpyl's Policy and overrides the base-stock
    order computation. Each period, the policy:

      1. Reads recent demand history from self.node.state_vars.
      2. Obtains the persistence estimate phi (via OLS or oracle).
      3. Computes alpha via the configured damping mode.
      4. Computes a self-calibrating base-stock level from the demand
         history using the newsvendor formula.
      5. Returns a damped order: (1-alpha) * demand + alpha * (BS - IP).

    At alpha equal to 1.0 this reduces to pure self-calibrating base-stock.
    At alpha less than 1.0 the policy always replaces current demand but
    closes only a fraction of the inventory deficit per period.

    State maintained across periods:
      - self.diagnostic_log['alpha'] : per-period alpha values
      - self.diagnostic_log['phi']   : per-period persistence estimates
      - self.diagnostic_log['bs']    : per-period base-stock levels
      - self.diagnostic_log['order'] : per-period order quantities

    These are used for the Phase 2.6 mechanistic validation metrics.

    Parameters
    ----------
    config : SpectralRadiusConfig
        Configuration controlling variant behavior.
    product_idx : int
        Stockpyl product index for reading demand from state_vars.
    node_idx : int
        Stockpyl node index, used for oracle phi provider lookups.
    initial_base_stock : float, optional
        Starting base-stock level used before self-calibration kicks in.
        If None, a conservative default is used.
    **kwargs : dict
        Passed to Policy constructor. Sets type='BS' and a placeholder
        base_stock_level for stockpyl's internal validation.
    """

    def __init__(
        self,
        config: SpectralRadiusConfig,
        product_idx: int,
        node_idx: int,
        initial_base_stock: Optional[float] = None,
        **kwargs,
    ):
        # Stockpyl Policy requires type='BS' and base_stock_level for
        # validation. We set a placeholder that gets overridden dynamically
        # when the policy computes its self-calibrated target.
        kwargs.setdefault('type', 'BS')
        kwargs.setdefault('base_stock_level', initial_base_stock or 30.0)
        super().__init__(**kwargs)

        # Store configuration and identifiers.
        self.config = config
        self.product_idx = product_idx
        self.node_idx = node_idx
        self.initial_base_stock = initial_base_stock or 30.0

        # Per-period diagnostic logs. These are lists that grow by one
        # element per call to _get_order_quantity_base_stock.
        self.diagnostic_log: Dict[str, List[float]] = {
            'alpha': [],
            'phi': [],
            'bs': [],
            'order': [],
            'demand': [],
            'period': [],
        }

        # Running demand statistics for self-calibration. These get
        # updated each period from state_vars.
        self._d_hat: Optional[float] = None  # EWMA demand forecast

    # ---------------------------------------------------------------
    # HELPER: read demand from stockpyl state variables
    # ---------------------------------------------------------------

    def _read_demand_history(self, up_to_period: int) -> np.ndarray:
        """Extract per-period demand at this node for this product.

        Stockpyl stores cumulative demand in state_vars[t].demand_cumul
        as a dict keyed by product index. Per-period demand is the
        difference between consecutive cumulative values. This method
        returns demand for periods [up_to_period - lookback, up_to_period).

        Follows the same pattern as ReactiveRobustPolicy._read_recent_demands
        in phase2_5_stage2_seven_policy_comparison.py.

        Parameters
        ----------
        up_to_period : int
            Return demand for periods strictly before this one.

        Returns
        -------
        np.ndarray
            Array of per-period demand values. Length equals lookback_window
            or up_to_period, whichever is smaller.
        """
        demands = []
        start = max(0, up_to_period - self.config.lookback_window)

        for t_past in range(start, up_to_period):
            if t_past >= len(self.node.state_vars):
                # State variable not yet populated; use 0 as placeholder.
                # This shouldn't happen in normal simulation flow.
                demands.append(0.0)
                continue

            sv_now = self.node.state_vars[t_past]
            sv_prev = (
                self.node.state_vars[t_past - 1]
                if t_past > 0 and t_past - 1 < len(self.node.state_vars)
                else None
            )

            if hasattr(sv_now, 'demand_cumul'):
                d_now = sv_now.demand_cumul.get(self.product_idx, 0.0) or 0.0
                d_prev = (
                    (sv_prev.demand_cumul.get(self.product_idx, 0.0) or 0.0)
                    if sv_prev else 0.0
                )
                demands.append(d_now - d_prev)
            else:
                demands.append(0.0)

        return np.asarray(demands, dtype=float)

    # ---------------------------------------------------------------
    # HELPER: obtain the persistence estimate (OLS or oracle)
    # ---------------------------------------------------------------

    def _get_phi(self, demand_history: np.ndarray, period: int) -> float:
        """Return persistence phi according to the configured estimator.

        In OLS mode, regress demand_history on its one-period lag.
        In oracle mode, consult the configured oracle_phi (scalar or
        callable) and return the true phi from the simulator.

        Parameters
        ----------
        demand_history : np.ndarray
            Recent demand observations.
        period : int
            Current simulation period. Passed to oracle callables for
            time-varying persistence support.

        Returns
        -------
        phi : float
            Persistence value in [0, 0.999].
        """
        if self.config.estimator_mode == ESTIMATOR_OLS:
            return estimate_ar1_persistence(demand_history)

        elif self.config.estimator_mode == ESTIMATOR_ORACLE:
            op = self.config.oracle_phi
            if op is None:
                # Oracle not configured; fall back to OLS. This indicates
                # a configuration error but we don't want to crash a run.
                return estimate_ar1_persistence(demand_history)
            if callable(op):
                return float(np.clip(op(period), 0.0, 0.999))
            return float(np.clip(op, 0.0, 0.999))

        else:
            raise ValueError(
                f"Unknown estimator_mode: {self.config.estimator_mode}"
            )

    # ---------------------------------------------------------------
    # HELPER: compute alpha according to the damping mode
    # ---------------------------------------------------------------

    def _compute_alpha(self, phi: float) -> float:
        """Return ordering aggressiveness alpha per the damping mode.

        Each mode corresponds to one of the Phase 2.6 experimental
        variants. The returned alpha is clipped to [alpha_floor, alpha_ceiling].

        Parameters
        ----------
        phi : float
            Persistence estimate.

        Returns
        -------
        alpha : float
            Clipped operational aggressiveness.
        """
        mode = self.config.damping_mode

        if mode == DAMPING_PAPER9:
            alpha = compute_alpha_pi_squared_over_two(
                phi, self.config.window, self.config.k_star
            )
        elif mode == DAMPING_NUMERICAL:
            alpha = compute_alpha_numerical(
                phi, self.config.window, k_star=1.0
            )
        elif mode == DAMPING_FIXED:
            alpha = self.config.fixed_alpha
        elif mode == DAMPING_DISABLED:
            alpha = 1.0
        else:
            raise ValueError(f"Unknown damping_mode: {mode}")

        # Clip to configured bounds. Most variants need [floor, 1.0] but
        # SR-disabled uses alpha=1.0 exactly and naive-damp uses its own
        # fixed value (which should already be in range).
        return float(np.clip(
            alpha, self.config.alpha_floor, self.config.alpha_ceiling
        ))

    # ---------------------------------------------------------------
    # HELPER: compute self-calibrating base-stock level
    # ---------------------------------------------------------------

    def _compute_base_stock(
        self,
        demand_history: np.ndarray,
    ) -> float:
        """Compute self-calibrating base-stock via the newsvendor formula.

        Standard operations practice:
            BS = mean_demand * lead_time + z * std_demand * sqrt(lead_time)

        The z factor corresponds to a target service level (1.645 for 95%).
        Lead time combines this node's shipment lead time and the order
        lead time from downstream (which is this node's supply lead time).

        This matches the self-calibration in beergame_validation.py and
        what a deployed system would do in real operations. Using self-
        calibration rather than oracle-set base-stock levels is the
        fair-comparison mode where all policies estimate parameters from
        data rather than receiving them as given.

        Parameters
        ----------
        demand_history : np.ndarray
            Recent demand observations.

        Returns
        -------
        bs_level : float
            Self-calibrated base-stock target.
        """
        if len(demand_history) < self.config.min_obs_for_calibration:
            # Not enough data yet; use the initial default.
            return self.initial_base_stock

        mean_d = float(demand_history.mean())
        std_d = float(demand_history.std(ddof=0)) if len(demand_history) > 1 else 1.0

        # Retrieve lead times from the node's configuration.
        # In stockpyl, these are attributes on the node object.
        L_shipment = getattr(self.node, 'shipment_lead_time', 1) or 1
        L_order = getattr(self.node, 'order_lead_time', 0) or 0
        L_total = max(1, int(L_shipment) + int(L_order))

        bs_level = (
            mean_d * L_total
            + self.config.safety_factor_z * std_d * np.sqrt(L_total)
        )
        return max(0.0, bs_level)

    # ---------------------------------------------------------------
    # HELPER: get current period demand from stockpyl state
    # ---------------------------------------------------------------

    def _get_current_period_demand(
        self,
        inventory_position_passed: float,
    ) -> float:
        """Compute this period's demand by reversing stockpyl's subtraction.

        Stockpyl's get_order_quantity computes:
            inventory_position_passed = IP_before_demand - demand
        Therefore:
            demand = IP_before_demand - inventory_position_passed

        IP_before_demand is available from self.node.state_vars_current.

        Parameters
        ----------
        inventory_position_passed : float
            The inventory_position argument stockpyl passed to
            _get_order_quantity_base_stock, AFTER demand subtraction.

        Returns
        -------
        demand : float
            Current period's incoming demand.
        """
        try:
            IP_before_demand = self.node.state_vars_current.inventory_position(
                product=self.product_idx, exclude_earmarked_units=True
            )
            return float(IP_before_demand - inventory_position_passed)
        except Exception:
            # If state_vars_current isn't available (e.g. during initial
            # setup), fall back to zero demand. This shouldn't happen in
            # normal simulation but we don't want to crash.
            return 0.0

    # ---------------------------------------------------------------
    # MAIN OVERRIDE: the damped-base-stock order quantity
    # ---------------------------------------------------------------

    def _get_order_quantity_base_stock(
        self,
        inventory_position: float,
    ) -> float:
        """Compute order quantity using Paper 9's damped base-stock rule.

        The formula, derived from Paper 7 Section 2.1, is:
            order = demand + alpha * (BS - IP_before_demand)

        Which, because inventory_position = IP_before_demand - demand,
        simplifies to:
            order = (1 - alpha) * demand + alpha * (BS - inventory_position)

        At alpha equal to 1.0 this collapses to BS - inventory_position,
        which is the standard base-stock rule. At alpha less than 1.0
        the policy replaces demand fully but closes only alpha fraction
        of the inventory gap each period. This is the damping mechanism
        that the Measurement Damage Theorem predicts stabilizes ordering
        against regime transitions.

        Parameters
        ----------
        inventory_position : float
            Stockpyl-computed inventory position AFTER demand subtraction.

        Returns
        -------
        order_quantity : float
            Non-negative damped-base-stock order.
        """
        # Determine current period. Stockpyl exposes this on the network.
        try:
            period = int(self.node.network.period)
        except (AttributeError, TypeError):
            period = 0

        # Step 1: read demand history from state_vars.
        demand_history = self._read_demand_history(period)

        # Step 2: obtain persistence estimate (OLS or oracle).
        phi = self._get_phi(demand_history, period)

        # Step 3: compute alpha according to damping mode.
        alpha = self._compute_alpha(phi)

        # Step 4: compute self-calibrating base-stock level.
        bs_level = self._compute_base_stock(demand_history)

        # Step 5: get current period's demand for the ordering formula.
        demand = self._get_current_period_demand(inventory_position)

        # Step 6: apply Paper 9's damped base-stock rule.
        # order = (1 - alpha) * demand + alpha * (BS - inventory_position)
        order = (1.0 - alpha) * demand + alpha * (bs_level - inventory_position)
        order = max(0.0, order)

        # Step 7: log diagnostics for Phase 2.6 validation analysis.
        self.diagnostic_log['period'].append(period)
        self.diagnostic_log['phi'].append(phi)
        self.diagnostic_log['alpha'].append(alpha)
        self.diagnostic_log['bs'].append(bs_level)
        self.diagnostic_log['demand'].append(demand)
        self.diagnostic_log['order'].append(order)

        # Update the Policy's base_stock_level attribute so external code
        # that inspects it sees the current calibrated value. (Stockpyl
        # doesn't need this for ordering; it's purely for introspection.)
        self._base_stock_level = bs_level

        return order


# =========================================================================
# FACTORY FUNCTIONS FOR THE FIVE PHASE 2.6 VARIANTS
# =========================================================================

def make_sr_paper9_ols(
    product_idx: int,
    node_idx: int,
    initial_base_stock: float = 30.0,
    window: int = 8,
    k_star: float = 0.90,
) -> SpectralRadiusPolicy:
    """Construct the SR-Paper9-OLS variant (the deployable version).

    Uses Paper 7 Section 2.1's pi-squared-over-two formula with the OLS
    persistence estimator. This is the implementation that would be
    published if Phase 2.6 validates the theory under realistic conditions.
    """
    config = SpectralRadiusConfig(
        window=window,
        k_star=k_star,
        damping_mode=DAMPING_PAPER9,
        estimator_mode=ESTIMATOR_OLS,
    )
    return SpectralRadiusPolicy(
        config=config,
        product_idx=product_idx,
        node_idx=node_idx,
        initial_base_stock=initial_base_stock,
    )


def make_sr_oracle_phi(
    product_idx: int,
    node_idx: int,
    oracle_phi: Union[float, Callable[[int], float]],
    initial_base_stock: float = 30.0,
    window: int = 8,
    k_star: float = 0.90,
) -> SpectralRadiusPolicy:
    """Construct the SR-oracle-phi diagnostic variant.

    Uses Paper 7's formula but receives true phi from the simulator
    ground truth. This isolates formula validity from OLS estimator
    bias and provides the cleanest possible test of whether the formula
    produces operational value.

    The oracle_phi parameter can be a scalar (constant true phi for the
    whole simulation) or a callable that takes the current period and
    returns true phi at that period (for time-varying persistence).
    """
    config = SpectralRadiusConfig(
        window=window,
        k_star=k_star,
        damping_mode=DAMPING_PAPER9,
        estimator_mode=ESTIMATOR_ORACLE,
        oracle_phi=oracle_phi,
    )
    return SpectralRadiusPolicy(
        config=config,
        product_idx=product_idx,
        node_idx=node_idx,
        initial_base_stock=initial_base_stock,
    )


def make_sr_disabled(
    product_idx: int,
    node_idx: int,
    initial_base_stock: float = 30.0,
) -> SpectralRadiusPolicy:
    """Construct the SR-disabled ablation baseline.

    Alpha is pinned at 1.0 so no damping is applied. The policy behaves
    as pure self-calibrating base-stock, which is functionally equivalent
    to what a modern ERP system with exponential-smoothing demand forecast
    and newsvendor safety stock would produce. This variant isolates the
    contribution of the SR damping mechanism: any performance difference
    between SR-Paper9-OLS and SR-disabled is attributable to damping.
    """
    config = SpectralRadiusConfig(
        damping_mode=DAMPING_DISABLED,
        estimator_mode=ESTIMATOR_OLS,  # phi not used, but must be valid
    )
    return SpectralRadiusPolicy(
        config=config,
        product_idx=product_idx,
        node_idx=node_idx,
        initial_base_stock=initial_base_stock,
    )


def make_naive_damp(
    product_idx: int,
    node_idx: int,
    fixed_alpha: float = 0.6,
    initial_base_stock: float = 30.0,
) -> SpectralRadiusPolicy:
    """Construct the naive-damp variant with fixed alpha.

    Alpha is held constant at the specified value (default 0.6) regardless
    of demand conditions. Tests whether the specific pi-squared-over-two
    rule matters beyond merely applying "some damping." If SR-Paper9-OLS
    outperforms naive-damp-0.6, the theoretically-derived damping level
    matters specifically; if not, any moderate damping produces similar
    results and the theoretical contribution is weaker than claimed.
    """
    config = SpectralRadiusConfig(
        damping_mode=DAMPING_FIXED,
        estimator_mode=ESTIMATOR_OLS,  # phi not used
        fixed_alpha=fixed_alpha,
    )
    return SpectralRadiusPolicy(
        config=config,
        product_idx=product_idx,
        node_idx=node_idx,
        initial_base_stock=initial_base_stock,
    )


def make_sr_numerical(
    product_idx: int,
    node_idx: int,
    initial_base_stock: float = 30.0,
    window: int = 8,
) -> SpectralRadiusPolicy:
    """Construct the SR-numerical variant using the pre-correction threshold.

    Uses the less-conservative numerical threshold that characterized
    the implementation before the April 22 correction. Expected to rarely
    engage damping at typical persistence levels, which is why Phase 2.6
    includes this variant: to document that the threshold change matters.
    """
    config = SpectralRadiusConfig(
        window=window,
        damping_mode=DAMPING_NUMERICAL,
        estimator_mode=ESTIMATOR_OLS,
    )
    return SpectralRadiusPolicy(
        config=config,
        product_idx=product_idx,
        node_idx=node_idx,
        initial_base_stock=initial_base_stock,
    )


# =========================================================================
# SELF-TEST (runs when file is executed directly)
# =========================================================================

def _self_test():
    """Verify the module's mathematical helpers match expected values.

    This does NOT test the Policy class (which requires a stockpyl network);
    it only tests the standalone formula functions. Integration tests against
    the full Phase 2.5 architecture are in a separate file.
    """
    print("=" * 60)
    print("SpectralRadiusPolicy module self-test")
    print("=" * 60)

    # Test 1: formula verification at phi=0.95, W=8.
    # Expected values from beergame_validation.py runtime check:
    #   S(0.95, 8) = 6.7318
    #   alpha_max = 0.7330
    #   with k*=0.9 : 0.6597
    S = cumulative_persistence_memory(0.95, 8)
    alpha_max = PI_SQUARED_OVER_TWO / S
    alpha_with_k = alpha_max * 0.90
    print(f"\nTest 1: Paper 7 formula at phi=0.95, W=8")
    print(f"  S         = {S:.4f}   (expected 6.7318)")
    print(f"  alpha_max = {alpha_max:.4f}   (expected 0.7330)")
    print(f"  w/ k*=0.9 = {alpha_with_k:.4f}   (expected 0.6597)")
    assert abs(S - 6.7318) < 0.01, "S mismatch"
    assert abs(alpha_max - 0.7330) < 0.01, "alpha_max mismatch"

    # Test 2: table of values at standard W=8, k*=0.90
    print(f"\nTest 2: alpha values across phi range (W=8, k*=0.90)")
    print(f"  {'phi':>6s}  {'S':>8s}  {'alpha_max':>10s}  {'alpha_op':>10s}  {'clipped':>8s}")
    for phi in [0.50, 0.70, 0.82, 0.85, 0.90, 0.95, 0.99]:
        alpha_raw = compute_alpha_pi_squared_over_two(phi, 8, 0.90)
        alpha_clipped = min(1.0, max(0.02, alpha_raw))
        S_val = cumulative_persistence_memory(phi, 8)
        alpha_max = PI_SQUARED_OVER_TWO / S_val
        print(f"  {phi:6.2f}  {S_val:8.3f}  {alpha_max:10.3f}  {alpha_raw:10.3f}  {alpha_clipped:8.3f}")

    # Test 3: numerical variant at same phi values
    print(f"\nTest 3: numerical variant alpha values (W=8, k*=1.0)")
    print(f"  {'phi':>6s}  {'alpha_raw':>10s}  {'alpha_clip':>10s}")
    for phi in [0.50, 0.70, 0.85, 0.90, 0.95, 0.99]:
        alpha_raw = compute_alpha_numerical(phi, 8, 1.0)
        alpha_clip = min(1.0, max(0.02, alpha_raw))
        print(f"  {phi:6.2f}  {alpha_raw:10.3f}  {alpha_clip:10.3f}")

    # Test 4: OLS estimator on synthetic AR(1) data
    print(f"\nTest 4: OLS estimator on synthetic AR(1)")
    np.random.seed(42)
    for true_phi in [0.3, 0.6, 0.85, 0.95]:
        n = 100
        x = np.zeros(n)
        x[0] = 10.0
        for t in range(1, n):
            x[t] = 5.0 + true_phi * (x[t-1] - 5.0) + np.random.normal(0, 1)
        est_phi = estimate_ar1_persistence(x)
        bias = est_phi - true_phi
        print(f"  true phi={true_phi:.2f}, n={n}, OLS estimate={est_phi:.4f}, bias={bias:+.4f}")

    print("\nAll self-tests completed.")
    print("=" * 60)


if __name__ == '__main__':
    _self_test()
