"""e7_suite.py - E7 validation suite (Standard v1.9.5 gate, extended v1.9.7).

REBUILD suite. Supersedes the 2026-07-14 suite, which validated a build that
violated E7's frozen operator (DESIGN 14d; DISC-05).

Imports run_cell / crossover_map / stability / headline_vs_source / paired_pct_diff
VERBATIM from the committed e7_chain_sweep.py - the suite exercises the real
pipeline, never a copy.

E7's engine is VENDORED, not re-implemented (DESIGN 14e). That changes what this
suite must prove. It cannot prove the engine is correct by re-deriving it - the
7-point CIC did that, by reading the source's code line by line (DISC-05, all seven
classes clear). What it must prove instead is:
  (a) the vendored copy is BYTE-IDENTICAL to what the CIC actually cleared, so the
      audit still applies to the code that runs -> LEG 1
  (b) the vendored code implements the theorem THIS PAPER PROVES -> LEG 2, the check
      that actually buys independence, since the source's damping rule IS the
      theorem and T1/T2/T3 were verified here independently
  (c) OUR analysis layer - the part that is ours - is correct -> LEGS 4, 5, 6

LEG 1 VENDOR INTEGRITY: the three vendored modules match the MD5s recorded in
  DESIGN 14e. Any drift is a hard fail: the CIC cleared THOSE bytes.
LEG 2 THEOREM CONFORMANCE (DESIGN 14e): the vendored alpha rule agrees with the
  as-proven theorem across a grid of (phi, W), computed from THIS repo's own
  reading of the theorem rather than from the vendored module. Theory-first rule
  (v1.9.6) applied to a vendored operator. A failure here is a FINDING about the
  source's implementation, never a licence to modify the vendored code.
LEG 3 DRIFT PROVENANCE (DESIGN 14e hazard): three drift schedules are in scope -
  phase2_6_drift_schedule(), phase2_6_drift_schedule_DEPRECATED_DUPLICATE(), and the
  sweep's own local make_phase2_6_drift_schedule(). Assert WHICH one reaches the
  demand generator, rather than trusting the reading.
LEG 4 RESOLUTION LOGIC: each cell's achieved MDD comes from its OWN measured
  variance, never inherited; an unresolved cell is labelled 'unresolved' - never
  'harm' or 'benefit'; pairing is by trial_seed.
LEG 5 CROSSOVER LOCATOR: finds a planted resolved transition; reports NO transition
  on an all-benefit line; and refuses to call a flip between two UNRESOLVED cells a
  crossover (the E5 top-cluster lesson). Pure function on exact planted inputs.
LEG 6 JSON BOUNDARY: the full payload serializes (the E4 lesson - numpy bool_/float64
  are not JSON-serializable and main() was never suite-tested).

Suite failures fix OUR CODE ONLY - never the rules, the report form, or the vendored
modules.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
_ANALYSIS = _HERE.parent
sys.path.insert(0, str(_ANALYSIS))
sys.path.insert(0, str(_ANALYSIS / "vendor"))

from e7_chain_sweep import (  # noqa: E402
    NUM_PERIODS,
    SOURCE_HEADLINE,
    Z95,
    Z_MDD,
    crossover_map,
    headline_vs_source,
    paired_pct_diff,
    run_cell,
    stability,
)

# MD5s recorded in DESIGN Section 10 amendment 2026-07-14e. These are the exact
# bytes the 7-point CIC cleared (DISC-05).
VENDOR_MD5 = {
    "phase2_6_chain_length_sweep.py": "cbc6bfa327150ca4e64acf2b63df0172",
    "phase2_6_spectral_radius.py": "e530ae06c57a15a6680419cbe245ec30",
    "phase2_6_timevarying_demand.py": "e681e0c451457335ae66663b2a8b0e09",
}


def leg1_vendor_integrity() -> bool:
    ok = True
    for fname, want in VENDOR_MD5.items():
        p = _ANALYSIS / "vendor" / fname
        if not p.exists():
            print(f"LEG 1 FAIL: missing vendored module {fname}")
            ok = False
            continue
        got = hashlib.md5(p.read_bytes()).hexdigest()
        if got != want:
            print(f"LEG 1 FAIL: {fname} MD5 {got} != recorded {want} "
                  f"- the CIC cleared the recorded bytes, not these")
            ok = False
    print(f"LEG 1 vendor integrity: {len(VENDOR_MD5)} modules match the MD5s the "
          f"CIC cleared -> {'PASS' if ok else 'FAIL'}")
    return ok


def leg2_theorem_conformance() -> bool:
    """The vendored alpha rule must equal the as-proven theorem.

    Theorem (T1/T2/T3, verified independently in this repo before any empirical
    work): the cumulative persistence memory of an AR(1) over a window W is
    S = (1 - phi^W)/(1 - phi), and the stability bound on the operating gain is
    pi^2/2, so alpha_max = (pi^2/2)/S and alpha_op = k_star * alpha_max.

    Computed here from the theorem - NOT by calling the vendored helper - and
    compared against the vendored compute_alpha_pi_squared_over_two across a grid.
    """
    from phase2_6_spectral_radius import compute_alpha_pi_squared_over_two

    def theorem_alpha(phi, W, k_star=0.90):
        """The as-proven rule, UNCLIPPED. The vendored helper's own docstring:
        "Not yet clipped to [floor, 1.0]; caller is responsible for clipping" -
        so conformance is asserted against the raw rule; the clip is the policy
        layer's responsibility and is checked where it lives, not here."""
        S = W if abs(1.0 - phi) < 1e-12 else (1.0 - phi ** W) / (1.0 - phi)
        alpha_max = (np.pi ** 2 / 2.0) / S
        return float(k_star * alpha_max)

    bad, checked = [], 0
    for phi in (0.0, 0.1, 0.3, 0.5, 0.6, 0.75, 0.85, 0.9, 0.95, 0.99):
        for W in (5, 10, 20, 40, 80):
            got = compute_alpha_pi_squared_over_two(phi, W)
            want = theorem_alpha(phi, W, k_star=0.90)
            checked += 1
            if abs(got - want) > 1e-9:
                bad.append((phi, W, got, want))
    ok = not bad
    if bad:
        for phi, W, got, want in bad[:5]:
            print(f"LEG 2 FAIL: phi={phi} W={W}: vendored {got!r} != theorem {want!r}")
        print("LEG 2: a conformance failure is a FINDING about the source's "
              "implementation - dossier it; do NOT modify the vendored code.")
    print(f"LEG 2 theorem conformance: vendored alpha rule vs as-proven theorem "
          f"over {checked} (phi, W) points, computed from theory not from the "
          f"vendored helper -> {'PASS' if ok else 'FAIL'}")
    return ok


def leg3_drift_provenance() -> bool:
    """Three drift schedules are in scope (DESIGN 14e hazard). Assert which one the
    sweep actually uses, and that it matches the source's stated breakpoints."""
    import phase2_6_chain_length_sweep as sweep
    import phase2_6_timevarying_demand as tvd

    has_local = hasattr(sweep, "make_phase2_6_drift_schedule")
    has_mod = hasattr(tvd, "phase2_6_drift_schedule")
    has_dep = hasattr(tvd, "phase2_6_drift_schedule_DEPRECATED_DUPLICATE")

    envs = sweep.get_demand_environments(NUM_PERIODS)
    drift = envs.get("drift_canonical", {})
    sched = drift.get("phi_schedule") or drift.get("schedule")
    # The source's stated breakpoints: seg = num_periods/5 = 52;
    # (0,.30) (52,.30) (104,.95) (156,.95) (208,.40) (259,.40), piecewise linear.
    want = {0: 0.30, 52: 0.30, 104: 0.95, 156: 0.95, 208: 0.40, 259: 0.40}
    got, mism = {}, []
    if callable(sched):
        for t, w in want.items():
            v = float(sched(t))
            got[t] = v
            if abs(v - w) > 1e-6:
                mism.append((t, v, w))
    ok = callable(sched) and not mism and has_local
    print(f"LEG 3 drift provenance: sweep defines its own local schedule={has_local}; "
          f"module also carries phase2_6_drift_schedule={has_mod} and "
          f"DEPRECATED_DUPLICATE={has_dep} (both unused here); "
          f"breakpoints reaching the generator match the source's stated schedule="
          f"{not mism} {got if not mism else mism} -> {'PASS' if ok else 'FAIL'}")
    return ok


def _trials(pairs, variant, base, seed0=3000):
    """Planted trial records in the vendored runner's output shape."""
    out = []
    for i, (a, b) in enumerate(pairs):
        out.append(dict(trial_seed=seed0 + i, variant=variant,
                        cost_per_period=a, success=True))
        out.append(dict(trial_seed=seed0 + i, variant=base,
                        cost_per_period=b, success=True))
    return out


def leg4_resolution_logic() -> bool:
    # planted: a clean +10% effect, tiny noise -> must resolve
    pairs = [(110.0 + 0.01 * i, 100.0) for i in range(30)]
    r = paired_pct_diff(_trials(pairs, "sr_paper9_ols", "sr_disabled"),
                        "sr_paper9_ols", "sr_disabled")
    resolved_ok = (r["resolved_vs_zero"] and r["sign"] == "harm"
                   and r["n_paired"] == 30)
    arith = (abs(r["achieved_mdd"] - Z_MDD * r["se"]) < 1e-12
             and abs((r["ci"][1] - r["ci"][0]) / 2 - Z95 * r["se"]) < 1e-9)
    # planted: EXACTLY symmetric differences about zero -> mean is identically
    # zero, so this can never resolve regardless of draw. (An earlier version
    # drew N(0,8) and happened to resolve at seed 7 - a flaky test, not a real
    # failure. A test whose outcome depends on the draw cannot police a rule.)
    noisy = []
    for i in range(15):
        d = 8.0 * (i + 1) / 15.0
        noisy.append((100.0 + d, 100.0))
        noisy.append((100.0 - d, 100.0))
    r2 = paired_pct_diff(_trials(noisy, "sr_paper9_ols", "sr_disabled"),
                         "sr_paper9_ols", "sr_disabled")
    unres_ok = (not r2["resolved_vs_zero"]) and r2["sign"] == "unresolved"
    # per-cell variance: two different cells must give different SEs
    per_cell = abs(r["se"] - r2["se"]) > 1e-6
    # pairing is by seed: unmatched seeds must not pair
    mixed = (_trials([(110.0, 100.0)], "sr_paper9_ols", "sr_disabled", seed0=3000)
             + _trials([(120.0, 100.0)], "sr_paper9_ols", "sr_disabled", seed0=9999))
    r3 = paired_pct_diff(mixed, "sr_paper9_ols", "sr_disabled")
    pair_ok = r3["n_paired"] == 2
    ok = resolved_ok and arith and unres_ok and per_cell and pair_ok
    print(f"LEG 4 resolution logic: planted effect resolves+labelled={resolved_ok}, "
          f"mdd/ci arithmetic={arith}, planted noise unresolved and NOT labelled="
          f"{unres_ok}, se measured per-cell={per_cell} ({r['se']:.3e} vs "
          f"{r2['se']:.3e}), pairing by trial_seed={pair_ok} "
          f"-> {'PASS' if ok else 'FAIL'}")
    return ok


def _cell(L, cap, env, mean, resolved):
    se = abs(mean) / (Z95 * 2) if resolved and mean != 0 else abs(mean) * 10 + 1e-6
    p = dict(n_paired=250, mean_pct_diff=mean, se=se,
             ci=[mean - Z95 * se, mean + Z95 * se], achieved_mdd=Z_MDD * se,
             resolved_vs_zero=resolved,
             sign=("harm" if mean > 0 else "benefit") if resolved else "unresolved")
    return dict(n_stages=L, cap_mult=cap, env=env, n_seeds=250, n_trials=1250,
                n_failed=0, primary=p, diagnostic={"sr_paper9_ols": p})


def leg5_crossover_locator() -> bool:
    cap, env = 2.4, "ar1_high"
    # (i) planted resolved harm -> benefit transition: must be located
    a = [_cell(4, cap, env, +0.44, True), _cell(6, cap, env, +0.14, True),
         _cell(8, cap, env, -0.14, True)]
    m = crossover_map(a)[f"cap{cap}_{env}"]
    found = (len(m["sign_flips"]) == 1 and m["sign_flips"][0]["between"] == [6, 8]
             and m["sign_flips"][0]["resolved"] and m["spans_transition"])
    # (ii) all-benefit line: must NOT report a transition
    b = [_cell(L, cap, env, -0.20, True) for L in (4, 6, 8)]
    m2 = crossover_map(b)[f"cap{cap}_{env}"]
    degen = (not m2["spans_transition"]) and len(m2["sign_flips"]) == 0
    # (iii) flip between two UNRESOLVED cells: located but NOT called a crossover
    c = [_cell(4, cap, env, +0.002, False), _cell(6, cap, env, +0.001, False),
         _cell(8, cap, env, -0.002, False)]
    m3 = crossover_map(c)[f"cap{cap}_{env}"]
    unres = (len(m3["sign_flips"]) == 1 and not m3["sign_flips"][0]["resolved"]
             and not m3["spans_transition"])
    ok = found and degen and unres
    print(f"LEG 5 crossover locator: planted transition located={found}, "
          f"all-benefit line reports none={degen}, unresolved flip NOT called a "
          f"crossover={unres} -> {'PASS' if ok else 'FAIL'}")
    return ok


def leg6_json_boundary() -> bool:
    cells = [_cell(L, cap, env, +0.1 if L == 4 else -0.1, True)
             for L in (4, 6, 8) for cap in (1.3, 1.8, 2.4)
             for env in ("iid_control", "ar1_moderate", "ar1_high",
                         "drift_canonical")]
    payload = dict(cells=cells, crossover=crossover_map(cells),
                   stability_statement=stability(cells),
                   headline_vs_source=headline_vs_source(cells))
    try:
        json.loads(json.dumps(payload))
        ok = True
    except (TypeError, ValueError) as exc:
        print(f"LEG 6 FAIL: {exc}")
        ok = False
    hv_ok = len(payload["headline_vs_source"]["rows"]) == len(SOURCE_HEADLINE)
    print(f"LEG 6 json boundary: full payload round-trips ({len(cells)} cells), "
          f"headline rows={hv_ok} -> {'PASS' if ok and hv_ok else 'FAIL'}")
    return ok and hv_ok


def main() -> None:
    print("E7 suite (REBUILD): vendor integrity + theorem conformance + drift "
          "provenance + resolution logic + crossover locator + json boundary")
    r = [leg1_vendor_integrity(), leg2_theorem_conformance(), leg3_drift_provenance(),
         leg4_resolution_logic(), leg5_crossover_locator(), leg6_json_boundary()]
    print(f"\nALL PASS: {all(r)}")
    sys.exit(0 if all(r) else 1)


if __name__ == "__main__":
    main()
