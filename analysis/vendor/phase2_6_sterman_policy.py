"""
Phase 2.6: Sterman Behavioral Ordering Policy
=============================================

Implements Sterman's (1989) anchor-and-adjust ordering heuristic as a stockpyl
Policy subclass, integrated with the Phase 2.5 multi-echelon architecture.

Why this exists
---------------

Phase 2.6's original branching_toggle infrastructure tested the Spectral
Radius formula against rational base-stock co-players, which produced the
"formula ties optimum, no benefit" result that we now understand was the
predicted behavior in stable regimes. The Master Project Plan (April 22)
explicitly listed Sterman behavioral as one of six benchmark policies,
identifying it as "the worst-case baseline representing untrained human
ordering." That dimension was lost during phase progression. This file
re-introduces it so the Spectral Radius formula can be tested against
the irrational human-behavioral co-players it was designed to outperform.

Why it works
------------

The Sterman formula (anchor-and-adjust) is:

    d_hat_t = theta * AO_t + (1 - theta) * d_hat_{t-1}        [EWMA forecast]
    order_t = max(0, d_hat_t + alpha_S  * (target_IL - IL_t)
                              + alpha_SL * (target_OO - OO_t))

where AO is the current period's incoming order, IL is the current
inventory level, OO is the current outstanding orders, and the parameters
alpha_S and alpha_SL weight responses to inventory and supply-line gaps.

The behavioral signature of Sterman ordering is alpha_SL substantially
smaller than alpha_S, meaning humans under-weight orders that have already
been placed but not yet received. When inventory drops below target the
policy panic-orders to close the gap, fails to give full credit to pipeline
orders already in flight, then ends up with massive overstock when those
pipeline orders arrive. This is the textbook bullwhip mechanism that the
formula is designed to dampen.

Reference implementation
------------------------

This port mirrors the Sterman implementation in beergame_validation.py
(located in the Archive folder). The reference implementation produced
the April 21 publication-grade results: bullwhip ratios of 5.57, 19.53,
57.77, and 59.34 across the four tiers when all stages used Sterman, and
50 to 70 percent cost reduction when Spectral Radius replaced Sterman
at one or more positions. Those results exceeded the Oroojlooyjadid et al.
2020 MSOM DQN benchmark on the irrational-coplayer comparison.

Parameter conventions
---------------------

The reference implementation used names alpha and beta for the inventory
and supply-line weights respectively. This port uses alpha_S and alpha_SL
to match the more common convention in the academic literature (Sterman
1989, Croson and Donohue 2003, Croson, Donohue, Katok and Sterman 2014).
The numerical defaults are unchanged from the reference: alpha_S equal
to 0.5, alpha_SL equal to 0.2, theta equal to 0.2.

Author: JAE with Claude as research assistant
Date: April 27, 2026
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
import numpy as np

from stockpyl.policy import Policy


# =========================================================================
# CONFIGURATION DATACLASS
# =========================================================================

@dataclass
class StermanConfig:
    """Configuration parameters for the StermanPolicy.

    The numerical defaults match beergame_validation.py and are consistent
    with the typical literature values for behavioral ordering experiments.
    The supply-line-gap weight alpha_SL being smaller than the inventory-gap
    weight alpha_S is the behavioral signature that produces bullwhip; do
    not change this asymmetry without understanding what the policy is
    intended to model.
    """

    # ----- Anchoring weights -----
    alpha_S: float = 0.5
    """Inventory-gap weight. Higher values mean the policy responds more
    aggressively to inventory deviations from target. Literature standard
    is 0.5; some sources use 0.26 (Sterman 1989) or 0.36 (later studies)."""

    alpha_SL: float = 0.2
    """Supply-line-gap weight. The behavioral signature of Sterman ordering
    is alpha_SL substantially smaller than alpha_S, meaning humans
    under-weight orders already in the pipeline. Literature values range
    from 0.09 to 0.26. Default 0.2 matches beergame_validation.py."""

    # ----- Demand forecast -----
    d_hat_ewma: float = 0.2
    """Exponential smoothing weight on the most recent demand observation.
    The forecast is d_hat_t = theta * AO_t + (1 - theta) * d_hat_{t-1}.
    Lower values mean slower adaptation to demand changes. Default 0.2
    matches beergame_validation.py and is between Sterman (1989) at 0.36
    and slower variants at 0.10."""

    # ----- Target anchor calibration -----
    target_IL_lt_multiplier: float = 1.0
    """Target inventory anchor as multiple of (mean_demand * lead_time).
    A value of 1.0 means the policy targets one lead-time's worth of
    safety stock as inventory. Higher values increase inventory holdings."""

    target_OO_lt_multiplier: float = 1.0
    """Target supply-line anchor as multiple of (mean_demand * lead_time).
    A value of 1.0 means the policy expects the pipeline to hold roughly
    one lead-time's worth of demand."""

    min_obs_for_anchor_calibration: int = 15
    """Minimum number of demand observations before target anchors
    self-calibrate from observed mean demand. Before this threshold,
    initial_target_IL and initial_target_OO are used."""

    # ----- Initial-period defaults -----
    initial_d_hat: Optional[float] = None
    """Starting demand forecast. If None, defaults to the first observed
    AO when AO > 0, or to a placeholder of 4.0 otherwise (matching
    beergame_validation convention for the classic C(4,8) demand mean)."""


# =========================================================================
# STERMAN POLICY CLASS
# =========================================================================

class StermanPolicy(Policy):
    """Sterman's behavioral anchor-and-adjust ordering policy.

    Subclasses stockpyl's Policy and overrides the base-stock order
    computation. Each period the policy:

      1. Reads the current period's incoming demand AO from state_vars.
      2. Updates the EWMA demand forecast d_hat.
      3. Reads the current inventory level IL and outstanding orders OO
         from state_vars.
      4. Computes self-calibrating targets target_IL and target_OO based
         on observed mean demand and lead time (after warmup).
      5. Computes order = max(0, d_hat + alpha_S * (target_IL - IL)
                                       + alpha_SL * (target_OO - OO)).

    State maintained across periods in self.diagnostic_log:
      - period   : per-period simulation period index
      - demand   : per-period observed AO
      - d_hat    : per-period EWMA-smoothed demand forecast
      - IL       : per-period inventory level
      - OO       : per-period outstanding orders
      - target_IL: per-period target inventory anchor
      - target_OO: per-period target supply-line anchor
      - order    : per-period ordered quantity

    These logs are used for the Phase 2.6 mechanistic validation metrics
    and are designed to match the structure of SpectralRadiusPolicy's
    diagnostic_log so the analyzer can treat both policy types uniformly.
    """

    def __init__(
        self,
        config: StermanConfig,
        product_idx: int,
        node_idx: int,
        initial_target_IL: float = 12.0,
        initial_target_OO: float = 16.0,
        **kwargs,
    ):
        # Stockpyl Policy requires type and base_stock_level for its own
        # validation. We use 'BS' as the type and a placeholder base_stock
        # equal to the sum of initial targets. The actual order computation
        # in _get_order_quantity_base_stock ignores stockpyl's notion of
        # base_stock_level entirely and computes from the Sterman formula.
        kwargs.setdefault('type', 'BS')
        kwargs.setdefault(
            'base_stock_level',
            initial_target_IL + initial_target_OO,
        )
        super().__init__(**kwargs)

        # Store configuration and identifiers.
        self.config = config
        self.product_idx = product_idx
        self.node_idx = node_idx
        self.initial_target_IL = initial_target_IL
        self.initial_target_OO = initial_target_OO

        # Diagnostic logs grow by one element per call to
        # _get_order_quantity_base_stock. Match the dict structure used
        # by SpectralRadiusPolicy.diagnostic_log so the analyzer code
        # can treat both policy types uniformly.
        self.diagnostic_log: Dict[str, List[float]] = {
            'period': [],
            'demand': [],
            'd_hat': [],
            'IL': [],
            'OO': [],
            'target_IL': [],
            'target_OO': [],
            'order': [],
        }

        # Internal state: the EWMA demand forecast carries across periods.
        # None means uninitialized; the first observed AO will seed it.
        self._d_hat: Optional[float] = config.initial_d_hat

    # ---------------------------------------------------------------
    # HELPER: read demand history from stockpyl state variables
    # ---------------------------------------------------------------
    # This method mirrors SpectralRadiusPolicy._read_demand_history exactly
    # so both policy types use identical demand-extraction logic. Demand
    # history is needed only for self-calibrating the target anchors after
    # warmup; the per-period AO comes from a different code path (see
    # _get_current_period_demand below).

    def _read_demand_history(self, up_to_period: int) -> np.ndarray:
        """Extract per-period demand at this node for this product.

        Stockpyl stores cumulative demand in state_vars[t].demand_cumul
        as a dict keyed by product index. Per-period demand is the
        difference between consecutive cumulative values. Returns demand
        for periods [max(0, up_to_period - lookback), up_to_period).

        Parameters
        ----------
        up_to_period : int
            Return demand for periods strictly before this one.

        Returns
        -------
        np.ndarray
            Array of per-period demand values.
        """
        # Lookback length matches SpectralRadiusPolicy's behavior: enough
        # history to compute reasonable mean and std for target calibration,
        # without using observations from the distant past that may not
        # reflect current demand level.
        lookback = max(20, self.config.min_obs_for_anchor_calibration)

        demands = []
        start = max(0, up_to_period - lookback)

        for t_past in range(start, up_to_period):
            if t_past >= len(self.node.state_vars):
                # State variable not yet populated. This shouldn't happen
                # in normal simulation flow but we handle it defensively
                # to avoid crashes during edge-case warmup behavior.
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
    # HELPER: read current period's incoming demand (AO)
    # ---------------------------------------------------------------
    # This uses the same trick as SpectralRadiusPolicy._get_current_period_demand:
    # stockpyl computes inventory_position_passed = IP_before_demand - demand,
    # so demand can be reconstructed from the difference. The "AO" in
    # Sterman's formula is exactly this current-period demand.

    def _get_current_period_demand(
        self,
        inventory_position_passed: float,
    ) -> float:
        """Compute this period's incoming demand AO from stockpyl state.

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
        AO : float
            Current period's incoming order. Non-negative.
        """
        try:
            IP_before_demand = self.node.state_vars_current.inventory_position(
                product=self.product_idx, exclude_earmarked_units=True
            )
            return float(max(0.0, IP_before_demand - inventory_position_passed))
        except Exception:
            # Fall back to zero if state_vars_current isn't ready. This
            # shouldn't happen in normal flow but defends against crashes.
            return 0.0

    # ---------------------------------------------------------------
    # HELPER: read current inventory level IL
    # ---------------------------------------------------------------
    # IL is signed: positive means on-hand inventory, negative means
    # backorders. Stockpyl stores this in state_vars_current.inventory_level
    # as a dict keyed by product index. This is exactly what Sterman's
    # formula needs.

    def _read_inventory_level(self) -> float:
        """Read current inventory level IL for this product.

        IL is signed: positive = on-hand units, negative = backorders.
        Sterman's formula uses signed IL because the gap (target - IL)
        is larger when backorders exist, which correctly increases the
        ordering response under stockout conditions.

        Returns
        -------
        IL : float
            Signed inventory level. Returns 0.0 on error.
        """
        try:
            il_dict = self.node.state_vars_current.inventory_level
            return float(il_dict.get(self.product_idx, 0.0) or 0.0)
        except Exception:
            return 0.0

    # ---------------------------------------------------------------
    # HELPER: read current outstanding orders OO
    # ---------------------------------------------------------------
    # OO is the total quantity ordered from upstream that has not yet
    # been received. Stockpyl stores this per-predecessor in
    # state_vars_current.on_order_by_predecessor; we sum across all
    # predecessors to get the aggregate OO that Sterman's formula needs.

    def _read_outstanding_orders(self) -> float:
        """Read total outstanding orders OO for this product.

        OO is the sum across all predecessors of orders placed but not
        yet received. In multi-tier networks a node may have multiple
        predecessors; in serial chains there is exactly one. The
        Sterman formula uses aggregate OO regardless.

        Returns
        -------
        OO : float
            Total outstanding orders. Non-negative. Returns 0.0 on error.
        """
        try:
            oo_by_pred = self.node.state_vars_current.on_order_by_predecessor
            total = 0.0
            for predecessor_idx, prod_dict in oo_by_pred.items():
                if isinstance(prod_dict, dict):
                    total += float(prod_dict.get(self.product_idx, 0.0) or 0.0)
            return max(0.0, total)
        except Exception:
            return 0.0

    # ---------------------------------------------------------------
    # HELPER: compute self-calibrating target anchors
    # ---------------------------------------------------------------
    # In Sterman's original beer game, targets were fixed by the
    # experimenters at literature-standard values. For our multi-product
    # simulation with varied lead times, fixed targets would be wrong
    # for SKUs with different mean demand. We self-calibrate from
    # observed demand history multiplied by lead time, which is what a
    # reasonable supply chain manager would do anyway. Before warmup
    # completes, the initial target values are used.

    def _compute_targets(
        self,
        demand_history: np.ndarray,
    ) -> tuple[float, float]:
        """Compute self-calibrating target_IL and target_OO.

        After enough observations exist, targets scale with observed
        mean demand multiplied by lead time and the configured
        multipliers. Before warmup completes, the initial targets
        passed to __init__ are used.

        Parameters
        ----------
        demand_history : np.ndarray
            Recent demand observations.

        Returns
        -------
        (target_IL, target_OO) : tuple of float
            Calibrated anchor values for this period.
        """
        if len(demand_history) < self.config.min_obs_for_anchor_calibration:
            # Not enough data; use initial defaults.
            return self.initial_target_IL, self.initial_target_OO

        mean_d = float(demand_history.mean())

        # Lead times come from the node's stockpyl configuration.
        # shipment_lead_time is the time for orders to physically arrive
        # from upstream. order_lead_time is the time for orders to be
        # transmitted to upstream (information delay). Total pipeline
        # lead time is the sum of these.
        L_shipment = getattr(self.node, 'shipment_lead_time', 1) or 1
        L_order = getattr(self.node, 'order_lead_time', 0) or 0
        L_total = max(1, int(L_shipment) + int(L_order))

        # Target_IL scales with mean demand and the inventory multiplier.
        # The lead-time factor is implicit because target_IL covers the
        # demand expected during one safety-stock lead time. Default
        # multiplier 1.0 produces target = mean_demand (i.e. one period
        # of demand as inventory cushion).
        target_IL = mean_d * L_total * self.config.target_IL_lt_multiplier

        # Target_OO matches the expected pipeline. With unit pipeline
        # demand of mean_demand per period and L_total periods of pipe,
        # the steady-state pipeline contains mean_demand * L_total units.
        target_OO = mean_d * L_total * self.config.target_OO_lt_multiplier

        return target_IL, target_OO

    # ---------------------------------------------------------------
    # HELPER: update the EWMA demand forecast d_hat
    # ---------------------------------------------------------------

    def _update_d_hat(self, observed_AO: float) -> float:
        """Update the exponentially-smoothed demand forecast.

        The update rule is:
            d_hat_t = theta * AO_t + (1 - theta) * d_hat_{t-1}

        On the first observation, d_hat is initialized from the observed
        AO if positive, or from the configured initial_d_hat if set, or
        from a placeholder of 4.0 (matching beergame_validation convention
        for classic C(4,8) demand mean).

        Parameters
        ----------
        observed_AO : float
            This period's incoming order quantity.

        Returns
        -------
        d_hat : float
            Updated demand forecast.
        """
        theta = self.config.d_hat_ewma

        if self._d_hat is None:
            # Initialization: use observed AO if positive, else fall back
            # to configured initial value or a placeholder.
            if observed_AO > 0:
                self._d_hat = float(observed_AO)
            elif self.config.initial_d_hat is not None:
                self._d_hat = float(self.config.initial_d_hat)
            else:
                # Placeholder default; matches beergame_validation.py
                # convention for classic C(4,8) demand mean of 4.
                self._d_hat = 4.0
        else:
            self._d_hat = (
                theta * observed_AO + (1.0 - theta) * self._d_hat
            )

        return self._d_hat

    # ---------------------------------------------------------------
    # MAIN OVERRIDE: the Sterman anchor-and-adjust order quantity
    # ---------------------------------------------------------------

    def _get_order_quantity_base_stock(
        self,
        inventory_position: float,
    ) -> float:
        """Compute order quantity using Sterman's anchor-and-adjust rule.

        The formula is:
            order = max(0, d_hat + alpha_S * (target_IL - IL)
                                 + alpha_SL * (target_OO - OO))

        where d_hat is the EWMA demand forecast, IL is signed inventory
        level, and OO is total outstanding orders summed across
        predecessors. The behavioral signature is alpha_SL smaller than
        alpha_S, which produces bullwhip because the policy responds
        more aggressively to inventory gaps than to supply-line gaps,
        causing it to over-order when inventory drops below target.

        Parameters
        ----------
        inventory_position : float
            Stockpyl-computed inventory position AFTER demand subtraction.

        Returns
        -------
        order_quantity : float
            Non-negative order quantity per Sterman's formula.
        """
        # Determine current period.
        try:
            period = int(self.node.network.period)
        except (AttributeError, TypeError):
            period = 0

        # Step 1: read current incoming demand AO. Use the same trick as
        # SpectralRadiusPolicy: AO = IP_before_demand - inventory_position_passed.
        observed_AO = self._get_current_period_demand(inventory_position)

        # Step 2: update the EWMA demand forecast d_hat.
        d_hat = self._update_d_hat(observed_AO)

        # Step 3: read current inventory level (signed) and outstanding
        # orders (non-negative) from stockpyl state.
        IL = self._read_inventory_level()
        OO = self._read_outstanding_orders()

        # Step 4: compute target anchors via self-calibration.
        demand_history = self._read_demand_history(period)
        target_IL, target_OO = self._compute_targets(demand_history)

        # Step 5: apply Sterman's anchor-and-adjust formula.
        # The two gap terms drive the ordering response:
        #   alpha_S * (target_IL - IL)  : closes inventory gap
        #   alpha_SL * (target_OO - OO) : closes supply-line gap
        # When alpha_SL < alpha_S, supply-line is under-weighted and
        # bullwhip emerges from over-correction during demand changes.
        order = (
            d_hat
            + self.config.alpha_S * (target_IL - IL)
            + self.config.alpha_SL * (target_OO - OO)
        )
        order = max(0.0, order)

        # Step 6: log diagnostics for Phase 2.6 validation analysis.
        # Match the dict structure used by SpectralRadiusPolicy so the
        # analyzer can treat both policy types uniformly.
        self.diagnostic_log['period'].append(period)
        self.diagnostic_log['demand'].append(observed_AO)
        self.diagnostic_log['d_hat'].append(d_hat)
        self.diagnostic_log['IL'].append(IL)
        self.diagnostic_log['OO'].append(OO)
        self.diagnostic_log['target_IL'].append(target_IL)
        self.diagnostic_log['target_OO'].append(target_OO)
        self.diagnostic_log['order'].append(order)

        return order


# =========================================================================
# FACTORY FUNCTIONS FOR COMMON CONFIGURATIONS
# =========================================================================

def make_sterman_classical(
    product_idx: int,
    node_idx: int,
    initial_target_IL: float = 12.0,
    initial_target_OO: float = 16.0,
) -> StermanPolicy:
    """Construct a Sterman policy with literature-standard parameters.

    Uses alpha_S=0.5, alpha_SL=0.2, theta=0.2 which match the reference
    implementation in beergame_validation.py and produce literature-
    consistent bullwhip behavior on the classic beer game demand patterns.
    Initial targets default to the original Sterman experimental values
    (target_IL=12, target_OO=16) which work for low-demand chains; for
    higher-demand SKUs the self-calibration after warmup will scale these
    up appropriately.
    """
    config = StermanConfig(
        alpha_S=0.5,
        alpha_SL=0.2,
        d_hat_ewma=0.2,
    )
    return StermanPolicy(
        config=config,
        product_idx=product_idx,
        node_idx=node_idx,
        initial_target_IL=initial_target_IL,
        initial_target_OO=initial_target_OO,
    )


def make_sterman_aggressive(
    product_idx: int,
    node_idx: int,
    initial_target_IL: float = 12.0,
    initial_target_OO: float = 16.0,
) -> StermanPolicy:
    """Construct a more aggressive Sterman variant.

    Uses alpha_S=0.5, alpha_SL=0.1, theta=0.36 which represents stronger
    behavioral bias (worse supply-line under-weighting) and faster demand
    forecast adaptation. Useful as a stress-test configuration showing
    what happens when human ordering behavior is more chaotic. May
    produce bullwhip values higher than the literature-standard range.
    """
    config = StermanConfig(
        alpha_S=0.5,
        alpha_SL=0.1,
        d_hat_ewma=0.36,
    )
    return StermanPolicy(
        config=config,
        product_idx=product_idx,
        node_idx=node_idx,
        initial_target_IL=initial_target_IL,
        initial_target_OO=initial_target_OO,
    )


def make_sterman_balanced(
    product_idx: int,
    node_idx: int,
    initial_target_IL: float = 12.0,
    initial_target_OO: float = 16.0,
) -> StermanPolicy:
    """Construct a Sterman variant with balanced anchoring weights.

    Uses alpha_S=0.5, alpha_SL=0.5 which removes the behavioral bias
    (no supply-line under-weighting). This is essentially "rational
    Sterman" and serves as a counterfactual benchmark: if the formula
    helps a balanced Sterman team, the benefit comes from the formula's
    prescription rather than from correcting a behavioral asymmetry.
    Produces lower bullwhip than classical Sterman.
    """
    config = StermanConfig(
        alpha_S=0.5,
        alpha_SL=0.5,
        d_hat_ewma=0.2,
    )
    return StermanPolicy(
        config=config,
        product_idx=product_idx,
        node_idx=node_idx,
        initial_target_IL=initial_target_IL,
        initial_target_OO=initial_target_OO,
    )


# =========================================================================
# SELF-TEST (runs when file is executed directly)
# =========================================================================

def _self_test():
    """Verify the module's structure without requiring a running simulation.

    The actual integration test against a stockpyl chain is in a separate
    file (verify_sterman_policy.py) so the policy can be tested under
    realistic chain dynamics. This self-test only validates that the
    StermanPolicy class can be instantiated and that its configuration
    defaults are coherent.
    """
    print("=" * 60)
    print("StermanPolicy module self-test")
    print("=" * 60)

    # Test 1: default configuration is well-formed.
    cfg = StermanConfig()
    print(f"\nTest 1: default StermanConfig")
    print(f"  alpha_S          = {cfg.alpha_S}    (literature 0.5)")
    print(f"  alpha_SL         = {cfg.alpha_SL}    (literature 0.2)")
    print(f"  d_hat_ewma       = {cfg.d_hat_ewma}    (literature 0.2)")
    print(f"  ratio alpha_SL/S = {cfg.alpha_SL/cfg.alpha_S:.2f}    "
          f"(behavioral signature: < 1.0)")
    assert cfg.alpha_SL < cfg.alpha_S, (
        "alpha_SL must be smaller than alpha_S for behavioral signature"
    )

    # Test 2: classical factory produces literature-standard policy.
    pol = make_sterman_classical(product_idx=0, node_idx=0)
    print(f"\nTest 2: make_sterman_classical produces StermanPolicy")
    print(f"  type: {type(pol).__name__}")
    print(f"  config.alpha_S:  {pol.config.alpha_S}")
    print(f"  config.alpha_SL: {pol.config.alpha_SL}")
    print(f"  diagnostic_log keys: {sorted(pol.diagnostic_log.keys())}")
    assert isinstance(pol, StermanPolicy), "factory must return StermanPolicy"
    assert pol.config.alpha_S == 0.5
    assert pol.config.alpha_SL == 0.2
    assert pol._d_hat is None, "d_hat should start uninitialized"

    # Test 3: balanced variant has alpha_SL == alpha_S.
    pol_b = make_sterman_balanced(product_idx=0, node_idx=0)
    print(f"\nTest 3: make_sterman_balanced removes behavioral bias")
    print(f"  alpha_S  = {pol_b.config.alpha_S}")
    print(f"  alpha_SL = {pol_b.config.alpha_SL}")
    assert pol_b.config.alpha_S == pol_b.config.alpha_SL, (
        "balanced variant should have equal weights"
    )

    # Test 4: EWMA update behaves correctly in isolation.
    pol_e = make_sterman_classical(product_idx=0, node_idx=0)
    d1 = pol_e._update_d_hat(observed_AO=10.0)
    d2 = pol_e._update_d_hat(observed_AO=10.0)
    d3 = pol_e._update_d_hat(observed_AO=20.0)
    print(f"\nTest 4: EWMA forecast update")
    print(f"  step 1 (AO=10): d_hat = {d1:.4f}  (expected 10.0 - first obs)")
    print(f"  step 2 (AO=10): d_hat = {d2:.4f}  (expected 10.0 - steady)")
    print(f"  step 3 (AO=20): d_hat = {d3:.4f}  (expected 12.0 - 0.2*20+0.8*10)")
    assert abs(d1 - 10.0) < 1e-9
    assert abs(d2 - 10.0) < 1e-9
    assert abs(d3 - 12.0) < 1e-9

    print("\nAll self-tests completed.")
    print("=" * 60)


if __name__ == '__main__':
    _self_test()
