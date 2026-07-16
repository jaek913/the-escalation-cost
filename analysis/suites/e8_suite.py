"""e8_suite.py - E8 validation suite (Standard v1.9.5 gate, extended v1.9.7).

Imports paired / claim_a / claim_b / load VERBATIM from the committed e8_pricing.py -
the suite exercises the real pipeline, never a copy.

E8 is an ANALYSIS of the source's verified artifact, not a re-execution (DESIGN 16e).
That changes what this suite must prove. It does NOT need to prove the source's
engine is correct - the 7-point CIC did that, by reading their code line by line
(16c, all seven clear) - nor that the vendored bytes are the audited bytes (LEG 1
below asserts the input; e7_suite LEG 1 asserts the shared modules). What it MUST
prove is that OUR ANALYSIS is correct, and above all that it does not commit the
defect it exists to expose:

LEG 1 INPUT INTEGRITY: the artifact's SHA256 matches the one registered in
  data/SOURCES.md, and a tampered artifact is REJECTED rather than analysed. The
  hash pins the evidence: every E8 finding was computed against these exact bytes.
LEG 2 TWO-CLAIM SEPARATION - THE LOAD-BEARING LEG (DISC-03). Claim A must compare
  phi_gated vs NAIVE_REACTIVE; Claim B must compare naive vs NO_PRICING. Substituting
  one for the other is exactly what v16 does, and it is what this experiment exists
  to expose - so the suite proves our code cannot make that substitution, by planting
  arms that are distinguishable ONLY by which base is used.
LEG 3 BOUND ARITHMETIC: the CI is mean +/- z*se, and the percentage-of-headline
  conversion divides by |Claim B| - the number the formula is credited with.
LEG 4 RESOLUTION LOGIC: resolved iff |mean| > z*se; an unresolved cell reports its
  BOUND and is never called "the formula works" or "the formula does nothing."
LEG 5 PAIRING BY SEED: differences are within-seed; unmatched seeds never pair.
  (The source's runner documents why this is valid: "Same seed across pricing
  scenarios produces identical baseline demand.")
LEG 6 CLAIM B VERDICT RULE: the frozen assert/partial/drop rule is implemented as
  written - ASSERTED requires raises resolved-positive under strain AND cuts negative
  in EVERY downward environment; a single non-negative cut cell forces PARTIAL.
LEG 7 JSON BOUNDARY: the full payload serializes (the E4 lesson).

Suite failures fix OUR CODE ONLY - never the rules, the report form, or the input.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent
_ANALYSIS = _HERE.parent
sys.path.insert(0, str(_ANALYSIS))

from e8_pricing import (  # noqa: E402
    DOWNWARD,
    ENVS,
    GATED,
    INPUTS,
    NAIVE,
    NOPRICE,
    RAW,
    STRAINED_UP,
    UPWARD,
    Z95,
    claim_a,
    claim_b,
    load,
    paired,
)


def _t(seed, env, scenario, rev, cost):
    return dict(trial_seed=seed, env=env, pricing_scenario=scenario,
                mean_revenue_per_period=rev, cost_per_period=cost, success=True)


def leg1_input_integrity() -> bool:
    fname, want = INPUTS["primary"]
    p = RAW / fname
    if not p.exists():
        print(f"LEG 1 FAIL: input missing at {p} - run: python data\\pull.py --verify")
        return False
    got = hashlib.sha256(p.read_bytes()).hexdigest()
    match = got == want
    # a tampered artifact must be REJECTED, not analysed
    rejects = False
    try:
        real = INPUTS["primary"]
        INPUTS["primary"] = (fname, "0" * 64)
        try:
            load("primary")
        except SystemExit:
            rejects = True
    finally:
        INPUTS["primary"] = real
    ok = match and rejects
    print(f"LEG 1 input integrity: registered SHA256 matches={match}, "
          f"tampered hash REJECTED={rejects} -> {'PASS' if ok else 'FAIL'}")
    return ok


def leg2_two_claim_separation() -> bool:
    """THE LOAD-BEARING LEG. Plant arms that are distinguishable ONLY by base.

    no_pricing = 100, naive = 200, phi_gated = 210. Then:
      Claim A (gated vs NAIVE)     MUST be +10   - the formula's contribution
      Claim B (naive vs NO_PRICING) MUST be +100 - the value of reacting at all
    If the code ever compared gated vs no_pricing it would report +110 and credit
    the formula with the reaction's value. That is v16's defect (DISC-03), and this
    leg proves our code cannot commit it.
    """
    tr = []
    for s in range(20):
        for e in ENVS:
            tr += [_t(s, e, NOPRICE, 100.0, 0.0),
                   _t(s, e, NAIVE, 200.0, 0.0),
                   _t(s, e, "phi_gated_asymmetric", 210.0, 0.0),
                   _t(s, e, "phi_gated_symmetric", 205.0, 0.0)]
    b = claim_b(tr)
    a = claim_a(tr, b)
    b_ok = all(abs(b["cells"][e]["mean"] - 100.0) < 1e-9 for e in ENVS)
    a_ok = all(abs(a["by_arm"]["phi_gated_asymmetric"][e]["mean"] - 10.0) < 1e-9
               for e in ENVS)
    sym_ok = all(abs(a["by_arm"]["phi_gated_symmetric"][e]["mean"] - 5.0) < 1e-9
                 for e in ENVS)
    # the smoking-gun check: Claim A must NOT equal gated-vs-no_pricing (+110)
    not_conflated = all(abs(a["by_arm"]["phi_gated_asymmetric"][e]["mean"] - 110.0) > 1
                        for e in ENVS)
    # and the bases must literally differ
    bases_differ = b["comparison"].endswith(NOPRICE) and NAIVE in a["comparison"]
    ok = b_ok and a_ok and sym_ok and not_conflated and bases_differ
    print(f"LEG 2 two-claim separation: ClaimB=+100 (reaction)={b_ok}, "
          f"ClaimA_asym=+10 (formula)={a_ok}, ClaimA_sym=+5={sym_ok}, "
          f"ClaimA is NOT gated-vs-no_pricing(+110)={not_conflated}, "
          f"bases differ={bases_differ} -> {'PASS' if ok else 'FAIL'}")
    return ok


def leg3_bound_arithmetic() -> bool:
    tr = []
    for s in range(30):
        tr += [_t(s, STRAINED_UP, NOPRICE, 100.0, 0.0),
               _t(s, STRAINED_UP, NAIVE, 200.0 + 0.01 * s, 0.0),
               _t(s, STRAINED_UP, "phi_gated_asymmetric", 210.0 + 0.01 * s, 0.0),
               _t(s, STRAINED_UP, "phi_gated_symmetric", 205.0, 0.0)]
    for e in ENVS[1:]:
        for s in range(30):
            tr += [_t(s, e, NOPRICE, 100.0, 0.0), _t(s, e, NAIVE, 90.0, 0.0),
                   _t(s, e, "phi_gated_asymmetric", 91.0, 0.0),
                   _t(s, e, "phi_gated_symmetric", 90.5, 0.0)]
    b = claim_b(tr)
    a = claim_a(tr, b)
    c = a["by_arm"]["phi_gated_asymmetric"][STRAINED_UP]
    ci_ok = abs((c["ci"][1] - c["ci"][0]) / 2 - Z95 * c["se"]) < 1e-9
    head = b["cells"][STRAINED_UP]["mean"]
    pct_ok = (abs(c["ci_pct_of_claim_b"][0] - c["ci"][0] / abs(head) * 100) < 1e-9
              and abs(c["ci_pct_of_claim_b"][1] - c["ci"][1] / abs(head) * 100) < 1e-9)
    head_ok = abs(c["claim_b_headline"] - head) < 1e-9
    # The percentage must divide by the CLAIM B headline, NOT by the formula's own
    # mean. Dividing by the formula's mean would inflate the ratio ~10x here and is
    # the arithmetic form of the conflation this experiment exists to expose.
    wrong = c["ci"][1] / abs(c["mean"]) * 100
    denom_ok = abs(c["ci_pct_of_claim_b"][1] - wrong) > 1.0
    ok = ci_ok and pct_ok and head_ok and denom_ok
    print(f"LEG 3 bound arithmetic: ci=mean+/-z*se={ci_ok}, pct divides by |ClaimB|="
          f"{pct_ok}, headline carried={head_ok}, denominator is the CREDITED number "
          f"not the formula's own mean={denom_ok} -> {'PASS' if ok else 'FAIL'}")
    return ok


def leg4_resolution_logic() -> bool:
    # planted clean effect -> resolves
    tr = [_t(s, STRAINED_UP, NAIVE, 100.0, 0.0) for s in range(30)]
    tr += [_t(s, STRAINED_UP, "phi_gated_asymmetric", 110.0 + 0.001 * s, 0.0)
           for s in range(30)]
    r = paired(tr, STRAINED_UP, "phi_gated_asymmetric", NAIVE)
    # planted mean is 10 + 0.001*mean(0..29) = 10.0145; tolerance must exceed the
    # jitter deliberately introduced to give the estimator non-zero variance.
    res_ok = r["resolved"] and abs(r["mean"] - 10.0145) < 1e-3
    # planted EXACTLY symmetric noise about zero -> mean identically 0, never resolves,
    # whatever the draw. (A test whose outcome depends on the draw cannot police a rule.)
    tr2 = [_t(s, STRAINED_UP, NAIVE, 100.0, 0.0) for s in range(30)]
    for i in range(15):
        d = 5.0 * (i + 1) / 15.0
        tr2 += [_t(2 * i, STRAINED_UP, "phi_gated_asymmetric", 100.0 + d, 0.0),
                _t(2 * i + 1, STRAINED_UP, "phi_gated_asymmetric", 100.0 - d, 0.0)]
    r2 = paired(tr2, STRAINED_UP, "phi_gated_asymmetric", NAIVE)
    unres_ok = (not r2["resolved"]) and abs(r2["mean"]) < 1e-9
    # identical arms are detected, not silently reported as a null
    tr3 = [_t(s, STRAINED_UP, NAIVE, 100.0, 0.0) for s in range(30)]
    tr3 += [_t(s, STRAINED_UP, "phi_gated_asymmetric", 100.0, 0.0) for s in range(30)]
    r3 = paired(tr3, STRAINED_UP, "phi_gated_asymmetric", NAIVE)
    ident_ok = r3["arms_identical"] and not r3["resolved"]
    ok = res_ok and unres_ok and ident_ok
    print(f"LEG 4 resolution logic: planted effect resolves={res_ok}, symmetric noise "
          f"never resolves={unres_ok}, identical arms flagged (not called a null)="
          f"{ident_ok} -> {'PASS' if ok else 'FAIL'}")
    return ok


def leg5_pairing() -> bool:
    tr = [_t(1, STRAINED_UP, NAIVE, 100.0, 0.0),
          _t(2, STRAINED_UP, NAIVE, 100.0, 0.0),
          _t(1, STRAINED_UP, "phi_gated_asymmetric", 110.0, 0.0),
          _t(9, STRAINED_UP, "phi_gated_asymmetric", 999.0, 0.0)]
    r = paired(tr, STRAINED_UP, "phi_gated_asymmetric", NAIVE)
    # only seed 1 pairs; seeds 2 and 9 are unmatched and must be dropped
    ok = r["n"] == 1
    print(f"LEG 5 pairing by seed: unmatched seeds dropped, n_paired={r['n']} "
          f"(expect 1) -> {'PASS' if ok else 'FAIL'}")
    return ok


def leg6_claim_b_verdict_rule() -> bool:
    def build(up_delta, down_deltas):
        tr = []
        for s in range(30):
            tr += [_t(s, STRAINED_UP, NOPRICE, 100.0, 0.0),
                   _t(s, STRAINED_UP, NAIVE, 100.0 + up_delta + 0.001 * s, 0.0)]
            for e in UPWARD[1:]:
                tr += [_t(s, e, NOPRICE, 100.0, 0.0),
                       _t(s, e, NAIVE, 100.0 + up_delta + 0.001 * s, 0.0)]
            for e, d in zip(DOWNWARD, down_deltas):
                tr += [_t(s, e, NOPRICE, 100.0, 0.0),
                       _t(s, e, NAIVE, 100.0 + d + 0.001 * s, 0.0)]
        for a in GATED:
            tr += [_t(s, e, a, 100.0, 0.0) for s in range(30) for e in ENVS]
        return tr
    asserted = claim_b(build(+50, [-50, -50, -50]))["verdict"] == "ASSERTED"
    # one downward cell POSITIVE -> "uniformly negative" is withdrawn -> PARTIAL
    partial = claim_b(build(+50, [-50, +50, -50]))["verdict"] == "PARTIAL"
    # raises not positive under strain -> DROPPED
    dropped = claim_b(build(-50, [-50, -50, -50]))["verdict"] == "DROPPED"
    ok = asserted and partial and dropped
    print(f"LEG 6 Claim B verdict rule: all-negative cuts -> ASSERTED={asserted}, one "
          f"non-negative cut -> PARTIAL={partial}, raises not positive -> DROPPED="
          f"{dropped} -> {'PASS' if ok else 'FAIL'}")
    return ok


def leg7_json_boundary() -> bool:
    tr = load("primary")
    b = claim_b(tr)
    a = claim_a(tr, b)
    try:
        json.loads(json.dumps(dict(claim_a=a, claim_b=b)))
        ok = True
    except (TypeError, ValueError) as exc:
        print(f"LEG 7 FAIL: {exc}")
        ok = False
    print(f"LEG 7 json boundary: full payload round-trips -> {'PASS' if ok else 'FAIL'}")
    return ok


def main() -> None:
    print("E8 suite: input integrity + two-claim separation + bound arithmetic + "
          "resolution logic + pairing + verdict rule + json boundary")
    r = [leg1_input_integrity(), leg2_two_claim_separation(), leg3_bound_arithmetic(),
         leg4_resolution_logic(), leg5_pairing(), leg6_claim_b_verdict_rule(),
         leg7_json_boundary()]
    print(f"\nALL PASS: {all(r)}")
    sys.exit(0 if all(r) else 1)


if __name__ == "__main__":
    main()
