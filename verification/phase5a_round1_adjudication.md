# Phase 5a Round-1 Adjudication - The Escalation Cost

Date: 2026-07-26. Review package SHA256
39c79ea74608245e3be1f3570a9062c824a6d821b987c8c0787c1759d6ef6958 (85 files,
588,182 bytes; instruments at b505aba). Review performed in an isolated
claude.ai session, ten mandated passes, proof-rigor ON, Standard v1.9.11.

Reviewer's summary, accepted: all 506 then-committed ledger rows recomputed
with ZERO mismatches; renderer byte-identical; 73/73 citations verified;
Appendix G clean; gap claims survived. Eighteen findings CONFIRMED (seven
load-bearing), fourteen candidate findings WITHDRAWN by the reviewer's own
verification. No wrong number found anywhere; the confirmed defect class is
uniformly descriptive - the manuscript's account of its experiments trailing
the code's care.

Rulings: sixteen FIX, two REBUT-in-writing. Every load-bearing factual
assertion was verified against the committed artifacts before ruling.
Execution commits: 8ce8d5e (Stage A), bd5cad2 + 4d19eb2 (Stage B + gate
remediation), 75f9d96 / 5bb772e / 65246ee (F-07 freeze / suite fix / run).
One process defect during execution is disclosed in Section "Process
defects" below; one self-found code finding is disclosed as SF-01.

## Per-finding rulings

- F-01 (load-bearing) FIX @ 8ce8d5e: E8 declared as an analysis of the
  source's committed trial records (analysis-not-run disclosed); TBL-A gains
  the phase27 registry row.
- F-02 FIX @ 8ce8d5e: COVERAGE's zero-drop posture corrected to the one
  escalated drop it contains.
- F-03 (load-bearing) FIX @ bd5cad2/4d19eb2: E6's computed-but-unreported
  SPEC-M leg enters the paper - TBL-6 gains the SPEC-M column (bins entirely
  BELOW the boundary, inverting the side while preserving the operative
  conclusion); 8.2 and C-06 conditioned on specification.
- F-04 REBUT, written into 5.4 @ 8ce8d5e: RECENT_WIN=12 vs S-4's 36-month
  floor - the floor governs level placement; the falsifier consumes a ranked
  change signal whose small-sample attenuation biases against firing. The
  rebuttal is the disclosure the paper owed.
- F-05 FIX @ 8ce8d5e: the falsifier's rank-invariance to tau disclosed
  (kappa pin exists for reproducibility, not dependence).
- F-06 FIX @ 8ce8d5e: sector classification stated as full-sample;
  out-of-sample label scoped accordingly in 6.3.
- F-07 (load-bearing) FIX by pre-registered amendment @ 75f9d96 -> 65246ee:
  the ordering conjunct's bare point comparison replaced by paired
  permutation contrasts with a reading committed before the run. RESULT:
  both contrasts UNRESOLVED at n=17 - c_rho +0.5049 (one-sided p 0.0515;
  crisis rho alone anti-correlates with realized damage, and the edge misses
  the frozen 0.05 by 0.0015 - recorded as unresolved, no rounding) and
  c_dphi +0.0294 (p 0.4203). Per the frozen rule 6.1 reports the ordering
  as point-estimate-descriptive with inferential weight on the association
  leg; the SUPPORT verdict stands (formula untouched). Suite Leg 4 proved
  the instrument could resolve at this n (planted edge p 0.0035), reads the
  tie case unresolved, and false-positives at 0.030 in a 0.02-0.09 band.
- F-08 FIX @ 8ce8d5e: contrast false-positive rate relabelled as the
  conditioned lower bound it is (want_index=2 conditioning stated).
- F-09 FIX @ 8ce8d5e: three "bias" mislabels renamed to mean estimates with
  reading direction stated. The id rename was declined - ledger ids are
  append-only continuity anchors; the labels, not the ids, carried the
  defect.
- F-10 FIX @ 8ce8d5e: SPEC-R named wherever "primary specification" was
  ambiguous.
- F-11 (load-bearing) FIX @ bd5cad2/4d19eb2: E5's SPEC-M exceedance floors
  at zero for eight of seventeen sectors - A34SIS's printed rank disclosed
  as a stable-sort artifact inside the tie; 8.1, TBL-4 caption, and C-05
  present tied-last; the ranking claim is a SPEC-R claim.
- F-12 (load-bearing) FIX @ bd5cad2/4d19eb2: the monitor's sustained-
  crossing record (the definition Methods states) now quoted as primary in
  7.4 with raw crossings beside it - under the stated definition ZERO
  crossings precede either onset, retiring the two-nominally-preceded hedge.
- F-13 FIX @ 8ce8d5e: fifty-vs-250 seed count corrected.
- F-14 FIX @ 8ce8d5e: Panel B's nested-seed structure disclosed.
- F-15 REBUT, written into Panel E @ 8ce8d5e: E12 Leg A's ci_disjoint_below
  is the pre-registered reading; the leg adjudicates the registered claim,
  and the paradox finding beyond registration is labelled as such.
- F-16 (load-bearing) FIX @ bd5cad2/4d19eb2: E10's raw-levels leg reported -
  TBL-5 gains the per-country phi (raw levels) column; 14 of 18 remain
  below one on levels, the explosive set grows to four (USA joins), and 9.1
  reports both counts; the withdrawn reading survives either leg.
- F-17 FIX @ 8ce8d5e: the unbacked "statistically indistinguishable" claim
  replaced by the descriptive comparison the artifact supports.
- F-18 FIX @ 8ce8d5e: sigma labelled as the t-statistic with both sign
  conventions stated.

## Reviewer's open verification items

- W-01 (store integrity, E1 inputs): CLOSED on the live store by read-only
  scan - 17/17 members, zero missing tokens, zero internal gaps; continuous
  1992-01..2026-05 (413 obs) for fourteen series, ..2026-04 (412) for the
  three retail series (release cadence). The committed uniform n_obs = 341
  is fully derived: per-sector evaluation count raw_n - 71, panel-minimum
  alignment for the joint bootstrap (min(342 x14, 341 x3) = 341).
- E9 provenance (exact-zero fidelity): TIER-EXACT is deterministic
  reproduction, not statistical agreement - the run executes the source's
  own vendored, CIC-cleared closure at the source's own twenty seeds
  (2000-2019, engine rand_seed fixed), regenerating the registered
  artifact's trial streams bit-identically; arms are paired per-seed.

## SF-01 - self-found during round closure, disclosed unprompted

E1's evaluation guard admits each series' final point with an eleven-month
forward window (guard tests t + FWD_WIN > n; a full window needs
t + 1 + FWD_WIN <= n), against the docstring's h = 1..12. The panel
alignment REMOVES that point for the fourteen longer series; it survives
only as the last of 341 points in the three retail series, exactly one of
which is oscillating - roughly one three-thousandth of the pooled falsifier
evidence flows through an 11-rather-than-12-month mean, direction unsigned.
Invisible from outputs; found by executing the loop bounds during W-01
closure. Author ruling: disclose-only (manuscript 5.4; REPLICATION.md
addendum; DECISIONS 82); the one-line guard correction is a Phase-5b
candidate with the committed statistics as the reproduction target.

## Process defects during execution, disclosed

bd5cad2 was committed with VERIFY RED: the runbook guard read the
renderer's exit code rather than verify's. Logged as DECISIONS 78, cured in
the block template (each exit code captured immediately), remediated at
4d19eb2 with the two verify-side completions the RED correctly demanded
(derived-registry twins; three OUTLINE family declarations). The gate
worked; the guard around it did not, and now does.

## Round status

This document executes the round cap's one fix-or-rebut round. Seven
findings were load-bearing; under the review protocol a second round is
available at the reviewer's option. Requested: acknowledgment of the
rulings and rebuttals, and the reviewer's decision on a second round.
