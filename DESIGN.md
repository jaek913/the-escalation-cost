# DESIGN - The Escalation Cost

**Title:** The Escalation Cost: Intensity, Duration, and the Growing Damage of Regime Change

**Author:** Jae Kim (jae@laggingtruth.com, ORCID 0009-0005-3260-7880)

**Date:** 2026-07-13. Phase 1 (Design). Research-to-Publication Standard v1.9.5.

**Status:** Pre-registration. Committed before the first analysis commit; the git timestamp is the pre-registration record. Every experiment below has an exact operator and a pre-registered decision rule. Amendments to this document are dated and appended, never overwritten (see Amendment log at the end). Source-manuscript values quoted in context are source material to be re-earned, never inherited.

---

## 0. Shared definitions and conventions (used by all experiments)

- **Managed variable:** the inventory-to-sales (I/S) ratio, monthly, seasonally adjusted, per sector. Chosen because it is stationary and is the quantity firms manage through ordering decisions.
- **Persistence phi:** AR(1) coefficient estimated by OLS regression of y_t on y_{t-1} (no intercept suppression; intercept included). Estimator choice pre-registered: OLS. (The source project tested Yule-Walker as an alternative on 200 synthetic AR(1) histories at true phi = 0.95, W = 40: OLS mean 0.835 vs Yule-Walker 0.803 - YW more downward-biased; OLS retained. This comparison will be re-earned as part of T1's numeric stress suite.)
- **Data floor:** persistence estimation requires monthly frequency and at least 36 observations; 60 preferred. Quarterly 20-observation samples are insufficient (cannot distinguish phi = 0.95 from 0.50) and are excluded by design.
- **Closed loop:** a trailing-average estimator of window W over y_t, feeding a proportional feedback policy of aggressiveness beta*gamma (written bg below), yields a W x W companion matrix A(phi, W, bg). **Spectral radius rho** = largest eigenvalue modulus of A. rho < 1 = perturbations decay; rho > 1 = perturbations compound. This construction and the pi^2/2 single-loop criterion are verified inputs from the companion paper "The Measurement Trap"; they are used, not re-proved.
- **Adaptation time tau:** the number of periods the trailing estimator takes to converge to a new persistence regime; a structural function of W carried from the companion papers on trailing-average adaptation.
- **Damage metric:** D = (rho_2/rho_1)^tau, where rho_1 = spectral radius under pre-transition persistence phi_1 and rho_2 = under post-transition phi_2, both at the system's (W, bg).
- **Named parameter specs (see Section 14, Specification disclosure):**
  - SPEC-M (monitoring): W = 8 months, bg = 0.05 - used for the rolling monitoring series and boundary-crossing narrative.
  - SPEC-R (ranking): W = 12 months, bg scale = 3.0 - used for the cross-sector instability ranking.
  - SPEC-B (Beer Game): W = 8, base bg = 0.50 - simulation ordering tool.
  - SPEC-S (sovereign): W = 5 years, bg = 0.05 calm / swept 0.05 -> 1.5 crisis.
  - SPEC-U (unemployment insurance): W = 3-5 year trailing claims window per state formula reading; quarterly persistence.
- **Statistics:** rank correlations are Spearman. Per-sector significance threshold in E1 is p < 0.01 (with 17 sectors, expected false positives under the global null < 0.2 sectors - stated in the paper). Episode tests (n = 17) are reported with exact p and explicitly labeled corroborating, not load-bearing alone.
- **Seeds and pairing:** all Monte Carlo comparisons use identical demand sequences across algorithms within a run (paired design); seeds recorded; run counts pre-registered per experiment.
- **Experiment-validation gate (v1.9.5):** before any experiment touches hashed real data in Phase 2, (1) its validity review below must be finalized in this document and (2) a committed synthetic suite with planted ground truth must recover a planted effect, a planted null, and a planted decision-flip at the real n, with measured false-positive rate ~nominal. The design below is the frozen object that gate protects; suite failures fix code, never these rules; any rule change is a dated amendment.

---

## 1. T1 - Measurement Damage Theorem: three-way verification

**Purpose:** verify the paper's central theorem, D = (rho_2/rho_1)^tau, as a bound on blind-period damage.

**Operator.** (a) Written proof: full rigorous proof in the paper/appendix (upgrading the source's sketch): damage accumulated while the estimator still reports regime-1 parameters, in a system that has transitioned to regime 2, is bounded by the stated ratio form; component lemmas (Compound Damage Bound; the adaptation-stability identity) proved in full. (b) Symbolic step-check: committed script (sympy) re-deriving each proof step. (c) Numeric stress test: committed script simulating the linearized closed loop across a grid - phi_1 in {0.10, 0.30, 0.50, 0.70, 0.85}, phi_2 in {0.60, 0.75, 0.90, 0.95, 0.99} with phi_2 > phi_1, W in {4, 8, 12, 24, 60}, bg in {0.02, 0.05, 0.20, 0.50}, 100 noise seeds per cell - measuring realized blind-period damage vs the bound. Also re-runs the OLS-vs-Yule-Walker estimator comparison (200 histories, phi = 0.95, W = 40).

**Decision rule (pre-registered).** SUPPORT: symbolic check passes every step; numeric grid shows realized damage <= bound within numerical tolerance (rel 1e-6 for the deterministic component; simulated exceedances explained by the stated noise term in no more than the theorem's allowed sense) in 100% of in-domain cells. REFUTE: any reproducible in-domain counterexample (realized damage exceeding the bound beyond tolerance), or a proof step that does not hold - either reopens Phase 3 and falsifies the theorem as stated.

**Validity review.** Referent: the linearized trailing-average feedback loop is the mechanism the theorem is ABOUT; the synthetic system IS the theorem's domain, so ground truth is exact. Rule-thesis link: the theorem is the thesis's theoretical half; the outcome partition is binary (bound holds everywhere in-domain / counterexample exists), and a counterexample maps to the honest verdict (falsified). Measure at n: deterministic + 100 seeds per cell makes noise negligible relative to the exponential quantities compared.

**Inputs:** none external (synthetic).

## 2. T2 - Optimal window W* (Lambert W closed form)

**Purpose:** verify the closed-form optimal measurement window against brute-force numerical optimization.

**Operator.** Committed script computes expected total cost (damage cost proportional to rho_2^{kappa*W}, kappa = 1 - epsilon/Delta_phi, plus estimation cost proportional to (1 - phi^2)/W) over integer W in [2, 120] across the T1 parameter grid (in-domain cells), locates the numerical argmin, and evaluates the closed-form W* (Lambert W expression) at the same parameters.

**Decision rule.** SUPPORT: closed-form W* matches the numerical argmin within +/-1 grid step in >= 99% of in-domain cells, and the cost curve is unimodal (single interior minimum) in every cell. REFUTE: systematic mismatch (> 1 step in > 1% of cells) or non-unique/boundary minima where the theorem asserts a unique interior optimum.

**Validity review.** Referent: same modeled loop as T1. Partition: match/mismatch is exhaustive. Measure: deterministic cost curves; no sampling noise.

**Inputs:** none external.

## 3. T3 - Optimal safety factor k*

**Purpose:** verify that operating below the pi^2/2 stability limit (k* ~ 0.85-0.95 under manufacturing-like parameters - source value, to be re-earned) minimizes expected cost under regime-change risk.

**Operator.** Committed script: systems parameterized to sit at fraction k of the pi^2/2 limit, k in {0.70, 0.75, ..., 1.00, 1.05}; regime-change scenarios drawn from the T1 grid with a pre-stated probability of transition per horizon; expected total cost (steady-state performance cost of under-aggressive feedback + transition damage cost) computed per k; argmin located.

**Decision rule.** SUPPORT: expected-cost argmin lies strictly below k = 1.0 under every regime-change-risk scenario tested, and within [0.80, 0.98] under the manufacturing-parameter scenario. REFUTE: argmin at k >= 1.0 in the manufacturing scenario (the buffer buys nothing), which strikes the k* claim.

**Validity review.** As T1/T2; the scenario probability is a stated model input, disclosed in the paper, and varied in the grid so the conclusion's sensitivity to it is reported.

**Inputs:** none external.

## 4. E1 - Rolling out-of-sample panel validation (THE PRIMARY FALSIFIER)

**Purpose:** test whether predicted damage D, computed from backward-looking data only, predicts subsequent realized I/S deviation across the 17-sector panel.

**Operator.** Data: 17 monthly, seasonally adjusted US Census M3/MWTS/MRTS I/S series (manifest, Section 13), January 1992 - February 2026 (extended to latest available at pull time; extension is not a spec change). At each month t and sector s: phi estimated by OLS on the trailing 60 months; regime-change detection from the trailing 12 months (phi_recent vs phi_baseline as in the source construction); tau from W per the adaptation-time function; D_t computed under SPEC-M. Outcome: the sector's I/S deviation over months t+1..t+12, measured as the excess absolute deviation from the sector's trailing baseline (exact deviation definition frozen in the analysis script before first real run; the synthetic suite validates it recovers planted regime damage). Correlate D_t with the subsequent deviation per sector (Spearman, all t with full windows).

**Decision rule (pre-registered - this is the thesis falsifier).** SUPPORT: a majority of regime-oscillating sectors (sectors whose rolling rho crosses 1.0 in both directions at least once in-sample; chronically-unstable sectors with rho > 1 in > 40% of months are classified boundary-condition cases, reported separately, per the theorem's stated domain) show positive Spearman with p < 0.01. FALSIFIED: a majority of regime-oscillating sectors fail that test, or the panel-wide sign is predominantly negative (more negative than positive point estimates). No-decision is not an outcome: every result maps to support, falsification, or (for chronic sectors only) documented boundary condition.

**AMENDMENT 2026-07-13 (pre-real-run, gate-motivated, author-ratified after quantified comparison).** The v1.9.5 mechanism-validation suite measured the rule above at the real sample size BEFORE any real-data run and found it broken in the SUPPORT direction: the pre-registered 24-month-block bootstrap null puts the per-sector p < 0.01 bar at Spearman ~0.30, while the operator's 12-month detection noise caps even strong planted true effects near 0.2-0.5 - measured power ~0 (the validity review's own noise-dwarfed-threshold defect, located in the decision rule). A power-curve comparison on panels with realistic cross-sector dependence (common macro factor, 50% shared regime timing) measured the minimal amendment (per-sector alpha 0.05, majority rule) at 0-10% SUPPORT across effect strengths vs 0-20% for a pooled redesign at stricter alpha - the pooled test dominating at every strength while modeling the cross-sector correlation the majority rule's arithmetic ignores. REPLACED RULE (ratified): THE FALSIFIER IS PANEL-LEVEL. Statistic: mean Spearman across regime-oscillating sectors (classification unchanged; chronic and never-crossing sectors reported as before). Null: joint circular block bootstrap - one set of 24-month block indices applied to every oscillating sector's outcome series simultaneously (preserving cross-sector dependence), D fixed, B = 2000. SUPPORT: at least 2 oscillating sectors AND pooled mean Spearman > 0 AND one-sided p < 0.01. FALSIFIED otherwise (including pooled sign non-positive or fewer than 2 oscillating sectors - the honest verdict when the domain is empty). The per-sector table (Spearman + block-bootstrap p, alpha 0.05 reference line) is retained as DESCRIPTIVE reporting only and no longer carries the verdict. Script-level frozen specifics (kappa = 0.75; outcome anchored to the trailing-12 baseline so its dependence matches the frozen block length - measured per-sector FP 3.7% at alpha 0.05, 0.7% at 0.01) are recorded in the committed analysis script. Verdict-level false-support measured 0% at null for the replaced rule. A PASS under this rule is strong evidence (noise floor verified ~never crossed by chance); a FAIL is reported as "indistinguishable from noise at this data resolution," not as disproof - the corroborating battery (E2 onward) carries weaker-signal evidence.

**Validity review.** Referent: sector I/S ratios are the real managed variable of real ordering systems; regime shifts in demand persistence are the real mechanism (documented GFC destocking literature). Rule-thesis link: this is the operational half of the thesis verbatim; the partition covers all outcomes and a true null falsifies. Measure at n: per sector, ~350+ rolling monthly observations; overlapping 12-month outcome windows induce serial correlation - addressed by pre-registering that per-sector p-values are computed with an effective-sample-size correction (block bootstrap, 24-month blocks, 2,000 resamples) rather than naive n, so the p < 0.01 threshold is not noise-dwarfed. [This correction is a strengthening added at design time; the source's headline will be re-earned under it and any divergence reported.]

**Inputs:** 17 I/S series (manifest).

## 5. E2 - GFC episode test (corroborating)

**Purpose:** test the predicted-damage ranking against realized damage in the one large, universally dated regime transition.

**Operator.** For each of 17 sectors: phi_1 from 2003-2006 (pre-crisis), phi_2 from 2008-2009 (crisis), tau from the measurement window (SPEC-M), D = (rho_2/rho_1)^tau. Realized outcome: excess I/S deviation during the 2007-2010 peak window (same deviation definition as E1). Spearman(D, realized), n = 17. Component bake-off, same episode: rho_crisis alone; |Delta phi| alone; tau alone - all four correlations reported.

**Decision rule.** SUPPORT (corroborating): positive Spearman for D with p < 0.10 (n = 17 stated; explicitly labeled marginal and corroborating), AND the combined D ranks at least comparably to each component (point estimate >= components, differences not over-read). WEAKENS: non-positive or clearly inferior-to-components correlation - reported honestly; E2 alone cannot falsify the thesis (E1 owns falsification) but a negative E2 is reported as evidence against, prominently.

**Validity review.** Referent: the GFC destocking episode is independently documented (Udenio-Fransoo-Peels 2015; Dooley et al. 2010). Partition: positive/negative/null all mapped. Measure at n: n = 17 gives wide CIs; that is exactly why the rule caps E2 at corroborating and pins the language.

**Inputs:** same 17 series.

## 6. E3 - COVID episode test (pre-registered expected null / boundary condition)

**Purpose:** probe the theorem's stated domain boundary: it models persistence INCREASES (Minsky tightening), not compound shocks where persistence drops.

**Operator.** Identical to E2 with phi_1 from 2017-2019, phi_2 from 2020-2021, realized deviation over 2020-2022. Additionally compute the direction of the persistence change per sector.

**Decision rule (pre-registered expectation: NULL).** CONSISTENT-WITH-BOUNDARY: non-significant correlation (|rho_s| with p > 0.10) AND persistence dropped in a majority of sectors. ANOMALY-REQUIRING-EXPLANATION: strongly positive significant correlation (would contradict our stated mechanism even while flattering the metric - reported as a problem for the theory's story, not a win); or persistence ROSE in a majority of sectors with a null result (which would convert COVID from boundary case to genuine counter-evidence against E1's mechanism, reported as such).

**Validity review.** Referent: COVID is the canonical compound shock. This experiment's honest function is domain mapping; the partition explicitly prevents reading any outcome as automatic support.

**Inputs:** same 17 series.

## 7. E4 - Beer Game Monte Carlo (does acting on the diagnostic save cost?)

**Purpose:** upgrade correlation to causation-in-simulation: same demand, different ordering brains.

**Operator (frozen; identical to source calibration).** Four-echelon chain (retailer, wholesaler, distributor, factory); lead time 2 periods; holding cost $1/unit/period; backorder cost $4/unit/period; demand AR(1), baseline 100 units, sigma = 10, persistence ramp phi 0.30 -> 0.95 over periods 30-70 (Minsky tightening); 1,000 Monte Carlo runs, unique seed per run, identical demand sequences across algorithms within a run. Algorithms: (1) naive full-reaction; (2) ERP baseline: exponential-smoothing forecast alpha = 0.3, safety factor 1.5, gap closure 0.50; (3) spectral-radius tool: ERP + rho-monitor (SPEC-B: W = 8, base bg = 0.50) damping orders when rolling rho > 1; (4) full theorem: (3) + pi^2/2 limit + safety factor k* + optimal-window input. Outputs: total cost per run per algorithm; paired differences.

**Decision rule.** SUPPORT: algorithm (3) mean total cost < algorithm (2) with paired-test p < 0.01 and a relative reduction whose 95% CI excludes zero; algorithm (4) <= (3) with pairwise win rate reported. REFUTE (practical half of the claim): (3) not significantly cheaper than (2) - the diagnostic would be descriptive but not actionable; reported as a failed practical claim even if E1 supports the theorem.

**Validity review.** Referent: the Beer Game is the canonical bullwhip environment; the ERP baseline is the realistic comparator (beating naive proves nothing - stated). Partition: better/equal/worse all mapped. Measure at n: 1,000 paired runs; paired design removes demand-draw variance.

**AMENDMENT 2026-07-16 (POST-AUDIT RECHARACTERIZATION; author-ratified Option A
- record-level fixes, no re-run; Standard v1.9.9. Full dossiers:
verification/Discrepancy_Register.md DISC-06 and DISC-07, both RESOLVED at the
E4 audit; every claim below traces to an artifact read directly, never a
summary.)**

THE "IDENTICAL TO SOURCE CALIBRATION" LABEL ABOVE IS WITHDRAWN. The 2026-07-13
build diverged from this operator and from the source's Appendix E in four
established ways: (1) BG_POLICY = 0.9561 was used in place of the stated "base
beta*gamma = 0.50" - reverse-engineered to pin an "engagement boundary ~0.83"
read from the corrupted supporting draft, a boundary that in fact belongs to a
DIFFERENT source construction (it is the chain-length sweep's closed-form
implicit gate, where 0.90 x (pi^2/2)/S(phi, 8) crosses 1.0 at phi = 0.8216);
(2) the ERP baseline - THIS OPERATOR'S ALGORITHM (2) AND THE VERDICT
COMPARATOR, exponential smoothing with 0.50 gap closure, confirmed by Appendix
E and by the source's archived beergame_validation.py (make_erp_team: alpha
pinned at 0.50) - was never built; the verdict was rendered against full-gap
self-calibrating base-stock instead; (3) algorithm (1) Naive (100% gap closure,
no forecasting - defined in v16 Section 5.4) was never built, and its recorded
value is a bit-identical duplicate of base-stock (DISC-06); (4) the full tier
omits Section 5.4's "preemptive dampening based on persistence drift
detection." The 2026-07-13 DECISIONS "clarification" that reinterpreted the
operator's 0.50 as a monitor parameter is DISPROVEN by ground truth and was
never a dated amendment to this document - the same failure class as E7's
amendment 14c (a partial source check declared complete).

WHAT STANDS, RE-SCOPED. E4's run is a real, internally valid paired comparison
between policies E4 itself defines: phi-gated rho-boundary damping (using this
repo's as-proven rho - the bisection is theorem-conformant, locating the exact
rho = 1 boundary) versus full-gap self-calibrating base-stock, at lean 1.3x
capacity. The instrument had dynamic range (phi_hat crosses the 0.83 gate on
the ramp; engagement observed) and the verdict rule was severe. VERDICT
RETAINED, RE-SCOPED: SUPPORT for "acting on the diagnostic reduces cost against
a rational self-calibrating base-stock baseline WITHIN E4'S OWN CONSTRUCTION"
(p = 0.0005, CI excludes zero, full <= spectral). E4 claims NO source fidelity
and does NOT re-earn v16 Section 5.4.

WHY NO REBUILD (both alternatives examined and rejected on evidence). A
faithful Section 5.4 rebuild is PROVABLY NON-SEVERE before any run: at the
stated parameters (bg = 0.50, W = 8) the rho = 1 boundary sits at phi = 0.9990
(numerical, T1-verified rho) and analytically bg x S > pi^2/2 requires
S > 9.87, impossible at W = 8 where S <= 8 - the tool as stated NEVER ENGAGES
on the stated demand (phi <= 0.95), so the instrument has zero dynamic range
(the E5 saturation disease, caught pre-build this time). A new-construction E4
would be a new experiment requiring its own v1.9.7 gate and is redundant with
E7's 45,000-trial coverage of the source's corrected construction.

CONSEQUENCE FOR THE SOURCE, carried to Phase 5a: v16's headline "~30% cost
reduction relative to a modern ERP-style forecasting baseline" rests on a
pre-correction implementation (the quartet predates the source's own April-22
threshold correction, proven by the 04-20 Strategic Plan copy) whose generating
script no longer exists anywhere on disk and whose stated construction is
incoherent with the paper's own proven theorem. The claim is UNVERIFIABLE by
anyone and the manuscript must not carry it as re-earned; the honest
replacement is E7's re-earned sweep plus E4's re-scoped model-bound result.

**Inputs:** none external (synthetic; seeds committed).

## 8. E5 - 17-sector structural-instability ranking (the CHIPS observation)

**Purpose:** rank sectors by the fraction of months with rolling rho > 1; test the reproducibility and robustness of the observation that the CHIPS Act's two dependent sectors rank at the top.

**Operator.** Rolling 60-month persistence per sector; rho computed under SPEC-R (W = 12, bg scale 3.0); per sector: peak rho, mean rho, % months rho > 1, full-sample. Ranking by % months. Robustness: recompute under SPEC-M; report both.

**Decision rule.** This is a descriptive diagnostic, not a hypothesis test; its pre-registered claims: (a) REPRODUCED if the ranking regenerates from re-pulled hashed data; (b) the CHIPS observation ("the two sectors the Act depends on are the two most structurally unstable") is ASSERTED only if computers/electronics manufacturing (NAICS 334) and wholesale machinery rank #1-#2 under SPEC-R AND remain in the top quartile under SPEC-M; DOWNGRADED to "among the most unstable" if top-quartile but not #1-#2; DROPPED if either falls below the top quartile in either spec.

**Validity review.** Referent: % months above the stability boundary is a direct reading of the framework on real data. The graded assertion rule prevents over-claiming from a rank that spec choice could flip.

**AMENDMENT 2026-07-13 (post-first-run, test-validity-motivated, author-ratified; pre-registered BLIND to the CHIPS outcome).** The first E5 run exposed a TEST-DESIGN DEFECT, not a result: under SPEC-R (bg scale 3.0) the ranking key % months rho > 1 SATURATES - the top six sectors (AMTMIS, AMDMIS, AMNMIS, A34SIS, A31SIS, R4233) all read 100.0%, a six-way tie at the ceiling. A saturated key carries ZERO ordering information among the tied sectors, so the emitted ranks (#1-#6) were tiebreak/sort artifacts, not measurements. The original DROPPED verdict was therefore computed from non-informative inputs and is INVALID in BOTH directions: the test could not show the CHIPS sectors WERE #1-#2, nor that they WERE NOT - it was incapable of adjudicating the ranking claim at all. Corrected first-run status: INCONCLUSIVE (test-invalid for ranking), NOT DROPPED. This is a validity finding (a broken ruler), not a data result, so replacing the ranking instrument does NOT constitute testing-after-seeing-results / HARKing: there was no informative ranking outcome to steer away from, and the replacement statistic is chosen SOLELY for having dynamic range (non-saturation), defined by the instrument's properties and NOT by where the CHIPS sectors land. The robustness spec SPEC-M (W=8, bg 0.05) did NOT saturate, but leaning the verdict on it now would be spec-shopping (it is the robustness spec, not primary); the clean fix is to redesign the PRIMARY ranking statistic and re-run BOTH specs under it.

REDESIGN (author-ratified, this amendment): the PRIMARY ranking statistic changes from '% months rho > 1' to MEAN EXCEEDANCE MAGNITUDE = mean over the sample of max(rho - 1, 0), i.e. the average distance the rolling spectral radius sits ABOVE the stability boundary (zero when below). This is continuous and non-saturating (it keeps increasing as rho climbs past 1, unlike the binary share which pegs at 100%), so it can order the leaders. Reported alternates (descriptive, not the ranking key): peak rho, mean rho, and the original % months rho > 1 (retained for continuity and to document the saturation). Ranking is by mean exceedance under SPEC-R (primary) with SPEC-M recomputed for robustness. The GRADED ASSERTION RULE is otherwise UNCHANGED and carried over verbatim onto the new key: ASSERTED iff computers/electronics (NAICS 334 -> A34SIS) AND wholesale machinery (R4238) rank #1-#2 under SPEC-R AND both remain top-quartile under SPEC-M; DOWNGRADED to 'among the most unstable' if both top-quartile but not #1-#2; DROPPED if either falls below the top quartile in either spec. A DISCLOSURE note recording the saturation, the corrected INCONCLUSIVE status of the first run, and this redesign is added to the manuscript methods/limitations - proper disclosure of what happened, in either eventual direction.

**AMENDMENT 2026-07-24 (PRE-BUILD; TBL-4 MONITORING CHARACTERIZATION; author-ratified full 17-sector scope; Standard v1.9.9. Made before any monitoring code exists.)**

PURPOSE. OUTLINE ARG-18 / Section 6.4 / TBL-4: the rolling-rho MONITORING characterization - per-sector boundary-crossing dates relative to the GFC and COVID onsets. This is a BACKWARD-LOOKING NARRATIVE and is registered as WEAKER THAN the Section 5.3 falsifier: it demonstrates what a monitoring dashboard WOULD have displayed, it does not test lead-time predictivity (E1 carries the out-of-sample claim). The manuscript states this scoping.

CLASSIFICATION (v1.9.7, pre-build): CHARACTERIZATION. Descriptive; NO verdict layer; no decision rule beyond the mechanical definitions below. The pre-registered outputs are dates and counts, reported as computed.

OPERATOR (frozen, this amendment; committed script analysis/e5_monitor_tbl4.py). The rolling construction is E5's VERBATIM: trailing 60-month OLS AR(1) persistence per sector (e1's ols_phi over y[t-60:t]), rho under SPEC-R (W=12, bg 3.0) and SPEC-M (W=8, bg 0.05), all 17 members, same load filtering; the rho at position t is dated to month t (strictly trailing, no look-ahead). INTEGRITY TIE: the script recomputes each sector's full-sample mean exceedance / peak rho / mean rho / % months > 1 under both specs and ASSERTS equality with E5's committed output rows; the committed e5 artifact's MD5 is embedded in the monitoring output as a hashed input. NEW CONTENT (the measurement E5's output does not carry): dated crossing analysis per sector x spec x episode. Episodes: GFC onset 2008-09; COVID onset 2020-03 (the paper's episode anchors). Episode window: onset +/- 24 months (the same 24-month evaluation convention as the registered forward prediction; fixed pre-run). Definitions (mechanical): UPWARD CROSSING at month m iff rho_m > 1 and rho_(m-1) <= 1 (prior month taken from the full series, so a window that opens above-boundary is not miscounted as a crossing); SUSTAINED CROSSING = first upward crossing followed by 3 consecutive months above (one quarter; fixed pre-run); per sector x episode STATUS in {above-throughout, never-above, crossing, mixed-no-upward-crossing} over the window - the fourth status is the residual class (a window that opens above the boundary and falls below without any upward transition, so it is neither all-above nor a crossing; the summary counts report the first three and the residual is recoverable as 17 minus their sum) - plus above-at-window-start and lead months vs onset (positive = crossing precedes onset). EXPECTED SATURATION DISCLOSED IN ADVANCE: under SPEC-R most sectors sit above the boundary for the whole sample (E5's committed % months = 100% for many), so SPEC-R episode statuses will be dominated by above-throughout - reported as the honest saturation record; the informative crossing story is expected at SPEC-M (E1's spec, where full-sample crossing fractions are 0-3%). Reporting both is the point: the crossing narrative is spec-conditional, consistent with E5's spec-sensitivity finding and the registered bet (B) honesty note.

REPORT FORM. TBL-4 = full 17-sector table, both specs: peak rho, mean rho, share of months above 1, per-episode status + first/sustained crossing dates. LEDGER ROWS (LB-E5-monitor family; planned pre-run): SPEC-M per-episode crossing count and preceding-onset count (4 int rows), SPEC-M manufacturing-aggregate (AMTMIS) status + first-crossing date per episode (4 str rows), SPEC-R per-episode above-throughout count (2 int rows) - 10 rows; any further per-sector date quoted in prose is added at drafting from the committed output. The TIE_EXEMPT entry for LB-E5-monitor is removed when the rows land.

SUITE (committed, in-script: python analysis/e5_monitor_tbl4.py --suite; synthetic, store-free). Legs: planted rho arrays hitting each status class; a single planted upward crossing detected at its EXACT month; sustained vs unsustained discrimination (2-month spike must NOT read sustained); window-opens-above must NOT read as a crossing; end-to-end synthetic series with a regime change - crossing detected after the jump and never before (the post-jump regime is a near-deterministic ramp because SPEC-M's boundary corner near phi = 0.998 is unreachable for stationary small-sample OLS, whose downward bias is about (1+3*phi)/60); dated-loader leg (missing-value "." filtering keeps dates aligned with e1's load_series values). Suite GREEN is Stage 1 of the two-stage handoff; the real run (store-dependent) is Stage 2.

**Inputs:** 17 I/S series.

## 9. E6 - Capacity-utilization stability threshold (semiconductors)

**Purpose:** test the empirical link between capacity utilization and rho, and locate the crossing relative to the Factory Physics 85-90% knee.

**Operator.** Fed G.17 semiconductor capacity utilization (CAPUTLG3344S) and industrial production (IPG3344S), monthly; sector rho series for NAICS 334 from E5's pipeline (SPEC-R primary, SPEC-M robustness). Bin months by utilization: < 75%, 75-85%, 85-90%, >= 90%; mean rho per bin; monotonicity and crossing bin identified. Current-utilization reading reported.

**Decision rule.** SUPPORT: mean rho increases monotonically across bins AND the rho = 1.0 crossing lies in the 85-90% or >= 90% bin (consistent with the Factory Physics knee). REFUTE (claim dropped): no monotone relationship, or crossing below 80% / no crossing - the "monitoring benchmark" section is cut or reframed accordingly.

**Validity review.** Referent: utilization-congestion nonlinearity is established (Hopp-Spearman VUT); the experiment tests whether OUR statistic sees it. Binned means at 400+ months give adequate n per bin (reported per bin).

**Inputs:** CAPUTLG3344S, IPG3344S + NAICS 334 I/S series.

**AMENDMENT 2026-07-14 (post-run, classification/report-form-motivated, author-ratified; Standard v1.9.7).** The real run exposed a SEVERITY DEFECT in the decision rule above, not in the measurement. Result as run: mean rho by utilization bin = 1.050 (< 75, n = 136) / 1.065 (75-85, n = 155) / 1.064 (85-90, n = 46) / 1.078 (>= 90, n = 16); monotone = False; crossing bin = < 75; current utilization 75.4% (2026-05). The rule returned REFUTE. But mean rho exceeds 1.0 in EVERY bin: NAICS 334 never occupies the stable regime at any utilization level, so a "rho = 1.0 crossing" has no sub-boundary baseline to cross FROM and was structurally guaranteed to land in the lowest bin regardless of where the Factory Physics knee sits. The test could not have returned SUPPORT for this sector no matter the truth of the knee hypothesis - it is NOT SEVERE in the sense of Standard v1.9.7, and a verdict from it is not an honest answer in either direction. The monotonicity leg fails on a 0.001 inversion (1.065 -> 1.064) that the per-bin noise dwarfs at n = 155 vs n = 46 - a tie, not a reversal.

CLASSIFICATION (v1.9.7, retroactive): E6 is a BLEND of boundary-condition/domain-mapping and model-fit/calibration (a point-prediction: does the predicted 85-90% knee appear in our statistic), NOT a hypothesis test. Severity: FAILED for the crossing claim on this sector (no dynamic range below the boundary); PASSED for the estimation leg (the bin means are informative measurements with adequate n).

REPORT FORM (ratified, replaces the SUPPORT/REFUTE rule above for this experiment): CHARACTERIZATION + ESTIMATE. E6 reports (1) the estimate - mean rho per utilization bin with its n, and the band width (1.050 to 1.078, width 0.028, entirely above 1); (2) the characterization - NAICS 334 runs persistently above the instability boundary across ALL utilization regimes, i.e. it is chronically unstable rather than utilization-triggered, so no capacity knee is detectable in this statistic for this sector; and (3) the scope statement - this test cannot adjudicate the Factory Physics knee hypothesis for a chronically-unstable sector, because such a sector never occupies the stable regime the knee is defined against. NO pass/fail label is attached.

DISCLOSURE (mandatory, per v1.9.7 and the Standard's re-design rule): the pre-registered rule's output (REFUTE: monotone = False, crossing bin < 75) IS REPORTED alongside the characterization, never suppressed - the change is to the report form, not to any number, and every value above is exactly as run. The severity defect was discoverable BEFORE the run (a probe of whether 334 ever sits below the boundary would have caught it; v1.9.7's dynamic-range probe now requires exactly that) and was found AFTER it: this is a process failure, disclosed as such in the paper's methods note, not remediated by re-running. NO re-run is performed - the instrument is sound for estimation and the data carry information; only the verdict layer bolted on top was invalid.

## 10. E7 - Chain-length sweep (robustness)

**Purpose:** map how the formula's value scales with chain length and capacity headroom, including the all-tier deployment harm-to-benefit crossover.

**Operator (frozen; source calibration).** Chain lengths {4, 6, 8}; capacity multipliers {1.3x, 1.8x, 2.4x}; four demand environments (high-persistence sustained, low-persistence noisy, plus the two source-defined variants - exact parameterizations frozen in the committed script config before first run); 50 seeds per cell; 9,000 simulations total; all-tier deployment vs base-stock baseline.

**Decision rule.** SUPPORT (robustness): the E4-configuration benefit is preserved in its own cell; the crossover pattern (small harm at 4-stage/2.4x high-persistence -> benefit by 8-stage) is REPORTED as found, whichever direction it lands. WEAKENS E4: benefit vanishes across all realistic cells adjacent to the E4 configuration.

**Validity review.** Referent: chain length and capacity are the two most arbitrary Beer Game conventions; sweeping them is the direct answer to "is this an artifact of 4 tiers?". Partition: all outcomes reportable; nothing here can be silently dropped (COVERAGE maps it).

**AMENDMENT 2026-07-14 (PRE-BUILD classification; author-ratified; Standard v1.9.7). The first experiment classified BEFORE build under the new gate - this paper is the pilot. Nothing has been built or run; this amendment precedes the script.**

CLASSIFICATION. E7 is a BLEND of three types, and per v1.9.7 it takes EVERY report form its components require, not merely the dominant one's:
(a) ROBUSTNESS / SENSITIVITY (dominant) - does E4's benefit survive changes to chain length and capacity headroom? A robustness experiment has NO standalone verdict: it QUALIFIES a primary result (E4). Scoring one as if it were a primary hypothesis test is a category error that manufactures false REFUTEs.
(b) REPLICATION - does E4's measured benefit regenerate in its own cell (4-stage, 1.3x, high-persistence sustained) inside this independent sweep?
(c) BOUNDARY-CONDITION / DOMAIN-MAPPING - where does all-tier deployment cross from harm to benefit? The deliverable is a MAP with its region of validity, not a verdict.

SEVERITY CHECK - TWO DEFECT RISKS FLAGGED PRE-BUILD, both of the E5/E6 class (no dynamic range where the answer lives). The synthetic suite MUST measure both before any real run; a failure on either is a design defect amended (dated) BEFORE the run, never a result.
RISK 1 - POWER AT THE PER-CELL n. E4 measured its benefit at +0.2% relative cost reduction (spectral vs base-stock, p = 0.0005) using its own far larger seed count. E7's operator specifies 50 seeds per cell. If the minimum detectable difference at 50 seeds EXCEEDS the ~0.2% effect being mapped, then every cell reads "no significant difference" as an ARTIFACT OF n, and the sweep would appear to show E4's benefit vanishing across the grid - a FALSE weakening manufactured by low power, not a finding. This is precisely the defect E1's Rule B amendment caught (a threshold the measured noise dwarfs). The suite must MEASURE the minimum detectable difference at 50 seeds and compare it to E4's effect size; if MDD > effect, the seed count is amended before the real run.
RISK 2 - GRID DYNAMIC RANGE FOR THE CROSSOVER. A harm-to-benefit crossover can only be LOCATED if the grid SPANS the transition. If every cell lands on the benefit side (or every cell on the harm side), there is no crossover in range and the map is degenerate - the same disease as E6, where a chronically-unstable sector made the crossing structurally unobservable. The suite must plant a known crossover and confirm the grid resolves it.

REPORT FORM (replaces the SUPPORT / WEAKENS rule above):
(a) Robustness: a STABILITY STATEMENT - "the benefit is robust to X, sensitive to Y" - carried by the per-cell effect sizes WITH their uncertainty. NO pass/fail.
(b) Replication: REGENERATED / NOT-REGENERATED plus HOW CLOSELY (the E4-cell effect size against E4's own, with uncertainty) - and this leg carries a verdict ONLY if Risk 1 clears.
(c) Crossover: a MAP - the harm region, the benefit region, the transition, AND an explicit resolution statement (if cells adjacent to the transition are statistically indistinguishable from one another, the boundary is reported as UNRESOLVED, exactly as E5's top cluster was).
E7 carries NO standalone SUPPORT/REFUTE verdict of its own. Its output QUALIFIES E4.

REPORTING COMMITMENT (pre-registered; binds WHAT is reported, not that a verdict is reached): every cell's mean cost difference against the base-stock baseline with its uncertainty; the E4-cell replication comparison; the stability statement across chain length and capacity; and the crossover map with its resolution. ALL cells reported regardless of direction; no cell dropped (COVERAGE maps it).

**AMENDMENT 2026-07-14b (pre-build, severity-motivated, author-ratified; Standard v1.9.7). SEED COUNT 50 -> 1000 PER CELL. Made BEFORE any E7 code exists, blind to every cell's outcome.**

Risk 1 from the classification amendment above is now QUANTIFIED from E4's own committed output. E4 measured its benefit at rel_reduction_mean = 0.001868 (0.1868%) with n_runs = 1000 and a bootstrap percentile CI of [0.001583, 0.002169] - near-symmetric, so a normal back-out is sound: implied SE = 0.000149, z = 12.5. At the frozen 50 seeds the SE inflates by sqrt(1000/50) = 4.47 to 0.000666 (z = 2.79; minimum detectable difference at 80% power = 0.167%).

CONSEQUENCE: the E4-cell REPLICATION leg would (barely) clear at 50 seeds - E4's 0.1868% effect exceeds the 0.1665% floor, about 87% power - but the CROSSOVER MAP would NOT. The 95% CI half-width at 50 seeds is +/- 0.131%, so ANY cell whose true benefit is below 70% of E4's reads as "no effect"; a cell carrying HALF of E4's benefit would be reported as a null. The sweep would then appear to show the benefit vanishing away from the E4 configuration when in fact the instrument had merely stopped resolving it - a FALSE weakening manufactured by low power, in an experiment that by classification (robustness) must not render verdicts at all. Same defect class as E1's original rule (a threshold the measured noise dwarfs) and E5's saturated ranking key (no dynamic range where the answer lives).

RESOLUTION (ratified): 50 -> 1000 SEEDS PER CELL, matching E4's own n. At 1000 seeds the CI half-width is +/- 0.029%, resolving cells down to 16% of E4's benefit - enough for the stability statement to distinguish "the benefit shrinks" from "the benefit is gone," which is this experiment's entire purpose. Cost: about 20x the originally specified compute (36 cells x 1000 seeds; chain lengths 4/6/8). The direction of this amendment is SELF-PENALIZING - it makes every cell HARDER to call a null and removes the low-power excuse for a convenient weakening - and it is made before any E7 code exists. The "9,000 simulations total" figure in the operator above is superseded accordingly (36 cells x 1000 seeds x the algorithms compared per cell).

CARRIED FORWARD TO THE SUITE (both mandatory): (1) the analytic power estimate above INHERITS E4's cell variance and must NOT be trusted across cells - the suite MEASURES per-cell difference variance empirically at the real n and reports the achieved MDD per cell; a cell whose achieved MDD exceeds the effect it is asked to resolve is reported as UNRESOLVED, never as a null. (2) Risk 2 (grid dynamic range for the crossover) remains open: the suite must plant a known harm-to-benefit crossover and confirm the grid locates it; if every cell lands on one side of zero, the map is degenerate and the crossover claim is INCONCLUSIVE, not a finding.

**AMENDMENT 2026-07-14c (pre-build, SOURCE-FIDELITY; author-ratified; Standard v1.9.7). Environments FROZEN FROM SOURCE; replication leg DROPPED; calibration leg ADDED; scope fixed at two scenarios. Made before any E7 code exists.**

Source check performed BEFORE writing the script (the E4 lesson: calibration must trace to the source, never to the adjacent script). Pinned source Paper9_The_General_Measurement_Trap_v16.md (MD5 93135760b92cc195da36eb3c2b785ded), "Chain-length sweep"; supporting Paper9_Supply_Chain_Experiments_DRAFT.md (MD5 7fa713e4debe3c61da214cafe45eaec3). Four findings:

(1) DEMAND ENVIRONMENTS - FROZEN FROM SOURCE, NOT CHOSEN. The operator above defers the four environments' "exact parameterizations" to the committed script config. The pinned source names them: iid_control (phi = 0), ar1_moderate (phi = 0.6), ar1_high (phi = 0.85), drift_canonical (phi trajectory 0.30 -> 0.95 -> 0.40 over the horizon). Now frozen from the source. NOTE THE NEAR-MISS: absent this check the natural fill would have been E4's own PHI_LO = 0.30 / PHI_HI = 0.95 (the values sitting in the adjacent script), which matches NONE of the four - and the source's headline is measured at phi = 0.85, so substituting 0.95 would have silently voided the calibration comparison in (2).
UNDER-DETERMINED RESIDUE (disclosed, not concealed): the source fixes drift_canonical's three waypoints (0.30, 0.95, 0.40) and that phi "walks" between them "over the simulation horizon," but NOT the interpolation shape or the leg lengths. Frozen choice, mirroring E4's canonical ramp timing: hold 0.30 through period 30, linear to 0.95 by period 70, linear to 0.40 by period 110, hold. The waypoints trace to source; the SHAPE is a declared author choice and is reported as such in the methods note.

(2) THE SOURCE MAKES A POINT-PREDICTION -> a CALIBRATION leg is ADDED. Source: "at high persistence with 2.4x capacity, the all-tier deployment produces +0.44% cost difference at 4 stages, +0.14% at 6 stages, -0.14% at 8 stages." E7 therefore also carries a MODEL-FIT / CALIBRATION (point-prediction) component: our measured ar1_high x 2.4x values at L = 4/6/8 are reported AGAINST those three numbers as estimate-vs-source with uncertainty - the same structure as E4's magnitude caveat (+0.2% measured vs the source's 8.7pp). Direction and sign may reproduce while magnitude does not; BOTH are reported.

(3) THE REPLICATION LEG (b) IS DROPPED - it is not well-defined. The classification amendment above proposed re-confirming E4's benefit "in its own cell (4-stage, 1.3x, high-persistence sustained)." NO SUCH CELL EXISTS in this grid: E4's environment is a MONOTONE ramp 0.30 -> 0.95 over periods 30-70, which is none of the four source environments (drift_canonical rises and then falls back to 0.40). Independently, the pinned source itself states the two are not comparable: "The Beer Game simulation used a different deployment pattern (formula at all tiers but with a simpler reference policy) and a different demand calibration." REPLACEMENT: an ENGINE-FIDELITY check in the SUITE - the parameterized engine must reproduce E4's committed per-run costs EXACTLY at E4's config and seeds. That is a CODE-IDENTITY test proving no drift was introduced while making the engine configurable; it is NOT evidence, NOT a finding, and is reported as a suite leg only.

(4) SCOPE - TWO SCENARIOS. The source's 9,000 simulations decompose exactly as 36 cells x 50 seeds x 5 scenarios (base-stock, sr_paper9_ols, sr_oracle_local, sr_naive_damp, all_sterman). E7's operator scope is "all-tier deployment vs base-stock baseline" = TWO scenarios. The oracle (sr_oracle_local) and fixed-alpha (sr_naive_damp) variants carry E12's claim (recipe-level non-stationarity: the oracle harms in every cell despite zero estimation error, while fixed-alpha damping produces large benefit at long chains), and are DEFERRED to E12, which reuses this harness. E7 runs base-stock baseline + all-tier spectral only.

CROSS-SOURCE TENSION (documented; E7 can adjudicate it): the supporting draft reports manufacturer-position harm GROWING with chain length (8.9pp at 4-stage -> ~12pp at 8-stage) at 1.3x capacity for all_sr vs sr_top3; the pinned source reports all-tier harm FLIPPING to benefit with chain length at 2.4x capacity for all-tier vs base-stock. Different comparisons at different capacities, so not strictly contradictory - but E7's grid spans BOTH 1.3x and 2.4x under the all-tier-vs-base-stock comparison, so it can report whether the SIGN of the chain-length effect depends on capacity headroom. Reported as found.

CORRECTED CLASSIFICATION (supersedes the type list in the 2026-07-14 classification amendment): E7 = BLEND of (a) ROBUSTNESS / SENSITIVITY (dominant; stability statement; no standalone verdict), (c) BOUNDARY-CONDITION / DOMAIN-MAPPING (the crossover map with its resolution), and (d) MODEL-FIT / CALIBRATION (estimate-vs-source on the three point-predictions). Leg (b) REPLICATION is WITHDRAWN. Report forms for (a) and (c) are unchanged; (d) reports estimate-vs-source with uncertainty. E7 still carries NO standalone SUPPORT/REFUTE verdict; its output QUALIFIES E4.

**AMENDMENT 2026-07-14d (post-run REMEDIATION; author-ratified; Standard v1.9.9). THE 2026-07-14 REAL RUN IS INVALID AND E7 IS REBUILT. The build violated this operator; the source is faithful. Full dossier: verification/Discrepancy_Register.md DISC-05.**

WHAT WENT WRONG. This operator reads "Operator (frozen; SOURCE CALIBRATION)". The 2026-07-14 build used E4's calibration instead - a BUILD defect, not a design defect. Divergences: engine (E4's hand-rolled base-stock vs the source's stockpyl.serial_system); demand (base 100 / sigma 10 vs mean 10 / std 2); stockout:holding (4:1 vs 10:1); horizon (120 periods, no warmup, vs 260 with 52 warmup); estimator cold-start prior (0.30, copied from E4, vs the source's 0.5); comparison (spectral vs basestock, rather than sr_paper9_ols vs sr_disabled); variant count (2 vs the 5 this operator's own "9,000 simulations total" implies: 36 cells x 50 seeds x 5 variants = 9,000 exactly). The stockout-to-holding ratio ALONE can flip the sign, because the tool works by suppressing orders - costly at a 10:1 stockout penalty, cheap at 4:1. AMENDMENT 2026-07-14c IS THE PROXIMATE CAUSE: it froze the four demand ENVIRONMENTS from the source, declared the source check complete, and never checked engine, demand scale, cost ratio, warmup, or prior - while stating, in that same document, "the E4 lesson: calibration must trace to the source, never to the adjacent script." The rule was written and violated in one breath. The 2026-07-14 result (36 cells, 29/36 resolved, 0 harm / 29 benefit, "the source's calibration fails on all three points") is WITHDRAWN: it measures an unauthorized construction and re-earns nothing. Its measurements were real; they answered a question nobody asked.

THE SOURCE IS FAITHFUL AND ITS CODE CLEARS THE CIC. Source recovery (playbook method 1, ground truth) located the original artifacts on disk: the sweep script at "C:\Users\jaek9\OneDrive\Desktop\Werner Research Paper\Beer Game Simulator\phase2_6_chain_length_sweep.py" (MD5 cbc6bfa327150ca4e64acf2b63df0172), its policy/estimator module phase2_6_spectral_radius.py (MD5 e530ae06c57a15a6680419cbe245ec30), and its committed output "C:\ResearchShare\aggregated_chain_length_sweep.json" (MD5 6ecfc6fec0b1e490febea64ef36cd058, 9,000 trial records). The 7-point CIC was run on the source's own code and ALL SEVEN CLASSES CLEAR - recorded in full in DISC-05. Decisively, CIC-1 (re-executes to the claim): recomputing the paired per-seed pct difference (sr_paper9_ols vs sr_disabled, ar1_high x 2.4x) directly from their 9,000 raw records returns +0.439% (L=4), +0.137% (L=6), -0.141% (L=8) - matching v16's stated +0.44 / +0.14 / -0.14 to three decimals. v16 -> their experimental record -> their raw trial data is faithful at every hop. ORIGINAL CORRECT is therefore EARNED (provenance AND correctness established separately), not asserted from a summary. Their construction is safe to adopt.

FROZEN CONSTRUCTION FOR THE REBUILD - read from the source's code, not from a summary and not from the adjacent script:
  engine      stockpyl.serial_system, single-SKU, retailer at the highest node index
  demand      DEMAND_MEAN = 10, DEMAND_STD = 2; gen_periods = num_periods + 20
              (the 20-period tail is generated and unused; retained for fidelity)
  costs       holding = 1.0, stockout = 10.0, shipment_lt = 2
  horizon     260 periods, 52 warmup -> 208 measured; cost summed over
              range(52, 260) across all nodes (holding + stockout + in-transit)
  estimator   OLS on per-period demand recovered by differencing stockpyl's
              cumulative demand_cumul over a trailing lookback window, reading
              periods STRICTLY BEFORE the current one; min_observations = 10 ->
              neutral prior 0.5; near-constant guard (denominator < 1e-6) -> 0.95;
              clip [0, 0.999]. Documented Hurwicz bias: true phi 0.95 -> est ~0.67.
  variants    FIVE: sr_paper9_ols, sr_oracle_local, sr_disabled, sr_naive_damp,
              sr_numerical
  envs        iid_control; ar1_moderate phi=0.6; ar1_high phi=0.85;
              drift_canonical phi 0.3 -> 0.95 -> 0.4
  grid        chain lengths {4, 6, 8} x capacities {1.3x, 1.8x, 2.4x} x 4 envs
  comparison  sr_paper9_ols vs sr_disabled, PAIRED per seed (all variants run on
              the same seed - common random numbers)
  seeds       the source used 3000-3049 (50 distinct, verified in their artifact)

THE 2-SCENARIO SCOPING OF AMENDMENT 2026-07-14c IS WITHDRAWN. It reduced the sweep to base-stock vs all-tier spectral on the reasoning that the oracle and fixed-alpha variants "carry E12's claim" and could be deferred. That was wrong on the source's own record: E12's recipe-level non-stationarity finding was DISCOVERED VIA THE THREE-VARIANT DIAGNOSTIC IN THIS SAME SWEEP (the oracle harms in drift_canonical at every cell despite zero estimation error, while fixed-alpha damping produces large benefit at long chains - which is what proves the defect is in the recipe, not the estimator). E7 and E12 share one run by construction; the scoping severed that. All five variants are restored.

LIBRARY PARITY (precondition for the fidelity leg): stockpyl sim.py on the author's machine (48,114 bytes, dated 2026-04-22) is BIT-IDENTICAL to the container's stockpyl 1.0.2 - MD5 5a1ba4e1ff4f84800a06b4a317d4d8a3 on both sides. A faithful rebuild can therefore be expected to reproduce the source's per-cell numbers on the source's own seeds, and can be container-QA'd before any author-local run.

SEEDS (this supersedes the seed clause of amendment 2026-07-14b while preserving its ratified intent). Real run: seeds 3000-3999 (1000 per cell). This CONTAINS the source's own 3000-3049 as its first 50, so the fidelity leg is a strict subset of the real run rather than a separate execution. The 50 -> 1000 increase stands and is now DOUBLY justified: (i) as originally ratified, on power; (ii) because the CIC established that THE SOURCE'S OWN DESIGN IS UNDER-POWERED - their measured SEs are 0.072 / 0.078 / 0.081 against effects of +0.439 / +0.137 / -0.141, so L=4 resolves at 6.1 sigma but L=6 (1.8 sigma) and L=8 (1.7 sigma) DO NOT resolve at 95%. v16 asserts a chain-length threshold where the formula "crosses from harm to benefit"; the only resolved point in their data is L=4's harm, and the crossover itself rests on two points indistinguishable from zero. At 1000 seeds the SE falls to roughly 0.016, which settles the crossover in either direction. The rebuild can adjudicate a claim the source's own design could not.

CORRECTED CLASSIFICATION (supersedes the classification in 2026-07-14c). E7 = BLEND of:
  (a) REPLICATION - does the rebuild reproduce the source's per-cell means on the
      source's own seeds (3000-3049)? Report form: REGENERATED / NOT-REGENERATED
      plus HOW CLOSELY (per-cell delta against their artifact). This REPLACES the
      withdrawn MODEL-FIT/CALIBRATION leg: once we build the source's construction,
      comparison to their numbers IS a replication, not a calibration against an
      external prediction. A fidelity failure here means our rebuild is wrong and
      stops the line - it is never evidence about the source.
  (b) BOUNDARY-CONDITION / DOMAIN-MAPPING (primary) - where, across chain length and
      capacity, does sr_paper9_ols cross from harm to benefit relative to
      sr_disabled? Report form: a MAP with its resolution; a boundary whose adjacent
      cells are statistically indistinguishable is reported as UNRESOLVED, never as
      a crossing. Expected-null polarity is stated: finding NO crossover is a
      legitimate outcome and is reported as found.
  (c) ROBUSTNESS / SENSITIVITY - the gradient across chain length and capacity, and
      the three-variant diagnostic (paper9_ols vs oracle_local vs naive_damp).
      Report form: a STABILITY STATEMENT. No standalone verdict.
E7 carries NO standalone SUPPORT/REFUTE verdict. It no longer "qualifies E4": E4 is
a different construction (hand-rolled base-stock, different scale and cost ratio),
so the two are not commensurable and E7 makes no claim about E4.

REPORTING COMMITMENT (pre-registered): the fidelity result per cell against the
source's artifact; every cell's paired mean pct difference with its uncertainty and
achieved MDD; the crossover map with its resolution; the stability statement; and
the three-variant diagnostic. ALL cells reported regardless of direction. No cell
dropped. Where our 1000-seed result resolves a cell the source's 50 seeds could not,
both are reported side by side.

**AMENDMENT 2026-07-14e (pre-build, BUILD STRATEGY; author-ratified; Standard v1.9.9). The source's construction is VENDORED unmodified rather than re-implemented; the fidelity leg of 14d is WITHDRAWN as vacuous and REPLACED by a theorem-conformance check; the source's self-under-specification is recorded as a finding.**

WHY NOT RE-IMPLEMENT. The obvious reading of "re-earn" is to write fresh code from the source's spec and prove it reproduces. On inspection that buys almost nothing here and costs a great deal. RE-IMPLEMENTING FROM THE SOURCE'S CODE IS TRANSCRIPTION, NOT INDEPENDENCE: the operator would read compute_alpha_pi_squared_over_two and retype it into this repo, faithfully reproducing any logic defect it contains while ADDING transcription risk on top. The errors stay correlated; only the typo surface grows. Genuine independence would require re-implementing from the PAPER'S METHODS PROSE, and that is IMPOSSIBLE for this experiment - see the finding below. Weighed against that, bit-identity would additionally require matching the source's numpy RNG call order exactly, and a near-miss there is INDISTINGUISHABLE from a real difference - which is precisely the failure mode that produced the 2026-07-14 invalid run and its "the source fails" mis-finding.

FINDING (completeness gap; reported in the methods note and flagged for the Phase-5a Methods-code fidelity pass): THE PAPER CANNOT BE RE-IMPLEMENTED FROM ITS OWN TEXT. v16's chain-length sweep specification gives the grid (3 lengths x 3 capacities), the four environments, the seed count, and the headline values. It does NOT give: k_star = 0.90; INITIAL_BS_MULTIPLIER = 1.5 (initial base stock = DEMAND_MEAN * SHIPMENT_LEAD_TIME * 1.5 = 30); SHIPMENT_LEAD_TIME = 2; HOLDING_COST = 1.0; STOCKOUT_COST = 10.0; DEMAND_MEAN = 10.0; DEMAND_STD = 2.0; the estimator's min_observations = 10 and its 0.5 neutral prior; the near-constant guard returning 0.95; the alpha_floor / alpha_ceiling clip; the estimator lookback window; sr_naive_damp's fixed_alpha = 0.6; sr_numerical's k_star = 1.0; or drift_canonical's breakpoint schedule (seg = num_periods/5; (0,0.30) (52,0.30) (104,0.95) (156,0.95) (208,0.40) (259,0.40), piecewise linear). Every one of these materially determines the result. This is a property of the source, not of our rebuild, and it stands whichever build path is taken. NOTE AGAINST THIS AMENDMENT'S OWN PREDECESSOR: amendment 2026-07-14c declared drift_canonical's interpolation shape an "under-determined residue" and recorded a "frozen choice, mirroring E4's canonical ramp timing." That was FALSE - the schedule is specified exactly in the source's code, as are the estimator prior and the environment parameterisations. Three parameters were declared unknowable without looking; the not-looking was then documented as a design decision. The lesson is the same one this dossier keeps recording: the source is the ARTIFACT, not the prose about it.

BUILD STRATEGY (ratified). The source's modules are VENDORED into analysis/vendor/ UNMODIFIED, byte-for-byte, with their MD5s recorded in this amendment and asserted by the suite. This repo then carries the committed code that regenerates every number, satisfying the Standard's contract. Our own committed code is the RUNNER and the ANALYSIS - the grid driver, the paired comparison, the resolution logic, the crossover locator, and the report - which is where this experiment's contribution lives. Justification: the 7-point CIC (DISC-05) read the source's code line by line and cleared all seven classes; THAT READING IS THE INDEPENDENT VERIFICATION OF THE LOGIC. Vendoring also makes the paper MORE reproducible than the present arrangement, in which the numbers live in this repo and the code lives on a desktop outside it.

WHAT THE PAPER MAY CLAIM, and may not. It may say: we audited the source's implementation against the 7-point CIC and against the paper's own proven theorem, vendored it unmodified, and re-ran it at 20x the seed count to resolve what the original design could not. It may NOT say: we independently re-implemented the experiment and confirmed it. The distinction is recorded here so the manuscript cannot drift into the stronger claim.

THE 14d FIDELITY LEG IS WITHDRAWN AS VACUOUS. Under vendoring, running the source's code on the source's seeds MUST reproduce the source's numbers - it is the same computation. That is a tautology, not evidence, and reporting it as a replication would be theatre. (It retains one narrow use, kept in the suite as a REGRESSION assertion rather than a finding: it proves the vendored copy is unmodified and the harness wires it correctly.)

REPLACED BY A THEOREM-CONFORMANCE CHECK - the check that actually buys independence. The source's damping rule IS this paper's theorem: S = (1 - phi^W)/(1 - phi); alpha_max = (pi^2/2)/S; alpha_op = alpha_max * k_star. T1/T2/T3 were verified independently in this repo (symbolic + numeric, green before any empirical work, DECISIONS 2026-07-13). The suite therefore asserts that the VENDORED CODE'S ALPHA RULE AGREES WITH THE AS-PROVEN THEOREM across a grid of phi and W, computed from this repo's own theory_lib rather than from the vendored module. This is the theory-first rule (v1.9.6) applied to a vendored operator: re-check the experiment's operator against the as-proven statements. It is aimed at the science rather than the plumbing, and it is the check that would catch the class of defect DISC-07 asks about. A conformance failure is a finding about the source's implementation, NOT a licence to modify the vendored code: the vendored copy stays byte-identical and the discrepancy is dossiered.

CLASSIFICATION IMPACT. Leg (a) REPLICATION is withdrawn (vacuous under vendoring; the regression assertion moves into the suite and is not a report form). E7's report forms are unchanged and are now exactly two: (b) BOUNDARY-CONDITION / DOMAIN-MAPPING - the crossover map with its resolution, expected-null polarity stated; and (c) ROBUSTNESS / SENSITIVITY - the stability statement across chain length and capacity, plus the three-variant diagnostic. E7 still carries NO standalone SUPPORT/REFUTE verdict.

VENDORED FILES (MD5s asserted by the suite; any drift is a hard fail):
  analysis/vendor/phase2_6_chain_length_sweep.py   cbc6bfa327150ca4e64acf2b63df0172
  analysis/vendor/phase2_6_spectral_radius.py      e530ae06c57a15a6680419cbe245ec30
  analysis/vendor/phase2_6_timevarying_demand.py   e681e0c451457335ae66663b2a8b0e09
Vendored 2026-07-15 by direct file copy (NOT retyped - emitting 1,500 lines through
an edit tool would reintroduce exactly the transcription risk this amendment rejects);
all three MD5s verified equal on both sides after the copy.
Third-party: stockpyl 1.0.2, sim.py MD5 5a1ba4e1ff4f84800a06b4a317d4d8a3, verified
bit-identical between the author's machine and the QA container.

A HAZARD FOUND WHILE VENDORING, to be asserted by the suite rather than assumed:
phase2_6_timevarying_demand.py defines BOTH phase2_6_drift_schedule() AND
phase2_6_drift_schedule_DEPRECATED_DUPLICATE(), and the sweep script calls NEITHER -
it defines its own make_phase2_6_drift_schedule() locally. Three drift schedules are
therefore in scope. Reading says the sweep uses its local one and the two
module-level definitions are dead code here, but that is a CIC-7 (input integrity)
hazard of exactly the kind that bites silently, so the suite ASSERTS which schedule
reaches the demand generator instead of trusting the reading.

**AMENDMENT 2026-07-14f (pre-run, MEASURED-COST; author-ratified; Standard v1.9.9). SEEDS 1000 -> 250 PER CELL. Made after the rebuild was wired to the vendored engine and its throughput MEASURED, before any real run, and blind to every cell's outcome.**

WHY. Amendment 2026-07-14b raised seeds 50 -> 1000 for POWER, and 14d re-affirmed it. That ratification was made against E4's variance, before the source's construction was recovered - the rebuild's true cost was unknown at the time. Measured in the QA container against the vendored engine (5 variants per seed): L=4 2.29 s/seed, L=6 3.42 s/seed, L=8 4.50 s/seed. The frozen grid is 3 lengths x 3 capacities x 4 environments = 36 cells, so the full grid at 1000 seeds projects to roughly 7.6 h (L=4) + 11.4 h (L=6) + 15.0 h (L=8) = ABOUT 34 HOURS single-machine. That is consistent with the source's own record - they ran 50 seeds in 15.3 minutes distributed across a 12-14 worker fleet, i.e. some hours single-machine, and 20x that is not a sitting. The author has a fleet, but it lives outside this repo and routing the run through it would complicate the Phase-5b clean-room reproduction gate.

THE POWER ARITHMETIC (the amendment's ratified INTENT was to resolve what the source's 50 seeds could not; this is what actually delivers it). From the source's MEASURED standard errors at 50 seeds (0.072 / 0.078 / 0.081, mean ~0.077), SE scales as 0.077 * sqrt(50/n):
    n =   50 (theirs)  SE 0.077   L=6 (+0.137) = 1.8 sigma   UNRESOLVED
    n =  100           SE 0.054   L=6 = 2.5 sigma            resolved
    n =  250           SE 0.034   L=6 = 4.0 sigma, L=8 (-0.141) = 4.1 sigma   RESOLVED
    n = 1000           SE 0.017   L=6 = 8.0 sigma            resolved (overkill)
250 seeds resolves BOTH previously-unresolved points at ~4 sigma - five times the source's power - for about 8.5 hours instead of 34. 1000 buys 8 sigma where 4 settles the question.

SELF-PENALIZING CHECK (mandatory, because REDUCING a sample size is the direction in which a defect could hide). The Standard's re-design test: would this change be made if it pushed the result the other way? A seed reduction is inadmissible if it lets an inconvenient cell fall back into "unresolved" and thereby avoids a finding. At 250 seeds the two cells the source could not resolve - L=6 (+0.137) and L=8 (-0.141) - BOTH resolve, at 4.0 and 4.1 sigma. The reduction therefore does NOT purchase an escape from any finding: the crossover is still adjudicated in whichever direction the data falls. Had 250 left either point unresolved, the reduction would have been refused and the 34 hours accepted. Recorded so this reasoning is auditable rather than assumed.

WHAT IS UNCHANGED. Seeds now 3000-3249. The source's own 3000-3049 remain the FIRST FIFTY of this range, so the regression assertion (that the vendored copy is unmodified and the harness wires it correctly, per 14e) still needs no separate execution. The grid, the construction, the 5 variants, the comparison, and both report forms are unchanged. The 50 -> 1000 -> 250 history stands in full: 14b's reasoning was sound on the information then available, and this amendment narrows it on measured cost, not on any result.

**Inputs:** none external.

## 11. E8 - Pricing-mechanism analysis (asymmetry)

**Purpose:** test whether the persistence calculation gives useful guidance on a second lever (price), and re-earn the asymmetric finding (raises help under strain; cuts are uniformly negative).

**Operator (frozen; source calibration).** Chain simulation extended with constant-elasticity demand response and a phi-gated pricing policy (raise on high-persistence upward shift; cut on high-persistence downward shift); five demand environments at 1.3x capacity, 50 seeds per cell; capacity sensitivity at 1.8x for the upward case. Outputs: per-period value of the pricing policy vs no-pricing baseline, per cell.

**Decision rule.** The asymmetry claim is ASSERTED only if: value of raises is positive in the capacity-strained sustained-upward environment (95% CI excluding zero) AND value of cuts is negative in EVERY downward environment tested. PARTIAL: raises positive but any cut-cell non-negative -> the "uniformly negative" language is withdrawn and the section reports the actual sign pattern. DROPPED: raises not positive under strain - the pricing section reduces to a null report.

**Validity review.** Referent: constant-elasticity immediate-arithmetic response is a stated modeling assumption, disclosed as bounding the finding (no competitor response, no brand effects); E9 attacks the biggest omission directly. Partition: assert/partial/drop covers all sign patterns.

**AMENDMENT 2026-07-15 (PRE-BUILD; classification + regenerate-or-escalate; Standard v1.9.7). Made before any E8 code exists.**

WHY E8 EXISTS (the reason, restated before any parameter is chosen): the paper claims the persistence calculation generalizes from inventory ordering to a SECOND LEVER - price - and that its guidance is ASYMMETRIC (raises help under capacity strain; cuts are uniformly negative). That is a claim about a MECHANISM, evidenced by SIGNS. The dollar figures, the elasticity value, and the 1.8x capacity number are DETAILS that follow from a construction; they are not the claim.

SOURCE CHECK (performed before writing the script). Authoritative spec is v16 "Pricing-mechanism analysis": five demand environments NAMED (level_shift_up_persistent, low_phi_shift_up, level_shift_down_persistent, low_phi_shift_down, mid_phi_shift_down), 50 seeds per cell, 1.3x baseline, constant-elasticity demand response with elasticity = 1.5 and reference price = 1.0. Mechanism described in the supporting draft Section 3.1: the retailer observes sales velocity over a trailing window and adjusts price proportionally to the velocity gap against a target; the phi-gated extension damps price adjustments only when the persistence of the velocity signal is high enough that over-correction becomes costly, damping the dangerous direction more than the safe one.

REGENERATE-OR-ESCALATE APPLIED (Standard rule; COVERAGE Phase-2 reconciliation). Each element's disposition is DETERMINED BY FACT, not chosen:
  - The phi-gated pricing MECHANISM is specified -> reproducible -> TRANSFORM (built, recomputed).
  - The ASYMMETRY SIGN PATTERN follows from the mechanism rather than from the unspecified scale constants -> reproducible -> TRANSFORM. This is the claim v16's abstract makes ("cutting prices in response to demand decreases is uniformly negative across every environment we tested") and is E8's primary.
  - The CAPACITY DEPENDENCE (direction and ratio) is reproducible because a ratio largely cancels the unknown scale constants -> TRANSFORM.
  - The ABSOLUTE DOLLAR LEVELS are NOT reproducible: the source specifies NEITHER the level-shift magnitude, NOR its timing, NOR the pricing gain, NOR the velocity target, NOR the trailing window - and every one of these sets the dollar level. -> DROP, not replicable in prior form. E8 reports its own dollar figures as CONSTRUCTION-SPECIFIC and issues NO calibration verdict against any source dollar figure. Logged as an escalation in DECISIONS.md; COVERAGE.md updated.

CORROBORATING EVIDENCE THAT THE SOURCE'S DOLLAR FIGURES CANNOT BE ARBITRATED (recorded, not adjudicated): (a) v16 states the upward benefit "drops from $10,142/period at 1.3x to under $900/period at 1.8x" and, separately, that it "collapses by 12x at 1.8x capacity" - $10,142/12 = $845, so the two v16 statements agree with each other; but the supporting draft's experimental record reads 1.3x = $10,142, 1.8x = $5,200, 2.4x = $2,100, 3.0x = $775, and calls that "a roughly twelve-fold reduction ACROSS THE CAPACITY RANGE" ($10,142/$775 = 13.1x). v16 compressed the draft's FULL-RANGE collapse onto the FIRST STEP; the actual 1.3x -> 1.8x step in the draft is only 2.0x. (b) The draft's own elasticity sweep reports $122-$144/period at 1.8x and phi = 0.85 - the same cell its capacity sweep calls $5,200 (39x apart). (c) The draft calls the 1.3x downward harm "approximately $4,000... roughly forty percent of the upward benefit" while v16 reports -$2,315 (22.8%). Three mutually exclusive values exist for the 1.8x cell ($845 / $5,200 / $133). No coherent prior value exists; this is a fact about the source, not a judgement about it.

CLASSIFICATION (v1.9.7). E8 is a BLEND of (a) HYPOTHESIS TEST - the asymmetry rule, which has a genuine null and a real fail condition (any downward cell non-negative), and (c) ROBUSTNESS/SENSITIVITY - the capacity leg, which qualifies (a) and carries NO standalone verdict. There is NO calibration leg: the source never made a calibratable prediction here - it reported dollars from a construction it did not specify. (Contrast E7, where the source's grid was fully specified and its three point-predictions were legitimately calibratable.)

SEVERITY. Two risks, both addressed before the run:
  RISK 1 - POWER AT THE PER-CELL n. The rule requires cuts negative in EVERY downward environment. The source concedes its own power problem: its 20-seed replication gave $8,401 against the 50-seed headline of $10,142, "approximately 17% below... with the headline value at the upper edge of our 95% confidence interval." Backing that admission out: 20-seed CI half-width ~$1,741 -> SE_20 ~$888 -> SD ~$3,972. At the frozen 50 seeds the CI half-width is ~$1,101, which SWALLOWS the smallest downward cell (-$581): "uniformly negative" would be unadjudicable BY CONSTRUCTION at that cell, in either direction. At 1000 seeds the half-width is ~$246 and all three downward cells resolve. SEEDS 50 -> 1000 (matching E4 and E7). The estimate above is a SIZING PRIOR inferred from the source's prose, not a measurement: the suite MEASURES per-cell variance and reports each cell's achieved MDD; a cell whose achieved MDD exceeds its own effect is reported UNRESOLVED, never as a null.
  RISK 2 - PARAMETER-MANUFACTURED SIGNS (first principles, where the protocol runs out). Because the scale constants are unspecified, our choice of shift magnitude and pricing gain could in principle manufacture the sign pattern. If the asymmetry is REAL it must survive reasonable choices of the free constants. Therefore the free parameters are SWEPT as a mandatory severity guard and the sign pattern is required to be INVARIANT across the sweep. If the pattern flips with the gain or the shift magnitude, the claim is PARAMETER-DEPENDENT and that is the finding - reported, not suppressed. An asymmetry that exists only at one arbitrary calibration is not an asymmetry.

DECLARED FREE PARAMETERS (frozen in the committed script config before first run; the source specifies none of them, so these are author choices, disclosed as such and swept per Risk 2): level-shift magnitude, shift timing, pricing gain, velocity target, and pricing trailing window. Environment persistences are INFERRED from the source's own vocabulary ("mild (0.3), moderate (0.6), strong (0.85)"): low_phi = 0.3, mid_phi = 0.6, persistent = 0.85. The inference is declared; the names trace to source.

REPORT FORM. (a) Asymmetry: VERDICT (ASSERTED / PARTIAL / DROPPED per the frozen rule above) - but ONLY if severity clears, i.e. every downward cell resolves AND the sign pattern is invariant across the free-parameter sweep. If any downward cell is unresolved, "uniformly negative" is reported INCONCLUSIVE for that cell rather than as a null. (c) Capacity: STABILITY STATEMENT, no standalone verdict. Dollar levels: reported as construction-specific magnitudes with uncertainty, explicitly NOT compared to any source figure.

REPORTING COMMITMENT (pre-registered): every cell's per-period pricing value vs the no-pricing baseline with its uncertainty and achieved MDD; the sign pattern across all five environments; the free-parameter invariance sweep; and the 1.3x-vs-1.8x capacity statement. ALL cells reported regardless of direction; no cell dropped.

**AMENDMENT 2026-07-16 (PRE-BUILD; the 2026-07-15 amendment above is WITHDRAWN as DISPROVEN; author-ratified; Standard v1.9.9). E8 re-opens at its classification gate on RECOVERED FACTS. Nothing has been built or run.**

THE 2026-07-15 AMENDMENT IS WITHDRAWN. It dispositioned the source's pricing dollar levels DROP - "not replicable in prior form" - on the stated grounds that the source specifies "NEITHER the level-shift magnitude, NOR its timing, NOR the pricing gain, NOR the velocity target, NOR the trailing window," and declared them "DECLARED FREE PARAMETERS... the source specifies none of them." ALL OF THAT IS FALSE. The DROP was asserted as an OPENING ASSUMPTION with the discrepancy ladder never run - the exact inversion the Standard forbids ("not replicable in prior form is a conclusion the ladder REACHES, never an opening assumption"). Withdrawn in DECISIONS 2026-07-15; withdrawn here; the COVERAGE row is corrected by the same date. The amendment stands above, unerased, as the record of the error.

WHAT THE LADDER ACTUALLY RECOVERED (playbook methods 1 and 3, GROUND TRUTH - see DISC-01 and DISC-02). The source's pricing code is ON DISK and was read directly, not summarized: phase2_7_validation_runner.py, phase2_7_pricing_manager.py, phase2_7_demand_response.py, phase2_7_pricing_policies.py, phase2_3_stage1_network.py (SKU_SPECS). Its committed OUTPUT is also on disk: C:\ResearchShare\phase27_validation_50seed\aggregated_phase27_validation_50seed.json, plus the capacity sweep (18x/24x/30x) and elasticity sweep (05/30) files. EVERY parameter the withdrawn amendment called unspecified is recovered:
  architecture      4-stage serial, 1.3x capacity, summed_at_retailer demand,
                    all_sr inventory scenario
  demand            12 SKUs (SKU_SPECS: mean demands 200/200/200/100/100/100/
                    40/40/40/10/10/2; unit costs $1-$100), summed x6 -> ~1,042
                    units/period at the retailer
  elasticity        1.5; reference_price = 1.0; revenue = price x quantity_sold
  horizon           DEFAULT_NUM_PERIODS = 260, DEFAULT_WARMUP_PERIODS = 52
                    -> 208 measured periods
  shift             +/-20% level shift at t = 130; shift_magnitude =
                    shift_fraction * 6.0 * sku.mean_demand
  review interval   20 periods
  estimator         OLS, W = 40 (the source's own window-size diagnostic found 40
                    dominates 20 and 100: same false-alarm rate as 20, better
                    legitimate-detection rate; 100 extends break contamination)
  thresholds        symmetric: phi > 0.60 both directions.
                    ASYMMETRIC: raise if phi > 0.60; cut only if phi > 0.75 -
                    "the asymmetric formula damps the dangerous direction more
                    than the safe direction"
  scenarios         no_pricing, naive_reactive, phi_gated_symmetric,
                    phi_gated_asymmetric
  metric            net_value = revenue - cost; the runner emits BOTH per-period
                    fields (cost_per_period, mean_revenue_per_period) AND a
                    cumulative one (net_value_post_warmup)
RISK 2 OF THE WITHDRAWN AMENDMENT IS THEREFORE MOOT. It proposed sweeping "free parameters" to guard against parameter-manufactured signs. There are no free parameters: the construction is fully recovered. The guard was a solution to a problem created by not looking.

DISC-02 (RESOLVED, ground truth): the source's five dollar figures are CORRECT, PER-PERIOD, and correctly labelled. Computing mean_revenue_per_period_mean - cost_per_period_mean per environment from their own committed output, then no_pricing vs naive_reactive: level_shift_up_persistent +10,141.86 (source +$10,142); low_phi_shift_up +1,646.78 (+$1,647); level_shift_down_persistent -2,315.25 (-$2,315); low_phi_shift_down -581.36 (-$581); mid_phi_shift_down -1,238.29 (-$1,238). All five reproduce exactly. The cumulative/relabel hypothesis raised twice against these figures is DEAD; both raisings rested on a magnitude check against E4, which is the WRONG REFERENCE SYSTEM (E4 is a single-product 4-echelon chain; this is 12 SKUs summed x6).

DISC-01 (RESOLVED, ground truth): the withdrawn amendment's "three mutually exclusive values for the 1.8x cell ($845 / $5,200 / $133)" is REVERSED. v16 IS FAITHFUL and the supporting DRAFT is the corrupted document. The source's own experimental record reads 1.3x +$10,142, 1.8x +$842, 2.4x +$777, 3.0x +$775, ">>> 12x collapse from 1.3x to 1.8x" - so v16's "under $900 at 1.8x" and "collapses by 12x at 1.8x" are BOTH exactly right. The draft's $5,200 and $2,100 exist in NO record; its "approximately $4,000 ... roughly forty percent of the upward benefit" is arithmetic on its own misreading of the record's "40% REDUCTION ACROSS CAPACITY RANGE" (-$2,316 -> -$1,374); and its "$122-$144 at 1.8x" is the asymmetric-vs-symmetric ADVANTAGE in low_phi_shift_down at 1.3x - a different quantity from a different row. There is a coherent prior target after all, and v16 is it.

DISC-03 - THE FRAMING GATE FINDING, and it governs everything E8 does (playbook method 8: run FIRST; its power is disconfirmation, and it rejects a route regardless of what that route reproduces). v16 frames this section as testing whether the PERSISTENCE FORMULA gives useful guidance on price, and reports +$10,142/period as its headline. THAT FIGURE IS THE no_pricing vs NAIVE_REACTIVE COMPARISON. In the source's own committed output, naive_reactive, phi_gated_symmetric and phi_gated_asymmetric all return cost_per_period_mean = 10942.385082660967 - BIT-IDENTICAL. The source's own record states the mechanism plainly: "PHI-GATING DOES NOT DIFFERENTIATE FROM NAIVE ... The persistence test always passes so phi-gated reduces to naive_reactive." THE $10,142 IS THE VALUE OF REACTING TO DEMAND SHIFTS AT ALL - not the value of the formula. The formula's own measured contribution is $144/period (asymmetric vs symmetric in low_phi_shift_down), 1.4% of the headline. This is the Paper-4 ratio-operator pattern: reproducible, and INADMISSIBLE for the sentence attached to it. It is independent of DISC-01 and DISC-02 - it holds even though every number is correct. CONSEQUENCE FOR THE GATE: the admissible primary comparison for a claim ABOUT THE FORMULA is phi_gated_* vs naive_reactive, NOT vs no_pricing. Any E8 result reported against no_pricing measures reaction, not persistence guidance, and may not be attributed to the formula.

DISC-04 - OPEN, AND IT BLOCKS THE BUILD STRATEGY. E7's build strategy (14e) vendored the source's construction because its code cleared all seven CIC classes. THAT PRECONDITION IS NOT ESTABLISHED HERE, and there is positive evidence against it: in the source's own pricing output, ar1_high and ar1_high_no_shift - DIFFERENT demand environments - return identical cost_per_period_mean, identical mean_revenue_per_period_mean and identical standard deviations to 15 significant figures; and phase2_7_validation_runner.py calls simulation(net, num_periods=..., rand_seed=42, progress_bar=False) with the seed HARD-CODED rather than threaded from trial_seed. DISC-05's CIC established that the same hard-coding is INERT in the chain-length sweep, because that script hands stockpyl an explicit deterministic demand list (DemandSource type='D'); the hypothesis to test is that the pricing runner instead hands over a STOCHASTIC demand source, which rand_seed=42 would then freeze identically across every trial. PROVENANCE IS NOT CORRECTNESS: the pricing code's authenticity is established, its correctness is NOT. THE 7-POINT CIC MUST RUN ON phase2_7_validation_runner.py BEFORE any decision about vendoring, and its outcome determines the build:
  CIC CLEARS  -> vendor as in E7, drive with our runner, re-run at higher n.
  CIC FAILS   -> the source's construction is defective and MUST NOT be vendored;
                 adjudication becomes RECONSTRUCTION CORRECT / ORIGINAL IN ERROR
                 (an authentic computation that reproduces its number through a
                 silent defect is adjudicated original-in-error, never "original
                 correct"), the affected cells are dossiered, and the build path is
                 re-decided on the ladder - not assumed.
No build decision is taken in this amendment. The CIC runs first.

CLASSIFICATION (v1.9.7), re-derived from the recovered facts rather than from the withdrawn amendment's assumptions. E8 is a BLEND of:
  (a) HYPOTHESIS TEST (primary) - the asymmetry claim, which has a genuine null and
      a real fail condition. But the DISC-03 gate rescopes it: the claim under test
      is that THE PERSISTENCE GATE improves pricing guidance, so the comparison is
      phi_gated_asymmetric vs naive_reactive (and phi_gated_symmetric vs
      naive_reactive), NOT vs no_pricing. Severity is NOT yet established - see
      below. Report form: VERDICT only if severity clears.
  (b) REPLICATION - do the source's five per-period figures regenerate? Under
      vendoring this is a regression assertion, not evidence (the E7 lesson);
      under a rebuild it is a genuine replication leg. Deferred until the CIC
      decides the build path.
  (c) ROBUSTNESS / SENSITIVITY - the capacity leg (1.3x vs 1.8x/2.4x/3.0x, whose
      output files are also on disk). Qualifies (a); NO standalone verdict.
There is no calibration leg: with the construction recovered, comparison to the
source's numbers is replication (b), not calibration.

SEVERITY - THE CENTRAL RISK, AND IT IS NOT THE ONE THE WITHDRAWN AMENDMENT NAMED. If phi_gated is BIT-IDENTICAL to naive_reactive in the source's own run, then a test of "does the gate help?" on those environments has NO DYNAMIC RANGE: the two arms are the same computation, the difference is exactly zero, and no sample size resolves it. That is the E5 saturation disease in its purest form - a comparison between two arms that are not distinct. The source itself diagnosed why: OLS structural-break inflation pushes the persistence estimate above BOTH thresholds (0.60 and 0.75) in essentially all trials of the high-persistence environments, so both gates always open and both variants reduce to naive. THE GATE ONLY DISCRIMINATES WHERE THE ESTIMATE STRADDLES A THRESHOLD - which the source's record locates in low_phi_shift_down (naive 2.8 -> symmetric 2.4 -> asymmetric 1.8 price changes; $144/period advantage) and mid_phi_shift_down (3.0 -> 2.8 -> 2.7). E8's severity check must therefore establish, BEFORE the real run and per environment, whether the two arms are distinct AT ALL - by measuring the engagement/threshold-straddle rate, which is a property of the instrument and the environment, not of the result. An environment where the arms are identical yields INCONCLUSIVE for the gate claim, never a null, and never a verdict.

NEXT (E8, in order; no build decision until the CIC lands): (1) run the 7-point CIC on phase2_7_validation_runner.py and its modules - DISC-04 is the first point and the seed/demand-source question is CIC-7 (input integrity); (2) adjudicate DISC-04 on that evidence; (3) re-derive the build strategy from the outcome; (4) complete the severity check (arm-distinctness per environment); (5) then, and only then, build.

**AMENDMENT 2026-07-16b (PRE-BUILD; CORRECTS the severity clause of amendment 2026-07-16 above; author-ratified; Standard v1.9.9). THE SEVERITY CONCERN IS WITHDRAWN - IT RESTED ON A FALSE PREMISE OF MINE. E8 IS RUNNABLE. DISC-04 is RESOLVED, NO DEFECT.**

WHAT THE CIC FOUND, and it contradicts two of my own claims from the amendment above.

CIC-7 (input integrity) CLEARS. Amendment 2026-07-16 above stated that DISC-04 "BLOCKS THE BUILD STRATEGY" and hypothesised that the pricing runner hands stockpyl a STOCHASTIC demand source which rand_seed=42 would freeze. IT DOES NOT. assign_realized_streams_to_retailer() sets DemandSource(type='D', demand_list=realized_streams[sku.sku_id].tolist()) - a DETERMINISTIC explicit list, exactly as the chain-length sweep does - so rand_seed=42 has nothing left to randomise and is inert here too. The hard-coded 42 is untidy, not defective. Further, ar1_high and ar1_high_no_shift are THE SAME DEMAND PROCESS UNDER TWO NAMES (both constant_schedule(0.85), no level shift; one legacy Phase-2.6, one added 2026-04-29 as the pricing control), so their identical output to 15 significant figures is CORRECT BEHAVIOUR and is weak positive evidence that the pipeline is deterministic. DISC-04 -> RESOLVED, no defect.

CIC-1 (re-executes to the claim) CLEARS, and decisively. The source's artifact carries 1,800 RAW trial records (9 environments x 4 scenarios x 50 seeds). Recomputing the paired per-seed no_pricing vs naive_reactive difference (mean_revenue_per_period - cost_per_period) directly from those records returns: level_shift_up_persistent +10141.86 (se 630.19, 16.1 sigma) vs published +$10,142; low_phi_shift_up +1646.78 vs +$1,647; level_shift_down_persistent -2315.25 vs -$2,315; low_phi_shift_down -581.36 vs -$581; mid_phi_shift_down -1238.29 vs -$1,238. All five reproduce to under one unit. Their arithmetic is exact.

THE SEVERITY CLAUSE OF AMENDMENT 2026-07-16 IS WITHDRAWN. It asserted that phi_gated is BIT-IDENTICAL to naive_reactive, that the two arms are "the same computation," that "the difference is exactly zero, and no sample size resolves it," and that this is "the E5 saturation disease in its purest form." ALL OF THAT IS FALSE. Measured per seed from the raw records, the arms are NOT identical in ANY of the five level-shift environments (sym==naive False and asym==naive False in all five). The bit-identity occurs ONLY in ar1_high_no_shift - which is the NO-SHIFT CONTROL, where there is nothing to react to, so every reactive policy does nothing and all three arms coincide. That is correct behaviour, not saturation. The error's origin: the summary key 'ar1_high|phi_gated_asymmetric' was read as though 'ar1_high' were the headline environment; it is the legacy control - the very naming duplication DISC-04 had just exposed, which failed to transfer because it arrived wearing different clothes. THE ARMS ARE DISTINCT, THE COMPARISON HAS DYNAMIC RANGE, AND E8 CAN ADJUDICATE IN EITHER DIRECTION.

DISC-03 SURVIVES AND IS STRENGTHENED BY BEING MEASURED RATHER THAN ARGUED. The framing gate stands unchanged and is now quantified from the raw records. In the environment carrying the paper's headline: no_pricing vs naive_reactive = +10141.86 (16.1 sigma), while phi_gated_asymmetric vs naive_reactive = +13.01 (se 21.52, 0.6 sigma) - UNRESOLVED. The formula's contribution in the very environment it is credited for is INDISTINGUISHABLE FROM ZERO, and amounts to 0.13% of the headline attributed to it. Across all five level-shift environments the formula has exactly ONE resolved win: low_phi_shift_down, phi_gated_asymmetric vs naive_reactive = +137.20 (se 31.41, 4.4 sigma) - the source's own "$144/period asymmetric advantage," confirmed. The remainder: low_phi_shift_up +19.42 (2.3 sigma, resolved but small), level_shift_down_persistent -24.28 (1.3 sigma), mid_phi_shift_down -24.55 (1.0 sigma). The gate therefore stands: the admissible primary comparison for any claim ABOUT THE FORMULA is phi_gated_* vs naive_reactive, NEVER vs no_pricing.

METHOD FAILURE, RECORDED - THE FOURTH OF ITS KIND IN THIS EFFORT. A defect was again INFERRED FROM A PATTERN rather than read from the records, and again the inference was wrong: (i) the magnitude check against E4 as the reference system; (ii) the cumulative/relabel hypothesis, raised twice; (iii) DISC-04's seed and environment suspicion; (iv) this severity clause. In every instance the ANOMALY WAS REAL and the DIAGNOSIS WAS INVENTED. The operative rule: an identical-values pattern is a signal to OPEN THE RAW RECORDS, never evidence of what caused it.

BUILD STRATEGY - now decidable on evidence, but SIX CIC CLASSES REMAIN. CIC-1 and CIC-7 clear. Classes 2 (index/row alignment), 3 (NaN and gap handling), 4 (no look-ahead), 5 (overlap vs non-overlapping subsample), and 6 (record boundaries) are OUTSTANDING. Vendoring requires all seven (the E7 precondition), so NO BUILD DECISION IS TAKEN HERE. Provenance is not correctness: this amendment establishes that two specific suspicions were unfounded, not that the code is sound.

NEXT (E8): (1) CIC classes 2-6 on phase2_7_validation_runner.py, phase2_7_pricing_manager.py, phase2_7_demand_response.py and phase2_7_pricing_policies.py - CIC-4 (look-ahead) matters most, since the pricing policy consults a rolling persistence estimate at each review; (2) decide the build strategy on the completed CIC; (3) then build.

**AMENDMENT 2026-07-16c (PRE-BUILD; CIC COMPLETE and BUILD STRATEGY; author-ratified; Standard v1.9.9). All seven CIC classes CLEAR on the pricing code. E8 carries TWO CLAIMS requiring TWO DIFFERENT COMPARISONS, and v16 conflates them - that conflation is the experiment's central finding.**

CIC COMPLETE - ALL SEVEN CLASSES CLEAR (phase2_7_validation_runner.py, phase2_7_pricing_manager.py, phase2_7_pricing_policies.py, phase2_7_demand_response.py):
  (1) RE-EXECUTES TO THE CLAIM: all five published figures recompute from the 1,800
      RAW trial records at 13-21 sigma (see 2026-07-16b).
  (2) INDEX/ROW ALIGNMENT: cost sums over range(warmup_periods, num_periods) =
      range(52, 260); revenue sums over rev_per_period[warmup_periods:] = [52:];
      both are 208 periods and both divide by measured_periods = num_periods -
      warmup_periods = 208. SAME WINDOW, SAME DIVISOR - which is load-bearing,
      because net_value = revenue - cost SUBTRACTS them, so a one-off in either
      would corrupt every figure. The code's own comment states the intent:
      "Revenue is restricted to post-warmup periods to match the cost window."
  (3) NaN AND GAP HANDLING: except Exception -> success=False plus a full traceback;
      the aggregator counts successes; 0 of 1,800 failed, so no failed record
      reaches any figure. OBSERVATION, inert here and recorded rather than assumed:
      extract_chain_costs carries the same silent-truncation guard as the sweep
      (`if t < len(node.state_vars)`), which would drop periods from the cost sum
      while measured_periods stays 208 - understating cost_per_period with no error
      raised. It never fires in this run.
  (4) NO LOOK-AHEAD: VERIFIED AT THE CALL SITE, not merely from the docstring. In
      apply_pricing_to_retailer_streams the loop appends period t's aggregate to
      the history, and only then, at a review boundary, calls
      policy.decide_price(period=t+1, demand_history=aggregated_demand_history,
      current_price=current_price). The history contains periods 0..t; the returned
      price governs t+1 onward. The policy never sees demand it is about to
      influence. The docstring's contract ("up to (but not including) the current
      period") is honoured by the caller.
  (5) OVERLAP vs NON-OVERLAPPING SUBSAMPLE: disjoint BY CONSTRUCTION. Per
      PricingPolicyConfig, "the baseline is the recent_window-to-(recent_window +
      baseline_window) period range, so it does not overlap with the recent window"
      - recent 20 periods, baseline the 60 before it.
  (6) RECORD BOUNDARIES: costs accrue per node over range(52, 260) and are then
      totalled; no computation spans a node boundary; per-tier accounting is a
      separate roll-up, not a re-slice.
  (7) INPUT INTEGRITY: cleared in 2026-07-16b - deterministic demand list makes
      rand_seed=42 inert; the "identical environments" are one no-shift control
      under two names.
ADJUDICATION: THE PRICING CODE IS CORRECT. Provenance (method 1) and correctness
(the CIC) are both established, separately and in that order - earned, not asserted.
The architecture explains the CIC-7 result structurally rather than coincidentally:
the pricing layer is a PURE UPSTREAM TRANSFORMATION ("the entire realized demand
stream can be pre-computed BEFORE running the inventory simulation"), which is WHY
the demand handed to stockpyl is a deterministic list.

BUILD STRATEGY: VENDOR, as in E7 (14e), and for the same reason - the CIC cleared,
so the source's construction is safe to adopt, and re-implementing FROM their code
would be transcription rather than independence. Ours remains the runner and the
analysis. The vendoring scope is LARGER than E7's three modules: the pricing runner
additionally imports phase2_3_stage1_network (SKU_SPECS), phase2_3_stage3_policy_comparison
(apply_capacity_constraints), phase2_3_stage2_demand, phase2_6_serial_network,
phase2_6_policy_scenarios, phase2_7_demand_response, phase2_7_pricing_policies and
phase2_7_pricing_manager. Every vendored module is MD5-asserted by the suite; the
exact set and hashes are recorded at vendor time. The same claim limits apply: E8
MAY say it audited the source's implementation against the 7-point CIC and re-ran
it; it MAY NOT claim independent re-implementation.

THE STRUCTURAL FINDING - E8 CARRIES TWO CLAIMS, AND THEY NEED DIFFERENT COMPARISONS.
This experiment's frozen purpose reads: "Test whether THE PERSISTENCE CALCULATION
gives useful guidance on a second lever (price), AND re-earn THE ASYMMETRIC FINDING
(raises help under strain; cuts are uniformly negative)." Those are two distinct
claims about two distinct things:
  CLAIM A - THE FORMULA'S VALUE. Does the persistence gate improve pricing guidance?
    Admissible comparison: phi_gated_asymmetric vs NAIVE_REACTIVE (and
    phi_gated_symmetric vs naive_reactive). The naive policy already reacts to
    demand shifts; the gate is the only difference between the arms, so the
    difference IS the formula's contribution. The source's own code says exactly
    this, in PricingPolicy's docstring: "Comparing against this baseline ISOLATES
    THE VALUE OF THE FORMULA'S PERSISTENCE-DISCRIMINATION CAPABILITY beyond the
    value of dynamic pricing in general." They built the right comparator.
  CLAIM B - THE ASYMMETRY OF PRICING REACTION. Do price raises help under strain and
    price cuts hurt, uniformly? This is a claim about REACTING TO SHIFTS AT ALL, not
    about the formula. Admissible comparison: no_pricing vs naive_reactive.
V16 CONFLATES THEM: it reports CLAIM B's number (+$10,142/period, no_pricing vs
naive_reactive) as the evidence for CLAIM A ("whether the formula gives useful
guidance"). Measured from the raw records, in that SAME environment
(level_shift_up_persistent): Claim B = +10141.86 (se 630.19, 16.1 sigma, RESOLVED);
Claim A = +13.01 (se 21.52, 0.6 sigma, UNRESOLVED) - 0.13% of the number it is
credited with. Across all five level-shift environments Claim A has exactly ONE
resolved win: low_phi_shift_down, +137.20 (se 31.41, 4.4 sigma). E8 THEREFORE
REPORTS BOTH CLAIMS, SEPARATELY AND NEVER SUBSTITUTED FOR ONE ANOTHER. This is not
a re-framing of the source's result; it is the source's own comparator set, used as
its own code says it should be.

CLASSIFICATION (v1.9.7), revised to the two-claim structure. E8 is a BLEND of:
  (a) HYPOTHESIS TEST - CLAIM A, the formula's value: phi_gated_* vs naive_reactive.
      Genuine null (the gate adds nothing), real fail condition. Arms are distinct
      (2026-07-16b), so the comparison has dynamic range. Report form: VERDICT per
      environment IF severity clears at the chosen n; otherwise the honest report is
      an ESTIMATE with its uncertainty, and an unresolved cell is reported
      UNRESOLVED - never as a null, and never as "the formula works."
  (b) HYPOTHESIS TEST - CLAIM B, the asymmetry of pricing reaction: no_pricing vs
      naive_reactive, against the frozen assert/partial/drop rule above. Severity is
      NOT in doubt: all five environments resolve at 13-21 sigma in the source's own
      50-seed data.
  (c) ROBUSTNESS / SENSITIVITY - the capacity leg (1.3x vs 1.8x/2.4x/3.0x, whose
      output files are also on disk) and the elasticity leg (0.5/1.5/3.0). Qualifies
      (a) and (b); NO standalone verdict.
There is no calibration leg: with the construction recovered and vendored,
comparison to the source's numbers is a regression assertion, not evidence (the E7
lesson).

SEVERITY AND SAMPLE SIZE - to be settled on MEASURED cost before any run, per the
14f precedent. From the source's own 50-seed standard errors, the seeds needed to
resolve CLAIM A at 95% per environment: level_shift_down_persistent ~115;
mid_phi_shift_down ~195; level_shift_up_persistent ~525 (its effect is +13.01, so
resolving it requires se < 6.64). low_phi_shift_down (4.4 sigma) and low_phi_shift_up
(2.3 sigma) already resolve at 50. NOTE WHAT RESOLUTION BUYS HERE, AND WHAT IT DOES
NOT: whether level_shift_up_persistent resolves at +13.01 +/- 5 or stays
"unresolved," BOTH support the same conclusion - the formula's contribution in the
paper's headline environment is negligible. Resolution converts "not distinguishable
from zero" into "pinned at 0.13% of the headline," which is a stronger and more
honest statement, but it does not change the direction of the finding. The runtime
must be measured before the seed count is fixed: the source's own record reports
1,800 trials in 82.9 minutes across 12 fleet workers (~16 hours single-machine at 50
seeds), which would make a 525-seed full grid infeasible on one machine. The scope
question (five level-shift environments, or all nine including the controls) is
settled by the operator: FIVE.

NEXT (E8, in order): (1) vendor the pricing module set, MD5-recorded; (2) measure
throughput on the vendored engine; (3) fix the seed count on that measurement as a
dated amendment, with the self-penalizing check recorded; (4) build the runner +
suite (vendor integrity, the two-claim comparison logic, resolution logic, JSON
boundary); (5) container QA; (6) freeze; (7) Stage 1; (8) Stage 2; (9)
stop-and-review.

**AMENDMENT 2026-07-16d (VENDORED SET RECORDED; author-ratified). The E8 pricing closure is vendored into analysis/vendor/ - 12 modules, resolved by AST walk rather than by guesswork, copied byte-exact and never retyped.**

HOW THE SET WAS DETERMINED. The closure was resolved MECHANICALLY, not by reading import lines and hoping: a throwaway script walked the AST of phase2_7_validation_runner.py, followed every local import transitively, and copied what it found. This matters because the direct imports alone (eight) are NOT the closure - phase2_6_sterman_policy and phase2_3_stage2_demand arrive only through second-order imports and would have been missed by inspection. Non-local imports, correctly NOT vendored: argparse, collections, concurrent, copy, dataclasses, json, numpy, stockpyl, time, traceback, typing.

VENDORED SET - analysis/vendor/, 13 unique modules (E8's 12 plus E7's chain_length_sweep). MD5s asserted by each experiment's suite; any drift is a hard fail, because the CIC cleared THESE bytes:
  phase2_3_stage1_network.py             28408 B  9a59f2e2e432f967d73ecf2296e157c2
  phase2_3_stage2_demand.py              20829 B  605e9fb9ec40c62b8eabc2d497f9ed07
  phase2_3_stage3_policy_comparison.py   36310 B  508f080332ba3fe42559f0454fce5e25
  phase2_6_chain_length_sweep.py         (E7)     cbc6bfa327150ca4e64acf2b63df0172
  phase2_6_policy_scenarios.py           26198 B  ee52c2923aa97f190b13914c1461b4ff
  phase2_6_serial_network.py              9813 B  2eedff408e63d620045525f9667a9d1c
  phase2_6_spectral_radius.py            34026 B  e530ae06c57a15a6680419cbe245ec30
  phase2_6_sterman_policy.py             30000 B  98a2a10eaad392647d2cb861914c9fa4
  phase2_6_timevarying_demand.py         35351 B  e681e0c451457335ae66663b2a8b0e09
  phase2_7_demand_response.py            15721 B  013540f272d0574cf5bf7c489ade4593
  phase2_7_pricing_manager.py            27035 B  52945aeab2a55e452689d07cb436ed88
  phase2_7_pricing_policies.py           36802 B  b7a108875f3c257c99cc1508bd806f0f
  phase2_7_validation_runner.py          39231 B  2b3fc842139e33d9fab5952930477883

A CROSS-CHECK THAT FELL OUT FOR FREE. E7 and E8 share two modules - phase2_6_spectral_radius.py and phase2_6_timevarying_demand.py - and the E8 closure resolved them to MD5s IDENTICAL to E7's independently-vendored copies (e530ae06... and e681e0c4...). Two vendorings, performed at different times from the same source tree by different routes, agree byte-for-byte. That is independent confirmation that neither copy drifted.

CONSOLIDATED INTO ONE DIRECTORY, and why. The closure was first written to a separate analysis/vendor_e8/, which duplicated those two shared modules across two trees. That is precisely the file-soup the Standard forbids ("one current version per script ... never analysis_v2_FINAL.py file-soup") and precisely the drift hazard the MD5 assertions exist to catch: two copies of spectral_radius.py can diverge silently and then nobody knows which one ran. Everything was merged into analysis/vendor/ and the duplicate tree deleted. E7's suite was RE-RUN on the merged directory and is still ALL PASS (6 legs), with LEG 1 confirming its three hashes untouched - the consolidation disturbed nothing. E7's suite asserts only its own three filenames, so the additional modules alongside them are ignored by it; E8's suite will assert its own twelve.

NOTE ON phase2_6_sterman_policy.py. It enters the closure through phase2_6_policy_scenarios and is the chaotic-ordering baseline the SOURCE's own large percentages (88-95% cost reductions vs all_sterman) are measured against. It is vendored because the closure requires it to import; whether E8 USES it is a separate question the operator's scope does not currently include, and it is not to be smuggled into E8's comparison set without a dated amendment. Recorded because DISC-06 already found E4 carrying an "ERP-style baseline" that was never built: the Sterman comparator EXISTS here, and that fact should not be lost.

NEXT: measure throughput on the vendored engine, then fix the seed count on that measurement as a dated amendment before any build.

**AMENDMENT 2026-07-16e (PRE-BUILD; NO RE-RUN; author-ratified; Standard v1.9.9). E8 is an ANALYSIS of the source's committed artifacts, not a re-execution. The seed-count question is dissolved rather than answered: the finding is a BOUND, and their 50-seed data already carries it.**

THROUGHPUT, MEASURED on the author's machine against the vendored engine (not the container - E7 established the container is the wrong yardstick, having projected 8.5h for a run that took 11.6h): 19.04 s per trial. Projected for the operator's scope of five level-shift environments x four scenarios: 50 seeds = 5.3h; 115 = 12.2h; 195 = 20.6h; 250 = 26.5h; 526 = 55.5h. This is consistent with the source's own record - 1,800 trials in 82.9 minutes across a 12-worker fleet, i.e. roughly 16h single-machine at 50 seeds - and is why they used a fleet.

WHY NO RE-RUN. Taken claim by claim, a re-execution buys nothing that the source's own verified artifact does not already provide.
  CLAIM B (the asymmetry of pricing reaction; no_pricing vs naive_reactive) is ALREADY SETTLED in their 50-seed data: all five environments resolve at 13-21 sigma, and CIC-1 confirms every published figure recomputes from the 1,800 raw records. More seeds add nothing to a 16-sigma result.
  CLAIM A (the formula's value; phi_gated vs naive_reactive) was the only reason to run - and the reasoning that motivated a run was MINE AND IT WAS WRONG. I framed it as a VERDICT question ("is the formula's contribution non-zero?"), which is the exact error Standard v1.9.7 exists to catch: forcing an estimation question through a pass/fail gate. Powering to detect +13.01 is also CIRCULAR - +13.01 is itself a 0.60-sigma reading, an estimate we do not trust, so powering to it ASSUMES IT IS REAL; if the true effect is zero, no sample size ever resolves it and 55 hours would purchase the word "unresolved."

THE FINDING IS A BOUND, AND THEIR 50 SEEDS ALREADY CARRY IT. The honest report form for Claim A is an ESTIMATE WITH UNCERTAINTY, and the estimate is decisive as it stands. Claim A's 95% CI per environment, computed from the 1,800 raw records, against each environment's own Claim B headline:
  level_shift_up_persistent    [ -29.17,  +55.19]  =  [-0.29%,  +0.54%] of +10141.86
  low_phi_shift_up             [  +2.86,  +35.98]  =  [+0.17%,  +2.18%] of  +1646.78
  level_shift_down_persistent  [ -60.89,  +12.33]  =  [-2.63%,  +0.53%] of  -2315.25
  low_phi_shift_down           [ +75.64, +198.76]  =  [+13.01%, +34.19%] of -581.36
  mid_phi_shift_down           [ -72.67,  +23.57]  =  [-5.87%,  +1.90%] of -1238.29
IN THE ENVIRONMENT CARRYING THE PAPER'S HEADLINE, THE FORMULA CANNOT BE CONTRIBUTING MORE THAN 0.54% OF WHAT IT IS CREDITED WITH, at 95% confidence, from the source's own data. That is not "we could not tell" - it is a hard ceiling, and it is resolved. The bound is also indifferent to the circularity above: it does not care whether the true effect is 0 or +13; it says the effect is under 0.54% either way. Conversely low_phi_shift_down is a GENUINE, RESOLVED WIN whose lower bound is well clear of zero - the formula's one real success, worth 13-34% of that environment's total, and absent from the paper's framing.

A 60-SEED RUN WAS CONSIDERED AND REJECTED ON ARITHMETIC. SE scales as sqrt(50/60) = 0.913, a 9% reduction; no cell changes status (0.60 -> 0.66 sigma; 1.30 -> 1.42; 1.00 -> 1.10). Six hours for an identical answer. Recorded because the proposal was reasonable and the refusal must be auditable.

WHAT E8 THEREFORE IS. Not a re-execution. An ANALYSIS, resting on verification already earned: (i) the source's pricing code is CORRECT - all seven CIC classes clear (2026-07-16c); (ii) its artifact is authentic and its published figures recompute from it exactly (CIC-1); (iii) the vendored closure is MD5-asserted (2026-07-16d) so the audited bytes are the bytes on record. Our contribution is the ANALYSIS: computing both claims separately from the raw records, with bounds, and reporting them without substitution.

CONSEQUENCE - E8 NOW HAS EXTERNAL INPUTS, AND THIS SECTION'S "Inputs: none external" IS FALSE. The source's committed artifacts become E8's DATA. Per the Standard's contract they must be hashed and recorded in SOURCES.md, and per the repo rule raw data is never committed - the artifacts are copied to the project-local store with their SHA256 recorded. The inputs are:
  C:\ResearchShare\phase27_validation_50seed\aggregated_phase27_validation_50seed.json  (1,800 raw trials; the primary)
  C:\ResearchShare\phase27_capsweep_18x\aggregated_phase27_capsweep_18x.json            (robustness: capacity)
  C:\ResearchShare\phase27_capsweep_24x\aggregated_phase27_capsweep_24x.json
  C:\ResearchShare\phase27_capsweep_30x\aggregated_phase27_capsweep_30x.json
  C:\ResearchShare\phase27_elasticity_05\aggregated_phase27_elasticity_05.json          (robustness: elasticity)
  C:\ResearchShare\phase27_elasticity_30\aggregated_phase27_elasticity_30.json
The vendored modules remain committed and MD5-asserted: they are what the CIC cleared and what produced these artifacts, so they are part of the evidence chain even though E8 does not execute them.

REPORT FORMS, revised (supersedes 16c's classification on Claim A only):
  CLAIM A - the formula's value: ESTIMATE WITH UNCERTAINTY per environment, reported
    as a CI in absolute terms AND as a percentage of that environment's Claim B
    headline. NOT a verdict: the question is "how large is it," and the answer is a
    bound. Where the CI excludes zero (low_phi_shift_down, low_phi_shift_up) that is
    reported as a resolved positive with its magnitude; where it includes zero, the
    BOUND is the finding, never "the formula works" and never "the formula does
    nothing."
  CLAIM B - the asymmetry of pricing reaction: VERDICT against the frozen
    assert/partial/drop rule. Severity is not in doubt at 13-21 sigma.
  ROBUSTNESS - the capacity and elasticity legs, from their own artifacts. Stability
    statement; no standalone verdict.

NEXT (E8): (1) copy the six artifacts to the project-local store and record their SHA256 in SOURCES.md; (2) build the analysis script + suite (input-hash assertion, the two-claim separation, the bound arithmetic, resolution logic, JSON boundary); (3) container QA; (4) freeze; (5) Stage 1; (6) run the analysis; (7) stop-and-review.

**Inputs:** none external.

## 12. E9 - Customer-hysteresis sensitivity sweep

**Purpose:** attack E8's raise-prices finding with its most obvious objection: permanent customer loss.

**Operator (frozen; source calibration).** Customer-pool variable decaying multiplicatively when price > reference, constant otherwise; hysteresis intensities {0.0, 0.10, 0.30, 0.60}; the two upward-shift environments at 1.3x capacity; 20 seeds per cell; 320 trials. Outputs: pricing benefit per cell; end-of-run customer pool fraction.

**Decision rule.** The E8 raise-claim is retained WITH the split framing only if the benefit remains positive at hysteresis 0.60 in the high-persistence strained environment; the noisy-environment fragility is reported as found. If the benefit goes negative at moderate hysteresis (0.30) even in the strained sticky environment, E8's raise-claim is downgraded to fragile everywhere and the practical guidance is withdrawn. The cuts-are-bad finding is unaffected by construction (hysteresis does not engage at/below reference) - stated, not tested here.

**Validity review.** Referent: hysteresis-as-attrition is the standard first-order model of the objection. 20 seeds/cell is smaller than E8's 50 - pre-registered consequence: cell means carry wider CIs; any cell mean within 1 SE of zero is reported as indeterminate rather than signed.

**AMENDMENT 2026-07-16 (PRE-BUILD classification gate + build strategy; author-ratified Option B; Standard v1.9.9. Made before any E9 code exists.)**

TRIANGLE TEST - PASSED (the Section-5.4 test, run FIRST). The source's hysteresis
experiment survives the check that Section 5.4 failed: script on disk
(phase2_7_hysteresis.py MD5 14a9de160c5ce159ec5d331a283f7df7;
phase2_7_pricing_manager_hyst.py 41550517a42a244f83ff529624c98bd6;
phase2_7_hysteresis_sweep_runner.py 5118bdee175ae7e69e5005f7bd652ed1;
dispatch wrapper phase2_7_pricing_manager_wrapper.py 0640558e1adcd4263b4191131a8de3d7)
-> committed artifact (phase2_7_hysteresis_results.json, MD5
765364e7120c3d59a84a5e7925fdf00f, SHA256
e5875b0fac7f35e1b9ccc4b956c8f99f28355a5fa6787df6dd2624368202ef3b, 320 trials,
0 failures, seeds 2000-2019) -> Appendix F: ALL FOUR published numbers recompute
EXACTLY (+8401.30 baseline; +5855.08 heavy, retention 69.7% ~ "70%"; -540.58
moderate-noisy; -3320.45 heavy-noisy). Post-correction era (2026-05-01); none of
Section 5.4's anatomy is present.

CLASSIFICATION (v1.9.7). E9 is a BLEND of (a) ROBUSTNESS / SENSITIVITY
(dominant) - it QUALIFIES E8's ASSERTED Claim-B raise verdict; the frozen
retain/downgrade rule above executes as a QUALIFICATION of E8's claim retention,
not a standalone verdict - and (b) BOUNDARY-CONDITION / DOMAIN-MAPPING - where
along the hysteresis axis the pricing benefit crosses from benefit to harm, per
environment; report form a MAP with its resolution. DISC-03 GATE COMPLIANCE: the
measured benefit is phi_gated_asymmetric vs no_pricing - the CLAIM-B FAMILY (the
value of the raise strategy), matching the claim E9 qualifies. NOTHING in E9 may
be attributed to the persistence formula; the naive arm is absent by design.

SEVERITY - MEASURED PRE-BUILD from the source's own artifact, and it CLEARS.
Per-cell paired benefit (mean, SE, sigma) at 20 seeds:
  level_shift_up_persistent  h=0.0 +8401.30 (813.42, 10.3) / h=0.1 +8628.03
  (841.83, 10.2) / h=0.3 +7808.21 (901.97, 8.7) / h=0.6 +5855.08 (947.88, 6.2)
  low_phi_shift_up           h=0.0 +1407.26 (178.40, 7.9) / h=0.1 +496.37
  (213.89, 2.3) / h=0.3 -540.58 (222.09, -2.4) / h=0.6 -3320.45 (274.28, -12.1)
EVERY decision-rule cell resolves at 20 seeds: the retention condition (hp at
0.60) at 6.2 sigma; the downgrade trigger (hp at 0.30) at 8.7 sigma - so the
rule could have fired in EITHER direction; both noisy-env crossings resolve.
INSTRUMENT ENGAGEMENT verified: pools decay (0.772 / 0.663 / 0.452 across
intensities) while the baseline arm is provably INERT (every no_pricing trial
ends with pool exactly 1.0 and zero price changes - the h-axis cannot
contaminate the comparator). Note for the record: at h=0.1 in hp the benefit
point estimate EXCEEDS h=0 (+8628 vs +8401) - within noise, reported as found.
CIC spot-checks on the new surface: CIC-2 clears at the runner (cost
range(52,260)/208 and revenue [52:]/208 - same window, same divisor, verified in
code AND arithmetically in the artifact); CIC-4's call-site pattern matches the
cleared base manager (history 0..t, price governs t+1); rand_seed=42 is the
known-inert deterministic-list pattern. OBSERVATION, recorded: the policy
observes POST-HYSTERESIS demand (its own past prices erode the signal it
estimates from) - realistic feedback, identical in kind to the base manager's
post-elasticity feed; a property, not a defect.

CONSTRUCTION - FROZEN FROM THE SOURCE'S CODE, not from prose:
  architecture   4-stage serial, summed_at_retailer, all_sr, capacity 1.3x
  horizon        260 periods, 52 warmup -> 208 measured; SAME window and divisor
                 for cost and revenue
  pricing        elasticity 1.5, reference price 1.0, review interval 20,
                 initial price 1.0; scenarios no_pricing and
                 phi_gated_asymmetric only
  environments   level_shift_up_persistent (AR(1) phi=0.85, +20% level shift at
                 t=130, persistent) and low_phi_shift_up (phi=0.30, same shift)
                 - dicts frozen verbatim from get_sweep_environments()
  hysteresis     pool(0)=1.0; each period, updated from the CURRENT price before
                 demand realizes: if price/ref <= 1 pool unchanged; else
                 pool *= max(0, 1 - h*(price/ref - 1)), then floored at 0.10;
                 ONE-DIRECTIONAL (never regrows); realized demand per SKU =
                 baseline * (price/ref)^(-elasticity) * pool; the policy's
                 demand history is the post-hysteresis aggregate
  intensities    {0.0, 0.10, 0.30, 0.60}
  seeds          2000-2019 (20 per cell - THE SOURCE'S OWN, so the fidelity
                 cross-check and the result are one run), 320 trials

BUILD STRATEGY (Option B, ratified - the "ours where new, verified where
inherited" pattern). The hysteresis layer is OURS, WRITTEN FROM SPECIFICATION
(this operator + the mathematical structure stated in the source module's
documentation), NEVER copied or transcribed from the source's code body. It
drives the ALREADY-CIC-CLEARED vendored pricing closure (amendment 2026-07-16c/d
under E8) through the vendored functions: build_phase2_6_serial_network,
apply_capacity_constraints, generate_summed_baseline_streams,
get_transition_period_for_environment, assign_realized_streams_to_retailer,
apply_scenario_multiproduct, extract_chain_costs, make_pricing_policy, and
stockpyl.simulation. The source's hysteresis module/wrapper/runner are NOT
vendored: their role is replaced by our spec-derived implementation, and their
artifact becomes the cross-check target. HONESTY LIMITS, recorded so the
manuscript cannot drift: the re-implementation is AUTHORSHIP-INDEPENDENT but NOT
BLIND - the source's code was read during this gate's verification, as the
Standard requires; E9 MAY claim "the hysteresis layer was re-implemented from
its specification and reproduces the source's committed artifact"; it MAY NOT
claim blind replication.

PARITY AT h=0 IS PROVED, NOT ARGUED. The source guaranteed intensity-0 parity by
DISPATCHING to the original manager; we replace that argument with a proof: the
suite asserts OUR walk at h=0 is BIT-IDENTICAL (realized streams, price history,
revenue) to the vendored elasticity-only apply_pricing_to_retailer_streams on
planted streams that force price changes. At pool = 1.0 the arithmetic reduces
exactly (x * 1.0 is IEEE-exact), so bit-identity is the correct bar.

FIDELITY CRITERION (pre-registered BEFORE the run). Our 320 trials at the
source's seeds are compared to the registered artifact per (env, scenario,
intensity, seed) on net value (mean_revenue_per_period - cost_per_period):
  TIER-EXACT : max relative difference <= 1e-9 across all 320 trials
               -> bit-faithful re-implementation.
  TIER-CLOSE : every (env, intensity) cell's paired-benefit mean within
               0.1 x that cell's SE of the artifact's
               -> mathematically faithful; float-order noise only.
  Anything worse -> FIDELITY FAIL: our build is defective, the line STOPS, the
  discrepancy is dossiered, and the result is NEVER evidence about the source.
The SAME RUN carries the E9 result: at 20 seeds every decision cell resolves in
the source's data, so no separate higher-n execution is required. If OUR run
leaves any decision-rule cell unresolved, the seed count is revisited ONLY by a
dated amendment on measured cost (the 14f pattern).

REPORT FORM (replaces nothing; instantiates the rule above): (a) the frozen
retain/downgrade rule executes against OUR cells, with the pre-registered
indeterminate rule (|mean| <= 1 SE) honored; (b) the crossover map along h per
environment with its resolution; (c) end-of-run customer-pool fraction per cell.
ALL cells reported regardless of direction.

INPUTS CORRECTION: this section's "Inputs: none external" is SUPERSEDED - the
source's hysteresis artifact becomes a registered local input (pull.py
kind="local", id phase27_hysteresis_20seed, SHA256
e5875b0fac7f35e1b9ccc4b956c8f99f28355a5fa6787df6dd2624368202ef3b) as the
FIDELITY TARGET, not as evidence. Copy-to-store and SOURCES.md regeneration are
part of this amendment's execution.

**Inputs:** none external.

## 13. E10 - Sovereign ratings extension (suggestive), E11 - UI extension (suggestive), E12 - non-stationarity limitation

**E10 operator.** JST Macrohistory R6, 18 countries, 1870-2020; debt/GDP persistence per country by OLS on linearly detrended series (raw-levels variant reported); rho per country under SPEC-S calm (W = 5y, bg = 0.05); crisis sweep bg in {0.05, 0.10, 0.25, 0.50, 1.00, 1.50}. **Decision rule.** The conditional-instability reading is OFFERED (suggestive framing locked) only if: all 18 countries rho < 1 at calm bg AND the count crossing 1.0 rises monotonically with bg AND cross-country rho ranking tracks persistence. Any failure -> the sovereign section reports what was found and withdraws the Greek-crisis suggestion. GROUND-UP RE-VERIFICATION mandatory: this analysis contained the source project's v14 fatal error (impossible rho values), fixed at v15 - the rebuild recomputes from scratch and cross-checks against an independent implementation before any value is ledgered.

**E11 operator.** DOL ETA 539 weekly claims, 53 jurisdictions, 1986-2026; insured unemployment rate persistence, quarterly aggregation; rho under SPEC-U at bg grid {0.05, 0.10, 0.25}; normal-period vs GFC-period (2008-2009) persistence. **Decision rule.** The procyclical-feedback reading is OFFERED only if normal-period rho < 1 at all tested bg AND GFC-period persistence crosses the boundary at bg > 0.05. Otherwise reported and withdrawn. Framing locked at suggestive (one reading of the formula's dynamics, not a welfare claim; Fath-Fuest counterpoint cited).

**E12 operator (pre-registered limitation documentation).** Within the E7 environment: oracle variant handed true phi each period vs OLS-estimated variant vs fixed-alpha damping vs no-formula baseline, under non-stationary persistence trajectory phi: 0.30 -> 0.95 -> 0.40; 50 seeds. **Decision rule.** This experiment CANNOT support the thesis; it documents a limitation. Expected (per source): fixed-alpha outperforms both oracle and OLS variants, establishing the recipe-level (not estimator-level) nature of the limitation. If instead the oracle variant WINS, the limitation section is rewritten as resolved (good news requiring explanation) - a dated amendment records either way. Only the one tested trajectory shape is claimed; the untested shapes (drift, square-wave, one-shot) are named as future work.

**Validity reviews.** E10/E11: bg values are assumption-driven proxies, not estimates - exactly why the decision rules lock SUGGESTIVE framing and the paper says so; the experiments test internal coherence of the reading, not causal claims. E12: the oracle design isolates recipe-vs-estimator attribution by construction (perfect information removes the estimator from the causal path).

**AMENDMENT 2026-07-17c (E11 PRE-BUILD classification gate; Standard v1.9.9).** CLASSIFICATION: characterization, suggestive tier locked. INPUT: eta539_ar539.csv (store MD5 8f5cd02610f88a147d20c8173429d787), IUR = column c19, quarterly mean per jurisdiction from rptdate. SEVERITY (T1-verified theory library, pre-build, suite-committed): across SPEC-U's grid (W in {12,16,20} quarters for the stated 3-5y range; bg in {0.05,0.10,0.25}) a boundary crossing is possible ONLY at W=20 x bg=0.25 with phi > 0.997992; everywhere else sup rho over stationary phi is 0.911-0.990 - so condition (1) reduces to stationarity + the W=20 corner, and condition (2) is live only at that corner or via an explosive estimate. GFC window = 8 quarters, so per-state AR(1) is meaningless (n~8); ESTIMATOR frozen: pooled within-jurisdiction-demeaned AR(1) on consecutive-quarter pairs across all jurisdictions, identically for normal (all quarters outside 2008Q1-2009Q4) and GFC (2008Q1-2009Q4) windows; per-jurisdiction normal-period table reported for LB-E11-normal (n~150 quarters each). REDUCED RULE frozen: OFFER iff pooled normal phi-hat < 1 with rho < 1 at every tested (W,bg) AND pooled GFC phi-hat >= 0.997992 (evaluated at the W=20 x 0.25 corner; >= 1 reported as explosive and satisfies a fortiori); otherwise report and WITHDRAW per the operator. Dual-implementation rho guards carried over from E10 (same functions, <= 1e-12, abort-before-ledger). W=16 primary for the normal-period table; 12/20 reported.

**AMENDMENT 2026-07-17b (E10 PRE-BUILD classification gate; Standard v1.9.9; the mandated ground-up re-verification).**

CLASSIFICATION (v1.9.7): E10 is a CHARACTERIZATION at the SUGGESTIVE tier (locked above) - a country-level phi/rho map with crossing counts; no thesis verdict either way. INPUT: JSTdatasetR6.dta from the registered pull (store copy MD5 5614589349612f4c79f5b73e11b3732d, pinned; Stage 1 re-verifies on the author machine), column debtgdp, 18 countries, coverage 1870-2020 (min n=99 Ireland, max 151; war gaps present).

SEVERITY, measured pre-build with the T1-verified theory library - THE PRE-REGISTERED RULE IS NEARLY VACUOUS AND THE GATE SAYS SO. Probes (committed in the suite): (a) rho is strictly increasing in phi at fixed (W=5, bg=0.05), so condition (3) 'ranking tracks persistence' is TRUE BY CONSTRUCTION (Spearman = 1 mathematically) - reported, zero evidential weight (the E5/E6 lesson applied pre-build). (b) For bg in {0.05, 0.10, 0.25, 0.50} NO stationary phi < 1 reaches rho = 1 (sup rho = 0.944/0.863/0.804/0.900), so condition (1) 'all 18 rho < 1 at calm' reduces exactly to 'all 18 estimated phi < 1' - A STATIONARITY TEST, real but narrow (debt/GDP is near-unit-root; an explosive OLS estimate is genuinely possible). (c) Crossings exist only at bg = 1.00 (phi* = 0.967084) and bg = 1.50 (phi* = 0.691462); since phi*(1.5) < phi*(1.0), the crossing count is WEAKLY MONOTONE BY CONSTRUCTION - condition (2)'s only live content is 'at least one country with phi-hat > 0.691462' (the strictly-rises-somewhere clause). REDUCED RULE, frozen: OFFER the suggestive reading iff (i) all 18 detrended phi-hat < 1 AND (ii) counts weakly increase along the grid and strictly increase somewhere; otherwise report and withdraw the Greek-crisis suggestion. The manuscript must present the by-construction structure alongside any offered reading.

ESTIMATION SPEC, frozen: per country, debtgdp over available years; PRIMARY = linear detrend (OLS on year) over non-missing obs, then AR(1) phi-hat by with-intercept OLS on residual pairs using ONLY consecutive-year pairs (war gaps break pairs, never bridged); RAW-LEVELS variant identically on the undetrended series, reported alongside, rule adjudicated on the primary. n_pairs reported per country.

GROUND-UP DUAL IMPLEMENTATION (the v14 mandate; fatal error = impossible rho values): every rho is computed twice - theory_lib.rho (as-proven, T1-verified) and an INDEPENDENT from-scratch companion-matrix eigenvalue implementation written in e10_sovereign.py without reference to theory_lib's construction - with agreement required <= 1e-12 over the full 18-country x 6-point grid, plus invariant rho(phi, W, 0) = |phi| to 1e-9, plus impossibility guards (every rho finite and > 0). Any guard failure aborts the run before any value is ledgered.

**AMENDMENT 2026-07-17 (E12 PRE-ANALYSIS classification gate; Standard v1.9.9. E12 is an ANALYSIS - zero new simulation.)**

EVIDENCE PATHS, both already in hand. LEG A (primary, 250 seeds): OUR OWN committed
E7 rebuild artifact analysis/outputs/e7_chain_sweep.json (MD5
fdb79fd32566d4129226eea422c356cb, pinned) - the rebuild ran ALL FIVE variants
(36 cells x 250 seeds x 5 = 45,000 trials; harness regression-verified 3/3
exact on the source's own seeds at E7), and every cell carries the three-variant
diagnostic (sr_paper9_ols / sr_oracle_local / sr_naive_damp, each paired
within-seed against sr_disabled, with CI, achieved MDD, and resolution). LEG B
(corroboration + paired contrasts, 50 seeds): the source's raw sweep artifact
C:\ResearchShare\aggregated_chain_length_sweep.json (MD5
6ecfc6fec0b1e490febea64ef36cd058 - matching the E7/DISC-05 record exactly -
SHA256 ea95218b2193b5ad0f174d380c13da358a9b365044cf2668fa243b34b0539e49; 9,000
per-trial records; code CIC-cleared at E7). LEG A's aggregates cannot yield
variant-vs-variant standard errors (per-seed values were not persisted); LEG B's
raw records yield PROPERLY PAIRED per-seed contrasts (oracle-OLS, fixed-oracle,
fixed-OLS, scaled by the same seed's baseline cost) with real SEs at the
source's n. A re-run to persist our own per-seed values is strictly dominated
(the ordering claims resolve conservatively from LEG A via CI disjointness, and
LEG B supplies the paired inference) and is REJECTED.

RECORD CORRECTION, logged here rather than dossiered because it consumes no
number: amendment 2026-07-14 (14d) described the source's 9,000-trial
decomposition as "base-stock, sr_paper9_ols, sr_oracle, sr_naive_damp,
all_sterman." The artifact's ground truth is sr_disabled / sr_paper9_ols /
sr_oracle_local / sr_naive_damp / SR_NUMERICAL (1,800 each) - the fifth variant
is the source's deliberately preserved PRE-CORRECTION rule, not a Sterman arm.
No E7 or E12 quantity touches the fifth variant; E12's LEG B will report
sr_numerical vs sr_disabled in the drift row as CONTEXT ONLY (clearly labeled
non-claim-carrying - the repudiated rule's actual performance, of interest to
the Phase-5a review of the Section 5.4 finding).

CLASSIFICATION (v1.9.7). E12 is a CHARACTERIZATION - pre-registered LIMITATION
DOCUMENTATION with attribution-by-construction (the operator above already
states it CANNOT support the thesis). Report form: the three-variant map over
the drift_canonical row (claim-carrying) with the three stationary rows as
CONTROLS, plus the frozen expected/unexpected rule governing how the limitation
section is framed. The DISC-03 lesson generalizes: every contrast is named by
its two arms; no contrast is attributed to anything its arms do not isolate.

SEVERITY - measured from data in hand, and DISCLOSED: LEG A's aggregates were
publicly committed at the E7 close (they are already part of the record), so
the rule below is the operator's own wording made precise, not tuned to unseen
data; LEG B's paired contrasts remain uncomputed at this gate. From LEG A: the
oracle-vs-baseline question resolves in ALL NINE drift cells; the fixed-alpha
benefit question resolves at the long-chain headroom cells; the instrument can
find the ordering in either direction (fixed is resolved-benefit in some cells
and oracle resolved-harm in all - had the reverse held, the same map would show
it). Achieved MDDs are carried per cell in the artifact.

DECISION RULE, formalized from the operator (frozen before the analysis run):
claim locus = drift_canonical at long chains with headroom (L in {6,8} x cap in
{1.8, 2.4}), where the source's record claims "fixed-alpha damping produces
large benefit at long chains."
  EXPECTED-CONFIRMED (limitation documented as RECIPE-LEVEL) iff (i) oracle vs
  baseline is resolved-HARM in all 9 drift cells, AND (ii) at the L=8 headroom
  cells fixed vs baseline is resolved-BENEFIT with its 95% CI disjoint-below
  BOTH the oracle's and the OLS's CIs (conservative ordering from LEG A), AND
  (iii) LEG B's properly-paired fixed-oracle and fixed-OLS contrasts resolve
  negative at those cells.
  ORACLE-WINS (limitation rewritten as RESOLVED, dated amendment) iff oracle vs
  baseline is resolved-BENEFIT with CI disjoint-below both other variants at
  the claim locus.
  Otherwise AS-FOUND characterization, all cells reported.
Only the tested trajectory shape (0.30 -> 0.95 -> 0.40) is claimed; drift,
square-wave, and one-shot shapes remain named future work per the operator.

N NOTE: the operator pre-registered 50 seeds; LEG A carries 250 (the E7 rebuild
supersession - a power upgrade, not a spec change; the operator's 50 survives
as LEG B's n by construction).

INPUTS CORRECTION: E12's "none external" is SUPERSEDED - the source's sweep
artifact becomes a registered local input (pull.py kind="local", id
phase26_chain_sweep_50seed) as LEG B's corroboration data. Copy-to-store and
SOURCES.md regeneration are part of this amendment's execution. LEG A's input
is our own committed artifact, pinned by MD5 above.

**Inputs:** E10 - JST R6. E11 - ETA 539 (+ context series). E12 - none external.

---

## 14. Data manifest (Phase 2 pulls and hashes against exactly this list)

All FRED series monthly, seasonally adjusted, January 1992 to latest available, unless noted. CAUTION (carried from Phase 0): the shared folder C:\Users\jaek9\Documents\LaggingTruth\Data holds multiple versions/variants of several datasets; Phase 2 pulls fresh from the primary sources below (or verifies any local file byte-for-byte against a fresh pull) before hashing into data/SOURCES.md - no local variant is trusted by filename.

**Panel (E1, E2, E3, E5, E6 rho input) - 17 sector I/S series + aggregates:**
- Manufacturing I/S (M3 via FRED): AMTMIS (total mfg), A34SIS, A36SIS, A35SIS, A25SIS, AMDMIS (durables), AMNMIS (nondurables); aerospace ratio constructed from ANAPTI / ANAPVS.
- Wholesale I/S (MWTS via FRED): R4231IM163SCEN through R4239IM163SCEN (motor vehicles ... misc durables), R423IRM163SCEN (durable total).
- Retail I/S (MRTS via FRED): MRTSIR452USS (general merchandise), MRTSIR441USS (motor vehicle dealers), MRTSIR444USS (building materials).
- Aggregates/context: ISRATIO, MNFCTRIRSA; activity context AMTMNO, AMTMVS, AMTMTI, DGORDER, ANDENO.
- The exact 17-sector membership is frozen from these series in the analysis config committed with pull.py; the mapping table is written into data/SOURCES.md at Phase 2 and never edited after first hash.

**AMENDMENT 2026-07-13 (pre-pull, pre-freeze; author-ratified option B).** Data-layer verification against fresh FRED pulls found a source defect: the source's appendix and this manifest list A25SIS among the manufacturing I/S panel series, but A25SIS's FRED-verified title is "Manufacturers' Inventories to Shipments Ratios: Chemical Products" - while the source's prose names "primary metals manufacturing" as the panel member (three mentions, including automotive layer L1 at phi = 0.979) and never mentions chemicals. Adjudication by trailing-60-month OLS phi on fresh pulls: A25SIS (chemicals) tracks the source's reported 0.979 (0.973 at 2020-12; 0.990 full-sample); A31SIS (FRED-verified "Primary Metals", SA) sits at 0.90-0.92 in the same windows. Conclusion: the source computed on chemicals data mislabeled as primary metals. RESOLUTION (ratified): the panel member is the source's stated INTENT - true primary metals, A31SIS - and A25SIS is pulled and hashed as an audit-trail series documenting the defect (non-member). E5's reproduction check reads against the corrected panel; the source's mislabeled row is documented as a source defect rather than reproduced. All panel statistics are re-earned by the rebuild's own experiments regardless.

**Semiconductors (E6):** CAPUTLG3344S (Fed G.17 capacity utilization, NAICS 3344), IPG3344S (industrial production).

**Sovereign (E10):** Jorda-Schularick-Taylor Macrohistory Database, Release 6 (18 countries, 1870-2020), macrohistory.net. Context-only (not load-bearing inputs): Fitch NRSRO rating history via ratingshistory.info; IMF Global Debt Database; FRED DGS10/DGS2/BAMLC0A4CBBB; BIS credit statistics - pulled only if a committed analysis uses them, else omitted from SOURCES.md.

**Unemployment insurance (E11):** DOL ETA 539 (53 jurisdictions, 1986-2026); context ETA 204, ETA 218, ETA 581, Financial Data Handbook 394; FRED UNRATE, PAYEMS, USREC, ICSA, CCSA (context).

**Firm-level illustration (companion/practical section only, non-load-bearing unless promoted by amendment):** Walmart and Target I/S from SEC EDGAR XBRL quarterly filings (40 filings, FY2020-FY2025) - used in the source as an illustration of the data floor (quarterly n insufficient); retained for that purpose only.

**Synthetic experiments (T1-T3, E4, E7, E8, E9, E12):** no external data; all seeds and configs committed.

---

## 15. Specification disclosure (anti-fishing)

Pre-registered specification counts, in full:
- Parameter specs: TWO named real-data specs (SPEC-M: W = 8, bg = 0.05; SPEC-R: W = 12, bg scale 3.0), both reported wherever both apply (E5, E6); neither is selected post hoc; E1's headline runs under SPEC-M only (single spec), with SPEC-R as a reported robustness column.
- E1: ONE outcome definition (frozen in script before first real run), ONE persistence window (60m), ONE regime window (12m), ONE forward horizon (12m), ONE significance procedure (block bootstrap, 24m blocks, 2,000 resamples, p < 0.01). No variants.
- E2/E3: ONE episode definition each (dates above). Component bake-off fixed at three comparators.
- E4: FOUR algorithms, ONE calibration (frozen above). No parameter search on the demand process.
- E7: the full 3 x 3 x 4 x 50 grid is THE experiment (9,000 runs), not a search; all cells reported.
- E8: 5 environments x 50 seeds + one capacity sensitivity; all cells reported. E9: 4 x 2 x 20 (320 trials); all cells reported.
- E10: bg sweep of six values, all reported; two detrending variants (linear detrend primary, raw levels secondary), both reported. E11: three bg values, all reported.
- T1-T3 grids as specified; grids are verification surfaces, not searches.
- Estimator: OLS only (YW comparison is a reported diagnostic, not a selectable spec).
- Any specification beyond the above requires a dated amendment to this document BEFORE the run, with the amendment test applied ("would I make this change if it pushed the result the other way?"); data-responsive changes are exploratory unless re-tested on held-out data.

---

## 16. Amendment log (append-only)

- Amendments are recorded inline in the section they amend (E1 Section 4, E5 Section 8, E6 Section 9, data manifest Section 14) and, for cross-cutting changes, as their own dated section (Section 17).

---

## 17. Experiment-type classification and report form (Standard v1.9.7; retroactive pass)

**AMENDMENT 2026-07-14 (author-ratified; Standard v1.9.7).** Standard v1.9.7 adds a mandatory pre-run classification gate: each experiment names its type, states a severity check (if the claim were false, could THIS test on THIS data tell, in the region that decides it), and takes the REPORT FORM that follows - a binary SUPPORT/REFUTE verdict ONLY for a genuine hypothesis test that passes severity; an estimate-with-uncertainty for effect-size/calibration; a characterization for descriptive/ranking/spectrum/boundary/exploratory questions. This paper's battery was designed under the prior binary regime, so E1-E6 are classified retroactively here and E7-E12 are classified before build. Classification depends on the CLAIM and the INSTRUMENT, both fixed at design time - never on the result - so this pass changes labels and report forms, and changes NO number. Every value already reported stands exactly as run.

| Exp | Primary type (v1.9.7) | Severity | Report form | Change |
|---|---|---|---|---|
| E1 | Hypothesis test (the primary falsifier) | PASS - power measured BEFORE the real run (the 2026-07-13 Rule B amendment replaced a ~0-power rule after a quantified power-curve comparison; verdict-level false-support 0% at null) | VERDICT (SUPPORT / FALSIFIED) | NONE - verdict earned |
| E2 | Blend: episode hypothesis test + mechanism/mediation (the compound-vs-components bake-off) | PASS | VERDICT + mechanism decomposition reported alongside | Formalize the blend - both forms reported |
| E3 | Boundary-condition / domain-mapping | PASS - polarity stated at design (expected null = SUCCESS) | CHARACTERIZATION (boundary map) | NONE - already recorded as CONSISTENT-WITH-BOUNDARY |
| E4 | Blend: simulation/in-silico + comparative/benchmark + model-fit/calibration | PASS for the comparison (paired, p = 0.0005); the calibration leg is estimate-vs-source | VERDICT (comparison - binds the MODEL, not the world) + ESTIMATE (magnitude vs the source's 8.7pp) | Formalize the blend - the magnitude caveat is a required report form, not a footnote |
| E5 | Descriptive / structural characterization (ranking) | First instrument FAILED (saturated key, six-way tie at the ceiling) -> INCONCLUSIVE, re-instrumented blind + pre-registered; second instrument PASSED (dynamic range confirmed) | CHARACTERIZATION (ordering + how resolved it is) | RECHARACTERIZE - the graded rule's DROPPED is reported alongside, not as the finding |
| E6 | Blend: boundary-condition + model-fit/calibration (point-prediction of the 85-90% knee) | FAILED for the crossing claim (chronically-unstable sector, no sub-boundary baseline); PASSED for the estimation leg | CHARACTERIZATION + ESTIMATE | RECHARACTERIZE - the rule's REFUTE is reported alongside, not as the finding |
| E7 | Robustness / sensitivity (chain-length sweep) | n/a - qualifies a primary result; no standalone verdict | Stability statement (robust to X, sensitive to Y) | Classify at its gate before build |
| E8 | To be classified at its gate (pricing-mechanism asymmetry - likely parameter-sweep hypothesis test) | TBD at gate | TBD at gate | Classify at its gate before build |
| E9 | To be classified at its gate (customer-hysteresis sweep - likely robustness/sensitivity) | TBD at gate | TBD at gate | Classify at its gate before build |
| E10 | To be classified at its gate (sovereign ratings extension - declared suggestive) | TBD at gate | Likely characterization (suggestive / exploratory) | Classify at its gate before build |
| E11 | To be classified at its gate (UI extension - declared suggestive) | TBD at gate | Likely characterization (suggestive / exploratory) | Classify at its gate before build |
| E12 | To be classified at its gate (non-stationarity limitation) | TBD at gate | Likely characterization (boundary / limitation) | Classify at its gate before build |

**Re-run vs recharacterize (the governing distinction, ratified 2026-07-14).** RE-RUN if and only if the INSTRUMENT was degenerate - the data carry no information (E5's first run: six sectors tied at the ceiling is a jammed ruler, not a measurement). RECHARACTERIZE if and only if the instrument was sound but the REPORT FORM was wrong (E6: the bin means are valid, informative measurements at adequate n; only the verdict layer bolted on top was invalid). Under this test the battery requires ZERO new re-runs: E5's re-run is already done (freeze 7b27abc, result 7c5737b), and E6 needs none.

**Defensibility conditions (all three mandatory, ratified 2026-07-14).** (1) Every report-form change is a DATED DESIGN amendment, never an overwrite - this section plus the Section 9 amendment. (2) The pre-registered output IS REPORTED alongside the recharacterization, never suppressed: for E5 the graded rule returned DROPPED, for E6 the rule returned REFUTE, and both are stated in the paper with the explanation that the rule imposed a verdict structure on a question that could not honestly carry one. (3) A methods/limitations note discloses the full arc - the battery was designed under a binary regime; execution revealed that several experiments were descriptive or non-severe; the classification standard was adopted mid-battery (Standard v1.9.7); labels and report forms changed; NO number changed. The Standard's re-design symmetry test ("would I make this change if it pushed the result the other way?") is answered YES on the record: E5's limited-resolution caveat would gut an ASSERTED verdict exactly as much as it softens the DROPPED one (a 0.0068 top-cluster spread makes "#1-#2" equally unresolvable), E6's severity defect would have invalidated a SUPPORT crossing exactly as much as it invalidates the REFUTE, and the classification was applied to ALL SIX completed experiments - E1-E4 keeping their verdicts and report forms unchanged - not only to the two whose results were unwelcome.

---

## 18. AMENDMENT 2026-07-25 - DATA MANIFEST EXTENSION + E14 (echelon variance decomposition)

**Status: PRE-PULL, PRE-RUN. Design frozen here BEFORE any new data is pulled and before the synthetic suite is written, per the v1.9.5 experiment-validation gate and the v1.9.7 classification step. No hashed-data run until both halves below are committed and the suite passes.**

**Why this amendment exists.** The Phase-4 source audit found that the pinned source reports an echelon-by-echelon variance decomposition of bullwhip amplification which this rebuild neither carried nor dispositioned. COVERAGE row 39 marks source 6.1 TRANSFORM with the disposition "Persistence estimates re-earned" - which covers the persistence estimates and NOT the decomposition. The decomposition is the paper's only opportunity to LOCATE its mechanism in real data: every other empirical result is predictive association (E1, E2) or simulation. Author-authorized 2026-07-25.

### 18.1 Data manifest extension (amends Section 14)

The pinned manifest holds inventory-to-sales RATIOS. The decomposition requires FLOW series, which were never pulled. Added to the manifest, monthly and seasonally adjusted, US Census via FRED, EVERY ID TO BE TITLE-VERIFIED AT PULL TIME before acceptance (the Section-14 discipline; a mislabeled id is the defect that produced the A25SIS audit-trail entry):

- Total retail sales (chain step 1)
- Merchant wholesalers sales (chain step 2)
- Manufacturers' value of shipments, total manufacturing (chain step 3)
- Manufacturers' new orders, total manufacturing (chain step 4)
- Manufacturers' new orders, durable goods (sector arm)

The exact FRED identifiers are resolved and title-verified at pull time and recorded in SOURCES.md with bytes, SHA256, store path and replicator tolerance, exactly as the existing 34. Coverage target 1992-01 onward to match the panel. These are REVISABLE series: per the v1.9.4 rule the pinned snapshot is the reproducibility anchor and a later live re-fetch is a drift-tolerant provenance check, not a gate.

### 18.2 E14 classification and report form (v1.9.7)

**Primary type: DESCRIPTIVE / STRUCTURAL CHARACTERIZATION.** The question is where along the chain variance amplification concentrates. It is not a hypothesis test and it does NOT receive a SUPPORT/REFUTE verdict.

**Severity check.** If the claim were false - if amplification distributed roughly evenly across echelons rather than concentrating - could THIS test on THIS data distinguish that? Yes. The statistic is a per-step variance ratio, unbounded above and bounded below at zero, with no ceiling to saturate against and no tie structure; an even distribution appears as every step near 1.0 with overlapping intervals, and concentration appears as one step materially above 1.0 with an interval excluding the others. Both patterns are observable and distinguishable at the available n. The instrument therefore has dynamic range where the answer lives.

**Report form: CHARACTERIZATION WITH UNCERTAINTY.** Per-step variance ratios with bootstrap confidence intervals, plus the compound product checked against the direct end-to-end ratio as an internal-consistency test. NO verdict is emitted. If the intervals overlap such that concentration cannot be distinguished from even distribution, the reported result is INCONCLUSIVE - a statement about resolution, never a negative finding.

**Pre-registered REPORTING commitment (binds what is reported, not that a verdict is reached).** Reported in full regardless of outcome: (a) each adjacent-step variance ratio on month-over-month changes, with a bootstrap interval; (b) the compound product of the step ratios; (c) the direct end-to-end ratio; (d) the discrepancy between (b) and (c) as an internal-consistency check; (e) the same computed excluding the COVID window, since the source claimed the concentration is structural rather than crisis-driven and that claim is checkable by exclusion; (f) the sector arm, where available, on the same construction. No step is omitted for being uninformative.

**Operator.** Observable: month-over-month change in each flow series. Statistic: ratio of variances between adjacent chain steps, computed on the common overlapping sample. Uncertainty: stationary block bootstrap on the paired changes, block length and resample count frozen in the analysis script before its first real run. Sample: 1992-01 onward, common coverage across the four chain series. Second pass excluding 2020-01 through 2021-12. No detrending beyond first-differencing, which is the transform the variance-ratio statistic is defined on.

**Validity review.** Real-world referent: these are the actual order and shipment flows the bullwhip literature measures, not a constructed proxy. What the statistic means at the actual n: roughly 400 monthly observations per series, and the block bootstrap carries the serial dependence that a naive variance-ratio interval would ignore. Scope: this locates WHERE amplification concentrates; it does NOT establish that the measurement mechanism CAUSED the concentration, and the write-up must say so - a concentration at the ordering step is CONSISTENT WITH the mechanism this paper models and does not exclude other explanations for the same location.

**Bias firewall.** This design is frozen at this commit. The synthetic suite is written next and must plant a known decomposition (one dominant step against near-unity steps) and recover it at the real n, plus plant an even distribution and correctly return INCONCLUSIVE. A suite failure fixes CODE, never this design. Any change to the operator or report form motivated by suite findings is a further dated amendment before any real run. Real data is touched once.

**Sector arm (item 2 of the audit finding).** The per-sector variance ratios are a BY-PRODUCT of the same series and the same operator, reported under the same characterization rules. They are not a separate experiment and carry no separate verdict.

**Third audit item, not part of E14.** The regime-era persistence comparison (stable, disruption, recovery eras) computes from the EXISTING hashed I/S panel with no new data and is handled separately; it is a descriptive re-cut of an already-pinned series, not a new experiment.

---

## 19. AMENDMENT 2026-07-25b - E14 IDENTIFIER RESOLUTION + SECTION 14 VERIFICATION RULE TIGHTENING

**Status: PRE-PULL, PRE-RUN. Nothing has entered the store or data/SOURCES.md; the manifest extension is still empty, which is the correct state. Author-authorized 2026-07-25 (items 19.1, 19.2, 19.5, 19.6). The sub-decision in 19.4 is OPEN and must be closed before any pull.**

### 19.1 Resolved identifiers for the E14 chain (closes the Section 18.1 deferral)

Section 18.1 named the five chain series in words and deferred the exact FRED identifiers to pull time. They are resolved HERE INSTEAD, before the pull, because resolving them surfaced three defects that pull-time title-verification alone would not have caught (19.2). Each identifier below was confirmed on 2026-07-25 against its OWN FRED series page - not against a search snippet, a sibling series, or a naming pattern - for EXISTENCE, TITLE, UNITS and SEASONAL ADJUSTMENT.

| Chain step | FRED id | FRED-verified title | Units | Adjustment | Coverage as read |
|---|---|---|---|---|---|
| 1 retail | MRTSSM44000USS | Retail Sales: Retail Trade | Millions of Dollars | Seasonally Adjusted | 1992-01 to 2026-03 |
| 2 wholesale | S42SMSM144SCEN | Total Merchant Wholesalers, Except Manufacturers' Sales Branches and Offices Sales | Millions of Dollars | Seasonally Adjusted | 1992-01 to 2026-05 |
| 3 shipments | AMTMVS | Manufacturers' Value of Shipments: Total Manufacturing | Millions of Dollars | Seasonally Adjusted | confirm at pull |
| 4 new orders | AMTMNO | Manufacturers' New Orders: Total Manufacturing | Millions of Dollars | Seasonally Adjusted | 1992-02 to 2026-05 |
| sector arm | DGORDER | Manufacturers' New Orders: Durable Goods | Millions of Dollars | Seasonally Adjusted | 1992-02 to 2026-04 |

**Retail: revised, not advance (author-ratified 2026-07-25).** MRTSSM44000USS is the Monthly Retail Trade Survey series; RSXFS is the Advance Monthly Retail Sales subsample estimate of the same concept, superseded in following months by the fuller survey. For a 34-year variance decomposition the revised series is the correct input: the advance estimate's extra sampling noise inflates the variance of chain step 1, and step 1 is the denominator against which the concentration claim at later steps is measured, so advance data would bias the FIRST link of the chain in a direction that flatters the hypothesis. RSAFS and MRTSSM44X72USS - both "Retail Trade AND Food Services" - remain rejected: food services are not part of the goods chain being decomposed.

### 19.2 Three defects found by resolving identifiers before the pull, and what each one teaches

**(1) NONEXISTENT IDENTIFIER.** The Section 18.1 working plan carried AMDMNO as the durable-goods new-orders series. AMDMNO IS NOT A FRED SERIES; it does not resolve. The actual seasonally adjusted series is DGORDER (its not-seasonally-adjusted sibling UMDMNO carries a word-for-word identical title). A plausible-looking identifier inherited from a plan is not a verified identifier. New failure mode: EXISTENCE.

**(2) IDENTIFIER CONSTRUCTED BY ANALOGY IS WRONG.** The Monthly Wholesale Trade sector series follow a visible pattern in which the seasonally adjusted sibling flips one letter: S4238SM144NCEN becomes S4238SM144SCEN. Applying that same pattern to the TOTAL series S42SMNM144NCEN yields S42SMNM144SCEN. The actual identifier is S42SMSM144SCEN - the letter flips in TWO positions, not one. An identifier derived from a sibling's naming pattern is a guess wearing the costume of a rule. New failure mode: CONSTRUCTION BY ANALOGY.

**(3) A WITHIN-FAMILY SUBSTITUTION SILENTLY REGRESSED SCOPE.** The prior working note recommended MRTSSM44X72USS as the revised counterpart of RSXFS. It is not. FRED's own cross-reference notes are explicit in both directions: RSXFS pairs with MRTSSM44000USS ("Retail Trade"), and RSAFS pairs with MRTSSM44X72USS ("Retail Trade AND Food Services"). RSAFS had ALREADY been rejected for including food services. Taking MRTSSM44X72USS would have reintroduced food services into chain step 1 while presenting itself as a strict upgrade from advance to revised - undoing a correct earlier exclusion under cover of an improvement. New failure mode: SCOPE REGRESSION ON SUBSTITUTION. The general lesson is that a prior session's recorded recommendation is a CANDIDATE, never a CLEARANCE, including when this project produced it; this is the same class as the E8 finding that provenance is not correctness.

**The identical-title collision is systemic in these families, not a one-off.** Total merchant wholesalers sales carries FOUR live series under a word-for-word identical title, separated only by units and adjustment: S42SMNM144NCEN (Millions of Dollars, NSA), S42SMSM144SCEN (Millions of Dollars, SA), M42MPCM157NCEN (Percent, NSA), P42MPCM157SCEN (Percent, SA). The M3 family does the same: AMTMVS/UMTMVS, AMTMNO/UMTMNO and DGORDER/UMDMNO are each identical-title SA/NSA pairs. Every series in this chain sits inside such a cluster. The percent-units near-miss recorded earlier was therefore the normal shape of these Census families on FRED, not bad luck, and the tightened rule in 19.5 is a response to the structure rather than to one incident.

### 19.3 The manifest extension is TWO new series, not five

Section 14 already lists AMTMNO, AMTMVS and DGORDER under "activity context", and data/SOURCES.md already carries all three as pulled, hashed rows (used-by field: "activity context"). Verified 2026-07-25 against the committed SOURCES.md: 32 FRED rows plus 12 non-FRED rows, 44 data rows in total. The extension therefore adds TWO new pulls - MRTSSM44000USS and S42SMSM144SCEN - taking the FRED rows from 32 to 34 and the total from 44 to 46. The earlier working estimate of five new pulls was wrong because it did not check what was already hashed.

**Role promotion, recorded.** E14 consumes AMTMNO, AMTMVS and DGORDER as LOAD-BEARING inputs. Their used-by field in SOURCES.md must change from "activity context" to name E14. This is a regeneration of a generated file through pull.py's manifest configuration, never a hand-edit of SOURCES.md.

### 19.4 OPEN - vintage policy for the three already-hashed chain series (must be closed before any pull)

The three chain series already in the store were pulled and hashed at the Phase-2 freeze (SOURCES.md generated 2026-07-17). The two new series would be pulled now. The chain would therefore mix vintages unless all five are re-pulled together. Two options, neither yet ratified:

- **Option A - reuse the frozen three, pull only the two new.** Preserves three already-committed SHA256 values untouched. The vintage mixture is absorbed by the operator's existing common-overlapping-sample rule, which truncates the analysis window to the EARLIEST common end date; the effect is to discard roughly one week of the newer series' tail, which is conservative. Requires the write-up to state that chain inputs carry two pull dates.
- **Option B - re-pull all five at one date.** One coherent vintage across the chain. Rewrites the SHA256 of three currently pinned rows. No experiment currently consumes those three, so nothing already reported is invalidated, but it discards a frozen reproducibility anchor to buy tidiness.

RECOMMENDED: Option A. A committed hash is not disturbed without cause, and the frozen operator already anticipates unequal coverage.

### 19.5 Section 14 verification rule, TIGHTENED (amends Section 14; author-ratified 2026-07-25)

Section 14 and Section 18.1 both require that every FRED identifier be TITLE-VERIFIED before acceptance. That standard is now demonstrably INSUFFICIENT: live series share word-for-word identical titles while differing in units and in seasonal adjustment, one planned identifier did not exist at all, and one was derivable only by a pattern that does not hold. The rule is replaced by the following, which governs this paper and is proposed to the Research-to-Publication Standard as a general note:

**Every external data identifier entering the manifest must be confirmed against its OWN publisher series page for all four of: EXISTENCE, TITLE, UNITS, and SEASONAL ADJUSTMENT. An identifier may NEVER be accepted on the strength of a naming pattern inferred from a sibling series, a search result snippet, a prior session's recommendation, or a plan document. Any substitution WITHIN a series family - advance to revised, not-seasonally-adjusted to seasonally adjusted, total to sub-aggregate - must be independently re-verified for SCOPE, because a substitution that is correct on vintage or adjustment can silently change what the series covers.**

### 19.6 Realised sample start (records a consequence, changes no operator)

AMTMNO and DGORDER begin 1992-02; the retail and wholesale series begin 1992-01. Section 18.2 states the sample as "1992-01 onward, common coverage across the four chain series", and the common-coverage clause already resolves this. Recorded so the write-up reports the REALISED start rather than the nominal one: the common sample begins 1992-02 in levels and 1992-03 in month-over-month changes. No operator changes.

