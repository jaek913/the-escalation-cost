"""beer_engine.py - parameterized multi-echelon Beer Game engine.

Extracted so the chain-length sweep (E7) and the recipe-level non-stationarity
diagnostic (E12) can vary chain length, capacity headroom, and the demand
environment without touching e4_beer_game.py, which stays frozen with its
result committed.

FIDELITY CONTRACT (enforced by e7_suite.py LEG 1): at E4's configuration this
module must reproduce e4_beer_game.simulate() per-run costs EXACTLY (bitwise).
The engine below is a mechanical parameterization of E4's simulate(): same
statement order, same rng draw order, same arithmetic. Any drift is a code
defect the suite catches before a real run.

DEMAND ENVIRONMENTS are FROZEN FROM THE PINNED SOURCE (DESIGN Section 10
amendment 2026-07-14c; Paper9_The_General_Measurement_Trap_v16.md MD5
93135760b92cc195da36eb3c2b785ded, "Chain-length sweep"):
  iid_control      phi = 0
  ar1_moderate     phi = 0.6
  ar1_high         phi = 0.85
  drift_canonical  phi walks 0.30 -> 0.95 -> 0.40 over the horizon
The three drift waypoints trace to the source; the INTERPOLATION SHAPE does not
(the source does not specify it) and is a declared author choice mirroring E4's
canonical ramp timing - disclosed in DESIGN 2026-07-14c and the methods note.

  ramp_e4 is E4's own monotone ramp (0.30 -> 0.95 over periods 30-70). It is NOT
  a source environment and is NOT part of E7's grid; it exists solely for the
  fidelity check.
"""

from __future__ import annotations

import pathlib
import sys
from dataclasses import dataclass

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from theory_lib import bg_star, rho, wstar_closed, interiority_c  # noqa: E402

# Source-frozen environment names (DESIGN 2026-07-14c). ramp_e4 is fidelity-only.
SOURCE_ENVS = ("iid_control", "ar1_moderate", "ar1_high", "drift_canonical")


@dataclass(frozen=True)
class ChainConfig:
    """All of E4's frozen calibration, with the three sweep axes exposed.
    Defaults reproduce E4 exactly (n_ech=4, cap_mult=1.3, env='ramp_e4')."""
    n_ech: int = 4
    cap_mult: float = 1.3
    env: str = "ramp_e4"
    lead: int = 2
    h_cost: float = 1.0
    b_cost: float = 4.0
    base_demand: float = 100.0
    sigma: float = 10.0
    n_periods: int = 120
    alpha_es: float = 0.3
    safety: float = 1.5
    w_mon: int = 8
    bg_policy: float = 0.9561
    k_star: float = 0.90
    kappa: float = 0.75
    w_min: int = 2
    # rolling_phi's cold-start prior; E4 uses its PHI_LO (0.30). Estimator
    # property, not an environment parameter - held fixed across the grid.
    phi_fallback: float = 0.30


def phi_path(env: str, n_periods: int) -> np.ndarray:
    """True per-period persistence for each environment."""
    if env == "iid_control":
        return np.zeros(n_periods)
    if env == "ar1_moderate":
        return np.full(n_periods, 0.6)
    if env == "ar1_high":
        return np.full(n_periods, 0.85)
    if env == "drift_canonical":
        # waypoints 0.30 / 0.95 / 0.40 from source; shape is the declared choice
        p = np.empty(n_periods)
        for t in range(n_periods):
            if t < 30:
                p[t] = 0.30
            elif t <= 70:
                p[t] = 0.30 + (t - 30) / 40.0 * (0.95 - 0.30)
            elif t <= 110:
                p[t] = 0.95 + (t - 70) / 40.0 * (0.40 - 0.95)
            else:
                p[t] = 0.40
        return p
    if env == "ramp_e4":
        # E4's make_demand(), verbatim: t<30 -> 0.30; t>70 -> 0.95; else linear
        p = np.empty(n_periods)
        for t in range(n_periods):
            if t < 30:
                p[t] = 0.30
            elif t > 70:
                p[t] = 0.95
            else:
                p[t] = 0.30 + (t - 30) / 40.0 * (0.95 - 0.30)
        return p
    raise ValueError(f"unknown env: {env}")


def make_demand(rng: np.random.Generator, cfg: ChainConfig) -> np.ndarray:
    """AR(1) demand with a per-period persistence path. One standard_normal
    draw per period, in period order - matching E4's rng consumption exactly."""
    phis = phi_path(cfg.env, cfg.n_periods)
    d = np.empty(cfg.n_periods)
    x = 0.0
    for t in range(cfg.n_periods):
        x = phis[t] * x + cfg.sigma * rng.standard_normal()
        d[t] = max(0.0, cfg.base_demand + x)
    return d


def engagement_phi(cfg: ChainConfig) -> float:
    """phi where rho(phi, w_mon, bg_policy) = 1 - the derived engagement
    boundary (~0.83 at E4's calibration). Bisection on the monotone rho."""
    lo, hi = 0.30, 0.999
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if rho(mid, cfg.w_mon, cfg.bg_policy) < 1.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def rolling_phi(hist: list[float], cfg: ChainConfig) -> float:
    """Trailing OLS AR(1) estimate of demand persistence (the tool's input)."""
    if len(hist) < 6:
        return cfg.phi_fallback
    y = np.asarray(hist[-24:])
    x, z = y[:-1], y[1:]
    xm, zm = x.mean(), z.mean()
    den = ((x - xm) ** 2).sum()
    if den <= 0:
        return cfg.phi_fallback
    return float(np.clip(((x - xm) * (z - zm)).sum() / den, -0.99, 0.999))


def alpha_spectral(phi_hat: float, cfg: ChainConfig, phi_eng: float) -> float:
    """phi-gated damping: alpha = 1 below the engagement boundary (reduces to
    base-stock - the no-harm property); above it, alpha < 1 sized to pull the
    effective gain back to the rho = 1 boundary."""
    if phi_hat <= phi_eng:
        return 1.0
    lo, hi = 1e-3, cfg.bg_policy
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if rho(phi_hat, cfg.w_mon, mid) < 1.0:
            lo = mid
        else:
            hi = mid
    bg_target = 0.5 * (lo + hi)
    return float(np.clip(bg_target / cfg.bg_policy, 0.05, 1.0))


def alpha_full(phi_hat: float, cfg: ChainConfig, phi_eng: float) -> float:
    """Spectral damping, then cap the effective gain at k* of the maximum safe
    aggressiveness bg*(phi, W). Takes the more conservative of the two."""
    a_spec = alpha_spectral(phi_hat, cfg, phi_eng)
    if phi_hat <= phi_eng:
        return a_spec
    bg_max = bg_star(phi_hat, cfg.w_mon)
    bg_target_full = min(cfg.bg_policy, cfg.k_star * bg_max)
    a_full = bg_target_full / cfg.bg_policy
    return float(np.clip(min(a_spec, a_full), 0.05, 1.0))


def optimal_window(phi_hat: float, r: float, cfg: ChainConfig) -> float:
    """W* with the FLAG-2 G.3(ii) boundary clamp (declared theorem input)."""
    a = cfg.kappa * np.log(max(r, 1.0000001))
    en = 1.0 - phi_hat ** 2
    return wstar_closed(a, en) if interiority_c(a, en) else float(cfg.w_min)


def simulate(demand: np.ndarray, algo: str, cfg: ChainConfig,
             phi_eng: float, count_engagement: bool = False):
    """One serial chain of cfg.n_ech echelons under a base-stock order-up-to
    policy (optionally alpha-damped). Shipments lead-delayed and capacity-capped.
    Cost = holding (inv >= 0) + backorder (inv < 0) over echelons and periods.

    Mechanical parameterization of e4_beer_game.simulate(); LEG 1 of the suite
    proves bitwise equality at E4's config.

    algo: 'basestock' (rational baseline) | 'spectral' (phi-gated damping,
    the all-tier deployment) | 'full' (spectral + k* speed-limit trim).

    Returns total_cost, or (total_cost, engaged_fraction) when count_engagement.
    """
    cap = cfg.cap_mult * cfg.base_demand
    inv = [cfg.base_demand * cfg.lead] * cfg.n_ech
    pipeline = [[cfg.base_demand] * cfg.lead for _ in range(cfg.n_ech)]
    forecast = [cfg.base_demand] * cfg.n_ech
    demand_hist: list[list[float]] = [[] for _ in range(cfg.n_ech)]
    total_cost = 0.0
    engaged = 0
    tier_periods = 0

    for t in range(cfg.n_periods):
        downstream = demand[t]
        for e in range(cfg.n_ech):
            arriving = pipeline[e].pop(0)
            inv[e] += arriving
            inv[e] -= downstream
            demand_hist[e].append(downstream)

            forecast[e] = cfg.alpha_es * downstream + (1 - cfg.alpha_es) * forecast[e]
            fc = forecast[e]

            target = fc * (cfg.lead + 1) * cfg.safety
            inv_position = inv[e] + sum(pipeline[e])
            order = max(0.0, target - inv_position)

            if algo in ("spectral", "full"):
                phi_hat = rolling_phi(demand_hist[e], cfg)
                if algo == "spectral":
                    a = alpha_spectral(phi_hat, cfg, phi_eng)
                else:
                    a = alpha_full(phi_hat, cfg, phi_eng)
                    r = rho(phi_hat, cfg.w_mon, cfg.bg_policy)
                    _ = optimal_window(phi_hat, r, cfg)  # declared theorem input
                order *= a
                if count_engagement:
                    tier_periods += 1
                    if a < 1.0:
                        engaged += 1

            order = min(order, cap * 2.0)
            pipeline[e].append(order)
            downstream = min(order, cap)

            cost = cfg.h_cost * inv[e] if inv[e] >= 0 else -cfg.b_cost * inv[e]
            total_cost += cost

    if count_engagement:
        frac = (engaged / tier_periods) if tier_periods else 0.0
        return total_cost, frac
    return total_cost
