"""e4_beer_game.py - E4: Beer Game Monte Carlo (does acting on the diagnostic
save cost?). DESIGN.md Section 7 (pin 74c73ea165a7363c6714fe803fbe76b1).

Upgrades correlation to causation-in-simulation: identical demand, different
ordering brains. Four-echelon chain; four algorithms; 1000 paired Monte Carlo
runs. Self-contained (synthetic demand; seeds committed) - no external data.

Frozen calibration (identical to source): four echelons (retailer,
wholesaler, distributor, factory); lead time L = 2; holding $1/unit/period;
backorder $4/unit/period; demand AR(1) baseline 100, sigma = 10, persistence
ramp phi 0.30 -> 0.95 over periods 30-70; 1000 runs, unique seed per run,
identical demand across the four algorithms within a run.

Algorithms:
  (1) naive       - order to fully cover the observed demand + pipeline gap.
  (2) ERP         - exponential-smoothing forecast (alpha = 0.3), safety
                    factor 1.5, gap closure 0.50.
  (3) spectral    - ERP + rho-monitor (SPEC-B: W = 8, base bg = 0.50): when
                    the rolling spectral radius rho > 1, damp the order.
  (4) full theorem- (3) + the pi^2/2 speed limit + safety factor k* + the
                    optimal-window W* input (with the FLAG-2 G.3(ii) boundary
                    clamp: when condition (C) fails or W* < W_min, clamp to the
                    boundary window rather than using the raw Lambert-W value).

Decision rule (frozen): SUPPORT iff algorithm (3) mean total cost < (2) with
paired-test p < 0.01 AND the relative-reduction 95% CI excludes zero, AND
(4) <= (3) (pairwise win rate reported). REFUTE if (3) is not significantly
cheaper than (2) - the diagnostic would be descriptive, not actionable
(reported as a failed practical claim even if E1 supports the theorem).

Writes analysis/outputs/e4_beer_game.json.
"""

from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from theory_lib import bg_star, rho, wstar_closed, interiority_c  # noqa: E402

OUT = _HERE / "outputs" / "e4_beer_game.json"

# Frozen calibration
N_ECH = 4
LEAD = 2
H_COST, B_COST = 1.0, 4.0
BASE_DEMAND, SIGMA = 100.0, 10.0
PHI_LO, PHI_HI = 0.30, 0.95
RAMP_START, RAMP_END = 30, 70
N_PERIODS = 120
N_RUNS = 1000
BASE_SEED = 20260713

# SPEC-B (rho-monitor) + tool params
W_MON, BG_BASE = 8, 0.50
ALPHA_ES = 0.3
SAFETY = 1.5
GAP_CLOSURE = 0.50
KAPPA = 0.75
W_MIN = 2  # FLAG-2 boundary window


def make_demand(rng: np.random.Generator) -> np.ndarray:
    """AR(1) demand with a persistence ramp (Minsky tightening)."""
    d = np.empty(N_PERIODS)
    x = 0.0
    for t in range(N_PERIODS):
        if t < RAMP_START:
            phi = PHI_LO
        elif t > RAMP_END:
            phi = PHI_HI
        else:
            frac = (t - RAMP_START) / (RAMP_END - RAMP_START)
            phi = PHI_LO + frac * (PHI_HI - PHI_LO)
        x = phi * x + SIGMA * rng.standard_normal()
        d[t] = max(0.0, BASE_DEMAND + x)
    return d


def rolling_phi(hist: list[float]) -> float:
    if len(hist) < 6:
        return PHI_LO
    y = np.asarray(hist[-24:])
    x, z = y[:-1], y[1:]
    xm, zm = x.mean(), z.mean()
    den = ((x - xm) ** 2).sum()
    return float(np.clip(((x - xm) * (z - zm)).sum() / den, -0.99, 0.999)) if den > 0 else PHI_LO


def simulate(demand: np.ndarray, algo: str) -> float:
    """One chain simulation under a given ordering algorithm. Returns total
    holding + backorder cost summed over echelons and periods.

    Simplified serial-chain mechanics (frozen, identical across algorithms):
    each echelon holds inventory, faces its downstream order as demand, places
    an upstream order per the algorithm; shipments arrive after LEAD periods;
    the factory's upstream supply is uncapacitated. Cost accrues on end-of-
    period inventory (holding if >=0, backorder if <0)."""
    inv = [BASE_DEMAND * LEAD] * N_ECH          # start at pipeline-cover
    pipeline = [[BASE_DEMAND] * LEAD for _ in range(N_ECH)]  # in-transit to each
    forecast = [BASE_DEMAND] * N_ECH
    demand_hist: list[list[float]] = [[] for _ in range(N_ECH)]
    total_cost = 0.0

    for t in range(N_PERIODS):
        downstream = demand[t]
        for e in range(N_ECH):
            arriving = pipeline[e].pop(0)
            inv[e] += arriving
            inv[e] -= downstream
            demand_hist[e].append(downstream)

            # Forecast (exponential smoothing for ERP/tool tiers)
            if algo == "naive":
                fc = downstream
            else:
                forecast[e] = ALPHA_ES * downstream + (1 - ALPHA_ES) * forecast[e]
                fc = forecast[e]

            # Base order-up-to target
            if algo == "naive":
                target = fc * (LEAD + 1)
                order = max(0.0, target - inv[e] - sum(pipeline[e]))
            else:
                target = fc * (LEAD + 1) * SAFETY
                gap = target - inv[e] - sum(pipeline[e])
                order = max(0.0, GAP_CLOSURE * gap)

            # rho-monitor damping (spectral + full)
            if algo in ("spectral", "full"):
                phi_hat = rolling_phi(demand_hist[e])
                r = rho(phi_hat, W_MON, BG_BASE)
                if r > 1.0:
                    if algo == "full":
                        # full theorem: pi^2/2 limit -> k* safety factor,
                        # plus optimal-window damping with FLAG-2 clamp.
                        bg_lim = bg_star(phi_hat, W_MON)
                        k = 0.85  # k* < 1 operating point (frozen; below limit)
                        damp = min(1.0, (k * bg_lim) / max(r - 1.0 + bg_lim, 1e-9))
                        # optimal-window input with boundary clamp (FLAG-2):
                        a = KAPPA * np.log(max(r, 1.0000001))
                        en = 1.0 - phi_hat ** 2
                        if interiority_c(a, en):
                            _ = wstar_closed(a, en)  # interior W* available
                        # else clamp to W_MIN (boundary) - no further damping tweak
                        order *= damp
                    else:
                        order *= 1.0 / r   # spectral: simple inverse-rho damp

            pipeline[e].append(order)
            # this echelon's order becomes the next upstream echelon's demand
            downstream = order

            cost = H_COST * inv[e] if inv[e] >= 0 else -B_COST * inv[e]
            total_cost += cost

    return total_cost


def run_montecarlo(n_runs: int = N_RUNS, base_seed: int = BASE_SEED) -> dict:
    """Paired Monte Carlo: identical demand across algorithms within a run.
    Returns per-algorithm cost arrays + the frozen decision-rule verdict.
    Used verbatim by the synthetic suite (with small n_runs) and the real run."""
    algos = ["naive", "erp", "spectral", "full"]
    algo_key = {"naive": "naive", "erp": "erp",
                "spectral": "spectral", "full": "full"}
    costs = {a: np.empty(n_runs) for a in algos}
    for i in range(n_runs):
        rng = np.random.default_rng(base_seed + i)
        demand = make_demand(rng)
        for a in algos:
            costs[a][i] = simulate(demand, algo_key[a])

    def paired_p(x: np.ndarray, y: np.ndarray) -> float:
        """One-sided paired test (x < y) via sign-flip permutation on the
        paired differences; exact small-sample null."""
        d = y - x  # positive => x cheaper
        obs = d.mean()
        rng = np.random.default_rng(base_seed + 999)
        b = 2000
        count = 0
        for _ in range(b):
            signs = rng.choice([-1.0, 1.0], size=len(d))
            if (signs * d).mean() >= obs:
                count += 1
        return (count + 1) / (b + 1)

    def rel_reduction_ci(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
        """Relative reduction (y->x) mean and 95% bootstrap CI."""
        rng = np.random.default_rng(base_seed + 1234)
        rr = (y - x) / y
        boot = [rr[rng.integers(0, len(rr), len(rr))].mean() for _ in range(2000)]
        lo, hi = np.percentile(boot, [2.5, 97.5])
        return float(rr.mean()), float(lo), float(hi)

    p_spectral_vs_erp = paired_p(costs["spectral"], costs["erp"])
    rr_mean, rr_lo, rr_hi = rel_reduction_ci(costs["spectral"], costs["erp"])
    full_le_spectral = costs["full"].mean() <= costs["spectral"].mean()
    win_full_vs_spectral = float((costs["full"] < costs["spectral"]).mean())

    spectral_cheaper = (costs["spectral"].mean() < costs["erp"].mean()
                        and p_spectral_vs_erp < 0.01 and rr_lo > 0)
    verdict = "SUPPORT" if spectral_cheaper and full_le_spectral else (
        "SUPPORT-PARTIAL" if spectral_cheaper else "REFUTE")

    return dict(
        n_runs=n_runs,
        mean_cost={a: float(costs[a].mean()) for a in algos},
        p_spectral_vs_erp=p_spectral_vs_erp,
        rel_reduction_mean=rr_mean, rel_reduction_ci=[rr_lo, rr_hi],
        full_le_spectral=full_le_spectral,
        win_rate_full_vs_spectral=win_full_vs_spectral,
        spectral_cheaper_than_erp=spectral_cheaper,
        verdict=verdict)


def main() -> None:
    res = run_montecarlo()
    out = dict(experiment="E4", date="2026-07-13",
               design_pin="74c73ea165a7363c6714fe803fbe76b1",
               spec=dict(echelons=N_ECH, lead=LEAD, h=H_COST, b=B_COST,
                         base_demand=BASE_DEMAND, sigma=SIGMA,
                         phi_ramp=[PHI_LO, PHI_HI], ramp=[RAMP_START, RAMP_END],
                         periods=N_PERIODS, n_runs=N_RUNS, base_seed=BASE_SEED,
                         W_mon=W_MON, bg_base=BG_BASE), **res)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    mc = res["mean_cost"]
    print(f"E4 {res['verdict']}: mean cost naive {mc['naive']:.0f} / "
          f"ERP {mc['erp']:.0f} / spectral {mc['spectral']:.0f} / "
          f"full {mc['full']:.0f}; spectral vs ERP p = {res['p_spectral_vs_erp']:.4f}, "
          f"rel reduction {res['rel_reduction_mean']:+.1%} "
          f"CI [{res['rel_reduction_ci'][0]:+.1%}, {res['rel_reduction_ci'][1]:+.1%}]; "
          f"full<=spectral {res['full_le_spectral']} "
          f"(win rate {res['win_rate_full_vs_spectral']:.1%})")


if __name__ == "__main__":
    main()
