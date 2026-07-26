"""e14_resolution.py - POST-HOC instrument resolution characterization for E14.

DESIGN Section 21 (amendment 2026-07-25d). **POST-HOC. EXPLORATORY.**
Specified AFTER the E14 real run and after seeing its result.

WHAT THIS IS. E14 returned INCONCLUSIVE on the registered chain. Under a
characterization design the value of an INCONCLUSIVE result is the statement of
what magnitude WOULD have been visible. The pre-registered suite in
e14_echelon.py measured resolution at adjacent-series correlations of 1.000,
0.976 and 0.920; the realised data sits at 0.629 / 0.768 / 0.685 (full) and
0.442 / 0.623 / 0.614 (COVID-excluded). EVERY realised coupling is BELOW the
lowest value tested, so that resolution statement does not transfer. This
script measures resolution IN THE REGIME THE DATA ACTUALLY OCCUPIES.

WHAT THIS IS NOT. It does not re-run E14. It does not modify or regenerate
e14_echelon.py or its output artifact - that script stays byte-frozen and its
result is untouched; it is imported READ ONLY. It cannot change a step ratio,
an interval or a classification. It characterizes the INSTRUMENT, never the
chain, and no sentence in the manuscript may attribute a finding about
amplification to it.

METHOD. Semi-parametric. The REAL retail log-change series is the driver, so
its serial dependence and distribution are exactly the data's own rather than
an assumed AR(1). Downstream steps are constructed to hit a TARGET variance
ratio R and a TARGET adjacent correlation rho exactly:
    a     = rho * sqrt(R)                       (amplification coefficient)
    var_e = R * var(upstream) * (1 - rho^2)     (independent noise variance)
which gives var(downstream)/var(upstream) = R and corr(up, down) = rho.
Steps 1 and 2 are held at their REALISED ratios and correlations; only the
ordering-step ratio is swept. Disclosed limitation: the injected noise is iid,
so downstream serial dependence is carried by the driver alone and is somewhat
weaker than the real downstream series. That makes bootstrap intervals slightly
NARROWER than reality, so the recovery rates below are, if anything,
OPTIMISTIC - the honest direction for a resolution bound.

Usage:
  python analysis\\e14_resolution.py
"""

from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from e14_echelon import (  # noqa: E402  - frozen experiment module, READ ONLY
    CHAIN, INPUT_SHA256, MEAN_BLOCK, RAW, SEED, adjacent_corr, analyse,
    build_panel, read_fred_csv, sha256, COVID_FROM, COVID_TO,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "analysis" / "outputs"

REPS = 100
B_RES = 2000
GRID = [1.0, 1.5, 2.0, 2.3667, 3.0, 3.1382, 4.0, 5.0, 6.0, 8.0]
LABELS = ["s1", "s2", "s3", "s4"]


def synth_from_driver(driver: np.ndarray, ratios: list, rhos: list,
                      rng: np.random.Generator) -> np.ndarray:
    """Build a chain on a REAL driver hitting target ratios and correlations."""
    cols = [driver]
    for R, rho in zip(ratios, rhos):
        up = cols[-1]
        vu = up.var(ddof=1)
        a = rho * np.sqrt(R)
        sd_e = np.sqrt(max(R * vu * (1.0 - rho ** 2), 0.0))
        cols.append(a * up + rng.normal(0.0, sd_e, size=up.size))
    return np.column_stack(cols)


def characterise(name: str, driver: np.ndarray, r1: float, r2: float,
                 rhos: list, n: int) -> dict:
    print(f"\n{'=' * 78}\n{name}: n={n}  realised rho={[round(r, 3) for r in rhos]}"
          f"  realised R1={r1:.4f} R2={r2:.4f}\n{'=' * 78}")
    print(f"  {'R3 (ordering step)':>20} | {'recovery rate':>14} | note")
    rows = []
    for R3 in GRID:
        hit = 0
        for r in range(REPS):
            rng = np.random.default_rng(400000 + r)
            X = synth_from_driver(driver, [r1, r2, R3], rhos, rng)
            a = analyse([f"d{i}" for i in range(n)], X, LABELS, B_RES, SEED + r)
            if a["result"] == "DISTINGUISHED" and a["dominant_step_index"] == 2:
                hit += 1
        rate = hit / REPS
        note = ""
        if abs(R3 - 2.3667) < 1e-6:
            note = "<-- OBSERVED, full sample"
        elif abs(R3 - 3.1382) < 1e-6:
            note = "<-- OBSERVED, COVID-excluded"
        elif R3 == 1.0:
            note = "no concentration planted (false-positive rate)"
        print(f"  {R3:>20.4f} | {rate:>14.2f} | {note}")
        rows.append(dict(r3=R3, recovery_rate=rate, note=note))
    thr = next((r["r3"] for r in rows if r["recovery_rate"] >= 0.80), None)
    print(f"\n  smallest swept R3 reaching 0.80 recovery: "
          f"{thr if thr is not None else 'NOT REACHED on this grid'}")
    return dict(configuration=name, n=n, realised_rho=rhos,
                realised_r1=r1, realised_r2=r2, reps=REPS, n_boot=B_RES,
                grid=rows, r3_at_80pct_recovery=thr)


def main() -> int:
    print("POST-HOC INSTRUMENT RESOLUTION CHARACTERIZATION (DESIGN 21)")
    print("EXPLORATORY. Specified after the E14 result. Changes no reported number.")

    # The characterization must run on the SAME bytes E14 ran on, or it
    # describes the resolution of a different dataset.
    for fname, want in INPUT_SHA256.items():
        got = sha256(RAW / fname)
        if got != want:
            raise SystemExit(f"INPUT HASH MISMATCH {fname}: {got} != {want}")
    print(f"  all {len(INPUT_SHA256)} input hashes match E14's frozen inputs")

    raw = {name: read_fred_csv(RAW / f) for name, f in CHAIN}
    dates, X = build_panel(raw)
    corr_full = adjacent_corr(X)[0]
    v = X.var(axis=0, ddof=1)
    r1_full, r2_full = float(v[1] / v[0]), float(v[2] / v[1])

    keep = [i for i, d in enumerate(dates) if not (COVID_FROM <= d <= COVID_TO)]
    Xe = X[keep]
    corr_ex = adjacent_corr(Xe)[0]
    ve = Xe.var(axis=0, ddof=1)
    r1_ex, r2_ex = float(ve[1] / ve[0]), float(ve[2] / ve[1])

    full = characterise("FULL SAMPLE", X[:, 0], r1_full, r2_full,
                        [float(c) for c in corr_full], X.shape[0])
    excl = characterise("COVID-EXCLUDED", Xe[:, 0], r1_ex, r2_ex,
                        [float(c) for c in corr_ex], Xe.shape[0])

    result = dict(
        characterization="E14 instrument resolution at realised coupling",
        design_pin="c81d4c6eb31aa74e51db4c3108dc63db",  # FROZEN literal (see
        # e14_echelon.py): a live md5 of DESIGN.md cannot reproduce
        # byte-identically under the rerun check once DESIGN moves on.
        status="POST-HOC / EXPLORATORY - specified after the E14 result (DESIGN 21)",
        changes_no_reported_number=True,
        method=("semi-parametric: real retail log changes as driver; downstream "
                "steps constructed to hit target variance ratio and target "
                "adjacent correlation exactly; only the ordering-step ratio swept"),
        disclosed_limitation=("injected noise is iid, so downstream serial "
                              "dependence comes from the driver alone and is "
                              "weaker than the real downstream series; bootstrap "
                              "intervals are therefore slightly narrower than "
                              "reality and these recovery rates are OPTIMISTIC"),
        full_sample=full,
        covid_excluded=excl,
    )
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "e14_resolution.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                    encoding="ascii", newline="\n")
    print(f"\nwrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
