"""e4_suite.py - E4 mechanism-validation suite (v1.9.5 experiment gate).

E4 is a self-contained simulation, so the suite validates the two things that
can silently break: (a) the VERDICT MACHINERY (paired test + relative-reduction
CI + the three-way rule) correctly distinguishes a genuinely-cheaper algorithm
from a tie from a worse one, at the real n = 1000 paired sample; (b) the
SIMULATION ENGINE runs, is deterministic under fixed seeds, satisfies the
source's phi-gated NO-HARM property (spectral == base-stock when persistence
stays below the engagement boundary), and genuinely DIFFERENTIATES (spectral
!= base-stock) once the persistence ramp crosses the boundary. The verdict
machinery is exercised on synthetic cost arrays with planted relationships
through the SAME statistics the real script uses (re-expressed identically).

Legs:
  1. PLANTED CHEAPER - synthetic paired costs where 'spectral' is genuinely
     ~8% cheaper than base-stock. Verdict must be SUPPORT.
  2. PLANTED TIE     - spectral == base-stock in expectation. Verdict must be
     REFUTE, and the paired-test false-positive rate ~nominal over 1000 null
     replications (accept 0.000 - 0.030 at alpha = 0.01).
  3. PLANTED WORSE   - spectral genuinely MORE expensive. Verdict REFUTE.
  4. ENGINE SMOKE    - real simulate() runs; deterministic under a fixed seed;
     NO-HARM: on an all-calm (phi below engagement) demand, spectral cost ==
     base-stock cost (alpha clips to 1); DIFFERENTIATION: on the real ramp
     demand (crosses the boundary), spectral cost != base-stock and full <=
     spectral; all mean costs finite and positive.

Firewall: suite failures fix CODE only, never rules/thresholds.
Usage: python analysis\\suites\\e4_suite.py    (no external data touched)
"""

from __future__ import annotations

import pathlib
import sys

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
from e4_beer_game import (BASE_DEMAND, N_PERIODS, PHI_ENG, PHI_LO,  # noqa: E402
                          SIGMA, make_demand, simulate)

N_PAIRED = 1000
BASE_SEED = 20260713
ALPHA = 0.01


def paired_p(x, y, base_seed=BASE_SEED, b=2000):
    d = y - x
    obs = d.mean()
    rng = np.random.default_rng(base_seed + 777)
    count = sum(1 for _ in range(b)
                if (rng.choice([-1.0, 1.0], size=len(d)) * d).mean() >= obs)
    return (count + 1) / (b + 1)


def rr_ci(x, y, base_seed=BASE_SEED, b=2000):
    rng = np.random.default_rng(base_seed + 888)
    rr = (y - x) / y
    boot = [rr[rng.integers(0, len(rr), len(rr))].mean() for _ in range(b)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return float(rr.mean()), float(lo), float(hi)


def verdict_of(spectral, basestock, full):
    p = paired_p(spectral, basestock)
    _, lo, _ = rr_ci(spectral, basestock)
    cheaper = spectral.mean() < basestock.mean() and p < ALPHA and lo > 0
    full_le = full.mean() <= spectral.mean()
    v = "SUPPORT" if cheaper and full_le else ("SUPPORT-PARTIAL" if cheaper else "REFUTE")
    return v, p, lo


def synth_costs(rng, rel, n=N_PAIRED, base=1000.0, paired_sd=60.0, run_sd=200.0):
    common = run_sd * rng.standard_normal(n)
    basestock = base + common + paired_sd * rng.standard_normal(n)
    spectral = base * (1 - rel) + common + paired_sd * rng.standard_normal(n)
    full = spectral - 5.0 + paired_sd * 0.5 * rng.standard_normal(n)
    return spectral, basestock, full


def leg1_cheaper() -> bool:
    rng = np.random.default_rng(41)
    s, b, f = synth_costs(rng, rel=0.08)
    v, p, lo = verdict_of(s, b, f)
    ok = v == "SUPPORT"
    print(f"LEG 1 planted cheaper (~8%): verdict={v} (p={p:.4f}, rr_lo={lo:+.3f}) "
          f"-> {'PASS' if ok else 'FAIL'}")
    return ok


def leg2_tie() -> bool:
    rng = np.random.default_rng(42)
    s, b, f = synth_costs(rng, rel=0.0)
    v, p, lo = verdict_of(s, b, f)
    verdict_ok = v == "REFUTE"
    print(f"LEG 2 planted tie: verdict={v} (p={p:.4f}, rr_lo={lo:+.3f}) "
          f"-> {'PASS' if verdict_ok else 'FAIL'}")
    rng_fp = np.random.default_rng(4242)
    hits = 0
    for _ in range(1000):
        ss, bb, _f = synth_costs(rng_fp, rel=0.0, n=N_PAIRED)
        p2 = paired_p(ss, bb, base_seed=int(rng_fp.integers(1, 2**31)))
        _, lo2, _ = rr_ci(ss, bb, base_seed=int(rng_fp.integers(1, 2**31)))
        if ss.mean() < bb.mean() and p2 < ALPHA and lo2 > 0:
            hits += 1
    fp = hits / 1000
    fp_ok = 0.0 <= fp <= 0.030
    print(f"LEG 2 FP rate: {hits}/1000 = {fp:.4f} (nominal {ALPHA}) "
          f"-> {'PASS' if fp_ok else 'FAIL'}")
    return verdict_ok and fp_ok


def leg3_worse() -> bool:
    rng = np.random.default_rng(43)
    s, b, f = synth_costs(rng, rel=-0.08)
    v, p, lo = verdict_of(s, b, f)
    ok = v == "REFUTE"
    print(f"LEG 3 planted worse: verdict={v} (p={p:.4f}, rr_lo={lo:+.3f}) "
          f"-> {'PASS' if ok else 'FAIL'}")
    return ok


def leg4_engine_smoke() -> bool:
    # deterministic under fixed seed
    d_a = make_demand(np.random.default_rng(7))
    d_b = make_demand(np.random.default_rng(7))
    det = np.allclose(d_a, d_b) and np.isclose(
        simulate(d_a, "spectral"), simulate(d_b, "spectral"))

    # NO-HARM: all-calm demand (constant low phi below engagement) -> spectral
    # must equal base-stock (alpha clips to 1). Build a calm AR(1) at PHI_LO.
    rng = np.random.default_rng(11)
    calm = np.empty(N_PERIODS)
    x = 0.0
    for t in range(N_PERIODS):
        x = PHI_LO * x + SIGMA * rng.standard_normal()
        calm[t] = max(0.0, BASE_DEMAND + x)
    bs_calm = simulate(calm, "basestock")
    sp_calm = simulate(calm, "spectral")
    no_harm = np.isclose(bs_calm, sp_calm, rtol=1e-9, atol=1e-6)

    # DIFFERENTIATION on the real ramp demand (crosses the boundary)
    means = {a: [] for a in ["naive", "basestock", "spectral", "full"]}
    for i in range(30):
        dem = make_demand(np.random.default_rng(1000 + i))
        for a in means:
            means[a].append(simulate(dem, a))
    m = {a: float(np.mean(v)) for a, v in means.items()}
    finite_pos = all(np.isfinite(v) and v > 0 for v in m.values())
    differentiates = not np.isclose(m["spectral"], m["basestock"], rtol=1e-6)
    full_le = m["full"] <= m["spectral"] * 1.0000001

    ok = det and no_harm and finite_pos and differentiates and full_le
    print(f"LEG 4 engine smoke: det={det}, no-harm(calm) bs={bs_calm:.1f} "
          f"sp={sp_calm:.1f} eq={no_harm}; ramp means naive {m['naive']:.0f}/"
          f"base-stock {m['basestock']:.0f}/spectral {m['spectral']:.0f}/"
          f"full {m['full']:.0f}, differentiates={differentiates}, "
          f"full<=spectral={full_le} -> {'PASS' if ok else 'FAIL'}")
    return ok


def main() -> int:
    print(f"E4 suite: verdict machinery at n={N_PAIRED} paired + engine smoke "
          f"(phi_eng={PHI_ENG:.3f})")
    r1 = leg1_cheaper()
    r2 = leg2_tie()
    r3 = leg3_worse()
    r4 = leg4_engine_smoke()
    all_pass = r1 and r2 and r3 and r4
    print(f"\nALL PASS: {all_pass}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
