"""e7_regression_check.py - the regression assertion DESIGN 14e promised.

WHY THIS EXISTS SEPARATELY, AND LATE. Amendment 2026-07-14e withdrew E7's fidelity
leg as vacuous under vendoring, and stated: "(It retains one narrow use, kept in the
suite as a REGRESSION assertion rather than a finding: it proves the vendored copy
is unmodified and the harness wires it correctly.)" THAT ASSERTION WAS NEVER
IMPLEMENTED. e7_suite.py LEG 1 proves the vendored BYTES are unmodified; nothing
proved OUR DRIVER wires them correctly. An earlier container attempt at this check
timed out and was abandoned without the gap being recorded. The 2026-07-15 real run
therefore completed with its harness unverified. This script closes that gap.

It is separate from e7_suite.py because it is SLOW (~11 minutes: three cells at 50
seeds each). The suite must stay fast enough to run at every Stage 1. This runs once,
and its output is committed as evidence.

WHAT IT PROVES, AND WHAT IT CANNOT. The vendored construction is DETERMINISTIC: the
demand array is pre-generated with seed=trial_seed and handed to stockpyl as an
explicit list (DemandSource type='D'), so the hard-coded rand_seed=42 is inert
(DISC-05, CIC-7). The source ran seeds 3000-3049. Our run used 3000-3249, which
CONTAINS theirs as its first fifty. Therefore, if our driver is wired correctly,
running seeds 3000-3049 through it must reproduce the source's per-cell means
EXACTLY - not approximately. Any deviation beyond floating-point noise means OUR
HARNESS IS WRONG and the 2026-07-15 real run is VOID.

This can only invalidate our own work. It is not evidence about the source, and a
failure here is never a finding about them - it is a finding about us. That
asymmetry is the point: the check is self-penalizing by construction.

TARGETS. The source's published values (v16 "Chain-length sweep") are +0.44 / +0.14
/ -0.14 at L = 4/6/8, ar1_high x 2.4x. The values below are the higher-precision
figures recomputed directly from the source's own 9,000-trial artifact
(C:\\ResearchShare\\aggregated_chain_length_sweep.json, MD5
6ecfc6fec0b1e490febea64ef36cd058) during the DISC-05 CIC, which matched their
published figures to three decimals. Those recomputed values are the target, because
they carry the precision this check needs.

Usage:
  python verification/e7_regression_check.py
Exit 0 = harness verified, the real run stands. Exit 1 = harness wrong, run VOID.
"""

from __future__ import annotations

import pathlib
import sys
import time

_HERE = pathlib.Path(__file__).resolve().parent
_ANALYSIS = _HERE.parent / "analysis"
sys.path.insert(0, str(_ANALYSIS))
sys.path.insert(0, str(_ANALYSIS / "vendor"))

from e7_chain_sweep import NUM_PERIODS, run_cell  # noqa: E402
from phase2_6_chain_length_sweep import get_demand_environments  # noqa: E402

# The source's own seeds (verified present in their artifact: 50 distinct, 3000-3049)
SOURCE_SEED_START, SOURCE_N_SEEDS = 3000, 50

# Recomputed from the source's raw 9,000-trial artifact during the DISC-05 CIC.
# Their published figures (+0.44 / +0.14 / -0.14) match these to three decimals.
TARGETS = {4: +0.4391, 6: +0.1371, 8: -0.1412}
ENV, CAP = "ar1_high", 2.4

# The construction is deterministic, so agreement should be to floating-point.
# The targets are quoted to 4dp, so allow only 4dp rounding slack. Anything larger
# is a wiring defect, not noise.
TOL = 5e-4


def main() -> None:
    print("E7 REGRESSION CHECK - does OUR harness reproduce the SOURCE on THEIR seeds?")
    print("=" * 74)
    print("construction: vendored (MD5-asserted by e7_suite LEG 1), deterministic")
    print(f"seeds       : {SOURCE_SEED_START}-{SOURCE_SEED_START + SOURCE_N_SEEDS - 1} "
          f"(the source's own; the first 50 of our real run's 3000-3249)")
    print(f"cells       : {ENV} x {CAP}x, L = 4 / 6 / 8")
    print("targets     : recomputed from the source's 9,000-trial artifact")
    print(f"tolerance   : {TOL} (deterministic construction - this is rounding slack, "
          f"not sampling slack)")
    print()
    print("A FAILURE HERE VOIDS THE 2026-07-15 REAL RUN. It is a finding about OUR")
    print("harness, never about the source.")
    print()

    envs = get_demand_environments(NUM_PERIODS)
    rows, t0 = [], time.time()
    for L in (4, 6, 8):
        c = run_cell(L, CAP, ENV, envs[ENV],
                     seed_start=SOURCE_SEED_START, n_seeds=SOURCE_N_SEEDS)
        p = c["primary"]
        got, want = p["mean_pct_diff"], TARGETS[L]
        delta = got - want
        ok = abs(delta) <= TOL
        rows.append((L, got, want, delta, ok, p["n_paired"], c["n_failed"]))
        print("  L=%d  n_paired=%2d failed=%d  ours %+.4f%%  source %+.4f%%  "
              "delta %+.6f  %s  [%.0fs]"
              % (L, p["n_paired"], c["n_failed"], got, want, delta,
                 "MATCH" if ok else "*** MISMATCH ***", time.time() - t0))

    all_ok = all(r[4] for r in rows)
    n_ok = sum(1 for r in rows if r[4])
    print()
    print("=" * 74)
    if all_ok:
        print(f"REGRESSION PASS: {n_ok}/3 cells reproduce the source exactly on the "
              f"source's own seeds.")
        print("The harness is verified. The 2026-07-15 real run (250 seeds, 36 cells) "
              "STANDS.")
        print("This closes the gap left by DESIGN 14e's unimplemented regression "
              "assertion.")
    else:
        print(f"REGRESSION FAIL: only {n_ok}/3 cells reproduce.")
        print("OUR HARNESS IS WRONG. The 2026-07-15 real run is VOID and must not be "
              "recorded.")
        print("Do NOT modify the vendored modules - the defect is in our driver.")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
