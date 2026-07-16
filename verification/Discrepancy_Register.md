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

**Kind:** computational. **State:** RESOLVED (cause). **Bears on:** ARG-19,
LB-E7-gradient, LB-E7-calibration, TBL-7, Section 6.5, Appendix F.

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

**CIC status (on the source's script, required before adoption).**
  - Point 1, input integrity / seed handling: CLEARED. The script hard-codes
    `rand_seed=42` at line 370, the same defect class as DISC-04. Here it is
    INERT: configure_demand() pre-generates the demand array with seed=trial_seed
    and hands stockpyl an explicit deterministic list (DemandSource type='D',
    demand_list=...), leaving rand_seed nothing to randomise. Confirmed by
    reading the code, not the drawer.
  - Points 2-7: NOT YET RUN.

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

**Kind:** consistency / attribution. **State:** OPEN (CONFIRMED). **NOT WORKED
HERE - belongs to E8, which does not open until E7 is closed.**

v16 frames its pricing section as testing whether the persistence formula could
provide useful guidance, and reports +$10,142/period as its headline. That figure
is the no_pricing vs NAIVE_REACTIVE comparison. In the source's own output file,
naive_reactive, phi_gated_symmetric and phi_gated_asymmetric return
cost_per_period_mean = 10942.385082660967 - BIT-IDENTICAL. The source's own
record states the mechanism: "PHI-GATING DOES NOT DIFFERENTIATE FROM NAIVE ...
The persistence test always passes so phi-gated reduces to naive_reactive."
The $10,142 is the value of reacting to demand shifts at all. The formula's own
measured contribution is $144/period (asymmetric vs symmetric in
low_phi_shift_down), 1.4% of the headline. Independent of DISC-01 and DISC-02:
it holds even though every number is correct. This is the Paper 4 ratio-operator
pattern - reproducible, but inadmissible for the sentence attached to it.

---

## DISC-04 - the pricing runner's hard-coded seed; two environments identical

**Kind:** computational. **State:** OPEN. **Awaits:** the 7-point CIC on
phase2_7_validation_runner.py. **NOT WORKED HERE - belongs to E8.**

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
