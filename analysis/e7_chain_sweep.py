"""e7_chain_sweep.py - E7: chain-length x capacity x demand-environment sweep.

REBUILD. Supersedes the 2026-07-14 build, WITHDRAWN as invalid: it violated this
experiment's frozen operator ("Operator (frozen; SOURCE CALIBRATION)") by using
E4's calibration instead of the source's. See DESIGN.md Section 10 amendments
2026-07-14d (remediation) and 2026-07-14e (build strategy), and
verification/Discrepancy_Register.md DISC-05.

BUILD STRATEGY (DESIGN 2026-07-14e). The source's construction is VENDORED
unmodified in analysis/vendor/ and driven by this runner. It is NOT re-implemented:
re-implementing from the source's own code is transcription, not independence - it
reproduces any logic defect while adding transcription risk - and genuine
independence (re-implementing from the paper's methods prose) is impossible here,
because the paper specifies neither k_star, nor the cost parameters, nor the
estimator prior, nor the drift schedule. See the completeness finding in 14e.

WHAT IS OURS AND WHAT IS THEIRS:
  theirs (vendored, byte-identical, MD5-asserted by the suite):
      the engine, the policy/estimator, the demand generators
  ours (this file):
      the grid driver, the paired comparison, the resolution logic,
      the crossover locator, the stability statement, the report

WHAT THIS EXPERIMENT MAY CLAIM: we audited the source's implementation against the
7-point CIC (all seven clear, DISC-05) and against the paper's own proven theorem
(suite LEG 2), vendored it unmodified, and re-ran it at 5x the seed count to
resolve what the original design could not. It may NOT claim independent
re-implementation.

CLASSIFICATION (Standard v1.9.7; corrected by 14d and 14e). E7 carries NO standalone
SUPPORT/REFUTE verdict. Two report forms:
  (b) BOUNDARY-CONDITION / DOMAIN-MAPPING (primary) -> the crossover MAP with its
      resolution. Expected-null polarity stated: finding NO crossover is a
      legitimate outcome, reported as found. A boundary whose adjacent cells are
      statistically indistinguishable is reported UNRESOLVED, never as a crossing.
  (c) ROBUSTNESS / SENSITIVITY -> a STABILITY STATEMENT across chain length and
      capacity, plus the three-variant diagnostic (paper9_ols vs oracle_local vs
      naive_damp).
E7 does NOT qualify E4: E4 is a different construction (hand-rolled base-stock,
different scale and cost ratio), so the two are not commensurable.

REPORTING COMMITMENT (pre-registered, 14d/14e): every cell's paired mean pct
difference with its uncertainty and achieved MDD; the crossover map with its
resolution; the stability statement; the three-variant diagnostic. ALL cells
reported regardless of direction. No cell dropped. Where our result resolves a cell
the source's 50 seeds could not, both are reported side by side.

SIGN CONVENTION (the source's): pct_diff = (sr_paper9_ols - sr_disabled)/sr_disabled
* 100. POSITIVE = the tool costs MORE = HARM. NEGATIVE = BENEFIT.

Writes analysis/outputs/e7_chain_sweep.json.
"""

from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE / "vendor"))

from phase2_6_chain_length_sweep import (  # noqa: E402
    DEFAULT_NUM_PERIODS as NUM_PERIODS,
    DEFAULT_WARMUP_PERIODS as WARMUP_PERIODS,
    calibrate_oracle_phi,
    get_demand_environments,
    run_one_seed_all_variants,
)

OUT = _HERE / "outputs" / "e7_chain_sweep.json"

# Frozen grid - the source's own (DESIGN Section 10 operator; 14d)
GRID_L = [4, 6, 8]
GRID_CAP = [1.3, 1.8, 2.4]

# Seeds (14d, narrowed by 14f on MEASURED cost): 3000-3249. The source used
# 3000-3049 = the FIRST FIFTY of this range, so their seeds remain a strict subset
# of ours and the regression assertion needs no separate execution. 250 resolves
# both points the source's 50 could not (L=6 at 4.0 sigma, L=8 at 4.1 sigma) - five
# times their power - for ~8.5h instead of the ~34h a 1000-seed full grid measured.
SEED_START = 3000
N_SEEDS = 250
SOURCE_SEED_START, SOURCE_N_SEEDS = 3000, 50

# The source's published values on the headline line, ar1_high x 2.4x (v16
# "Chain-length sweep"; verified to 3dp against their own 9,000-trial artifact in
# DISC-05 CIC-1). Reported side-by-side. NOT a calibration target: we run their
# construction, so agreement is expected and is a regression check, not evidence.
SOURCE_HEADLINE = {4: +0.439, 6: +0.137, 8: -0.141}
SOURCE_SE = {4: 0.072, 6: 0.078, 8: 0.081}
HEADLINE_ENV, HEADLINE_CAP = "ar1_high", 2.4

PRIMARY, BASELINE = "sr_paper9_ols", "sr_disabled"
DIAGNOSTIC = ["sr_paper9_ols", "sr_oracle_local", "sr_naive_damp"]

Z95 = 1.959963984540054
Z_MDD = 1.644853626951472 + 0.8416212335729143  # 80% power, one-sided alpha=0.05


def paired_pct_diff(trials: list, variant: str, base: str) -> dict:
    """Paired per-seed pct difference of `variant` against `base`.

    Pairing is by trial_seed: the vendored runner executes all five variants on the
    same seed (common random numbers), so the difference is within-seed. Returns the
    estimate with its measured uncertainty and this cell's OWN achieved MDD - never
    inherited from another cell.
    """
    a = {t["trial_seed"]: t["cost_per_period"] for t in trials
         if t["variant"] == variant and t.get("success")}
    b = {t["trial_seed"]: t["cost_per_period"] for t in trials
         if t["variant"] == base and t.get("success")}
    common = sorted(set(a) & set(b))
    if len(common) < 2:
        return dict(n_paired=len(common), mean_pct_diff=None, se=None, ci=None,
                    achieved_mdd=None, resolved_vs_zero=False, sign="unresolved")
    d = np.array([(a[s] - b[s]) / b[s] * 100.0 for s in common])
    mean = float(d.mean())
    se = float(d.std(ddof=1) / np.sqrt(len(d)))
    resolved = bool(abs(mean) > Z95 * se)
    return dict(
        n_paired=len(common), mean_pct_diff=mean, se=se,
        ci=[float(mean - Z95 * se), float(mean + Z95 * se)],
        achieved_mdd=float(Z_MDD * se), resolved_vs_zero=resolved,
        sign=("harm" if mean > 0 else "benefit") if resolved else "unresolved",
    )


def run_cell(n_stages: int, cap: float, env_name: str, env_config: dict,
             seed_start: int = SEED_START, n_seeds: int = N_SEEDS) -> dict:
    """One grid cell: drive the VENDORED engine across seeds, then analyse.

    The oracle's phi provider is calibrated per environment by the vendored
    calibrate_oracle_phi (a constant for the stationary envs; the drift schedule
    callable for drift_canonical).
    """
    oracle_phi = calibrate_oracle_phi(env_name, env_config)
    trials = []
    for s in range(seed_start, seed_start + n_seeds):
        trials.extend(run_one_seed_all_variants(
            env_config, s, NUM_PERIODS, WARMUP_PERIODS, n_stages, cap, oracle_phi,
        ))
    n_fail = sum(1 for t in trials if not t.get("success"))
    out = dict(n_stages=int(n_stages), cap_mult=float(cap), env=env_name,
               n_seeds=int(n_seeds), n_trials=len(trials), n_failed=int(n_fail))
    out["primary"] = paired_pct_diff(trials, PRIMARY, BASELINE)
    out["diagnostic"] = {v: paired_pct_diff(trials, v, BASELINE) for v in DIAGNOSTIC}
    return out


def crossover_map(cells: list) -> dict:
    """Locate, per (cap, env), where the sign flips across chain length.

    A flip between two cells that are BOTH unresolved is NOT a crossover - it is an
    unresolved boundary, reported as such. Expected-null polarity: a grid line with
    no resolved harm region has no crossover to locate, and that is a legitimate
    finding reported as found, not a failure.
    """
    out = {}
    for cap in sorted({c["cap_mult"] for c in cells}):
        for env in sorted({c["env"] for c in cells}):
            series = sorted([c for c in cells
                             if c["cap_mult"] == cap and c["env"] == env],
                            key=lambda c: c["n_stages"])
            if not series:
                continue
            flips = []
            for x, y in zip(series, series[1:]):
                mx = x["primary"]["mean_pct_diff"]
                my = y["primary"]["mean_pct_diff"]
                if mx is None or my is None:
                    continue
                if (mx > 0) != (my > 0):
                    both = (x["primary"]["resolved_vs_zero"]
                            and y["primary"]["resolved_vs_zero"])
                    flips.append(dict(between=[x["n_stages"], y["n_stages"]],
                                      from_=mx, to=my, resolved=bool(both)))
            any_harm = any(c["primary"]["mean_pct_diff"] is not None
                           and c["primary"]["mean_pct_diff"] > 0
                           and c["primary"]["resolved_vs_zero"] for c in series)
            any_ben = any(c["primary"]["mean_pct_diff"] is not None
                          and c["primary"]["mean_pct_diff"] < 0
                          and c["primary"]["resolved_vs_zero"] for c in series)
            out["cap%s_%s" % (cap, env)] = dict(
                by_length={str(c["n_stages"]): c["primary"]["mean_pct_diff"]
                           for c in series},
                resolved={str(c["n_stages"]): c["primary"]["resolved_vs_zero"]
                          for c in series},
                sign_flips=flips,
                spans_transition=bool(any_harm and any_ben),
                note=("grid line spans a resolved harm region and a resolved benefit "
                      "region - a crossover is locatable here"
                      if (any_harm and any_ben) else
                      "no resolved harm-to-benefit transition on this grid line - "
                      "no crossover is locatable (reported as found)"))
    return out


def stability(cells: list) -> dict:
    """The robustness deliverable: a stability statement, not a verdict."""
    def spread(key):
        d = {}
        for v in sorted({c[key] for c in cells}):
            sub = [c["primary"]["mean_pct_diff"] for c in cells
                   if c[key] == v and c["primary"]["mean_pct_diff"] is not None]
            if sub:
                d[str(v)] = dict(mean=float(np.mean(sub)), min=float(np.min(sub)),
                                 max=float(np.max(sub)))
        return d
    res = [c for c in cells if c["primary"]["resolved_vs_zero"]]
    return dict(
        by_chain_length=spread("n_stages"), by_capacity=spread("cap_mult"),
        by_env=spread("env"), n_cells=len(cells), n_resolved=len(res),
        n_unresolved=len(cells) - len(res),
        n_harm=sum(1 for c in res if c["primary"]["mean_pct_diff"] > 0),
        n_benefit=sum(1 for c in res if c["primary"]["mean_pct_diff"] < 0))


def headline_vs_source(cells: list) -> dict:
    """Side-by-side of our result against the source's published 50-seed values on
    the headline line. NOT a calibration: we ran their construction, so agreement is
    expected. Its purpose is to report, per cell, whether OUR seeds resolve what
    THEIRS could not - the source's SEs (0.072/0.078/0.081) leave L=6 at 1.8 sigma
    and L=8 at 1.7 sigma, both unresolved at 95%.
    """
    rows = []
    for L in sorted(SOURCE_HEADLINE):
        c = next((c for c in cells if c["n_stages"] == L
                  and c["cap_mult"] == HEADLINE_CAP
                  and c["env"] == HEADLINE_ENV), None)
        if c is None:
            continue
        p = c["primary"]
        src, src_se = SOURCE_HEADLINE[L], SOURCE_SE[L]
        src_res = bool(abs(src) > Z95 * src_se)
        rows.append(dict(
            n_stages=L, source_mean=src, source_se=src_se,
            source_sigma=float(abs(src) / src_se),
            source_resolved_at_95=src_res,
            ours_mean=p["mean_pct_diff"], ours_se=p["se"], ours_ci=p["ci"],
            ours_resolved_at_95=p["resolved_vs_zero"],
            source_in_our_ci=(bool(p["ci"][0] <= src <= p["ci"][1])
                              if p["ci"] else None),
            newly_resolved=bool(p["resolved_vs_zero"] and not src_res)))
    return dict(env=HEADLINE_ENV, cap_mult=HEADLINE_CAP, rows=rows)


def run_sweep(seed_start: int = SEED_START, n_seeds: int = N_SEEDS,
              grid_l=None, grid_cap=None, envs=None, verbose: bool = True) -> dict:
    """Full grid. Used verbatim by the suite (at reduced n) and by the real run."""
    grid_l = grid_l or GRID_L
    grid_cap = grid_cap or GRID_CAP
    all_envs = get_demand_environments(NUM_PERIODS)
    names = envs if envs is not None else sorted(all_envs)
    cells, t0 = [], time.time()
    total = len(grid_l) * len(grid_cap) * len(names)
    for L in grid_l:
        for cap in grid_cap:
            for env_name in names:
                cells.append(run_cell(L, cap, env_name, all_envs[env_name],
                                      seed_start, n_seeds))
                if verbose:
                    p = cells[-1]["primary"]
                    m = p["mean_pct_diff"]
                    lo, hi = (p["ci"] if p["ci"] else (float("nan"),) * 2)
                    print("  [%2d/%d] L=%d cap=%s %-16s %+.4f%% [%+.4f,%+.4f] %s (%.0fs)"
                          % (len(cells), total, L, cap, env_name, m, lo, hi,
                             "RESOLVED" if p["resolved_vs_zero"] else "unresolved",
                             time.time() - t0), flush=True)
    return dict(cells=cells, crossover=crossover_map(cells),
                stability_statement=stability(cells),
                headline_vs_source=headline_vs_source(cells),
                elapsed_sec=float(time.time() - t0))


def main() -> None:
    envs = sorted(get_demand_environments(NUM_PERIODS))
    print("E7 chain-length sweep (REBUILD; vendored source construction): "
          "%dx%dx%d = %d cells x %d seeds x 5 variants"
          % (len(GRID_L), len(GRID_CAP), len(envs),
             len(GRID_L) * len(GRID_CAP) * len(envs), N_SEEDS), flush=True)
    res = run_sweep()
    out = dict(experiment="E7", date="2026-07-15",
               design_pin="74c73ea165a7363c6714fe803fbe76b1",
               build="REBUILD - vendored source construction (DESIGN 14d/14e); "
                     "supersedes the withdrawn 2026-07-14 run",
               report_form="characterization: boundary/crossover map with resolution "
                           "+ stability statement; NO standalone verdict",
               spec=dict(grid_chain_lengths=GRID_L, grid_capacity=GRID_CAP,
                         environments=envs, seed_start=SEED_START, n_seeds=N_SEEDS,
                         source_seeds=[SOURCE_SEED_START,
                                       SOURCE_SEED_START + SOURCE_N_SEEDS - 1],
                         num_periods=NUM_PERIODS, warmup_periods=WARMUP_PERIODS,
                         primary=PRIMARY, baseline=BASELINE,
                         sign_convention="positive = tool costs MORE = harm"),
               **res)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))

    st = res["stability_statement"]
    cx = res["crossover"]
    hv = res["headline_vs_source"]
    print("\nE7 CHARACTERIZATION (no verdict). %d/%d cells resolved vs zero; "
          "%d harm, %d benefit, %d unresolved."
          % (st["n_resolved"], st["n_cells"], st["n_harm"], st["n_benefit"],
             st["n_unresolved"]))
    print("\nHeadline line (%s x %sx) - ours vs the source's published 50-seed values:"
          % (HEADLINE_ENV, HEADLINE_CAP))
    for r in hv["rows"]:
        print("  L=%d: source %+.3f%% (se %.3f, %.1f sigma, resolved=%s) | "
              "ours %+.4f%% (se %.4f, resolved=%s) | newly resolved=%s"
              % (r["n_stages"], r["source_mean"], r["source_se"], r["source_sigma"],
                 r["source_resolved_at_95"], r["ours_mean"], r["ours_se"],
                 r["ours_resolved_at_95"], r["newly_resolved"]))
    spans = [k for k, v in cx.items() if v["spans_transition"]]
    print("\nGrid lines with a locatable harm->benefit crossover: %s"
          % (spans if spans else "NONE (reported as found)"))


if __name__ == "__main__":
    main()
