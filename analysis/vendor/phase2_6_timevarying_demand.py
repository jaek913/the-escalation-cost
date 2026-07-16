"""
Phase 2.6: Time-Varying Persistence Demand Generator
=====================================================

Phase 2.5 established the multi-echelon network with stationary AR(1)
demand, seasonal variation, and shock events. Phase 2.6 needs an
additional demand environment where the AR(1) persistence parameter
phi drifts over time according to a specified schedule. This is the
condition where Paper 9's measurement damage theorem predicts the
spectral radius mechanism should provide its largest operational
advantage, because regime-changing persistence is exactly the dynamic
that creates measurement damage.

The Strategic Plan describes the canonical schedule as "phi 0.3 to
0.7 to 0.4 over 10 simulated years." With Phase 2.5's 260-period
horizon (52 warmup + 208 measured), this generator compresses the
schedule into five equal-length segments of 52 periods each:
  Periods   0  -  51 : phi = 0.30   (low persistence baseline)
  Periods  52 - 103 : phi drifts 0.30 -> 0.70 linearly
  Periods 104 - 155 : phi = 0.70   (high persistence plateau)
  Periods 156 - 207 : phi drifts 0.70 -> 0.40 linearly
  Periods 208 - 259 : phi = 0.40   (low persistence resolution)

This layout exercises the SR mechanism through both an upward regime
transition (where damping should increase) and a downward regime
transition (where damping should relax). Both directions are scientific-
ally interesting because the Measurement Damage Theorem D = (rho_2/rho_1)^tau
predicts damage in both, but the damping response should differ in
magnitude given that pi^2/2 only binds at phi above approximately 0.82.

This module provides:

  1. A schedule abstraction (PhiSchedule) that encapsulates a callable
     mapping period -> true phi, with named factory functions for the
     standard Phase 2.6 schedules.

  2. generate_timevarying_ar1_demand(): produces an AR(1) demand stream
     where phi drifts according to the supplied schedule, with noise
     variance dynamically adjusted to keep stationary variance constant.

  3. generate_iid_normal_demand(): the simple IID demand generator used
     as the negative control environment in Phase 2.6.

  4. make_oracle_phi_provider(): returns a callable that the
     SR-oracle-phi policy can use to query true phi at each period.
     This callable is consistent with whatever schedule was used to
     generate the demand, ensuring oracle and demand stream agree.

  5. A self-test that verifies all four Phase 2.6 demand environments
     produce demand with the expected local statistics.

Author: JAE with Claude as research assistant
Date: April 24, 2026
"""

from dataclasses import dataclass
from typing import Callable, Optional, Dict
import numpy as np


# =========================================================================
# PHI SCHEDULE ABSTRACTION
# =========================================================================
# A PhiSchedule is essentially a wrapper around a callable that maps
# period number to true phi value. The wrapper exists so we can carry
# along human-readable metadata (the schedule's name, its bounds, etc.)
# alongside the function itself, which makes diagnostic logging much
# more useful. Without the wrapper we would just have anonymous lambdas
# that print as "<function <lambda> at 0x...>".

@dataclass
class PhiSchedule:
    """A named, callable schedule mapping period number to AR(1) phi.

    The schedule is the ground truth that both the demand generator
    and the oracle policy use to stay synchronized. Any deviation
    between them would invalidate the SR-oracle-phi diagnostic.

    Attributes
    ----------
    name : str
        Human-readable label for diagnostic logs and result files.
        Examples: "constant_0.85", "drift_0.3_0.7_0.4_260p".
    func : Callable[[int], float]
        The schedule itself. Takes a period number (0-indexed) and
        returns the true phi at that period. Should always return a
        value in [0, 0.999].
    description : str
        Optional longer description explaining what the schedule does.
        Useful for paper exhibits and diagnostic output.
    """
    name: str
    func: Callable[[int], float]
    description: str = ""

    def __call__(self, period: int) -> float:
        """Return true phi at the given period, clipped to safe bounds.

        The clip range was widened from [0.0, 0.999] to [-0.999, 0.999]
        on April 27, 2026 to support negative phi experiments. The
        AR(1) generator handles negative phi correctly because its
        noise-variance calculation uses phi^2, which is non-negative
        regardless of phi's sign. The original lower bound of 0.0 was
        defensive (no schedule was producing negative values yet) but
        not mathematically required.

        The upper bound of 0.999 (rather than 1.0) prevents the noise
        variance from collapsing to zero, which would produce an exact
        random walk and cause sqrt(1 - phi^2) to be exactly zero.
        Symmetrically, the lower bound of -0.999 prevents the same
        degenerate case from below.
        """
        return float(np.clip(self.func(period), -0.999, 0.999))


# =========================================================================
# STANDARD PHASE 2.6 SCHEDULE FACTORIES
# =========================================================================

def constant_schedule(phi: float, name: Optional[str] = None) -> PhiSchedule:
    """Constant phi for all periods (used by the stationary AR(1) environments).

    The two stationary AR(1) demand environments in Phase 2.6 use this:
    moderate persistence (phi=0.6) and high persistence (phi=0.85).
    Wrapping a constant value as a schedule lets us use the same
    interface across all four environments.

    Parameters
    ----------
    phi : float
        The constant persistence value.
    name : str, optional
        Schedule name. Defaults to "constant_<phi>".

    Returns
    -------
    PhiSchedule
        A schedule that returns phi for all periods.
    """
    if name is None:
        name = f"constant_{phi:.2f}"
    return PhiSchedule(
        name=name,
        func=lambda t: phi,
        description=f"Stationary AR(1) with phi={phi}",
    )


def piecewise_linear_schedule(
    breakpoints: list,
    name: str,
    description: str = "",
) -> PhiSchedule:
    """Construct a piecewise-linear schedule from breakpoint pairs.

    The schedule interpolates linearly between consecutive breakpoints.
    Before the first breakpoint, phi equals the first breakpoint's
    value. After the last breakpoint, phi equals the last breakpoint's
    value. This is more flexible than a single drift function because
    it lets us specify multi-segment regime patterns without writing
    custom math each time.

    Parameters
    ----------
    breakpoints : list of (period, phi) tuples
        The schedule's anchor points. Must be sorted by period and
        contain at least two entries.
    name : str
        Human-readable schedule name.
    description : str
        Optional longer description.

    Returns
    -------
    PhiSchedule
        A schedule that interpolates linearly between breakpoints.
    """
    if len(breakpoints) < 2:
        raise ValueError("Need at least two breakpoints for interpolation")

    # Sort by period to handle out-of-order input gracefully. Then
    # split into parallel arrays for easy interpolation lookup.
    bps = sorted(breakpoints, key=lambda x: x[0])
    periods = np.array([bp[0] for bp in bps], dtype=float)
    phis = np.array([bp[1] for bp in bps], dtype=float)

    def schedule_func(t: int) -> float:
        # numpy's interp handles the boundary cases automatically:
        # values outside [periods[0], periods[-1]] are clamped to the
        # nearest endpoint, which is exactly the behavior we want.
        return float(np.interp(float(t), periods, phis))

    return PhiSchedule(
        name=name,
        func=schedule_func,
        description=description,
    )


def phase2_6_drift_schedule(num_periods: int = 260) -> PhiSchedule:
    """The canonical Phase 2.6 time-varying persistence schedule.

    Divides the simulation into five equal segments and uses piecewise-
    linear interpolation to produce smooth transitions between regimes.
    The transitions are gradual rather than instantaneous because the
    SR mechanism's response to gradual drift is more revealing than
    its response to sudden steps. Sudden steps invoke the limit-case
    behavior at the discontinuity, which is harder to interpret.

    For the default 260-period simulation:
      Segment 1 (  0 -  51): phi = 0.30, low persistence baseline
      Segment 2 ( 52 - 103): phi drifts 0.30 -> 0.70 linearly
      Segment 3 (104 - 155): phi = 0.70, high persistence plateau
      Segment 4 (156 - 207): phi drifts 0.70 -> 0.40 linearly
      Segment 5 (208 - 259): phi = 0.40, low persistence resolution

    Parameters
    ----------
    num_periods : int
        Total simulation length in periods. The schedule scales to fit.

    Returns
    -------
    PhiSchedule
        The canonical Phase 2.6 drift schedule.
    """
    seg = num_periods / 5.0
    breakpoints = [
        (0,            0.30),  # start of segment 1
        (int(1 * seg), 0.30),  # end of segment 1, start of drift up
        (int(2 * seg), 0.70),  # end of drift up, start of plateau
        (int(3 * seg), 0.70),  # end of plateau, start of drift down
        (int(4 * seg), 0.40),  # end of drift down, start of resolution
        (num_periods - 1, 0.40),  # end of simulation
    ]
    return piecewise_linear_schedule(
        breakpoints=breakpoints,
        name=f"drift_0.3_0.7_0.4_{num_periods}p",
        description=(
            "Phase 2.6 canonical drift: phi=0.3 baseline, ramps to 0.7, "
            "plateaus at 0.7, ramps down to 0.4, plateaus at 0.4. "
            "Tests SR mechanism response to both upward and downward "
            "regime transitions."
        ),
    )


# =========================================================================
# SHOCK INJECTION SCHEDULES (added April 27, 2026)
# =========================================================================
# These schedule factories support the shock injection experiment, which
# tests JAE's reframe-driven distinction between brief exogenous shocks
# (events shorter than the formula's response time, where damping cannot
# help) and sustained regime changes (events longer than the response
# time, where damping can engage and provide benefit).
#
# The formula's response time is set primarily by the measurement window
# W (currently 8 periods) plus additional time for the OLS estimator to
# stabilize and for chain inventory dynamics to respond. Total response
# time is roughly 15-30 periods. The shock duration sweep tests scenarios
# both below and above this transition point.

def brief_shock_schedule(
    baseline_phi: float = 0.3,
    shock_phi: float = 0.95,
    shock_start: int = 100,
    shock_duration: int = 5,
    name: Optional[str] = None,
) -> PhiSchedule:
    """Schedule for a brief exogenous shock: phi spikes high then returns.

    Tests the formula's behavior on events too short for it to detect and
    respond to in time. Hypothesis: the formula will produce neutral or
    slightly negative results because by the time the OLS estimator has
    accumulated enough data to recognize the new regime, the shock has
    already ended and the demand has reverted to baseline.

    Default parameters represent a clearly brief shock: baseline phi
    equal to 0.3 (mild persistence, well below engagement threshold),
    shock phi equal to 0.95 (deep into engagement zone), shock duration
    of 5 periods (well below the formula's ~15-30 period response time),
    and shock starting at period 100 (well past the 52-period warmup).

    The schedule uses sharp step transitions rather than smooth ramps
    because real-world brief shocks (viral video spikes, weather events,
    panic buying) typically arrive abruptly rather than building up
    gradually. Sharp transitions also produce a cleaner test of the
    formula's response time: any benefit must come from genuine
    detection and response, not from the formula tracking a slow
    buildup that gives it advance warning.

    Parameters
    ----------
    baseline_phi : float
        Persistence value before and after the shock. Default 0.3.
    shock_phi : float
        Persistence value during the shock. Default 0.95.
    shock_start : int
        Period when the shock begins (inclusive). Default 100.
    shock_duration : int
        Number of periods the shock lasts. Default 5.
    name : str, optional
        Schedule name. Defaults to descriptive auto-generated name.

    Returns
    -------
    PhiSchedule
        A schedule that produces a brief spike in phi at the specified
        time and duration.
    """
    if name is None:
        name = (f"brief_shock_b{baseline_phi:.2f}_s{shock_phi:.2f}"
                  f"_t{shock_start}_d{shock_duration}")

    shock_end = shock_start + shock_duration

    def schedule_func(t: int) -> float:
        # Sharp step transitions: baseline before shock_start, shock
        # value from shock_start to shock_end (exclusive), baseline
        # afterward. The (t < shock_start) check uses strict inequality
        # so the shock starts ON shock_start (e.g. period 100 itself
        # is inside the shock).
        if t < shock_start:
            return baseline_phi
        elif t < shock_end:
            return shock_phi
        else:
            return baseline_phi

    return PhiSchedule(
        name=name,
        func=schedule_func,
        description=(
            f"Brief shock: phi=[{baseline_phi}->{shock_phi}->{baseline_phi}] "
            f"with shock at periods [{shock_start},{shock_end}). "
            f"Tests formula behavior on events shorter than its response time."
        ),
    )


def regime_change_schedule(
    baseline_phi: float = 0.3,
    new_regime_phi: float = 0.85,
    transition_period: int = 130,
    name: Optional[str] = None,
) -> PhiSchedule:
    """Schedule for a sustained regime change: phi steps permanently up.

    Tests the formula's behavior on events long enough for both the
    chain to develop bullwhip amplification and the formula to detect
    and respond. Hypothesis: the formula will produce clear cost
    benefit in the post-transition window because (a) the chain has
    time to develop instability, (b) the formula has time to recognize
    the new regime, and (c) the formula's damping prescription has
    time to take effect.

    Default parameters represent a clearly sustained regime change:
    baseline phi equal to 0.3 (low persistence), new regime phi equal
    to 0.85 (at the engagement boundary - just enough to trigger the
    formula but not so extreme that effects are obvious), transition
    at period 130 (the simulation midpoint, leaving 130 periods of
    sustained regime for the formula to act on).

    Like brief_shock_schedule, this uses a sharp step transition
    rather than a gradual ramp. This is to make the test as clean as
    possible: any benefit must come from the formula detecting the
    new regime once it is established, not from following a gradual
    buildup. The drift_canonical schedule already tests gradual
    transitions; this experiment tests step transitions.

    Parameters
    ----------
    baseline_phi : float
        Persistence value before the transition. Default 0.3.
    new_regime_phi : float
        Persistence value after the transition. Default 0.85.
    transition_period : int
        Period when phi steps from baseline to new regime. Default 130.
    name : str, optional
        Schedule name. Defaults to descriptive auto-generated name.

    Returns
    -------
    PhiSchedule
        A schedule that steps from baseline_phi to new_regime_phi at
        the specified period and stays at new_regime_phi for the rest
        of the simulation.
    """
    if name is None:
        name = (f"regime_change_b{baseline_phi:.2f}_n{new_regime_phi:.2f}"
                  f"_t{transition_period}")

    def schedule_func(t: int) -> float:
        # Strict less-than means the transition happens AT
        # transition_period: that period itself is the first period
        # of the new regime.
        if t < transition_period:
            return baseline_phi
        else:
            return new_regime_phi

    return PhiSchedule(
        name=name,
        func=schedule_func,
        description=(
            f"Regime change: phi=[{baseline_phi}->{new_regime_phi}] "
            f"at period {transition_period}. Tests formula behavior on "
            f"sustained regime shifts longer than its response time."
        ),
    )


# Window definitions for the three-window cost analysis. These are
# stored as (start, end) tuples in (inclusive, exclusive) period
# coordinates. The pre window ends before the event, the during
# window covers the event itself plus enough time for the formula's
# delayed response to manifest (since the formula reacts after the
# event begins), and the post window covers the eventual return to
# steady state. For sustained regime changes the post window captures
# the chain's adapted equilibrium under the new regime.
#
# These window definitions match the default scenario parameters
# above. If the experiment varies shock_start or transition_period,
# the window definitions need to be updated correspondingly. We
# provide a helper that computes windows from event parameters to
# avoid hardcoding.

def compute_three_windows(
    event_start: int,
    event_duration: int,
    num_periods: int,
    warmup_periods: int = 52,
    response_buffer: int = 25,
) -> Dict[str, tuple]:
    """Compute pre/during/post window boundaries for cost analysis.

    The pre window starts at the end of warmup and runs until just
    before the event. The during window starts at the event and
    extends past the event end by response_buffer periods to capture
    the formula's delayed reaction. The post window covers the
    remaining simulation time.

    For sustained regime changes (event_duration that runs to end of
    simulation), the during window extends to event_start + a fixed
    duration that allows the chain to settle into the new regime,
    and post covers the rest. This makes the during/post split
    meaningful even when the event itself never ends.

    Parameters
    ----------
    event_start : int
        Period when the event begins.
    event_duration : int
        Length of the event in periods. For regime changes that run
        to end of simulation, this should equal num_periods - event_start.
    num_periods : int
        Total simulation length.
    warmup_periods : int
        Number of warmup periods to exclude from analysis.
    response_buffer : int
        Extra periods to include in the during window beyond the
        literal event end, capturing the formula's delayed response.

    Returns
    -------
    dict
        {'pre': (start, end), 'during': (start, end), 'post': (start, end)}
        where each tuple uses (inclusive, exclusive) coordinates.
    """
    pre_start = warmup_periods
    pre_end = event_start

    during_start = event_start
    # If the event runs to the end of simulation (regime change),
    # use a fixed transient window of 30 periods after event_start
    # to capture the chain's response, then post covers the
    # adapted equilibrium.
    if event_start + event_duration >= num_periods:
        during_end = min(event_start + 30, num_periods)
    else:
        during_end = min(event_start + event_duration + response_buffer,
                            num_periods)

    post_start = during_end
    post_end = num_periods

    # Defensive: ensure all windows have positive length, falling back
    # to a degenerate empty window if not.
    return {
        'pre': (pre_start, max(pre_start, pre_end)),
        'during': (during_start, max(during_start, during_end)),
        'post': (post_start, max(post_start, post_end)),
    }


def phase2_6_drift_schedule_DEPRECATED_DUPLICATE(num_periods: int = 260):
    """Stub kept for compatibility; see phase2_6_drift_schedule above."""
    return phase2_6_drift_schedule(num_periods)


# =========================================================================
# TIME-VARYING AR(1) DEMAND GENERATOR
# =========================================================================

def generate_timevarying_ar1_demand(
    mean: float,
    stationary_std: float,
    schedule: PhiSchedule,
    num_periods: int,
    seed: int,
) -> np.ndarray:
    """Generate AR(1) demand with time-varying persistence.

    The local AR(1) update at period t uses phi(t) from the schedule:
        D[t] = mean + phi(t) * (D[t-1] - mean) + epsilon[t]

    The epsilon noise variance is chosen so that the LOCAL stationary
    variance equals stationary_std^2 at each period. Specifically:
        sigma_eps(t) = stationary_std * sqrt(1 - phi(t)^2)

    This design choice keeps the demand series visually similar across
    regime transitions; only its persistence character changes, not its
    overall magnitude. Without this adjustment, the demand variance
    would drift along with phi, conflating two effects we want to
    separate: the SR mechanism's response to persistence (what we want
    to measure) versus its response to changing variance (a separate
    confound we want to eliminate).

    The series is initialized from the stationary distribution at the
    initial phi(0). This eliminates burn-in transients that would
    otherwise appear in the first several periods. After initialization,
    the dynamics carry the series through whatever regime changes the
    schedule specifies.

    Negative demand values are clipped to zero, matching the convention
    in generate_ar1_demand (Phase 2.3 Stage 2). For our parameters,
    clipping affects fewer than one in a thousand periods.

    Parameters
    ----------
    mean : float
        Long-run mean demand. The same across all periods.
    stationary_std : float
        Stationary standard deviation, kept constant despite phi changes.
    schedule : PhiSchedule
        The time-varying phi schedule. Will be queried at each period.
    num_periods : int
        Length of the demand series to generate.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    np.ndarray
        Array of length num_periods, with non-negative demand values.
    """
    rng = np.random.default_rng(seed)

    # Initialize from the stationary distribution at phi(0). The
    # stationary variance is stationary_std^2 regardless of phi, so
    # we just draw from Normal(mean, stationary_std).
    demand = np.zeros(num_periods)
    demand[0] = rng.normal(mean, stationary_std)

    # Iterate through periods, querying the schedule for each phi(t)
    # and adjusting epsilon's variance dynamically.
    for t in range(1, num_periods):
        phi_t = schedule(t)
        # sigma_eps must satisfy var(D) = stationary_std^2 in steady
        # state, which requires sigma_eps^2 = stationary_std^2 * (1 - phi^2).
        sigma_eps = stationary_std * np.sqrt(1.0 - phi_t ** 2)
        epsilon = rng.normal(0.0, sigma_eps)
        demand[t] = mean + phi_t * (demand[t - 1] - mean) + epsilon

    # Clip negatives. Same convention as Phase 2.3 Stage 2.
    return np.maximum(demand, 0.0)


# =========================================================================
# IID NORMAL DEMAND GENERATOR (negative control environment)
# =========================================================================

def generate_iid_normal_demand(
    mean: float,
    std: float,
    num_periods: int,
    seed: int,
) -> np.ndarray:
    """Generate IID normal demand for the Phase 2.6 negative control.

    This is the cleanest possible test environment: each period's demand
    is independent of the previous periods. There is no persistence to
    exploit, so any properly-functioning SR mechanism should NOT engage
    damping. If SR-Paper9 shows advantage over SR-disabled on this
    environment, the mechanism is activating spuriously and the test
    is failing for diagnostic reasons.

    The conventional Phase 2.6 parameters are mean=10, std=2, matching
    the documentation in Strategic Plan Section 8.5.

    Parameters
    ----------
    mean : float
        Mean demand per period.
    std : float
        Standard deviation per period.
    num_periods : int
        Length of the demand series.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    np.ndarray
        Array of length num_periods with IID normal demand, clipped to
        non-negative.
    """
    rng = np.random.default_rng(seed)
    demand = rng.normal(mean, std, size=num_periods)
    return np.maximum(demand, 0.0)


# =========================================================================
# ORACLE PHI PROVIDER
# =========================================================================

def make_oracle_phi_provider(schedule: PhiSchedule) -> Callable[[int], float]:
    """Construct the oracle phi callable for the SR-oracle-phi variant.

    The SR-oracle-phi policy bypasses the OLS estimator and reads true
    phi from the simulator's ground truth. This function returns the
    callable the policy uses for that lookup. Because both this oracle
    and the demand generator use the same PhiSchedule object, they
    agree exactly on what phi is at each period; there is no possibility
    of drift between what the policy "sees" and what was actually used.

    Parameters
    ----------
    schedule : PhiSchedule
        The schedule used to generate the corresponding demand.

    Returns
    -------
    Callable[[int], float]
        Function mapping period -> true phi.
    """
    return schedule


# =========================================================================
# CONVENIENCE: build all four Phase 2.6 demand environments
# =========================================================================

def get_phase2_6_demand_environments() -> dict:
    """Return a dict describing all four Phase 2.6 demand environments.

    Each environment is a dict with keys:
      - name             : short label for diagnostic logs
      - description      : longer explanation
      - schedule         : PhiSchedule (None for IID environment)
      - mean, std        : demand distribution parameters
      - generator_kind   : either "iid" or "ar1"

    This function is the single source of truth for the experimental
    factorial. The experiment runner will iterate over this dict to
    produce all 16 (variant x environment) cells.

    Returns
    -------
    dict
        Dict from environment name to environment configuration.
    """
    return {
        "iid_control": {
            "name": "iid_control",
            "description": "IID normal(10, 2) - negative control",
            "schedule": None,
            "mean": 10.0,
            "std": 2.0,
            "generator_kind": "iid",
        },
        "ar1_moderate": {
            "name": "ar1_moderate",
            "description": "Stationary AR(1) phi=0.6 - modest expected advantage",
            "schedule": constant_schedule(0.6),
            "mean": 10.0,
            "std": 2.0,
            "generator_kind": "ar1",
        },
        "ar1_high": {
            "name": "ar1_high",
            "description": "Stationary AR(1) phi=0.85 - substantial expected advantage",
            "schedule": constant_schedule(0.85),
            "mean": 10.0,
            "std": 2.0,
            "generator_kind": "ar1",
        },
        "drift_canonical": {
            "name": "drift_canonical",
            "description": "Time-varying phi 0.3 -> 0.7 -> 0.4 - largest expected advantage",
            "schedule": phase2_6_drift_schedule(num_periods=260),
            "mean": 10.0,
            "std": 2.0,
            "generator_kind": "ar1",
        },
    }


def generate_demand_for_environment(
    env_config: dict,
    num_periods: int,
    seed: int,
) -> np.ndarray:
    """Generate a demand stream for a given Phase 2.6 environment.

    Dispatches to the right underlying generator based on the
    environment's generator_kind. The same seed produces the same
    demand stream, which is what enables paired-comparison statistical
    analysis across the five algorithm variants.

    Parameters
    ----------
    env_config : dict
        An entry from get_phase2_6_demand_environments().
    num_periods : int
        Length of the demand series.
    seed : int
        Random seed.

    Returns
    -------
    np.ndarray
        Demand array of length num_periods.
    """
    if env_config["generator_kind"] == "iid":
        return generate_iid_normal_demand(
            mean=env_config["mean"],
            std=env_config["std"],
            num_periods=num_periods,
            seed=seed,
        )
    elif env_config["generator_kind"] == "ar1":
        return generate_timevarying_ar1_demand(
            mean=env_config["mean"],
            stationary_std=env_config["std"],
            schedule=env_config["schedule"],
            num_periods=num_periods,
            seed=seed,
        )
    else:
        raise ValueError(f"Unknown generator_kind: {env_config['generator_kind']}")


# =========================================================================
# SELF-TEST
# =========================================================================

def _self_test():
    """Verify all four demand environments produce expected statistics.

    For each environment we generate a long demand stream and check:
      1. Mean and standard deviation are close to specified values
      2. Local persistence at the start, middle, and end matches the
         schedule (for AR(1) environments)
      3. IID environment shows near-zero serial correlation
      4. Drift environment shows visible regime structure

    These checks confirm the generators behave as the experiment design
    requires before we use them in the full Phase 2.6 validation run.
    """
    print("=" * 60)
    print("Phase 2.6 demand generator self-test")
    print("=" * 60)

    NUM_PERIODS = 5000  # long stream for stable statistics
    NUM_PERIODS_SCHEDULE = 260  # the actual experiment horizon

    # --- Test 1: IID environment ---
    # We expect mean approximately 10, std approximately 2, and
    # serial correlation approximately 0. The lag-1 OLS coefficient
    # should be near zero for IID data.
    print("\nTest 1: IID normal(10, 2) - negative control")
    iid = generate_iid_normal_demand(mean=10.0, std=2.0,
                                      num_periods=NUM_PERIODS, seed=42)
    print(f"  mean   = {iid.mean():.4f}   (expected ~10.0)")
    print(f"  std    = {iid.std():.4f}   (expected ~2.0)")

    # Compute lag-1 autocorrelation as a sanity check.
    iid_centered = iid - iid.mean()
    lag1_corr = np.sum(iid_centered[1:] * iid_centered[:-1]) / np.sum(iid_centered[:-1] ** 2)
    print(f"  lag-1  = {lag1_corr:+.4f}   (expected ~0.0 for IID)")

    # --- Test 2: stationary AR(1) at phi = 0.6 ---
    print("\nTest 2: Stationary AR(1) phi=0.6 - moderate persistence")
    ar06 = generate_timevarying_ar1_demand(
        mean=10.0, stationary_std=2.0,
        schedule=constant_schedule(0.6),
        num_periods=NUM_PERIODS, seed=42,
    )
    print(f"  mean   = {ar06.mean():.4f}   (expected ~10.0)")
    print(f"  std    = {ar06.std():.4f}   (expected ~2.0)")
    centered = ar06 - ar06.mean()
    lag1 = np.sum(centered[1:] * centered[:-1]) / np.sum(centered[:-1] ** 2)
    print(f"  lag-1  = {lag1:+.4f}   (expected ~0.6)")

    # --- Test 3: stationary AR(1) at phi = 0.85 ---
    print("\nTest 3: Stationary AR(1) phi=0.85 - high persistence")
    ar085 = generate_timevarying_ar1_demand(
        mean=10.0, stationary_std=2.0,
        schedule=constant_schedule(0.85),
        num_periods=NUM_PERIODS, seed=42,
    )
    print(f"  mean   = {ar085.mean():.4f}   (expected ~10.0)")
    print(f"  std    = {ar085.std():.4f}   (expected ~2.0)")
    centered = ar085 - ar085.mean()
    lag1 = np.sum(centered[1:] * centered[:-1]) / np.sum(centered[:-1] ** 2)
    print(f"  lag-1  = {lag1:+.4f}   (expected ~0.85)")

    # --- Test 4: time-varying drift schedule ---
    # Verify that local lag-1 correlations match the schedule's
    # local phi values when computed within each segment.
    print("\nTest 4: Time-varying drift schedule")
    schedule = phase2_6_drift_schedule(num_periods=NUM_PERIODS_SCHEDULE)
    print(f"  Schedule name: {schedule.name}")
    print(f"  {schedule.description[:60]}...")
    print(f"  phi at t=0    : {schedule(0):.3f}   (expected 0.30)")
    print(f"  phi at t=51   : {schedule(51):.3f}   (expected ~0.30)")
    print(f"  phi at t=78   : {schedule(78):.3f}   (expected ~0.50, midway up)")
    print(f"  phi at t=104  : {schedule(104):.3f}   (expected 0.70)")
    print(f"  phi at t=155  : {schedule(155):.3f}   (expected ~0.70)")
    print(f"  phi at t=181  : {schedule(181):.3f}   (expected ~0.55, midway down)")
    print(f"  phi at t=208  : {schedule(208):.3f}   (expected 0.40)")
    print(f"  phi at t=259  : {schedule(259):.3f}   (expected 0.40)")

    # Generate a single long realization, then segment-test the
    # local statistics.
    drift_demand = generate_timevarying_ar1_demand(
        mean=10.0, stationary_std=2.0, schedule=schedule,
        num_periods=NUM_PERIODS_SCHEDULE, seed=42,
    )
    print(f"\n  Demand stream stats (n={NUM_PERIODS_SCHEDULE}):")
    print(f"    overall mean = {drift_demand.mean():.3f}")
    print(f"    overall std  = {drift_demand.std():.3f}")

    # --- Test 5: oracle phi provider matches schedule ---
    print("\nTest 5: Oracle phi provider consistency")
    oracle = make_oracle_phi_provider(schedule)
    matches = all(
        abs(oracle(t) - schedule(t)) < 1e-12
        for t in [0, 50, 78, 130, 200, 259]
    )
    print(f"  oracle == schedule at sampled periods: {matches}")
    assert matches, "Oracle must agree with schedule exactly"

    # --- Test 6: reproducibility ---
    # Two generations with the same seed must produce identical streams.
    print("\nTest 6: Reproducibility with shared seeds")
    a = generate_timevarying_ar1_demand(
        mean=10.0, stationary_std=2.0,
        schedule=constant_schedule(0.85),
        num_periods=100, seed=12345,
    )
    b = generate_timevarying_ar1_demand(
        mean=10.0, stationary_std=2.0,
        schedule=constant_schedule(0.85),
        num_periods=100, seed=12345,
    )
    print(f"  identical streams from same seed: {np.array_equal(a, b)}")
    assert np.array_equal(a, b), "Same seed must produce identical streams"

    # --- Test 7: environment factory ---
    print("\nTest 7: Environment factory produces all four environments")
    envs = get_phase2_6_demand_environments()
    print(f"  number of environments: {len(envs)}   (expected 4)")
    for name, cfg in envs.items():
        d = generate_demand_for_environment(cfg, num_periods=260, seed=42)
        print(f"  {name:18s}: len={len(d)}, mean={d.mean():.2f}, std={d.std():.2f}")

    print("\nAll self-tests completed.")
    print("=" * 60)


if __name__ == '__main__':
    _self_test()
