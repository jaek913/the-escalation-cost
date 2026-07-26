"""e14_contrast.py - E14 SECONDARY analysis on contrasts (DESIGN Section 22).

**POST-HOC. SECONDARY. The reading was committed in DESIGN 22.3 BEFORE this
file existed.** The pre-registered primary is unchanged and remains primary:
INCONCLUSIVE on the registered chain, detection probability 0.00 at the
observed effect. analysis/e14_echelon.py and its output stay byte-frozen and
are imported READ ONLY.

WHY (DESIGN 22.1, result-independent). Non-overlap of two 95 percent intervals
is roughly a 0.005-level test, not 0.05, and the pre-registered rule required
it against every other step. Worse, DESIGN 20.3 chose JOINT resampling
specifically to preserve cross-series dependence, so every resample yields a
complete vector of step ratios - and the pre-registered rule then collapsed
each step to a marginal interval, discarding the covariance the joint
resampling existed to preserve. The contrast computed WITHIN each resample is
the correctly-targeted statistic.

WHAT IS COMPUTED (DESIGN 22.2), from the SAME joint resamples:
  (i)   simultaneous contrast: per resample, min over other steps of
        (R_kstar - R_j); its 95 percent percentile interval
  (ii)  argmax probability per step
  (iii) power AND false-positive rate of the contrast rule at realised
        coupling - because a looser rule that fires more often is not an
        improvement unless it fires more on TRUE effects and no more on none

THE COMMITTED READING (DESIGN 22.3), repeated here so it travels with the code:
  A: interval excludes 0 AND FPR <= 0.05  -> ordering step separated under the
     correctly-targeted statistic; SECONDARY/POST-HOC labelling mandatory;
     primary still reported INCONCLUSIVE and non-severe.
  B: interval includes 0                  -> the DATA do not separate the steps
     even under the better statistic. Stronger and more final than the primary.
  C: FPR > 0.05                           -> contrast rule INADMISSIBLE; its
     interval carries no weight; the primary stands alone.

Usage:
  python analysis\\e14_contrast.py --suite   synthetic suite, no store access
  python analysis\\e14_contrast.py           real run, writes outputs/e14_contrast.json
"""

from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from e14_echelon import (  # noqa: E402  - frozen experiment module, READ ONLY
    CHAIN, CI_LEVEL, COVID_FROM, COVID_TO, INPUT_SHA256, MEAN_BLOCK, N_BOOT,
    RAW, SECTOR_ARM_LAST, SEED, adjacent_corr, bootstrap, build_panel, ci,
    point_estimates, read_fred_csv, sha256,
)
from e14_resolution import synth_from_driver  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "analysis" / "outputs"

FPR_CEILING = 0.05          # DESIGN 22.3 outcome C threshold
POWER_GRID = [1.0, 1.5, 2.0, 2.3667, 3.1382]
POWER_REPS = 100
B_POWER = 2000
LABELS4 = ["s1", "s2", "s3", "s4"]


def contrast_analyse(X: np.ndarray, labels: list, B: int, seed: int) -> dict:
    """Simultaneous contrast + argmax probabilities from ONE joint bootstrap."""
    pe = point_estimates(X)
    bs = bootstrap(X, B, MEAN_BLOCK, seed)
    sb = bs["step"]                                  # (B, k-1)
    nstep = sb.shape[1]
    kstar = int(np.argmax(pe["step"]))
    others = [j for j in range(nstep) if j != kstar]
    # simultaneous: min over other steps WITHIN each resample
    d = np.min(sb[:, [kstar]] - sb[:, others], axis=1)
    lo, hi = ci(d, CI_LEVEL)
    am = np.argmax(sb, axis=1)
    return dict(
        step_labels=[f"{labels[i]}->{labels[i+1]}" for i in range(nstep)],
        step_ratio=[float(x) for x in pe["step"]],
        largest_step_index=kstar,
        largest_step=f"{labels[kstar]}->{labels[kstar+1]}",
        contrast_point=float(np.min(pe["step"][kstar] - pe["step"][others])),
        contrast_ci_low=lo, contrast_ci_high=hi,
        contrast_excludes_zero=bool(lo > 0.0),
        argmax_probability=[float((am == i).mean()) for i in range(nstep)],
    )


def contrast_fires(X: np.ndarray, B: int, seed: int, want_index: int) -> bool:
    r = contrast_analyse(X, LABELS4, B, seed)
    return r["contrast_excludes_zero"] and r["largest_step_index"] == want_index


def power_curve(name: str, driver: np.ndarray, r1: float, r2: float,
                rhos: list) -> dict:
    print(f"\n  {name}: power and FPR of the CONTRAST rule at realised coupling")
    print(f"    {'R3':>10} | {'fire rate':>10} | note")
    rows, fpr = [], None
    for R3 in POWER_GRID:
        hit = 0
        for r in range(POWER_REPS):
            rng = np.random.default_rng(400000 + r)
            Xs = synth_from_driver(driver, [r1, r2, R3], rhos, rng)
            if contrast_fires(Xs, B_POWER, SEED + r, 2):
                hit += 1
        rate = hit / POWER_REPS
        note = ""
        if R3 == 1.0:
            note = "FALSE-POSITIVE RATE (DESIGN 22.3 outcome C gate)"
            fpr = rate
        elif abs(R3 - 2.3667) < 1e-6:
            note = "<-- OBSERVED, full sample"
        elif abs(R3 - 3.1382) < 1e-6:
            note = "<-- OBSERVED, COVID-excluded"
        print(f"    {R3:>10.4f} | {rate:>10.2f} | {note}")
        rows.append(dict(r3=R3, fire_rate=rate, note=note))
    return dict(configuration=name, grid=rows, false_positive_rate=fpr,
                reps=POWER_REPS, n_boot=B_POWER)


# ---------------------------------------------------------------------------

def suite() -> int:
    print("=" * 78)
    print("E14 CONTRAST SUITE (DESIGN 22) - synthetic, no store access")
    print("=" * 78)
    fails = []

    def check(label, cond, detail=""):
        print(f"  {'PASS' if cond else 'FAIL'}  {label}"
              f"{'  ' + detail if detail else ''}")
        if not cond:
            fails.append(label)

    n = 411
    drv = np.random.default_rng(11).normal(0, 0.01, size=n)

    # determinism
    Xd = synth_from_driver(drv, [1.15, 0.93, 3.0], [0.63, 0.77, 0.69],
                           np.random.default_rng(2))
    r1 = contrast_analyse(Xd, LABELS4, 1000, SEED)
    r2 = contrast_analyse(Xd, LABELS4, 1000, SEED)
    check("determinism: same seed reproduces the contrast interval",
          (r1["contrast_ci_low"], r1["contrast_ci_high"])
          == (r2["contrast_ci_low"], r2["contrast_ci_high"]))

    # argmax probabilities are a distribution
    check("argmax probabilities sum to 1",
          abs(sum(r1["argmax_probability"]) - 1.0) < 1e-12,
          f"sum {sum(r1['argmax_probability']):.6f}")

    # fires on a planted dominant step
    check("contrast rule fires on a planted dominant step",
          r1["contrast_excludes_zero"] and r1["largest_step_index"] == 2,
          f"CI [{r1['contrast_ci_low']:.4f}, {r1['contrast_ci_high']:.4f}]")

    # WATCHED TO FAIL: no planted dominance must NOT separate
    Xe = synth_from_driver(drv, [1.0, 1.0, 1.0], [0.63, 0.77, 0.69],
                           np.random.default_rng(3))
    re_ = contrast_analyse(Xe, LABELS4, 1000, SEED)
    check("WATCHED TO FAIL: even chain does NOT separate",
          not re_["contrast_excludes_zero"],
          f"CI [{re_['contrast_ci_low']:.4f}, {re_['contrast_ci_high']:.4f}]")

    # SIMULTANEITY: two jointly-high steps must NOT separate either
    Xt = synth_from_driver(drv, [1.0, 3.0, 3.0], [0.63, 0.77, 0.69],
                           np.random.default_rng(4))
    rt = contrast_analyse(Xt, LABELS4, 1000, SEED)
    check("SIMULTANEITY: two jointly-high steps do NOT separate",
          not rt["contrast_excludes_zero"],
          f"CI [{rt['contrast_ci_low']:.4f}, {rt['contrast_ci_high']:.4f}]")

    # false-positive rate of the contrast rule on even chains
    fp = 0
    for r in range(100):
        Xr = synth_from_driver(drv, [1.0, 1.0, 1.0], [0.63, 0.77, 0.69],
                               np.random.default_rng(6000 + r))
        pe = point_estimates(Xr)
        k = int(np.argmax(pe["step"]))
        if contrast_fires(Xr, 1000, SEED + r, k):
            fp += 1
    check("contrast rule false-positive rate on even chains <= 0.05",
          fp / 100 <= 0.05, f"rate {fp / 100:.2f}")

    print("=" * 78)
    print("ALL PASS" if not fails else f"FAILURES: {fails}")
    print("=" * 78)
    return 0 if not fails else 1


def real_run() -> int:
    print("E14 SECONDARY CONTRAST ANALYSIS (DESIGN 22) - POST-HOC")
    print("The primary result is UNCHANGED and remains primary.")
    for fname, want in INPUT_SHA256.items():
        got = sha256(RAW / fname)
        if got != want:
            raise SystemExit(f"INPUT HASH MISMATCH {fname}: {got} != {want}")
    print(f"  all {len(INPUT_SHA256)} input hashes match E14's frozen inputs")

    raw = {name: read_fred_csv(RAW / f) for name, f in CHAIN}
    labels = [name for name, _ in CHAIN]
    dates, X = build_panel(raw)
    keep = [i for i, d in enumerate(dates) if not (COVID_FROM <= d <= COVID_TO)]
    Xe = X[keep]

    arm_raw = {name: raw[name] for name, _ in CHAIN[:-1]}
    arm_raw[SECTOR_ARM_LAST[0]] = read_fred_csv(RAW / SECTOR_ARM_LAST[1])
    arm_labels = labels[:-1] + [SECTOR_ARM_LAST[0]]
    _, XA = build_panel(arm_raw)

    blocks = {}
    for tag, Xi, lb in (("full_sample", X, labels),
                        ("covid_excluded", Xe, labels),
                        ("sector_arm", XA, arm_labels)):
        r = contrast_analyse(Xi, lb, N_BOOT, SEED)
        blocks[tag] = r
        print(f"\n  {tag.upper()}: largest = {r['largest_step']} "
              f"(ratio {r['step_ratio'][r['largest_step_index']]:.4f})")
        print(f"    simultaneous contrast {r['contrast_point']:.4f}  "
              f"CI [{r['contrast_ci_low']:.4f}, {r['contrast_ci_high']:.4f}]  "
              f"-> {'EXCLUDES 0' if r['contrast_excludes_zero'] else 'INCLUDES 0'}")
        for i, lab in enumerate(r["step_labels"]):
            print(f"      P(argmax = {lab:26s}) = {r['argmax_probability'][i]:.4f}")

    v, ve = X.var(axis=0, ddof=1), Xe.var(axis=0, ddof=1)
    cf, ce = adjacent_corr(X)[0], adjacent_corr(Xe)[0]
    pw_full = power_curve("FULL SAMPLE", X[:, 0], float(v[1] / v[0]),
                          float(v[2] / v[1]), [float(c) for c in cf])
    pw_excl = power_curve("COVID-EXCLUDED", Xe[:, 0], float(ve[1] / ve[0]),
                          float(ve[2] / ve[1]), [float(c) for c in ce])

    worst_fpr = max(pw_full["false_positive_rate"], pw_excl["false_positive_rate"])
    if worst_fpr > FPR_CEILING:
        outcome = "C - contrast rule INADMISSIBLE (false-positive rate too high)"
    elif blocks["full_sample"]["contrast_excludes_zero"] or \
            blocks["covid_excluded"]["contrast_excludes_zero"]:
        outcome = "A - separated under the correctly-targeted statistic"
    else:
        outcome = "B - data do not separate the steps even under the contrast"

    print(f"\n  worst false-positive rate: {worst_fpr:.2f} "
          f"(ceiling {FPR_CEILING})")
    print(f"  DESIGN 22.3 OUTCOME: {outcome}")

    result = dict(
        analysis="E14 secondary contrast analysis",
        design_pin="c81d4c6eb31aa74e51db4c3108dc63db",  # FROZEN literal (see
        # e14_echelon.py): a live md5 of DESIGN.md cannot reproduce
        # byte-identically under the rerun check once DESIGN moves on.
        status="POST-HOC / SECONDARY - reading committed in DESIGN 22.3 before execution",
        primary_unchanged=("e14_echelon.json is byte-frozen; primary remains "
                           "INCONCLUSIVE with detection probability 0.00 at the "
                           "observed full-sample effect"),
        design_22_3_outcome=outcome,
        false_positive_rate_worst=worst_fpr,
        fpr_ceiling=FPR_CEILING,
        contrast=blocks,
        power_full_sample=pw_full,
        power_covid_excluded=pw_excl,
        scope=("Locates WHERE amplification concentrates. Does NOT establish "
               "that the measurement mechanism CAUSED the concentration."),
    )
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "e14_contrast.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                    encoding="ascii", newline="\n")
    print(f"\nwrote {path}")
    return 0


def main() -> int:
    return suite() if "--suite" in sys.argv else real_run()


if __name__ == "__main__":
    sys.exit(main())
