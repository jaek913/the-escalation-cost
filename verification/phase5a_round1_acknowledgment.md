# Phase 5a Round-1 Acknowledgment - The Escalation Cost (reviewer document, verbatim)

Provenance: reviewer's acknowledgment message, delivered in the isolated
claude.ai review session in response to verification/phase5a_round1_adjudication.md,
received 2026-07-28 and transcribed verbatim into the repository the same day.
Chat-interface artifacts (collapse controls, activity-summary lines) removed;
reviewer prose untouched.

---

Phase 5a Round-1 Acknowledgment — The Escalation Cost

Reviewer, isolated session. Package under review at round 1: SHA256 39c79ea7…6ef6958. This acknowledgment responds to verification/phase5a_round1_adjudication.md.

What this acknowledgment is, and what it is not

I have the adjudication document. I do not have the post-fix package. Sixteen rulings are FIX, executed at commits I cannot open, and I have no fresh verify.py output for the head state. So this is an acknowledgment of the rulings as reasoned, not a verification of the executed text. Where I say "accepted," I mean the ruling is correct given the finding; I am not attesting that the manuscript now reads as described. That distinction matters more than usual here, for a reason I take up under Second round.

What I can verify is the arithmetic in the adjudication itself, and I did. Every checkable quantity reconciles against the computations I ran independently in round 1:

adjudication claim | my round-1 computation
F-03: SPEC-M bins entirely below the boundary | 0.7599 / 0.8226 / 0.8117 / 0.8813 ✓
F-11: exceedance floors at zero for 8 of 17 | ranks 10–17 all exactly 0.0 ✓
F-12: zero crossings precede either onset under the stated definition | AMTMIS 2020-02→2020-04, AMDMIS 2020-01→2020-04 ✓
F-16: 14 of 18 below one on levels; USA joins the explosive set | 1.0128 ✓
W-01: 413 obs (1992-01..2026-05), 412 for retail | 34×12+5 = 413 ✓
W-01: evaluation count = raw_n − 71; min(342, 341) = 341 | guard admits t ≤ n−12 from t = 60 → n−71 ✓

That the derived figures reconcile against an independent recomputation is the best available evidence that the adjudication was performed against the artifacts rather than asserted over them. Recorded as such.

Rulings accepted without reservation

F-01, F-02, F-05, F-06, F-08, F-09, F-10, F-13, F-14, F-17, F-18 — accepted as ruled.

On F-09, the declined id rename is accepted and I think it is the right call: append-only ledger ids are continuity anchors across the verification record, and renaming them to fix a prose defect would trade a real invariant for a cosmetic gain. The reasoning is better than my proposal.

F-03, F-11, F-12, F-16 — accepted, and these four are the substantive ones. Each moves a reported number or inverts a reported side, and in every case the direction of the correction runs against the paper's rhetorical interest: E6's SPEC-M bins sit below the boundary rather than above it; A34SIS is tied last rather than tenth; the monitor's pre-onset leads go to zero; the sovereign explosive set grows to four. Reporting all four is the outcome I would have wanted and not the one that flatters the manuscript.

F-04 — REBUT accepted. I flagged in round 1 that this was the most likely legitimate rebuttal, and having checked the mechanism I think it is correct and slightly stronger than the adjudication states. The Kendall–Marriott bias at n = 12 is approximately −(1+3φ)/n, so φ̂ ≈ 0.75φ − 0.083: the map is monotone increasing in φ, which means the small-sample bias compresses the ranking without reordering it in expectation, and the residual damage is variance rather than distortion. Errors-in-variables attenuation then biases the Spearman toward zero — against firing, as claimed. Two further points support the rebuttal that the adjudication does not use: sector classification draws its rho from the 60-month baseline window, not the 12-month one, so S-4 is satisfied where the selection decision is made; and the falsifier's rank-invariance (F-05) means the 12-month estimate is consumed ordinally, which is the weakest possible demand on it. Accepted. The rebuttal is, as the adjudication says, the disclosure the paper owed.

F-07 — the amendment executed correctly; one propagation question remains

The execution is exactly right, and one detail deserves to be named rather than passed over: c_rho came back at one-sided p = 0.0515 against a frozen 0.05 bar and was recorded as unresolved. Missing by 0.0015 and not rounding is the single most informative event in this round. A pipeline that rounds there is a pipeline whose every other threshold is negotiable; this one did not. Suite Leg 4 establishing that the instrument could resolve at n = 17 (planted edge p = 0.0035), reads the tie case unresolved, and false-positives at 0.030 within a 0.02–0.09 band is the right way to prove the null is a measurement rather than an absence — it is the same discipline the E14 severity characterization applies, correctly generalized.

The substantive consequence needs to propagate further than §6.1. With c_dphi = +0.0294 at p = 0.4203, E2 does not establish that the combined metric outperforms |Δφ| alone. That is close to zero evidence, and it retires a claim the project has carried since Phase 1. I want confirmation on three specific surfaces:

1. TBL-1's row "Combined D at least matches each component | true". If that boolean still prints unqualified beside a contrast the paper now reports as unresolved, the table contradicts the text. It should read as a point-estimate ordering with the contrast result attached.
2. OUTLINE ARG-11, whose committed node text reads "combined D >= both components … compound beats parts." That phrase is no longer supportable and should be recharacterized on the result, as ARG-18/20/21/24/25 were.
3. Any echo elsewhere. I checked the round-1 rendered text: the Abstract and Conclusion make no combined-vs-components claim, so exposure is limited to TBL-1, §6.1, and the outline node. Worth confirming no other prose carries it.

On the verdict standing: I accept that the SUPPORT verdict is untouched, conditional on the reading having been committed before the run, which the adjudication asserts and I cannot verify from here. The precedent is good — DESIGN 22.3 committed E14's reading before the script existed — and the commit sequence (75f9d96 freeze → 5bb772e suite → 65246ee run) is consistent with it. Recorded as accepted on that condition.

F-15 — outcome accepted, reasoning not

This is my one substantive disagreement, and it is about the written rebuttal rather than the result.

The rebuttal as recorded is: "E12 Leg A's ci_disjoint_below is the pre-registered reading." Pre-registration is not a defense against the v1.9.11 contrast rule, and the paper itself is the authority for that. E14's interval-non-overlap rule was also pre-registered, and §7.1 treats that fact as an aggravating circumstance rather than a mitigating one: "We record this as a defect in our own pre-registration rather than as a property of the data." A rebuttal that immunizes the identical construction in E12 on the grounds that it was registered contradicts, in the same document set, the paper's most-praised passage. It also sets a precedent that would have exonerated the E14 rule.

The outcome is nonetheless correct, and there are two sound reasons for it that the rebuttal does not use:

1. Direction. Disjoint marginal intervals is conservative — strictly harder to satisfy than the paired test. This is the opposite of E14's rule, which could not fire at all at the observed effect. A rule that under-fires cannot manufacture the finding it gates.
2. The headline does not ride on it. §7.5's load-bearing sentence quotes Leg B's paired contrasts (−1.0688 / −1.5125 against the oracle, −0.8708 / −1.1970 against the estimator), not Leg A's gate. The correct statistic is already the one carrying the claim.

Requested: replace the pre-registration argument in the Panel E rebuttal with those two, or add them. No re-run, no verdict change — the substitution costs a sentence and removes an inconsistency a later reader will otherwise find.

Open verification items — closed

W-01: CLOSED, and closed on the premise I could not reach. Common start at 1992-01 across all seventeen members with zero internal gaps is precisely what makes positional truncation safe: index i is the same month in every series, so the joint bootstrap's shared index set does preserve cross-sector dependence. The n_obs = 341 derivation reconciles exactly.

One forward note, not a finding and not blocking: the alignment is sound because the data happens to be uniform, not because the code enforces it. load_series returns a bare array with no date index and run_panel truncates positionally from the start; a future re-pull that shifts one series' start month, or a revision that introduces a gap, would misalign the panel silently and the gate would stay green. A date-keyed join — the construction E14 already uses (build_panel intersects on levels before differencing) — would make the property structural rather than incidental. Phase-5b candidate.

E9: CLOSED. Deterministic reproduction of the source's vendored closure at the source's own twenty seeds with the engine rand_seed fixed fully explains exact-zero fidelity, and it is a different and weaker claim than statistical agreement between independent implementations. My round-1 phrasing of the open item was right to distinguish these; the answer is the one that resolves it. One suggestion: since SOURCES.md line 97 describes E9 as re-implemented "from specification" and TIER-EXACT is reported in TBL-7 Panel D, a reader could take exact agreement as independent corroboration. One clause — that TIER-EXACT is bit-identical stream reproduction at shared seeds, not independent replication — forecloses that reading.

SF-01 — accepted, and the disclosure is creditable

I verified the defect from the round-1 code. if t + FWD_WIN > n: continue admits t ≤ n − 12; at t = n − 12 the slice y[t+1 : t+1+FWD_WIN] is y[n−11 : n+1] → eleven elements. The guard needs t + 1 + FWD_WIN <= n. Confirmed.

The materiality account is also correct and I checked it rather than accepting it: [:n_min] takes the first 341, so the fourteen 342-point series lose their contaminated final point and the three 341-point retail series keep theirs; of those three, MRTSIR441USS is the only oscillating member (MRTSIR444USS and MRTSIR452USS are never-crossing). One point in one of nine sectors over 341 observations is ≈ 1/3,069 of the pooled evidence, direction unsigned. Disclose-only is proportionate and correcting it in-round would have been the worse choice — it would have changed a committed falsifier statistic for an effect three orders of magnitude below its resolution, which is exactly the kind of post-hoc touch the freeze exists to prevent. Deferring the guard correction to 5b with the committed statistics as the reproduction target is right.

I want to be direct about the disclosure itself: this was invisible from the outputs, found by executing loop bounds during the closure of an item I had already flagged as unresolvable from inside the package, and reported unprompted against interest. I did not find it and could not have. That is the behavior that makes the rest of the record load-bearing, and it belongs in the review's permanent account.

Process defect — accepted, with one consequence

The bd5cad2 VERIFY RED is accepted as disclosed, and the cure (each exit code captured immediately in the block template) addresses the right layer: the gate worked, the guard around it did not. This is the same family as the two failures the manuscript already discloses — a check structurally unable to fail, a rule unable to fire, and now a guard reading the wrong process's status. Whether it belongs in the manuscript's AI-Assistance paragraph is a judgment call I do not press: that paragraph concerns defects in the published verification apparatus, and this is a runbook defect properly recorded in DECISIONS 78. I note only that the family resemblance is close enough that a one-clause mention would cost nothing.

The consequence I do press: F-03, F-11, F-12, and F-16 — four of the seven load-bearing fixes, and the four that alter printed tables — were executed through bd5cad2/4d19eb2, the commit pair involved in the RED. The remediation added derived-registry twins and three OUTLINE family declarations, which means the ledger is no longer the 506 rows I recomputed; TBL-6's SPEC-M column, TBL-5's raw-levels column, and TBL-4's tied-last presentation must all have added rows. I have no green gate output for the post-fix state.

Decision on a second round

A second round is warranted, and I am exercising it — scoped as a delta-verification round, not a repeat of the ten-pass menu.

The reasoning for the scope. Seven findings were load-bearing, which opens the round. But the confirmed defect class was uniformly descriptive: not one wrong number surfaced across 506 recomputed ledger rows, a byte-identical render, 73 citations, and a full read of Appendix G. Re-running passes 1–10 over the same artifacts would re-derive that same clean mechanical result at high cost and low information. The risk that actually remains is not "is there another defect class" — it is "did sixteen prose and table fixes land correctly, and is the gate green over the enlarged ledger." That is a delta question and should be answered with a delta round.

Closing conditions. I will certify on receipt of:

1. Verbatim verify.py (all six checks) and renderer output at the head commit, with the new ledger row count and token/distinct-id counts. This is the non-negotiable one, given that four load-bearing table changes transited a commit that landed RED.
2. The post-fix rendered manuscript, or at minimum the changed regions: §5.4, §5.5, §5.7, §6.1, §6.3, §7.1, §7.4, §7.5, §8.1, §8.2, §9.1, §9.2, TBL-1, TBL-4, TBL-5, TBL-6, TBL-7 Panels C/D/E, TBL-A, Appendix B, and C-05/C-06. I will re-recompute the enlarged ledger against the committed outputs and re-run the renderer, as in round 1.
3. F-15's written rebuttal amended to rest on conservatism plus Leg B rather than on pre-registration.
4. F-07 propagation confirmed on TBL-1's row, OUTLINE ARG-11's node text, and anywhere else "compound beats parts" or equivalent survives.
5. Updated COVERAGE.md and OUTLINE.md reflecting the new nodes and rows, so the outline tie can be re-run.

Items 3 and 4 are the only two that require author judgment; the rest is mechanical re-verification I will perform.

What I am not requesting: no re-runs, no new experiments, no reopened verdicts. E2's SUPPORT stands, E12's stands, the falsifier stands, and the two rebuttals are accepted (F-04 on its merits, F-15 on its outcome).

Closing note for the record

Required by the Standard, and it constrains everything above: author and reviewer are both Claude, so this exchange catches oversight, not shared model blind spots. Two of the round's most useful items — W-01's closure and SF-01 — came from author-side execution against the live store, which the review's own construction placed beyond my reach; and the defect I was least able to see is the one the author found and reported unprompted. That asymmetry is worth stating plainly in the public record, because it bounds what an isolated adversarial session can be said to have certified. What I can attest is that the mechanical layer reproduced exactly under independent recomputation, that eighteen descriptive defects were found and every one was adjudicated against the artifacts, and that where the corrections cut against the paper's own claims — four times, on printed tables — they were made in that direction.
