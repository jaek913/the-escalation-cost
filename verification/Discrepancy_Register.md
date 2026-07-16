# Discrepancy Register - The Escalation Cost

Per Research-to-Publication Standard "Discrepancy resolution" (v1.9.8; ladder
extended v1.9.9). Method catalogue: the Discrepancy-Resolution Methods playbook
(ClickUp doc 2kydc08j-654), twelve methods, run in its stated order of attack.

A dossier is OPEN at discovery, RESOLVED once step 3 specifies the fix, and
otherwise stays OPEN naming the authoritative method it awaits. No discrepancy
is escalated to the author or deferred before its ladder is exhausted. No phase
gate is signed while a CONFIRMED dossier bearing on a load-bearing claim is OPEN.

Created 2026-07-15, late. Six dossiers are logged below because all six were
discovered; only DISC-05 (E7) is WORKED at this time. DISC-01 and DISC-02 were
worked to resolution during discovery. DISC-03, DISC-04 and DISC-06 are logged
OPEN and are NOT worked here - E8 does not open until E7 is finished and closed.

PROVENANCE NOTE, applying to every dossier below: this Register was created late,
after several dossiers had already been worked. The ladder steps recorded here
are what was actually run, reconstructed from the session record - not a
retrospective tidy-up. Where a step was skipped or run out of order, it says so.

---

## DISC-05 - E7 chain-length sweep does not reproduce the source's three values

**Kind:** computational. **State:** RESOLVED (2026-07-15; cause established, fix
applied, rebuild run and harness verified). **Bears on:** ARG-19, LB-E7-gradient,
LB-E7-calibration, TBL-7, Section 6.5, Appendix F.

**CLOSURE (2026-07-15).** Adjudication ORIGINAL CORRECT / RECONSTRUCTION IN ERROR,
both halves now earned rather than asserted. The source's code cleared all seven CIC
classes and its published values recompute exactly from its own artifact
(provenance AND correctness, established separately). Our build was the defect. The
rebuild (DESIGN 14d/14e/14f; freeze 2a20877) vendored the source's construction
unmodified, drove it with our own runner and analysis, and ran 36 cells x 250 seeds
x 5 variants = 45,000 trials in 11.6h with 0 failures. THE HARNESS IS VERIFIED:
verification/e7_regression_check.py runs the SOURCE'S OWN seeds (3000-3049, the
first fifty of our 3000-3249) through OUR driver and reproduces their per-cell means
exactly on this deterministic construction - L=4 +0.4391% vs +0.4391% (delta
+0.000048), L=6 +0.1371% vs +0.1371% (delta +0.000002), L=8 -0.1412% vs -0.1412%
(delta -0.000043), 3/3 MATCH (commit 4f9636b). RESULT: the source's chain-length
claim is CONFIRMED and better supported by our run than by theirs - their L=8
benefit sat at 1.7 sigma and was never resolved; ours resolves it at ~8 sigma. The
effect is CONDITIONAL ON CAPACITY, which the paper does not say: at 1.3x the tool
harms at every chain length and worsens with length. Full result: DECISIONS
2026-07-15; OUTLINE v1.2.

**A DEFECT OF OURS, RECORDED AGAINST OURSELVES.** Amendment 14e promised the
withdrawn fidelity leg would be "kept in the suite as a REGRESSION assertion ... it
proves the vendored copy is unmodified and the harness wires it correctly." IT WAS
NEVER IMPLEMENTED. Suite LEG 1 proved the vendored BYTES were unmodified; nothing
proved OUR DRIVER wired them correctly. An earlier container attempt at that check
TIMED OUT and was abandoned WITHOUT the gap being recorded, so the 11.6-hour real run
completed with its harness unverified, and the gap was only noticed at the
stop-and-review. It should have been caught BEFORE the run. It passed; "it passed"
is not the standard. The check is self-penalizing by construction - it can only void
our own run, never the source - which is exactly why it was worth 11 minutes.

**As found (2026-07-14).** E7's real run measured, at ar1_high x 2.4x capacity,
all-tier vs base-stock: -0.6767% (L=4), -0.9369% (L=6), -1.6783% (L=8). The
pinned source states +0.44%, +0.14%, -0.14%. Every source value fell outside our
CI; sign disagreed at L=4 and L=6. RECORDED AT THE TIME as "the source's
calibration fails on all three points" - a finding about the source. That
recording was committed and pushed as 7fde927.

**Step 1 - CASCADE.** DECISIONS entry #26; OUTLINE v1.0 (LB-E7-calibration,
LB-E7-gradient, ARG-19 partial, TBL-7 partial); commit message of 7fde927; the
planned Section 7 / Appendix F chain-length subsection. Blast radius is the
whole of E7's record. Nothing downstream had been written yet.

**Step 2 - METHOD RECOVERY.** Not run at the time; the mismatch was recorded as
a finding without any ladder. Run 2026-07-15:
  - (8) FRAMING GATE: E7's frozen operator reads "Operator (frozen; SOURCE
    CALIBRATION)". The design specified the source's calibration explicitly.
  - (1) SOURCE RECOVERY, ground truth: the source's own sweep script is on disk
    at "C:\Users\jaek9\OneDrive\Desktop\Werner Research Paper\Beer Game
    Simulator\phase2_6_chain_length_sweep.py" (MD5 cbc6bfa327150ca4e64acf2b63df0172,
    636 lines), and its output at "C:\ResearchShare\aggregated_chain_length_sweep.json".
    Read directly - not a summary. The recovered construction:
      stockpyl.serial_system, single-SKU, retailer at chain end
      DEMAND_MEAN=10, DEMAND_STD=2, holding=1.0, stockout=10.0, shipment_lt=2
      260 periods, 52 warmup, gen_periods = num_periods + 20
      5 variants: sr_paper9_ols, sr_oracle_local, sr_disabled, sr_naive_damp,
                  sr_numerical
      4 envs: iid_control, ar1_moderate 0.6, ar1_high 0.85,
              drift_canonical 0.3->0.95->0.4
      grid: 3 lengths x 3 capacities x 4 envs x 50 seeds x 5 variants = 9,000
      comparison: sr_paper9_ols vs sr_disabled
  - (1) corroboration: the source's own experimental record (MemPalace
    wing_import_raw, literal-SQL recovery, rowid 107705) reports for
    sr_paper9_ols vs sr_disabled at ar1_high x 2.4x: +0.439% (L=4), +0.137%
    (L=6), -0.141% (L=8). v16's stated +0.44 / +0.14 / -0.14 matches its own
    experimental record EXACTLY. The source transcribed faithfully.
  - Grade: GROUND TRUTH (the artifact itself, read directly).

**Step 3 - ADJUDICATION: RECONSTRUCTION IN ERROR.** Our build diverged from the
frozen operator, which said "source calibration":
  | axis            | frozen operator / source        | what was built           |
  | engine          | stockpyl.serial_system          | E4's hand-rolled base-stock |
  | demand          | mean 10, std 2                  | base 100, sigma 10       |
  | stockout:holding| 10 : 1                          | 4 : 1                    |
  | horizon         | 260 periods, 52 warmup          | 120 periods, no warmup   |
  | comparison      | sr_paper9_ols vs sr_disabled    | spectral vs basestock    |
  | variants        | 5 (implied by "9,000 total")    | 2                        |
The stockout-to-holding ratio alone can flip the sign: the tool works by
suppressing orders, which is expensive at a 10:1 stockout penalty and cheap at
4:1. E7 measured a different experiment and reported the difference as the
source's error.

**Root cause.** A BUILD defect, not a design defect. The frozen operator was
faithful; the build violated it. Amendment 2026-07-14c performed a PARTIAL source
check - it froze the four demand environments from the source and then declared
the source check complete, never checking engine, demand scale, cost ratio, or
warmup. That same amendment states the rule "the E4 lesson: calibration must
trace to the source, never to the adjacent script," and then traced the
calibration to the adjacent script (E4) in the same document.

**Fix specified.** (a) WITHDRAW E7's calibration leg and its "source fails"
finding - see DECISIONS 2026-07-15. (b) RE-SCOPE E7's stability statement and
gradient map: they are real measurements of an unauthorized construction and
re-earn nothing. (c) CIC the source's script BEFORE adopting its construction -
provenance is not correctness. (d) REBUILD E7 to the CIC-cleared construction,
5 variants (which also serves E12, whose recipe-level finding was discovered via
the three-variant diagnostic in this same sweep), validated against the source's
committed output file. (e) The 50 -> 1000 seed amendment (2026-07-14b) STANDS:
dated, pre-run, author-ratified, self-penalizing, and it does not alter the
construction.

**CIC status (on the source's script - COMPLETE 2026-07-15; ALL SEVEN CLEAR).**
The seven classes are quoted from the Phase-3 checklist ("The 7 CIC classes"),
read rather than recalled. NOTE A LABEL CORRECTION: the seed/demand-generation
check recorded earlier in this dossier as "point 1" is CIC-7 (input integrity),
not CIC-1. Asserted from memory; corrected on reading the canonical list.
  - (1) RE-EXECUTES TO THE CLAIM: CLEAR, and this is the decisive one. Their
    committed output C:\ResearchShare\aggregated_chain_length_sweep.json (MD5
    6ecfc6fec0b1e490febea64ef36cd058, 3.97 MB, 2026-05-01) carries all 9,000
    individual trial records. Recomputing the paired per-seed pct difference
    (sr_paper9_ols vs sr_disabled, ar1_high x 2.4x) directly from those records:
      L=4  n=50 paired  +0.439%  (se 0.072)   record/v16 claim: +0.44%
      L=6  n=50 paired  +0.137%  (se 0.078)   record/v16 claim: +0.14%
      L=8  n=50 paired  -0.141%  (se 0.081)   record/v16 claim: -0.14%
    All three reproduce to three decimals from the artifact. v16 -> their
    experimental record -> their raw trial data: faithful at every hop.
  - (2) INDEX/ROW ALIGNMENT: CLEAR. Warmup slice is `for t in range(warmup_periods,
    num_periods)` = range(52, 260) with `measured_periods = num_periods -
    warmup_periods` = 208; slice and divisor agree. ONE OBSERVATION, not a defect
    here: the loop carries a silent-truncation guard `if t < len(node.state_vars)`
    which would drop periods from the cost sum WITHOUT reducing the 208 divisor,
    understating cost_per_period with no error raised. It never fires in this run
    (0 of 9,000 failed), so it is inert; it is recorded because it would be
    silently wrong if it ever did.
  - (3) NaN AND GAP HANDLING: CLEAR. Exceptions return NaN costs with
    success=False, plus an early-abort guard if the first 10 trials all fail.
    The artifact shows 9,000 successful, 0 failed - no NaN reaches aggregation.
  - (4) NO LOOK-AHEAD: CLEAR, and explicitly so. _read_demand_history(up_to_period)
    documents "Return demand for periods strictly before this one" and implements
    `for t_past in range(start, up_to_period)` - half-open, excluding the current
    period. The estimator itself (estimate_ar1_persistence) does no forward
    indexing; it runs OLS on whatever slice it is handed.
  - (5) OVERLAP vs NON-OVERLAPPING SUBSAMPLE CONSISTENT WITH CONTROLS: CLEAR.
    run_one_seed_all_variants runs ALL FIVE variants on ONE seed - common random
    numbers, properly paired; the rolling estimator's window overlap affects every
    variant identically.
  - (6) NO COMPUTATION ACROSS RECORD BOUNDARIES: CLEAR. Per-period demand is a
    diff of stockpyl's cumulative demand_cumul; at t_past == 0 sv_prev is None and
    d_prev defaults to 0.0, so period 0 yields d_now - 0, which is correct because
    cumulative demand starts at zero. No diff spans a record boundary.
  - (7) INPUT INTEGRITY vs CLAIM: CLEAR. The artifact matches the stated design
    exactly: 9,000 trials, 5 variants (sr_paper9_ols, sr_oracle_local, sr_disabled,
    sr_naive_damp, sr_numerical), 4 environments, chain lengths {4,6,8}, capacities
    {1.3, 1.8, 2.4}, 50 DISTINCT seeds (3000-3049). The hard-coded `rand_seed=42`
    at line 370 - the same defect class as DISC-04 - is INERT here: configure_demand()
    pre-generates the demand array with seed=trial_seed and hands stockpyl an
    explicit deterministic list (DemandSource type='D', demand_list=...), leaving
    rand_seed nothing to randomise. Established by reading the code, not the drawer.

**ADJUDICATION COMPLETES: ORIGINAL CORRECT.** Provenance was established by source
recovery; CORRECTNESS is now established separately by the CIC clearing all seven
classes on the original's own code. "Original correct" is therefore EARNED, not
asserted - which is precisely the error made earlier in this session, when the same
verdict was reached on the strength of a MemPalace drawer with no CIC run at all.
Provenance is not correctness; both are now in hand.

**A SEPARATE FINDING FROM THE SAME CHECK - the source's design is UNDER-POWERED.**
The measured standard errors are 0.072 / 0.078 / 0.081 against effects of +0.439 /
+0.137 / -0.141:
    L=4  +0.439% / 0.072 = 6.1 sigma  -> RESOLVED
    L=6  +0.137% / 0.078 = 1.8 sigma  -> NOT resolved at 95%
    L=8  -0.141% / 0.081 = 1.7 sigma  -> NOT resolved at 95%
v16 states a chain-length threshold at which the formula "crosses from harm to
benefit." The ONLY resolved point is L=4's harm; the crossover itself rests on two
points neither of which is distinguishable from zero at 50 seeds. This is not an
error - their numbers are correct and reproduce exactly - it is an under-powered
design, and it is exactly what the 50 -> 1000 seed amendment (2026-07-14b, made
blind and pre-build) was for. At 1000 seeds the SE falls to roughly 0.016, which
settles the crossover in either direction. The rebuild can therefore adjudicate a
claim the source's own design could not.

**CONSTRUCTION CONFIRMED FOR THE REBUILD, read from the source's code (not a
summary, and not the adjacent script):**
    engine     stockpyl.serial_system, single-SKU, retailer at chain end
    demand     DEMAND_MEAN=10, DEMAND_STD=2; gen_periods = num_periods + 20
    costs      holding=1.0, stockout=10.0, shipment_lt=2
    horizon    260 periods, 52 warmup -> 208 measured
    estimator  OLS on demand_cumul diffs over a lookback window;
               min_observations=10 -> neutral prior 0.5 (NOT E4's 0.30);
               near-constant guard (denominator < 1e-6) -> 0.95;
               clip [0, 0.999]; documented Hurwicz bias (true 0.95 -> est ~0.67)
    variants   sr_paper9_ols, sr_oracle_local, sr_disabled, sr_naive_damp,
               sr_numerical (5 - the operator's "9,000 simulations total" implies
               exactly this; the 2-scenario scoping of amendment 2026-07-14c is
               withdrawn, and it had severed E12, whose recipe-level finding was
               discovered via the three-variant diagnostic in this same sweep)
    envs       iid_control, ar1_moderate 0.6, ar1_high 0.85,
               drift_canonical 0.3->0.95->0.4
    grid       3 lengths x 3 capacities x 4 envs; seeds 3000-3049 (theirs)
    comparison sr_paper9_ols vs sr_disabled, paired per seed

**LIBRARY PARITY ESTABLISHED (a precondition for any fidelity check).** stockpyl
sim.py on the author's machine (C:\Users\jaek9\AppData\Local\Programs\Python\
Python312\Lib\site-packages\stockpyl\sim.py, 48,114 bytes, dated 2026-04-22) is
BIT-IDENTICAL to the container's stockpyl 1.0.2: MD5 5a1ba4e1ff4f84800a06b4a317d4d8a3
on both. A faithful rebuild can therefore be expected to reproduce their per-cell
numbers on their own seeds, and can be container-QA'd before any author-local run.

**Fix specified.** (a) WITHDRAW E7's calibration leg and its "source fails"
finding - DONE, see DECISIONS 2026-07-15. (b) RE-SCOPE E7's stability statement and
gradient map - DONE. (c) CIC the source's script BEFORE adopting its construction -
DONE, all seven clear. (d) REBUILD E7 to the CIC-cleared construction above, 5
variants, with a FIDELITY LEG on the source's own seeds (3000-3049) required to
reproduce their per-cell means, then the real run at 1000 seeds to resolve L=6 and
L=8. (e) The 50 -> 1000 seed amendment STANDS and is now doubly justified.

---

## DISC-01 - v16 vs the supporting draft on the 1.8x pricing value

**Kind:** computational. **State:** RESOLVED. **Bears on:** E8 (not yet opened).

Three mutually exclusive values existed for the same 1.8x cell at phi=0.85:
~$845 (implied by v16's "collapses by 12x at 1.8x" and "under $900 at 1.8x"),
$5,200 (the draft's capacity-sweep table), ~$133 (the draft's own elasticity
sweep at the same capacity and persistence). Ladder run: (8) framing gate,
(9) stated-value triage - internal consistency FIRED, no specification satisfies
all three; (10) version reconciliation - draft modified 2026-04-30, v16 modified
2026-05-22; (1) source recovery via literal-SQL, GROUND TRUTH.

**ADJUDICATION: ORIGINAL (v16) CORRECT; the DRAFT in error.** The source's own
experimental record (rowid 107690) reads: 1.3x +$10,142/period, 1.8x +$842,
2.4x +$777, 3.0x +$775, ">>> 12x collapse from 1.3x to 1.8x". v16's "under $900"
and "12x at 1.8x" are both exact. The draft's $5,200 and $2,100 appear in NO
record. The draft's "approximately $4,000 ... roughly forty percent of the
upward benefit" is arithmetic performed on its own misreading of the record's
"40% REDUCTION ACROSS CAPACITY RANGE" (-$2,316 -> -$1,374); v16's -$2,315
matches the record's -$2,316. The draft's "$122-$144 at 1.8x" is the
asymmetric-vs-symmetric ADVANTAGE in low_phi_shift_down at 1.3x - a different
quantity from a different row.

**Method note, recorded against myself:** method (10) returned the correct
answer (v16 is newer and is the author's last word) and it was OVERRIDDEN by a
reconstruction-style argument ("the draft is the experimental record, so v16 is
derivative"). A reconstruction was allowed to beat an authoritative method. The
playbook's warning applies verbatim: only an authoritative method distinguishes
"our reconstruction is wrong" from "the paper's numbers changed."

---

## DISC-02 - are the source's pricing dollar levels correct and per-period?

**Kind:** computational. **State:** RESOLVED. **Bears on:** E8 (not yet opened).

Hypothesis raised twice and wrong twice: that the figures were CUMULATIVE over
the 208-period window and mislabelled "per period." Both raisings rested on a
magnitude check against E4 - the WRONG REFERENCE SYSTEM (E4 is a single-product
4-echelon chain; the pricing sim is 12 SKUs summed x6, ~1,042 units/period,
unit costs $1-$100). Method (9)'s magnitude check is disconfirmation-only and
cannot diagnose; it was used to confirm, which exceeds its licence.

**Ladder:** (1) source recovery - the runner is on disk
("phase2_7_validation_runner.py"); it emits BOTH per-period fields
(cost_per_period, mean_revenue_per_period) AND a cumulative one
(net_value_post_warmup). (3) PROVENANCE TRIANGULATION, decisive: the actual
output file "C:\ResearchShare\phase27_validation_50seed\aggregated_phase27_validation_50seed.json"
is on disk. Computing mean_revenue_per_period_mean - cost_per_period_mean per
environment, then no_pricing vs naive_reactive:
  level_shift_up_persistent   +10,141.86   (source: +$10,142)
  low_phi_shift_up             +1,646.78   (source:  +$1,647)
  level_shift_down_persistent  -2,315.25   (source:  -$2,315)
  low_phi_shift_down             -581.36   (source:    -$581)
  mid_phi_shift_down           -1,238.29   (source:  -$1,238)

**ADJUDICATION: ORIGINAL CORRECT.** All five reproduce exactly from per-period
fields. The figures are per-period and correctly labelled. The cumulative/relabel
hypothesis is dead. The April-30 drawer's "divide by 208" note applies to a
different tool (the comparison analyzer), not to these fields.

**Consequence.** The escalation logged in DECISIONS on 2026-07-15 - which
dispositioned the source's pricing dollar levels DROP, "not replicable in prior
form," on the grounds that the shift magnitude, timing, pricing gain, velocity
target and trailing window were unspecified - is DISPROVEN. Every one of those
parameters was recovered from the source's own code and record:
  4-stage serial, 1.3x capacity, summed_at_retailer, all_sr inventory scenario
  elasticity=1.5, reference_price=1.0, review_interval=20
  260 periods, 52 warmup -> 208 measured
  shift: +/-20% at t=130 ; OLS window W=40
  thresholds: symmetric 0.6 ; asymmetric 0.6 raise / 0.75 cut
  scenarios: no_pricing, naive_reactive, phi_gated_symmetric, phi_gated_asymmetric
  net value = revenue - cost
"Not replicable in prior form" was asserted as an OPENING ASSUMPTION without
running source recovery at all - the exact inversion the Standard's
regenerate-or-escalate rule now forbids. The escalation is withdrawn.

---

## DISC-03 - v16 attributes to the persistence formula a benefit the formula did not produce

**Kind:** consistency / attribution. **State:** OPEN (CONFIRMED, and CORRECTED
2026-07-16 - the finding stands and is now BETTER evidenced; the severity concern
attached to it was MINE and is WITHDRAWN). **Bears on:** E8's primary comparison,
Section 7 / the pricing section, and v16's abstract.

**THE FINDING (confirmed from the source's 1,800 RAW trial records, not the
summary).** v16 frames its pricing section as testing whether the PERSISTENCE
FORMULA gives useful guidance on price, and reports +$10,142/period as its headline.
That figure is the no_pricing vs NAIVE_REACTIVE comparison - it measures the value
of REACTING TO DEMAND SHIFTS AT ALL, not the value of the formula. Recomputed per
seed from the raw records (mean_revenue_per_period - cost_per_period, paired):
    level_shift_up_persistent    no_pricing vs naive  +10141.86  (se 630.19, 16.1 sigma)
and in that SAME environment, the formula's own contribution:
    level_shift_up_persistent    phi_gated_asymmetric vs naive  +13.01  (se 21.52, 0.6 sigma)
                                                                 -> UNRESOLVED
The formula adds an amount INDISTINGUISHABLE FROM ZERO - 0.13% of the headline it is
credited with. Across all five level-shift environments the formula has exactly ONE
resolved win:
    low_phi_shift_down           phi_gated_asymmetric vs naive  +137.20 (se 31.41, 4.4 sigma)
                                                                 -> RESOLVED
(this is the source's own "$144/period asymmetric advantage" finding, confirmed at
4.4 sigma). The other three are unresolved: low_phi_shift_up +19.42 (2.3 sigma,
resolved at 95% but small), level_shift_down_persistent -24.28 (1.3 sigma),
mid_phi_shift_down -24.55 (1.0 sigma). This is the Paper-4 ratio-operator pattern:
reproducible, and INADMISSIBLE for the sentence attached to it. It is independent of
DISC-01 and DISC-02 - it holds even though every number is correct, and CIC-1
confirms every number IS correct (all five published figures reproduce from the raw
records at 13-21 sigma).

**CORRECTION 2026-07-16 - A SEVERITY CLAIM OF MINE, WITHDRAWN.** This dossier
previously asserted that naive_reactive, phi_gated_symmetric and phi_gated_asymmetric
return cost_per_period_mean = 10942.385082660967 BIT-IDENTICAL, and DESIGN's
2026-07-16 E8 amendment built a severity argument on it: that the two arms are "the
same computation," the difference "exactly zero," and "no sample size resolves it" -
the E5 saturation disease. THAT IS WRONG. Checked against the raw records, the arms
are NOT identical in any of the five level-shift environments (sym==naive False,
asym==naive False in all five). The bit-identity occurs ONLY in ar1_high_no_shift -
and ar1_high, which DISC-04 established is THE SAME no-shift control under a second
name. In a no-shift control there is nothing to react to, so every reactive policy
does nothing and all three arms coincide: that is CORRECT BEHAVIOUR, not saturation.
The error's origin: the summary key 'ar1_high|phi_gated_asymmetric' was read as if
'ar1_high' were the headline environment; it is the legacy control. The source's own
record ("PHI-GATING DOES NOT DIFFERENTIATE FROM NAIVE ... the persistence test always
passes so phi-gated reduces to naive_reactive") describes a real and documented
estimator property - OLS structural-break inflation pushing the estimate above both
thresholds - but it manifests as a SMALL UNRESOLVED difference, not as arithmetic
identity.

**CONSEQUENCE: the severity concern is withdrawn and E8 is RUNNABLE.** The arms are
distinct, the comparison has dynamic range, and the test can adjudicate in either
direction. What survives - and is strengthened by being measured rather than argued -
is the ATTRIBUTION finding: in the environment carrying the paper's headline, the
formula's measured contribution is unresolved at 0.6 sigma while the paper credits it
with the whole $10,142.

**METHOD FAILURE RECORDED AGAINST OURSELVES - the FOURTH of this kind.** A defect was
again INFERRED FROM A PATTERN (identical summary values) rather than read from the
records, and again the inference was wrong: (i) the magnitude check against E4 as the
reference system; (ii) the cumulative/relabel hypothesis, raised twice; (iii)
DISC-04's seed/environment suspicion; (iv) this. In every case the ANOMALY WAS REAL
and the DIAGNOSIS WAS INVENTED. Note the specific trap here: the same naming
duplication that produced DISC-04's false alarm produced this one, one dossier later -
the lesson did not transfer because the second instance arrived wearing different
clothes. The general rule: an identical-values pattern is a signal to open the raw
records, never evidence of what caused it.

**Remaining for E8:** the primary comparison for any claim ABOUT THE FORMULA is
phi_gated_* vs naive_reactive, NEVER vs no_pricing. Any result reported against
no_pricing measures reaction, not persistence guidance, and may not be attributed to
the formula. That gate stands unchanged.


---

## DISC-04 - the pricing runner's hard-coded seed; two environments identical

**Kind:** computational. **State:** RESOLVED 2026-07-16 - **NO DEFECT.** Both
limbs of the suspicion were wrong. **Bears on:** E8 (the build strategy it was
blocking is now unblocked on this count).

**As found.** In the source's committed pricing output, ar1_high and
ar1_high_no_shift - apparently DIFFERENT demand environments - return identical
cost_per_period_mean, identical mean_revenue_per_period_mean, and identical standard
deviations to 15 significant figures. Separately,
phase2_7_validation_runner.py calls simulation(net, num_periods=..., rand_seed=42,
progress_bar=False) with the seed HARD-CODED rather than threaded from trial_seed.
The hypothesis was that the runner hands stockpyl a STOCHASTIC demand source, which
rand_seed=42 would then freeze identically across every trial - making the control
environments worthless and casting doubt on the whole pricing battery.

**RESOLVED by reading the code (playbook method 1, ground truth). BOTH LIMBS FAIL.**

(1) THE SEED IS INERT, exactly as in the chain-length sweep. The runner's
assign_realized_streams_to_retailer() sets
    demand_sources[ret_prod.index] = DemandSource(
        type='D',                       # DETERMINISTIC
        demand_list=realized_streams[sku.sku_id].tolist(),
    )
    retailer.demand_source = demand_sources
The demand is pre-generated per trial and handed over as an explicit list, leaving
rand_seed=42 nothing to randomise. Identical mechanism, identical harmlessness, to
DISC-05's CIC-7 finding on the sweep. The hard-coded 42 is untidy, not defective.

(2) THE TWO ENVIRONMENTS ARE THE SAME DEMAND PROCESS UNDER TWO NAMES. From
get_validation_environments():
    'ar1_high_no_shift': schedule = constant_schedule(0.85),
                         level_shift_fraction = 0.0,   # "no shift = control"
    'ar1_high'         : schedule = constant_schedule(0.85)   # no shift key at all
One is the legacy Phase-2.6 persistence-only environment; the other was added
2026-04-29 as the pricing control. Both are stationary AR(1) at phi = 0.85 with no
level shift. Same schedule, same seed, deterministic list -> IDENTICAL DEMAND ->
identical cost. The 15-significant-figure agreement is CORRECT BEHAVIOUR and is in
fact weak positive evidence that the pipeline is deterministic and wired properly.
It is a naming duplication in the environment table, not a computational defect.

**METHOD FAILURE RECORDED AGAINST OURSELVES.** This is the THIRD time in this
verification effort that a defect was INFERRED FROM A PATTERN rather than read from
the code, and the third time the inference was wrong: (i) the magnitude check
against E4 as the reference system (DISC-02) - the pattern was real, E4 was the
wrong yardstick; (ii) the cumulative/relabel hypothesis for the dollar figures
(DISC-02) - raised twice, wrong twice; (iii) this. In every case the ANOMALY WAS
REAL and the DIAGNOSIS was invented. The pattern is the signal to go and read the
code; it is not itself evidence of what is wrong. Method 9 (stated-value triage) is
DISCONFIRMATION-ONLY by design for exactly this reason, and it was repeatedly used
to diagnose, which exceeds its licence.

**Consequence for E8.** DISC-04 no longer blocks the build on the seed question:
CIC-7 (input integrity) CLEARS for the pricing runner. The remaining six CIC classes
are still outstanding and must run before any vendoring decision - provenance is not
correctness, and this dossier's closure establishes only that these two specific
suspicions were unfounded, not that the code is sound.

In the source's committed output file, ar1_high and ar1_high_no_shift - different
demand environments - return identical cost_per_period_mean, identical
mean_revenue_per_period_mean, and identical standard deviations to 15 significant
figures. The runner calls simulation(net, num_periods=..., rand_seed=42,
progress_bar=False) with the seed hard-coded rather than threaded from
trial_seed. DISC-05's CIC established that this same hard-coding is INERT in the
chain-length sweep because that script hands stockpyl a deterministic demand
list; the hypothesis to test is that the pricing runner instead hands over a
stochastic demand source, which rand_seed=42 would then freeze identically across
every trial. Does not touch the five headline cells, which do vary by
environment; may invalidate the control environments.

---

## DISC-06 - E4's naive tier is a no-op, and the OUTLINE records a fabricated mechanism

**Kind:** computational + consistency. **State:** OPEN. **Bears on:** LB-E4-naive,
LB-E4-erp, ARG-14. **NOT WORKED HERE.**

e4_beer_game.simulate() branches only on `if algo in ("spectral", "full")`, so
"naive" and "basestock" execute identical code and return bit-identical costs
(122962.3769772079 both, confirmed in the committed e4_beer_game.json). The
docstring claims naive means "no forecast"; no such branch was ever written.
OUTLINE records: "LB-E4-naive | Beer Game mean cost, naive policy. VALUE
2026-07-13: 122962 (== base-stock at lean 1.3x; CAPACITY BINDS EQUALLY)." That
parenthetical is a FABRICATED PHYSICAL MECHANISM invented to explain a missing
code branch - two identical numbers were rationalized instead of read.
LB-E4-naive and LB-E4-erp are the same number carried as two separate
load-bearing findings.

E4's VERDICT IS UNAFFECTED: its rule is spectral vs base-stock (p=0.0005, CI
excludes zero, full <= spectral); naive plays no role. What is affected is (a)
the record reporting a number that measures nothing distinct, (b) the fabricated
mechanism, and (c) v16's headline "~30% cost reduction relative to a modern
ERP-style forecasting baseline" - E4 implements NO such comparator, so E4 cannot
speak to that claim, and LB-E4-erp is named "erp" while holding a base-stock
value.

---

## DISC-07 - E4 and the source's chain-length sweep use DIFFERENT damping rules

**Kind:** computational. **State:** OPEN. **Bears on:** E4's construction
fidelity, ARG-14, LB-E4-tool, LB-E4-full. **NOT WORKED HERE** - E4 is closed and
E7 is the open unit; logged at discovery per the rule that a discrepancy is never
silently dropped. To be worked when E4's audit is opened, not before.

**As found (2026-07-15),** while reading the source's chain-length sweep code to
specify E7's rebuild. The two constructions compute the tool's damping factor
alpha by different means:

  THE SOURCE'S SWEEP (phase2_6_spectral_radius.py, compute_alpha_pi_squared_over_two,
  damping_mode DAMPING_PAPER9) uses a CLOSED FORM:
      S         = (1 - phi^W) / (1 - phi)        [cumulative_persistence_memory]
      alpha_max = (pi^2 / 2) / S
      alpha_op  = alpha_max * k_star,  k_star = 0.90
      then clipped to [alpha_floor, alpha_ceiling]
  There is no engagement gate: alpha is computed analytically at every period and
  simply clips at the ceiling when it would exceed it.

  E4's REBUILD (analysis/e4_beer_game.py, alpha_spectral) uses BISECTION:
      if phi_hat <= phi_eng: return 1.0          [an explicit engagement GATE]
      else bisect bg in [1e-3, bg_policy] for rho(phi_hat, W_mon, bg) = 1.0
      alpha = clip(bg_target / bg_policy, 0.05, 1.0)
  with phi_eng ~ 0.83 itself derived by bisection on rho(., W_mon, bg_policy) = 1.

These are not the same rule. The source's is an analytic pi^2/2 bound; E4's is a
numerical search for the rho = 1 boundary, gated below an engagement threshold.

**Why this is NOT yet a finding about either.** The two may legitimately come from
different source sections describing different constructions - E4's rebuild traced
phi ~ 0.83 to the source's OWN STATED engagement boundary (recorded 2026-07-13,
"Path A", matching the source's stated value exactly by bisection), which is
evidence its construction was traced to something real. Note also that the source's
own code carries a variant named sr_numerical using pi^2/S with k_star = 1.0 and no
safety margin, described in its docstring as "the pre-correction numerical rule ...
preserved specifically to document that the threshold change matters" - so the
source itself distinguishes an analytic rule from a numerical one, and an April-22
correction moved it from the numerical threshold to the closed-form Paper 7 bound.
Whether E4's bisection corresponds to the pre-correction numerical rule, to a
different source section, or to a mis-read is exactly what this dossier must
establish - and it cannot be established by inspection alone.

**Ladder: NOT RUN.** When opened, it starts at (8) the framing gate - which
construction was E4's operator actually specifying? - then (1) source recovery
against the Phase 2.6 Beer Game source section and any committed Beer Game script
on disk, then (10) version reconciliation across the source documents, before any
reconstruction. It must NOT be adjudicated from this Register's inspection notes:
that would be the exact error made against DISC-01/02 earlier in this session,
where a summary was mistaken for the artifact.

**Provisional impact if E4's rule proves mis-read.** E4's verdict (spectral beats
base-stock, p = 0.0005) is a comparison between two policies E4 itself defines, so
it remains internally valid whatever the rule's provenance; what would be at risk is
E4's claim to have re-earned the SOURCE's Beer Game construction, and with it the
source-fidelity of LB-E4-tool and LB-E4-full. Recorded now so the question cannot
be lost.
