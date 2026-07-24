# Three-Way Proof Verification Record

The Escalation Cost - per-theorem record of the three verification legs required
by the Standard (written proof + symbolic step-check + numeric stress test), with
the result of each. Machine legs are claims.lock rows re-verified by verify.py on
every run; written proofs live in the manuscript's Appendix G (working draft
history: paper/proofs_appendix_g.md v0.2).

## THM-1 - Compound Damage Bound
- Written proof: Appendix G.2 (with Lemma G.1 matrix-general bound and Lemma G.1b
  in-domain Gain Envelope; scope condition A4). Result: COMPLETE (v0.2; step (ii)
  corrected from false global gain monotonicity to G.1b after container QA).
- Symbolic step-check: LB-T1-bound-symbolic (sympy S1 charpoly identity, S2
  convexity, S3 induction identity). Result: PASS.
- Numeric stress test: LB-T1-bound-numeric-indomain / -counterexamples /
  -allpass (frozen grid; dense gain-envelope sweep per in-domain cell;
  deterministic dominant-mode identity at rel 1e-6). Result: PASS, zero
  counterexamples.

## THM-2 - Optimal Measurement Window
- Written proof: Appendix G.3 (strict convexity; explicit interiority condition
  (C); exact Lambert-W closed form via the defining identity u e^u = z).
  Result: COMPLETE.
- Symbolic step-check: LB-T2-wstar-symbolic (S4 convexity, S5 interiority-
  condition identity, S6 Lambert-W solves the FOC). Result: PASS.
- Numeric stress test: LB-T2-wstar-numeric-match / -matchrate /
  -unimodal-failures (closed form vs brute-force argmin across the frozen
  grid). Result: PASS, exact agreement, zero unimodality failures.

## Comparative Statics (Theorem 2 corollary; source Section 4.5 CORRECTED)
- Written derivation: Appendix G.4 (implicit-function signs; sign (b) REVERSED
  from the source under the model's own Cramer-Rao cost term - manuscript
  Section 4.5 follows G.4). Result: COMPLETE.
- Symbolic step-check: LB-T2-statics-symbolic (S7a-c derivative identities).
  Result: PASS.
- Numeric stress test: LB-T2-statics-numeric-monophi-fail / -monobg-fail
  (monotonicity counters on the frozen grid). Result: PASS, zero failures.

## THM-3 - Adaptation-Stability Identity
- Written proof: Appendix G.5 (exact identity for the non-adaptive envelope;
  bound-vs-identity Remark G.5.1). Result: COMPLETE.
- Symbolic step-check: LB-THM3-symbolic (S8 log-identity). Result: PASS.
- Numeric stress test: LB-THM3-numeric / -numeric-checked (dedicated dual-path
  log-identity assertion per in-domain cell x kappa, rel 1e-12). Result: PASS,
  zero failures.

## k* Optimal Safety Factor - PROPOSITION, not a theorem
- Written derivation: Appendix G.6 (approximation chain with every step
  labeled; the 2pW inflation factor retained from the source as a modeling
  constant and flagged as such). Result: COMPLETE as a Proposition.
- Symbolic step-check: NONE BY DESIGN - labeled proposition-numeric-only per
  the author ruling (DECISIONS 42); the two-row theorem rule does not attach.
- Numeric verification: LB-T3-kstar-mfg-argmin / -inband / -allbelow1 /
  -verdict (committed T3 grid; the grid governs over the approximation chain).
  Result: PASS.

Every machine-leg row above is re-verified against committed outputs by
verify.py (checks 1 and 4) on every run; this record's on-disk existence is
asserted by the reconciliation gate whenever the manuscript references it.
