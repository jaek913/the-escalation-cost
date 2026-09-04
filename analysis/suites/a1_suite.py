"""a1_suite.py - A1 mechanism-validation suite.

Validates the WHOLE A1 pipeline (aggregation -> constant patching ->
estimator -> comparison -> decision rule) on planted ground truth, importing
the committed A1 and E1 code verbatim. The suite never reimplements what it
validates.

A1 is a FREQUENCY test, so its failure modes are different from E1's, and
the legs target them specifically:

  1. AGGREGATION CORRECTNESS - to_quarterly() on a hand-built series with
     known calendar structure returns exactly the calendar-quarter means, in
     order, with partial head/tail quarters dropped. A silent off-by-one in
     quarter bucketing would corrupt every downstream number while leaving
     the run looking healthy, so it is checked against arithmetic, not eyeball.

  2. CONSTANT PATCHING IS EXACT AND RESTORED - run_quarterly() must set E1's
     module globals to the quarterly values DURING the call and restore every
     one afterwards. If patching leaked, a later monthly run in the same
     process would silently produce quarterly numbers. Verified by observing
     the constants from inside the estimator and re-checking them after.

  3. PLANTED EFFECT SURVIVES AGGREGATION - synthetic sectors with a real
     planted mechanism, built at MONTHLY resolution, aggregated by the same
     to_quarterly(), must still return a positive pooled Spearman. This is
     the suite's core claim: if the machinery cannot see a mechanism it KNOWS
     is there after averaging, A1 cannot interpret a null on real data.

  4. PLANTED NULL STAYS NULL - fixed-persistence sectors with no regime
     dynamics must NOT produce a SUPPORT verdict after aggregation. Guards
     against aggregation manufacturing an artifact: averaging raises measured
     AR(1) persistence, and a pipeline that turned that into a positive
     result would be reporting the transform, not the world.

  5. RANK-CORRELATION COMPONENT IS WIRED CORRECTLY - the c2 test must read
     +1 for identical orderings, -1 for reversed, and must pass/fail at the
     pre-registered 0.50 threshold in the right direction. This is the
     component most likely to be silently mis-signed.

  6. SEPARATION - IS THE TEST INFORMATIVE AT ALL? Added 2026-09-04 after the
     first suite run: legs 3 and 4 passed while the planted NULL scored a
     HIGHER pooled Spearman (+0.0696) than the planted EFFECT (+0.0672).
     Both legs were one-sided ('effect positive', 'null not SUPPORT') and a
     pipeline that is entirely blind satisfies both. A test whose effect and
     null distributions coincide cannot produce a verdict in either
     direction, and a real-data number from it would be uninterpretable.
     This leg measures separation directly: many independent effect panels
     against many independent null panels, at BOTH frequencies. Monthly is
     the control - if monthly separates and quarterly does not, the loss is
     caused by aggregation (which is A1's actual question, surfacing in the
     suite) rather than by a broken pipeline.
     A1 MAY NOT BE RUN ON REAL DATA UNLESS QUARTERLY SEPARATION IS
     DEMONSTRATED. If it is not, the honest reading is that quarterly
     sampling destroys the discriminating information, and A1 reports that
     as its result without ever touching the panel.

Firewall: suite failures fix CODE ONLY, never the pre-registered rule or its
thresholds (A1_FREQUENCY_INVARIANCE.md Section 3, committed at c0da772).
Strengthening the SUITE is not a rule change: leg 6 adds a precondition on
running the experiment, it does not alter what PASS/PARTIAL/FAIL mean.

Usage: python analysis\\suites\\a1_suite.py    (no external data touched)
"""

from __future__ import annotations

import pathlib
import sys

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
import e1_rolling_validation as e1  # noqa: E402
import a1_frequency_invariance as a1  # noqa: E402
from e1_suite import gen_regime_series, gen_null_series  # noqa: E402

N_MONTHS = 410
N_SECTORS = 17
FAILS: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""))
    if not ok:
        FAILS.append(name)


# ---------------------------------------------------------------------------
def leg1_aggregation() -> None:
    """to_quarterly must return exact calendar-quarter means, in order, and
    drop partial quarters at BOTH ends."""
    print("\nLEG 1 - aggregation correctness")

    # Full-quarter case: 2020Q1..2020Q4, values 1..12 -> means 2, 5, 8, 11
    dates = [f"2020-{m:02d}-01" for m in range(1, 13)]
    vals = np.arange(1.0, 13.0)
    q = a1.to_quarterly(dates, vals)
    check("full quarters -> exact means",
          np.allclose(q, [2.0, 5.0, 8.0, 11.0]), f"got {q.tolist()}")

    # Partial head (starts Feb) and partial tail (ends Nov): both dropped,
    # leaving Q2 and Q3 only.
    dates = [f"2021-{m:02d}-01" for m in range(2, 12)]
    vals = np.arange(2.0, 12.0)
    q = a1.to_quarterly(dates, vals)
    check("partial head+tail quarters dropped",
          np.allclose(q, [5.0, 8.0]), f"got {q.tolist()}")

    # Order is chronological across a year boundary, not dict insertion order.
    dates = ([f"2019-{m:02d}-01" for m in range(10, 13)]
             + [f"2020-{m:02d}-01" for m in range(1, 4)])
    vals = np.array([10.0, 10.0, 10.0, 1.0, 1.0, 1.0])
    q = a1.to_quarterly(dates, vals)
    check("chronological across year boundary",
          np.allclose(q, [10.0, 1.0]), f"got {q.tolist()}")

    # A ratio is AVERAGED, never summed (the frozen choice).
    dates = [f"2022-{m:02d}-01" for m in range(1, 4)]
    q = a1.to_quarterly(dates, np.array([1.5, 1.5, 1.5]))
    check("ratio averaged, not summed", np.allclose(q, [1.5]), f"got {q.tolist()}")

    # Length: 410 monthly points from Jan 1992 -> 136 full quarters + partial
    dates = []
    y, m = 1992, 1
    for _ in range(N_MONTHS):
        dates.append(f"{y}-{m:02d}-01")
        m += 1
        if m == 13:
            m, y = 1, y + 1
    q = a1.to_quarterly(dates, np.arange(float(N_MONTHS)))
    check("410 months -> 136 full quarters", len(q) == 136, f"got {len(q)}")


# ---------------------------------------------------------------------------
def leg2_patching() -> None:
    """Constants must be quarterly DURING the call and restored after."""
    print("\nLEG 2 - constant patching is exact and restored")

    before = (e1.BASE_WIN, e1.RECENT_WIN, e1.FWD_WIN, e1.BLOCK, e1.W_SPEC, e1.TAU)
    seen = {}
    real_run_panel = e1.run_panel

    def spy(panel, seed=e1.SEED):
        seen["consts"] = (e1.BASE_WIN, e1.RECENT_WIN, e1.FWD_WIN,
                          e1.BLOCK, e1.W_SPEC, e1.TAU)
        return dict(sectors=[], n_oscillating=0, n_chronic=0,
                    pooled_mean_spearman=0.0, p_panel=1.0, verdict="FALSIFIED")

    e1.run_panel = spy
    try:
        a1.run_quarterly({"x": np.zeros(50)}, w=3)
    finally:
        e1.run_panel = real_run_panel

    check("quarterly constants active inside the call",
          seen.get("consts") == (a1.Q_BASE_WIN, a1.Q_RECENT_WIN, a1.Q_FWD_WIN,
                                 a1.Q_BLOCK, 3, e1.KAPPA * 3),
          f"saw {seen.get('consts')}")
    after = (e1.BASE_WIN, e1.RECENT_WIN, e1.FWD_WIN, e1.BLOCK, e1.W_SPEC, e1.TAU)
    check("monthly constants restored after the call", after == before,
          f"{before} -> {after}")

    # Restored even if the estimator raises.
    def boom(panel, seed=e1.SEED):
        raise RuntimeError("planted")
    e1.run_panel = boom
    try:
        a1.run_quarterly({"x": np.zeros(50)}, w=3)
    except RuntimeError:
        pass
    finally:
        e1.run_panel = real_run_panel
    after2 = (e1.BASE_WIN, e1.RECENT_WIN, e1.FWD_WIN, e1.BLOCK, e1.W_SPEC, e1.TAU)
    check("constants restored even when the estimator raises",
          after2 == before, f"{before} -> {after2}")


# ---------------------------------------------------------------------------
def _monthly_dates(n: int) -> list[str]:
    dates, y, m = [], 1992, 1
    for _ in range(n):
        dates.append(f"{y}-{m:02d}-01")
        m += 1
        if m == 13:
            m, y = 1, y + 1
    return dates


def leg3_planted_effect() -> None:
    """A mechanism that is really there must survive aggregation."""
    print("\nLEG 3 - planted effect survives aggregation")
    rng = np.random.default_rng(4242)
    dates = _monthly_dates(N_MONTHS)
    panel_q = {}
    for i in range(N_SECTORS):
        y = gen_regime_series(rng, n=N_MONTHS)
        panel_q[f"S{i:02d}"] = a1.to_quarterly(dates, y)
    res = a1.run_quarterly(panel_q, w=a1.W_PRIMARY)
    print(f"    pooled S={res['pooled_mean_spearman']:+.4f} "
          f"p={res['p_panel']:.4f} osc={res['n_oscillating']} {res['verdict']}")
    check("pooled Spearman positive on planted effect",
          res["pooled_mean_spearman"] > 0,
          f"got {res['pooled_mean_spearman']:+.4f}")
    check("at least 2 sectors classified oscillating after aggregation",
          res["n_oscillating"] >= 2, f"got {res['n_oscillating']}")


def leg4_planted_null() -> None:
    """No mechanism -> aggregation must not manufacture one."""
    print("\nLEG 4 - planted null stays null")
    rng = np.random.default_rng(99)
    dates = _monthly_dates(N_MONTHS)
    panel_q = {}
    for i in range(N_SECTORS):
        y = gen_null_series(rng, n=N_MONTHS)
        panel_q[f"N{i:02d}"] = a1.to_quarterly(dates, y)
    res = a1.run_quarterly(panel_q, w=a1.W_PRIMARY)
    print(f"    pooled S={res['pooled_mean_spearman']:+.4f} "
          f"p={res['p_panel']:.4f} osc={res['n_oscillating']} {res['verdict']}")
    check("no SUPPORT verdict on a planted null",
          res["verdict"] != "SUPPORT", f"got {res['verdict']}")


# ---------------------------------------------------------------------------
def leg5_rank_component() -> None:
    """The c2 comparison must be correctly signed and correctly thresholded."""
    print("\nLEG 5 - rank-correlation component wiring")
    a = np.array([0.5, 0.3, 0.1, -0.1, -0.3, -0.5, 0.2, 0.0])
    check("identical orderings -> +1", abs(e1.spearman(a, a) - 1.0) < 1e-12)
    check("reversed orderings -> -1", abs(e1.spearman(a, -a) + 1.0) < 1e-12)
    check("identical passes the 0.50 threshold",
          e1.spearman(a, a) >= a1.RANK_CORR_MIN)
    check("reversed fails the 0.50 threshold",
          not (e1.spearman(a, -a) >= a1.RANK_CORR_MIN))
    # A deliberately middling case must land on the correct side of 0.50.
    b = np.array([0.5, 0.3, 0.1, -0.1, -0.3, -0.5, 0.2, 0.0])[::-1].copy()
    rc = e1.spearman(a, b)
    check("threshold comparison is a >=, not a >",
          (rc >= a1.RANK_CORR_MIN) == (rc >= 0.50), f"rc={rc:+.4f}")
    check("pre-registered threshold is still 0.50 (firewall)",
          a1.RANK_CORR_MIN == 0.50, f"got {a1.RANK_CORR_MIN}")
    check("primary W is still 3 (firewall)", a1.W_PRIMARY == 3,
          f"got {a1.W_PRIMARY}")
    check("quarterly constants are the frozen /3 values (firewall)",
          (a1.Q_BASE_WIN, a1.Q_RECENT_WIN, a1.Q_FWD_WIN, a1.Q_BLOCK)
          == (20, 4, 4, 8),
          f"got {(a1.Q_BASE_WIN, a1.Q_RECENT_WIN, a1.Q_FWD_WIN, a1.Q_BLOCK)}")


def leg6_separation() -> None:
    """Can the statistic tell a planted effect from a planted null AT ALL?

    Legs 3 and 4 are one-sided and a blind pipeline passes both. This leg
    measures the thing that actually matters: the distance between the
    effect and null distributions of the pooled statistic. Monthly is the
    control - the same generators, the same estimator, three times the
    resolution - so a monthly separation with no quarterly separation
    localises the loss to aggregation rather than to a bug.

    AUC is the readout: the probability that a random effect panel outscores
    a random null panel. 0.50 = coin flip = no information. The bootstrap is
    not needed here (only pooled Spearman is read), so B is reduced for
    runtime; that changes no reported statistic.
    """
    print("\nLEG 6 - separation: is the test informative at all?")
    n_rep = 12
    dates = _monthly_dates(N_MONTHS)

    def pooled(panel, w, quarterly):
        if quarterly:
            return a1.run_quarterly(panel, w=w)["pooled_mean_spearman"]
        saved_w, saved_tau = e1.W_SPEC, e1.TAU
        try:
            e1.W_SPEC, e1.TAU = w, e1.KAPPA * w
            return e1.run_panel(panel, seed=e1.SEED)["pooled_mean_spearman"]
        finally:
            e1.W_SPEC, e1.TAU = saved_w, saved_tau

    def auc(eff, nul):
        wins = sum((e > n) + 0.5 * (e == n) for e in eff for n in nul)
        return wins / (len(eff) * len(nul))

    saved_b = e1.B_BOOT
    e1.B_BOOT = 200          # pooled S only; p-values unused in this leg
    try:
        res = {}
        for label, quarterly, w in (("monthly", False, 8), ("quarterly", True, a1.W_PRIMARY)):
            eff, nul = [], []
            for r in range(n_rep):
                rng_e = np.random.default_rng(9000 + r)
                rng_n = np.random.default_rng(19000 + r)
                pe = {f"e{i:02d}": gen_regime_series(rng_e, n=N_MONTHS)
                      for i in range(N_SECTORS)}
                pn = {f"n{i:02d}": gen_null_series(rng_n, n=N_MONTHS)
                      for i in range(N_SECTORS)}
                if quarterly:
                    pe = {k: a1.to_quarterly(dates, v) for k, v in pe.items()}
                    pn = {k: a1.to_quarterly(dates, v) for k, v in pn.items()}
                eff.append(pooled(pe, w, quarterly))
                nul.append(pooled(pn, w, quarterly))
            res[label] = (np.array(eff), np.array(nul), auc(eff, nul))
            e_, n_, a_ = res[label]
            print(f"    {label:9s} effect {e_.mean():+.4f} +/- {e_.std():.4f} | "
                  f"null {n_.mean():+.4f} +/- {n_.std():.4f} | AUC {a_:.3f}")
    finally:
        e1.B_BOOT = saved_b

    auc_m = res["monthly"][2]
    auc_q = res["quarterly"][2]
    # Control: the generators and estimator must separate at monthly
    # resolution, or nothing downstream is interpretable.
    check("monthly control separates (AUC >= 0.75)", auc_m >= 0.75,
          f"AUC={auc_m:.3f}")
    # The precondition on running A1 for real.
    check("quarterly separates well enough to interpret (AUC >= 0.70)",
          auc_q >= 0.70,
          f"AUC={auc_q:.3f} - if this fails, quarterly sampling destroys the "
          f"discriminating information and A1's answer is FAIL by power loss, "
          f"reportable WITHOUT running on real data")


def main() -> None:
    print("A1 SUITE - planted-ground-truth validation of the frequency test")
    leg1_aggregation()
    leg2_patching()
    leg3_planted_effect()
    leg4_planted_null()
    leg5_rank_component()
    leg6_separation()
    print("\n" + ("ALL PASS" if not FAILS else
                  f"FAILURES ({len(FAILS)}): " + "; ".join(FAILS)))
    sys.exit(0 if not FAILS else 1)


if __name__ == "__main__":
    main()
