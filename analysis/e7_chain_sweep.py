"""e7_chain_sweep.py - E7: chain-length x capacity x demand-environment sweep.
DESIGN.md Section 10 (pin 74c73ea165a7363c6714fe803fbe76b1) + amendments
2026-07-14 (classification), 2026-07-14b (seeds 50 -> 1000), 2026-07-14c
(environments frozen from source; replication leg dropped; calibration leg
added; two-scenario scope).

CLASSIFICATION (Standard v1.9.7) - E7 carries NO standalone SUPPORT/REFUTE
verdict. It is a BLEND of:
  (a) ROBUSTNESS / SENSITIVITY (dominant) -> a STABILITY STATEMENT
  (c) BOUNDARY-CONDITION / DOMAIN-MAPPING -> the crossover MAP with its
      resolution (an unresolved boundary is reported as unresolved)
  (d) MODEL-FIT / CALIBRATION -> our ar1_high x 2.4x values at L = 4/6/8
      reported AGAINST the source's +0.44% / +0.14% / -0.14%, with uncertainty
Its output QUALIFIES E4. A robustness experiment scored as a primary hypothesis
test manufactures false REFUTEs - that category error is what this rule avoids.

REPORTING COMMITMENT (pre-registered, DESIGN 2026-07-14): every cell's mean
relative cost difference with its uncertainty; the stability statement; the
crossover map with its resolution; the calibration comparison. ALL cells
reported regardless of direction. No cell dropped.

SIGN CONVENTION (matches the source): rel_diff = (all_tier - basestock)/basestock.
POSITIVE = all-tier deployment costs MORE = HARM. NEGATIVE = BENEFIT.

Writes analysis/outputs/e7_chain_sweep.json.
"""

from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from beer_engine import (ChainConfig, SOURCE_ENVS, engagement_phi,  # noqa: E402
                         make_demand, simulate)

OUT = _HERE / "outputs" / "e7_chain_sweep.json"

# Frozen grid (DESIGN Section 10 operator; seeds per amendment 2026-07-14b)
GRID_L = [4, 6, 8]
GRID_CAP = [1.3, 1.8, 2.4]
GRID_ENV = list(SOURCE_ENVS)
N_SEEDS = 1000
BASE_SEED = 20260714

# The source's point-prediction for the calibration leg (v16 "Chain-length
# sweep"): ar1_high x 2.4x capacity, all-tier vs base-stock, by chain length.
SOURCE_CALIB = {4: +0.0044, 6: +0.0014, 8: -0.0014}
CALIB_ENV, CALIB_CAP = "ar1_high", 2.4

Z95 = 1.959963984540054
# 80%-power one-sided detectable multiple of the SE (z_{0.95} + z_{0.80})
Z_MDD = 1.644853626951472 + 0.8416212335729143


def run_cell(n_ech: int, cap_mult: float, env: str, n_seeds: int = N_SEEDS,
             base_seed: int = BASE_SEED) -> dict:
    """One grid cell: paired base-stock vs all-tier spectral on identical demand.
    Returns the estimate with its measured uncertainty and the ACHIEVED minimum
    detectable difference at this cell's own variance (never inherited)."""
    cfg = ChainConfig(n_ech=n_ech, cap_mult=cap_mult, env=env)
    phi_eng = engagement_phi(cfg)
    diffs = np.empty(n_seeds)
    engs = np.empty(n_seeds)
    for i in range(n_seeds):
        d = make_demand(np.random.default_rng(base_seed + i), cfg)
        base = simulate(d, "basestock", cfg, phi_eng)
        sr, frac = simulate(d, "spectral", cfg, phi_eng, count_engagement=True)
        diffs[i] = (sr - base) / base
        engs[i] = frac

    mean = float(diffs.mean())
    se = float(diffs.std(ddof=1) / np.sqrt(n_seeds))
    lo, hi = mean - Z95 * se, mean + Z95 * se
    mdd = float(Z_MDD * se)                    # this cell's achieved MDD
    resolved = bool(abs(mean) > Z95 * se)      # distinguishable from zero
    return dict(n_ech=int(n_ech), cap_mult=float(cap_mult), env=env,
                n_seeds=int(n_seeds), rel_diff_mean=mean,
                rel_diff_ci=[float(lo), float(hi)], se=se, achieved_mdd=mdd,
                resolved_vs_zero=resolved,
                sign=("harm" if mean > 0 else "benefit") if resolved else "unresolved",
                engagement_rate=float(engs.mean()), phi_eng=float(phi_eng))


def crossover_map(cells: list[dict]) -> dict:
    """Locate, for each (cap, env), where the sign flips across chain length.
    A flip between two cells that are BOTH unresolved is NOT a crossover - it is
    an unresolved boundary and is reported as such (the E5 top-cluster lesson)."""
    out = {}
    for cap in GRID_CAP:
        for env in GRID_ENV:
            series = sorted([c for c in cells
                             if c["cap_mult"] == cap and c["env"] == env],
                            key=lambda c: c["n_ech"])
            key = f"cap{cap}_{env}"
            flips = []
            for a, b in zip(series, series[1:]):
                if (a["rel_diff_mean"] > 0) != (b["rel_diff_mean"] > 0):
                    both_res = a["resolved_vs_zero"] and b["resolved_vs_zero"]
                    flips.append(dict(between=[a["n_ech"], b["n_ech"]],
                                      from_=a["rel_diff_mean"],
                                      to=b["rel_diff_mean"],
                                      resolved=bool(both_res)))
            any_harm = any(c["rel_diff_mean"] > 0 and c["resolved_vs_zero"]
                           for c in series)
            any_benefit = any(c["rel_diff_mean"] < 0 and c["resolved_vs_zero"]
                              for c in series)
            out[key] = dict(
                by_length={str(c["n_ech"]): c["rel_diff_mean"] for c in series},
                resolved={str(c["n_ech"]): c["resolved_vs_zero"] for c in series},
                sign_flips=flips,
                spans_transition=bool(any_harm and any_benefit),
                note=("no resolved harm region in this grid line - the grid does "
                      "not span a transition here, so no crossover is locatable"
                      if not (any_harm and any_benefit) else
                      "grid line spans both a resolved harm and a resolved "
                      "benefit region"))
    return out


def calibration(cells: list[dict]) -> dict:
    """Estimate-vs-source on the source's three point-predictions. Reports
    direction agreement AND magnitude separately - direction can reproduce while
    magnitude misses by orders (the E4 lesson)."""
    rows = []
    for L, src in SOURCE_CALIB.items():
        c = next(c for c in cells if c["n_ech"] == L
                 and c["cap_mult"] == CALIB_CAP and c["env"] == CALIB_ENV)
        ours = c["rel_diff_mean"]
        rows.append(dict(
            n_ech=L, source=src, ours=ours, ci=c["rel_diff_ci"],
            sign_agrees=bool((src > 0) == (ours > 0)),
            source_in_our_ci=bool(c["rel_diff_ci"][0] <= src <= c["rel_diff_ci"][1]),
            abs_gap=float(abs(ours - src))))
    return dict(env=CALIB_ENV, cap_mult=CALIB_CAP, rows=rows,
                signs_all_agree=bool(all(r["sign_agrees"] for r in rows)),
                source_crossover_reproduces=bool(
                    rows[0]["ours"] > 0 and rows[-1]["ours"] < 0
                    and rows[0]["sign_agrees"] and rows[-1]["sign_agrees"]))


def stability(cells: list[dict]) -> dict:
    """The robustness deliverable: a stability statement, not a verdict."""
    def spread(key):
        d = {}
        for v in sorted({c[key] for c in cells}):
            sub = [c["rel_diff_mean"] for c in cells if c[key] == v]
            d[str(v)] = dict(mean=float(np.mean(sub)), min=float(np.min(sub)),
                             max=float(np.max(sub)))
        return d
    res = [c for c in cells if c["resolved_vs_zero"]]
    return dict(
        by_chain_length=spread("n_ech"), by_capacity=spread("cap_mult"),
        by_env=spread("env"),
        n_cells=len(cells), n_resolved=len(res),
        n_unresolved=len(cells) - len(res),
        n_harm=sum(1 for c in res if c["rel_diff_mean"] > 0),
        n_benefit=sum(1 for c in res if c["rel_diff_mean"] < 0))


def run_sweep(n_seeds: int = N_SEEDS, base_seed: int = BASE_SEED,
              grid_l=None, grid_cap=None, grid_env=None, verbose: bool = True) -> dict:
    """Full grid. Used verbatim by the suite (at reduced n) and the real run."""
    grid_l = grid_l or GRID_L
    grid_cap = grid_cap or GRID_CAP
    grid_env = grid_env or GRID_ENV
    cells = []
    t0 = time.time()
    total = len(grid_l) * len(grid_cap) * len(grid_env)
    for L in grid_l:
        for cap in grid_cap:
            for env in grid_env:
                cells.append(run_cell(L, cap, env, n_seeds, base_seed))
                if verbose:
                    c = cells[-1]
                    print(f"  [{len(cells):2d}/{total}] L={L} cap={cap} {env:16s} "
                          f"{c['rel_diff_mean']:+.4%} "
                          f"[{c['rel_diff_ci'][0]:+.4%},{c['rel_diff_ci'][1]:+.4%}] "
                          f"{'RESOLVED' if c['resolved_vs_zero'] else 'unresolved'} "
                          f"eng={c['engagement_rate']:.1%} "
                          f"({time.time()-t0:.0f}s)", flush=True)
    return dict(cells=cells, crossover=crossover_map(cells),
                calibration_vs_source=calibration(cells),
                stability_statement=stability(cells),
                elapsed_sec=float(time.time() - t0))


def main() -> None:
    print(f"E7 chain-length sweep: {len(GRID_L)}x{len(GRID_CAP)}x{len(GRID_ENV)} "
          f"= {len(GRID_L)*len(GRID_CAP)*len(GRID_ENV)} cells x {N_SEEDS} seeds "
          f"x 2 scenarios", flush=True)
    res = run_sweep()
    out = dict(experiment="E7", date="2026-07-14",
               design_pin="74c73ea165a7363c6714fe803fbe76b1",
               report_form="characterization (stability statement + crossover map) "
                           "+ estimate-vs-source calibration; NO standalone verdict",
               spec=dict(grid_chain_lengths=GRID_L, grid_capacity=GRID_CAP,
                         grid_environments=GRID_ENV, n_seeds=N_SEEDS,
                         base_seed=BASE_SEED, scenarios=["basestock", "spectral"],
                         source_calibration=SOURCE_CALIB,
                         sign_convention="positive = all-tier costs MORE = harm"),
               **res)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))

    st, cx, cal = res["stability_statement"], res["crossover"], res["calibration_vs_source"]
    print(f"\nE7 CHARACTERIZATION (no verdict). {st['n_resolved']}/{st['n_cells']} cells "
          f"resolved vs zero; {st['n_harm']} harm, {st['n_benefit']} benefit, "
          f"{st['n_unresolved']} unresolved.")
    print("\nCalibration vs source (ar1_high x 2.4x):")
    for r in cal["rows"]:
        print(f"  L={r['n_ech']}: source {r['source']:+.2%} | ours {r['ours']:+.4%} "
              f"[{r['ci'][0]:+.4%},{r['ci'][1]:+.4%}] | sign agrees={r['sign_agrees']} "
              f"| source in our CI={r['source_in_our_ci']}")
    print(f"  source's harm->benefit crossover reproduces: "
          f"{cal['source_crossover_reproduces']}")
    spans = [k for k, v in cx.items() if v["spans_transition"]]
    print(f"\nGrid lines spanning a resolved harm->benefit transition: "
          f"{spans if spans else 'NONE (no crossover locatable in this grid)'}")


if __name__ == "__main__":
    main()
