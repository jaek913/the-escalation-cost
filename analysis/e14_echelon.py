"""e14_echelon.py - E14 echelon variance decomposition (The Escalation Cost).

DESIGN Section 18 (amendment 2026-07-25, classification + reporting commitment)
and DESIGN Section 20 (amendment 2026-07-25c, operator specification frozen).

CLASSIFICATION: DESCRIPTIVE / STRUCTURAL CHARACTERIZATION. NO verdict is
emitted. Overlapping intervals yield INCONCLUSIVE, which is a statement about
RESOLUTION and never a negative finding.

Operator, frozen at DESIGN 20 before this file existed:
- Observable: first difference of natural log (monthly growth rate). 20.1.
- Statistic: ratio of variances between adjacent chain steps, common sample.
- Uncertainty: stationary block bootstrap, mean block 12 months, 10,000
  resamples, 95 percent percentile intervals, JOINT across the chain. 20.3.
- DISTINGUISHED iff exactly one step's CI lower bound exceeds every other
  step's CI upper bound; otherwise INCONCLUSIVE. 20.2.
- Common window built on LEVELS then differenced; realised n asserted. 20.5.

Reporting commitment (DESIGN 18.2 a-f), all reported regardless of outcome:
(a) each adjacent-step variance ratio with bootstrap interval
(b) compound product of the step ratios
(c) direct end-to-end ratio
(d) discrepancy between (b) and (c)  -- SEE DESIGN 20.4: this is an ALGEBRAIC
    IDENTITY and is exactly zero by construction. It carries NO information
    about the data. It is retained because the commitment binds, and reported
    only as what it is. The bootstrap-distribution agreement of (b) and (c) is
    NOT a companion check: it is the same identity and cannot fail. The real
    resampler self-test is CROSS-SERIES CORRELATION PRESERVATION (DESIGN 20.4
    correction), which per-series resampling collapses toward zero.
(e) the same excluding 2020-01..2021-12
(f) the sector arm (final step replaced by durable goods new orders)

SCOPE, and it must appear in the write-up: this locates WHERE amplification
concentrates. It does NOT establish that the measurement mechanism CAUSED the
concentration. Concentration at the ordering step is CONSISTENT WITH the
modelled mechanism and does not exclude other explanations.

Usage:
  python analysis\\e14_echelon.py --suite   synthetic suite, no store access
  python analysis\\e14_echelon.py           real run, writes outputs/e14_echelon.json
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "analysis" / "outputs"
STORE = pathlib.Path(os.environ.get(
    "EC_STORE", r"C:\Users\jaek9\Documents\LaggingTruth\The-Escalation-Cost"))
RAW = STORE / "raw"

# ---------------------------------------------------------------------------
# FROZEN OPERATOR CONSTANTS (DESIGN 20.3, 20.5). Changing any of these after
# the first real run is a dated DESIGN amendment, never an edit here.
MEAN_BLOCK = 12          # months; annual dependence in monthly flow data
N_BOOT = 10000           # resamples
CI_LEVEL = 95.0          # percent, percentile interval
SEED = 20260725          # recorded in the output
EXPECTED_N_CHANGES = 411
EXPECTED_FIRST_CHANGE = "1992-03-01"
EXPECTED_LAST_CHANGE = "2026-05-01"
COVID_FROM, COVID_TO = "2020-01-01", "2021-12-01"

# Chain, in order. DESIGN 18.2.
CHAIN = [
    ("retail", "fred_MRTSSM44000USS.csv"),
    ("wholesale", "fred_S42SMSM144SCEN.csv"),
    ("shipments", "fred_AMTMVS.csv"),
    ("orders", "fred_AMTMNO.csv"),
]
SECTOR_ARM_LAST = ("orders_durable", "fred_DGORDER.csv")

# SHA256 of every input, from the committed data/SOURCES.md at commit a4dd055.
# A changed input FAILS LOUDLY rather than silently producing a different
# number under the same experiment id.
INPUT_SHA256 = {
    "fred_MRTSSM44000USS.csv":
        "a497e0a523d5f55118796f60379604c1ed50f1996705188ac77a907dbb2654e4",
    "fred_S42SMSM144SCEN.csv":
        "943568eae777b0f363b1242d463a866f3f34dbb516a5735ad90e0146507b6bc7",
    "fred_AMTMVS.csv":
        "d1b343e91c3fa3b4d4010c49cef5900be038d920373e0db9a8c34da37eb2a703",
    "fred_AMTMNO.csv":
        "83373afa9ce779e45952943be547f0ea422cfe3cd89a8d2bfc251a22491766bf",
    "fred_DGORDER.csv":
        "b0606fb7cfce5f7862b9d1487ad3ad9f0400c2c0a0756d9472b4bd7b73fda040",
}


# ---------------------------------------------------------------------------
# I/O

def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def md5(path: pathlib.Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_fred_csv(path: pathlib.Path) -> dict:
    """date string -> float. A non-numeric observation is a hard failure.

    FRED writes a bare period for a gap. Parsed loosely that becomes a string
    or a NaN and poisons a variance silently; here it stops the run.
    """
    out = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    for ln in lines[1:]:
        if not ln.strip():
            continue
        parts = ln.split(",")
        if len(parts) != 2:
            raise ValueError(f"{path.name}: malformed row: {ln!r}")
        d, v = parts[0].strip(), parts[1].strip()
        try:
            val = float(v)
        except ValueError:
            raise ValueError(f"{path.name}: non-numeric observation at {d}: {v!r}")
        if not math.isfinite(val) or val <= 0.0:
            # log-differencing requires strictly positive levels
            raise ValueError(f"{path.name}: non-positive or non-finite at {d}: {val}")
        out[d] = val
    if not out:
        raise ValueError(f"{path.name}: no observations")
    return out


# ---------------------------------------------------------------------------
# Operator

def log_changes(series: dict, dates: list) -> np.ndarray:
    """Log differences across a PRE-INTERSECTED, sorted date list (DESIGN 20.5)."""
    lv = np.array([series[d] for d in dates], dtype=np.float64)
    return np.diff(np.log(lv))


def build_panel(series_by_name: dict) -> tuple:
    """Intersect on LEVELS, then difference. Returns (change_dates, X)."""
    common = None
    for s in series_by_name.values():
        common = set(s) if common is None else (common & set(s))
    level_dates = sorted(common)
    if len(level_dates) < 3:
        raise ValueError("common window too short")
    change_dates = level_dates[1:]
    X = np.column_stack([log_changes(s, level_dates)
                         for s in series_by_name.values()])
    return change_dates, X


def ratios_from_variances(v: np.ndarray) -> tuple:
    """v shape (..., k). Returns (step_ratios, compound, end_to_end)."""
    step = v[..., 1:] / v[..., :-1]
    compound = np.prod(step, axis=-1)
    e2e = v[..., -1] / v[..., 0]
    return step, compound, e2e


def point_estimates(X: np.ndarray) -> dict:
    v = X.var(axis=0, ddof=1)
    step, compound, e2e = ratios_from_variances(v)
    return dict(variances=v, step=step, compound=float(compound),
                end_to_end=float(e2e))


def stationary_bootstrap_indices(n: int, B: int, mean_block: int,
                                 rng: np.random.Generator) -> np.ndarray:
    """Politis-Romano stationary bootstrap index matrix, shape (B, n).

    Geometric block lengths with mean `mean_block`, wrap-around continuation.
    """
    p = 1.0 / mean_block
    idx = np.empty((B, n), dtype=np.int64)
    idx[:, 0] = rng.integers(0, n, size=B)
    restart = rng.random((B, n)) < p
    fresh = rng.integers(0, n, size=(B, n))
    for t in range(1, n):
        idx[:, t] = np.where(restart[:, t], fresh[:, t], (idx[:, t - 1] + 1) % n)
    return idx


def bootstrap(X: np.ndarray, B: int, mean_block: int, seed: int,
              chunk: int = 1000) -> dict:
    """JOINT stationary bootstrap (DESIGN 20.3): one set of DATE blocks is
    applied to EVERY series, preserving cross-series co-movement."""
    n, k = X.shape
    rng = np.random.default_rng(seed)
    steps, comps, e2es, corrs = [], [], [], []
    done = 0
    while done < B:
        b = min(chunk, B - done)
        idx = stationary_bootstrap_indices(n, b, mean_block, rng)
        Xb = X[idx]                       # (b, n, k) - SAME idx for all series
        v = Xb.var(axis=1, ddof=1)        # (b, k)
        st, cp, ee = ratios_from_variances(v)
        steps.append(st); comps.append(cp); e2es.append(ee)
        corrs.append(adjacent_corr(Xb))
        done += b
    return dict(step=np.vstack(steps), compound=np.concatenate(comps),
                end_to_end=np.concatenate(e2es), adj_corr=np.vstack(corrs))


def adjacent_corr(A: np.ndarray) -> np.ndarray:
    """Correlation of each adjacent pair of columns. A is (b, n, k) or (n, k).

    This is the RESAMPLER SELF-TEST statistic (DESIGN 20.4 correction). Joint
    resampling preserves within-month co-movement, so the bootstrap mean sits
    on the sample value; per-series resampling collapses it toward zero. The
    telescoping identity cannot make that distinction - this can.
    """
    if A.ndim == 2:
        A = A[None, :, :]
    C = A - A.mean(axis=1, keepdims=True)
    num = (C[:, :, :-1] * C[:, :, 1:]).sum(axis=1)
    den = np.sqrt((C[:, :, :-1] ** 2).sum(axis=1) * (C[:, :, 1:] ** 2).sum(axis=1))
    return num / den


def ci(a: np.ndarray, level: float = CI_LEVEL) -> tuple:
    lo = (100.0 - level) / 2.0
    return float(np.percentile(a, lo)), float(np.percentile(a, 100.0 - lo))


def classify(step_ci: list) -> dict:
    """DESIGN 20.2: DISTINGUISHED iff EXACTLY ONE step's CI lower bound
    exceeds EVERY other step's CI upper bound. Otherwise INCONCLUSIVE."""
    seps = []
    for i, (lo_i, _) in enumerate(step_ci):
        others_hi = [hi for j, (_, hi) in enumerate(step_ci) if j != i]
        if others_hi and lo_i > max(others_hi):
            seps.append(i)
    if len(seps) == 1:
        return dict(result="DISTINGUISHED", dominant_step_index=seps[0])
    return dict(result="INCONCLUSIVE", dominant_step_index=None)


def analyse(change_dates: list, X: np.ndarray, labels: list, B: int,
            seed: int) -> dict:
    pe = point_estimates(X)
    bs = bootstrap(X, B, MEAN_BLOCK, seed)
    step_ci = [ci(bs["step"][:, i]) for i in range(bs["step"].shape[1])]
    verdict = classify(step_ci)
    # DESIGN 20.4: (d) is an identity; report it as such. The resampler
    # self-test is CORRELATION PRESERVATION, not the (b)/(c) distributions -
    # those agree by the same identity and cannot fail.
    discrepancy = pe["compound"] - pe["end_to_end"]
    samp_corr = adjacent_corr(X)[0]
    boot_corr = bs["adj_corr"].mean(axis=0)
    corr_dev = float(np.max(np.abs(boot_corr - samp_corr)))
    return dict(
        n_changes=len(change_dates),
        first_change=change_dates[0], last_change=change_dates[-1],
        step_labels=[f"{labels[i]}->{labels[i+1]}" for i in range(len(labels) - 1)],
        step_ratio=[float(x) for x in pe["step"]],
        step_ci_low=[c[0] for c in step_ci],
        step_ci_high=[c[1] for c in step_ci],
        compound_product=pe["compound"],
        end_to_end=pe["end_to_end"],
        identity_discrepancy=float(discrepancy),
        sample_adjacent_corr=[float(x) for x in samp_corr],
        bootstrap_mean_adjacent_corr=[float(x) for x in boot_corr],
        resampler_corr_max_deviation=corr_dev,
        result=verdict["result"],
        dominant_step_index=verdict["dominant_step_index"],
        dominant_step=(None if verdict["dominant_step_index"] is None
                       else f"{labels[verdict['dominant_step_index']]}->"
                            f"{labels[verdict['dominant_step_index']+1]}"),
    )


# ---------------------------------------------------------------------------
# Synthetic suite (DESIGN 18.2 bias firewall)

def synth_chain(alphas: list, n: int, rng: np.random.Generator,
                phi: float = 0.3, noise: float = 0.05) -> np.ndarray:
    """Chain with PLANTED per-step amplification.

    g_1 is AR(1) so the block bootstrap has serial dependence to carry;
    g_{k+1} = alpha_k * g_k + independent noise, so the planted population
    variance ratio at step k is alpha_k^2 + noise^2 / Var(g_k).
    """
    g = np.empty(n)
    g[0] = rng.normal(0, 1)
    for t in range(1, n):
        g[t] = phi * g[t - 1] + rng.normal(0, 1)
    cols = [g]
    for a in alphas:
        cols.append(a * cols[-1] + rng.normal(0, noise, size=n))
    return np.column_stack(cols)


def suite() -> int:
    print("=" * 78)
    print("E14 SYNTHETIC SUITE - operator frozen at DESIGN Section 20")
    print(f"  n = {EXPECTED_N_CHANGES} (the realised change count), "
          f"mean block = {MEAN_BLOCK}")
    print("=" * 78)
    fails = []

    def check(label, cond, detail=""):
        print(f"  {'PASS' if cond else 'FAIL'}  {label}"
              f"{'  ' + detail if detail else ''}")
        if not cond:
            fails.append(label)

    n = EXPECTED_N_CHANGES
    labels = ["s1", "s2", "s3", "s4"]

    # -- LEG 1: determinism -------------------------------------------------
    rng = np.random.default_rng(1)
    X = synth_chain([1.0, 1.0, 1.0], n, rng)
    a1 = analyse([f"d{i}" for i in range(n)], X, labels, 500, SEED)
    a2 = analyse([f"d{i}" for i in range(n)], X, labels, 500, SEED)
    check("determinism: identical seed reproduces identical intervals",
          a1["step_ci_low"] == a2["step_ci_low"]
          and a1["step_ci_high"] == a2["step_ci_high"])

    # -- LEG 2: telescoping identity (DESIGN 20.4) --------------------------
    check("(d) is an algebraic identity: compound == end-to-end",
          abs(a1["identity_discrepancy"]) < 1e-9,
          f"discrepancy {a1['identity_discrepancy']:.3e}")

    # -- LEG 3: resampler self-test - joint resampling preserves co-movement
    check("resampler self-test: joint resampling preserves cross-series corr",
          a1["resampler_corr_max_deviation"] < 0.02,
          f"max deviation {a1['resampler_corr_max_deviation']:.4f}")

    # -- LEG 3b: THE SELF-TEST IS WATCHED TO FAIL --------------------------
    # A check watched only to pass is not a tested check. The identity in
    # LEG 2 CANNOT fail here - it holds within every resample however the
    # indices were drawn - which is exactly why DESIGN 20.4 was corrected and
    # why it is not the self-test. This one can fail, and is made to.
    rng_bad = np.random.default_rng(7)
    ia = stationary_bootstrap_indices(n, 400, MEAN_BLOCK, rng_bad)
    ib = stationary_bootstrap_indices(n, 400, MEAN_BLOCK, rng_bad)
    Xbad = np.stack([X[ia][:, :, 0], X[ib][:, :, 1],
                     X[ia][:, :, 2], X[ib][:, :, 3]], axis=2)
    samp = adjacent_corr(X)[0]
    bad_dev = float(np.max(np.abs(adjacent_corr(Xbad).mean(axis=0) - samp)))
    _, cp_b, ee_b = ratios_from_variances(Xbad.var(axis=1, ddof=1))
    id_blind = float(np.max(np.abs(cp_b - ee_b)))
    check("self-test IS TESTED: fires on deliberately broken per-series draws",
          bad_dev > 0.10, f"deviation under broken resampling {bad_dev:.4f}")
    check("and the telescoping identity is BLIND to that same defect",
          id_blind < 1e-9,
          f"identity still {id_blind:.2e} - why it is not a self-test (DESIGN 20.4)")

    # -- LEG 4: PLANTED DOMINANT recovered at the real n --------------------
    reps, B_pow = 40, 2000
    planted = [1.02, 1.75, 1.02]     # step 2 dominant
    hits, dom_right = 0, 0
    for r in range(reps):
        rr = np.random.default_rng(1000 + r)
        Xp = synth_chain(planted, n, rr)
        a = analyse([f"d{i}" for i in range(n)], Xp, labels, B_pow, SEED + r)
        if a["result"] == "DISTINGUISHED":
            hits += 1
            if a["dominant_step_index"] == 1:
                dom_right += 1
    rate = hits / reps
    check("planted DOMINANT step recovered at the real n (rate >= 0.90)",
          rate >= 0.90, f"rate {rate:.2f} ({hits}/{reps})")
    check("recovered step is the PLANTED one, never a different one",
          dom_right == hits, f"{dom_right}/{hits} correct")

    # -- LEG 5: PLANTED EVEN returns INCONCLUSIVE ---------------------------
    fp = 0
    for r in range(reps):
        rr = np.random.default_rng(5000 + r)
        Xe = synth_chain([1.0, 1.0, 1.0], n, rr)
        a = analyse([f"d{i}" for i in range(n)], Xe, labels, B_pow, SEED + r)
        if a["result"] == "DISTINGUISHED":
            fp += 1
    fpr = fp / reps
    check("planted EVEN distribution returns INCONCLUSIVE (false rate <= 0.05)",
          fpr <= 0.05, f"false-DISTINGUISHED rate {fpr:.2f} ({fp}/{reps})")

    # -- LEG 6: RESOLUTION CHARACTERIZATION --------------------------------
    # A suite that only passes on easy data has not established resolution.
    # The legs above use near-deterministic steps (adjacent correlation about
    # 0.999), which is optimistic. Here the instrument is characterised across
    # step noise AND planted dominance, and the numbers are REPORTED. Only one
    # thing is asserted: at dominance 1.0 - a genuinely even chain - the
    # instrument must not manufacture a concentration at ANY noise level.
    print("\n  RESOLUTION (recovery rate of the planted dominant step, "
          "20 reps each):")
    print("    noise  adj.corr |  " + "  ".join(f"a={a:<4}" for a in
                                                (1.0, 1.25, 1.5, 1.75)))
    even_rates = []
    for noise in (0.05, 0.5, 1.0):
        rr0 = np.random.default_rng(90)
        ac = float(np.mean(adjacent_corr(synth_chain([1.5, 1.5, 1.5], n, rr0,
                                                     noise=noise))[0]))
        cells = []
        for a in (1.0, 1.25, 1.5, 1.75):
            hit = 0
            for r in range(20):
                rr = np.random.default_rng(7000 + r)
                Xr = synth_chain([1.0, a, 1.0], n, rr, noise=noise)
                res = analyse([f"d{i}" for i in range(n)], Xr, labels, 1000,
                              SEED + r)
                if res["result"] == "DISTINGUISHED" and \
                        res["dominant_step_index"] == 1:
                    hit += 1
            cells.append(hit / 20)
        even_rates.append(cells[0])
        print(f"    {noise:<6} {ac:<8.3f} |  " +
              "  ".join(f"{c:<6.2f}" for c in cells))
    check("even chain (dominance 1.0) never manufactures concentration, "
          "at ANY noise level", max(even_rates) <= 0.10,
          f"max false rate {max(even_rates):.2f}")

    # -- LEG 7: input guards ------------------------------------------------
    try:
        read_fred_csv_from_text("observation_date,X\n1992-01-01,.\n")
        check("non-numeric observation rejected", False, "no error raised")
    except ValueError as e:
        check("non-numeric observation rejected", "non-numeric" in str(e))

    try:
        read_fred_csv_from_text("observation_date,X\n1992-01-01,0\n")
        check("non-positive level rejected (log requires positive)", False)
    except ValueError as e:
        check("non-positive level rejected (log requires positive)",
              "non-positive" in str(e))

    print("=" * 78)
    print("ALL PASS" if not fails else f"FAILURES: {fails}")
    print("=" * 78)
    return 0 if not fails else 1


def read_fred_csv_from_text(text: str) -> dict:
    """Suite helper: same parser contract, in-memory."""
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False,
                                     encoding="utf-8") as fh:
        fh.write(text)
        p = pathlib.Path(fh.name)
    try:
        return read_fred_csv(p)
    finally:
        p.unlink()


# ---------------------------------------------------------------------------
# Real run

def real_run() -> int:
    print("E14 echelon variance decomposition - REAL RUN")
    print(f"  store: {RAW}")

    for fname, want in INPUT_SHA256.items():
        p = RAW / fname
        if not p.exists():
            raise SystemExit(f"missing input: {p}")
        got = sha256(p)
        if got != want:
            raise SystemExit(
                f"INPUT HASH MISMATCH {fname}\n  registered {want}\n  on-disk   {got}")
    print(f"  all {len(INPUT_SHA256)} input hashes match SOURCES.md")

    raw = {name: read_fred_csv(RAW / f) for name, f in CHAIN}
    labels = [name for name, _ in CHAIN]
    change_dates, X = build_panel(raw)

    if (len(change_dates) != EXPECTED_N_CHANGES
            or change_dates[0] != EXPECTED_FIRST_CHANGE
            or change_dates[-1] != EXPECTED_LAST_CHANGE):
        raise SystemExit(
            f"REALISED SAMPLE MISMATCH (DESIGN 20.5): got n={len(change_dates)} "
            f"{change_dates[0]}..{change_dates[-1]}; expected "
            f"n={EXPECTED_N_CHANGES} {EXPECTED_FIRST_CHANGE}..{EXPECTED_LAST_CHANGE}")

    full = analyse(change_dates, X, labels, N_BOOT, SEED)

    keep = [i for i, d in enumerate(change_dates)
            if not (COVID_FROM <= d <= COVID_TO)]
    ex_dates = [change_dates[i] for i in keep]
    ex = analyse(ex_dates, X[keep], labels, N_BOOT, SEED)

    arm_raw = {name: raw[name] for name, _ in CHAIN[:-1]}
    arm_raw[SECTOR_ARM_LAST[0]] = read_fred_csv(RAW / SECTOR_ARM_LAST[1])
    arm_labels = labels[:-1] + [SECTOR_ARM_LAST[0]]
    arm_dates, XA = build_panel(arm_raw)
    arm = analyse(arm_dates, XA, arm_labels, N_BOOT, SEED)

    result = dict(
        experiment="E14",
        design_pin=md5(ROOT / "DESIGN.md"),
        classification="DESCRIPTIVE / STRUCTURAL CHARACTERIZATION - no verdict",
        operator=dict(observable="first difference of natural log",
                      statistic="variance ratio between adjacent chain steps",
                      mean_block=MEAN_BLOCK, n_boot=N_BOOT,
                      ci_level=CI_LEVEL, seed=SEED,
                      resampling="joint across the chain"),
        inputs={k: v for k, v in sorted(INPUT_SHA256.items())},
        full_sample=full,
        covid_excluded=ex,
        sector_arm=arm,
        scope=("Locates WHERE amplification concentrates. Does NOT establish "
               "that the measurement mechanism CAUSED the concentration."),
        identity_note=("compound_product and end_to_end are algebraically "
                       "identical on a common sample; identity_discrepancy is "
                       "zero by construction and carries no information about "
                       "the data (DESIGN 20.4)."),
    )
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "e14_echelon.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                    encoding="ascii", newline="\n")
    print(f"  wrote {path}")
    for tag, blk in (("FULL", full), ("COVID-EXCLUDED", ex), ("SECTOR ARM", arm)):
        print(f"\n  {tag}: n={blk['n_changes']} "
              f"{blk['first_change']}..{blk['last_change']}  -> {blk['result']}")
        for i, lab in enumerate(blk["step_labels"]):
            print(f"    {lab:24s} ratio {blk['step_ratio'][i]:8.4f}  "
                  f"CI [{blk['step_ci_low'][i]:.4f}, {blk['step_ci_high'][i]:.4f}]")
        print(f"    compound {blk['compound_product']:.6f}  "
              f"end-to-end {blk['end_to_end']:.6f}  "
              f"identity discrepancy {blk['identity_discrepancy']:.3e}")
    return 0


def main() -> int:
    if "--suite" in sys.argv:
        return suite()
    return real_run()


if __name__ == "__main__":
    sys.exit(main())
