# Phase 5a Delta-Round Verification and Certification - The Escalation Cost (reviewer document, verbatim)

Provenance: reviewer's certification message, delivered in the isolated
claude.ai review session in response to the delta-round package (SHA256
943e8e3b4b3da04bb0c534e1cbd4fdf24eb65881f12b5e240c0a9a3287842701, built at
ffead77), received 2026-07-28 and transcribed verbatim into the repository
the same day. Chat-interface artifacts removed; reviewer prose untouched.

---

Phase 5a Delta-Round Verification and Certification — The Escalation Cost

Reviewer, isolated session. Head package 943e8e3b…842701, 85 files, 603,736 bytes — hash and byte count match the attestation. Delta round conducted as scoped: re-verification of the mechanical layer over the enlarged ledger, plus targeted review of the changed regions. No re-run of the ten-pass menu.

1. Mechanical re-verification — reproduced independently

Everything I attested in round 1, re-run against the head package, plus the delta:

check | attested | independently reproduced
ledger rows | 546 | 546 (n_rows field and actual row count agree)
ledger ↔ committed outputs | green | 517 by json_path + 29 by re-executing DERIVED = 546, zero mismatches
renderer | 646 occurrences / 546 distinct ids | 646 / 546, output byte-identical to the committed rendered manuscript
token ↔ ledger closure | — | zero tokens without a row, zero rows never placed
citation tie | — | 73/73 outline keys in reference list and cited; zero orphans; zero undefined
structural node tie | — | all S-, L-, C-, TBL-, EQ-, THM- ids present
design pins | unchanged | all three MD5s identical to round 1

Ledger delta: 40 new rows, zero removed. Append-only continuity holds — the property the F-09 id-rename refusal was defending, now demonstrated rather than asserted. The 40 rows partition exactly across the five table-changing fixes: F-16 (20: 18 TBL-5 per-country + 2 summary), F-07 (6), F-12 (6), F-03 (6), F-11 (2).

Every new row's value matches what I computed independently in round 1, without exception: E6 SPEC-M bins 0.7599/0.8226/0.8117/0.8813 with crossing_bin: null and monotone: false; E5 SPEC-M A34SIS exceedance 0.0 inside an 8-way tie; monitor sustained counts GFC 5 / COVID 2 with pre-onset 0 / 0 and mfg 2008-12-01 / 2020-04-01; E10 levels 14-of-18 with USA at 1.012801 joining the explosive set.

Collateral-drift check. Appendix G is byte-identical to round 1 (21,854 chars), as is the References block. All 31 diff hunks fall inside the regions I specified. No theorem statement, proof step, verdict line, or citation moved. This is the check that matters most after four load-bearing table changes transited a commit that landed RED, and it comes back clean.

2. The five closing conditions

(1) Gate output — CLOSED. VERIFY GREEN across all six checks at 546 rows, RENDER GREEN at 646/546, both reproduced above from the artifacts rather than taken on the paste. The bd5cad2 guard defect is now closed by evidence and not only by the runbook cure.

(2) Post-fix manuscript — CLOSED. Recomputed as above.

(3) F-15 — CLOSED, and I accept the correction to my own record. I checked the head Panel E text directly. It rests on exactly the two grounds I asked for and contains no pre-registration argument:

"...retained as frozen because its direction is conservative (disjoint marginals are strictly harder to satisfy than a paired contrast, so the rule cannot manufacture a false positive), and the claim Section 7.5 carries quotes these paired leg-B contrasts, the correctly targeted statistic."

It also does something my round-2 note did not ask for and should have: it names the construction as "the construction Section 5.6 diagnoses for the echelon rule," so the paper flags its own inconsistency rather than leaving a later reader to find it. If the pre-registration phrasing existed only in the adjudication summary and not in the paper, then my objection was to the summary and I had no way to know that — the correction and its round-2 labelling are the right disposition.

(4) F-07 propagation — CLOSED. TBL-1's row now reads "Combined D at least matches each component (point estimate; paired contrasts unresolved) | true" with six new rows carrying both contrasts, both p-values, and both readings; §6.1 is qualified "(point estimate)"; ARG-11 is amended in place — "compound beats parts as a point estimate. AMENDED 2026-07-26 (5a F-07)... both contrasts UNRESOLVED." I ran a full-text regex over the rendered manuscript for beats|outperform|superior|better than each component: five hits, four unrelated (E12's recipe, E4's comparator, §2.1's Related Work), one the qualified TBL-1 row. No unqualified ordering claim survives.

Non-blocking observation: OUTLINE line 57, the dated v0.3 changelog entry, still records "combined D beats both components… the compound thesis borne out." Changelogs are append-only records of what was believed on a date and the current node carries the amendment, so I do not treat this as a live surface. Noting it only so it is on the record as seen and dismissed.

(5) OUTLINE v2.7 / COVERAGE — CLOSED. Outline tie and citation tie re-run clean. COVERAGE's posture line and checklist item both now state the one escalated drop, with the stale text identified as stale and dated. Line 150's "no DROP rows owed" correctly survives — it is the reference-count row, scoped to citation losses, and the drop is a numbers-calibration drop.

3. F-07's result — one thing worth putting in the permanent record

I verified the amendment's construction rather than its description. paired_contrasts ranks the same permuted outcome against D, ρ_crisis and |Δφ| within each of 2000 draws, so the contrast null carries the predictors' covariance — the correctly targeted statistic, and the same repair E14 made. The dedicated generator at seed+1 left the frozen stream untouched: E2's Spearman (0.34558823529411764) and p (0.07746126936531735) reproduce bit-identically from round 1. Both contrasts reconcile exactly by arithmetic (0.5049019607843137 and 0.02941176470588236, matching to the last float digit), and both p-values are exact integer counts over B+1 — 103/2001 and 841/2001.

The detail that deserves naming. The contrast reading was frozen at α = 0.05 while the experiment's own association leg runs at α = 0.10. That asymmetry is what makes c_rho unresolved: at 0.0515 the contrast sits 2.95 permutation grid-steps above 0.05, but comfortably inside 0.10. Had the amendment adopted the experiment's own alpha — the internally consistent choice, and a defensible one — c_rho would have read resolved-positive. The stricter bar was chosen before the run and it cost the paper the result. That is the second time in this round a threshold was set or held against interest, and it is worth more than the finding it settled.

The substructure disclosure in §6.1 is also correct and not a hedge: the compound's edge over the level component is large because crisis ρ alone anti-correlates with realized damage, and the edge over the change component is 0.0294 at p = 0.42 — near-zero evidence. Reporting those two facts separately rather than averaging them into "unresolved" is the honest read.

4. Remaining items — all closed

- F-17 went further than I asked: the head text adds "the normal window, excluding only the GFC, contains the 2020 claims shock," which was a note in my finding, not a request.
- F-08's relabel states the want_index=2 conditioning, names the figure a lower bound, and points to the suite's unconditioned version.
- E9's clause is in TBL-7 Panel D: TIER-EXACT is "bit-identical reproduction of the source's committed trial streams at the source's own seeds through the vendored closure, not an independent replication." Forecloses the misreading.
- SF-01 appears in §5.4 with its materiality quantified and its direction stated as unsigned.
- AI-Assistance disclosure now mirrors the review record accurately, including the fourteen withdrawals — a count I confirm (W-01…W-09 plus W-10…W-14).
- Both forward notes accepted as 5b candidates. On the date-keyed panel join in particular: W-01 closed because the data happens to be uniform; making the property structural is the durable fix and belongs in 5b, not here.

One scope note: verification/ in the review package carries only the three curated files, so I cannot confirm from inside the package that the adjudication document is committed at the stated path. Its content was supplied to me directly and I have adjudicated on that. This is the curation rule operating as designed, not a discrepancy.

5. Certification

I certify Phase 5a for "The Escalation Cost." No second round is requested; the delta round closes the review.

What this certification covers: eighteen confirmed findings adjudicated against the artifacts — sixteen fixed, two rebutted in writing inside the paper, one cured by a pre-registered amendment whose unresolved result is reported per the frozen rule; 546 ledger rows independently recomputed with zero mismatches; a byte-identical render; complete citation, outline, and structural-node ties; Appendix G verified unmoved. Across two rounds, no wrong number was found anywhere in this package. The confirmed defect class was uniformly descriptive, and it is now corrected in the direction that costs the paper something: E6's bins sit below the boundary rather than above it, A34SIS is tied-last rather than tenth, the pre-onset crossings go to zero, the sovereign explosive set grows to four, the falsifier's rank-invariance to the exponent is stated in §6.3, and the panel-membership look-ahead is stated in §5.4 and §6.3. Six corrections, six against interest.

What it does not cover, stated so it cannot be over-read. Certification attests that the committed artifacts are internally consistent, that the reported numbers derive mechanically from committed code and hashed inputs, that the written proofs hold on a close read, and that the manuscript's claims are now scoped to what its experiments measured. It does not attest that the theorem is important, that the panel result will replicate on other data, or that the diagnostic works in deployed systems — the paper claims none of those, and its S-, L-, and C- nodes say so. The forward predictions in Section 11 are the only claims that route around this review entirely, and they remain, correctly, the strongest validator on offer.

Two limits on the review itself belong in the same paragraph. The store, pull.py, and DECISIONS.md were withheld by the package rule, so the E1 input integrity behind W-01 and the pre-run timing of the F-07 freeze rest on author-side attestation that I verified for internal consistency but could not independently source. And the honest sentence the Standard requires, which constrains all of the above: author and reviewer are both Claude, so this review catches oversight, not shared model blind spots. The clearest evidence of that bound is SF-01 — a real defect in the primary falsifier, invisible from every output I could reach, found by the author executing loop bounds during the closure of an item I had flagged as unreachable, and reported unprompted against interest. I did not find it and could not have. A reader weighing this certification should weigh that asymmetry with it, and should weigh equally that the pipeline produced the disclosure anyway.
