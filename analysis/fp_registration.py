#!/usr/bin/env python3
"""fp_registration.py - THE ESCALATION COST - forward-prediction registration
constants (LB-FP-diagnostic family; Phase-4 deliverable, OUTLINE ARG-27).

Emits the REGISTERED CONSTANTS of the paper's two forward predictions as a
committed, deterministic artifact so every constant the manuscript quotes is a
ledger row (no protocol number is ever retyped by hand):

BET (A) - self-service diagnostic (carried from the pinned source, locked
April 2026; restated and re-registered at this rebuild's commit): any firm
computes the closed-loop spectral radius rho from its own estimated demand
persistence phi_hat (OLS AR(1) with intercept - the paper's pre-registered
estimator), its measurement window W, and its feedback gain beta*gamma via the
paper's companion-matrix construction (EQ-1). Standing claim: rho > 1 implies
the response to the firm's next demand shock AMPLIFIES (bullwhip); rho < 1
implies it DECAYS. Calculator: LaggingTruth.com/diagnostic.

BET (B) - sector-level two-class bet (new at this rebuild; registers at
publication). The class lists are extracted MECHANICALLY from the committed E1
rolling-validation output (its full-sample pre-registered partition): sectors
classified "oscillating" (boundary-crossing under E1's frozen rolling
construction) versus "never-crossing". Standing claim: at the next NBER-dated
US recession onset after registration, the oscillating class shows amplifying
inventory/sales responses - peak absolute deviation of log I/S from its
pre-onset baseline mean, within the evaluation window, normalized by the
pre-onset baseline standard deviation - EXCEEDING the never-crossing class
(one-sided Mann-Whitney at the registered alpha). HONESTY NOTE, registered
as part of the claim: under this committed construction the CHIPS-dependent
computers/electronics sector (A34SIS) falls in the NEVER-CROSSING class and
wholesale machinery (R4238...) in the flagged class - the earlier informal
sketch that named both CHIPS sectors as flagged is superseded by the
committed classification (spec-sensitivity is a finding of this paper).

Deterministic: constants are literals; class lists are read from the committed
e1 output whose MD5 is embedded for input-integrity verification. No network,
no store access, no randomness, no timestamps beyond the registration literal.

Output: analysis/outputs/fp_registration.json
"""
from __future__ import annotations

import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
E1 = ROOT / "outputs" / "e1_rolling_validation.json"
OUT = ROOT / "outputs" / "fp_registration.json"

DESIGN_PIN = "74c73ea165a7363c6714fe803fbe76b1"
REGISTRATION_DATE = "2026-07-24"  # finalized this date; re-stated at commit
HORIZON = "2031-07-31"            # untestable / carry-forward past this date


def main() -> None:
    raw = E1.read_bytes()
    e1_md5 = hashlib.md5(raw).hexdigest()
    e1 = json.loads(raw.decode("utf-8"))

    def ids(klass: str) -> list[str]:
        return sorted(s["sector"].split(" ")[0] for s in e1["sectors"]
                      if s["klass"] == klass)

    flagged = ids("oscillating")
    decay = ids("never-crossing")
    assert len(flagged) + len(decay) + sum(
        1 for s in e1["sectors"] if s["klass"] == "chronic") == len(e1["sectors"])

    out = {
        "experiment": "FP",
        "date": REGISTRATION_DATE,
        "design_pin": DESIGN_PIN,
        "e1_md5": e1_md5,
        "registered": REGISTRATION_DATE,
        "horizon": HORIZON,
        "threshold_rho": 1.0,
        "estimator": "ols_ar1_intercept",
        "calculator_url": "LaggingTruth.com/diagnostic",
        "bet_a": {
            "carried_from": "pinned source (locked April 2026); restated and "
                            "re-registered at the rebuild commit",
            "claim": "rho > 1 at measurement implies amplifying response to "
                     "the firm's next demand shock; rho < 1 implies decaying",
        },
        "bet_b": {
            "trigger": "next NBER-dated US recession onset after registration",
            "metric_window_months": 24,
            "baseline_months": 60,
            "metric": "peak |log I/S deviation from pre-onset baseline mean| "
                      "within the evaluation window, divided by the pre-onset "
                      "baseline standard deviation",
            "test": "one-sided Mann-Whitney, oscillating > never-crossing",
            "alpha": 0.05,
            "n_flagged": len(flagged),
            "n_decay": len(decay),
            "flagged_sectors": ",".join(flagged),
            "decay_sectors": ",".join(decay),
        },
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(out, indent=2, sort_keys=True))
    print(f"FP registration written: {len(flagged)} flagged / {len(decay)} "
          f"decay sectors; e1_md5 {e1_md5}")


if __name__ == "__main__":
    main()
