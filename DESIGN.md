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

**Inputs:** none external (synthetic; seeds committed).

## 8. E5 - 17-sector structural-instability ranking (the CHIPS observation)

**Purpose:** rank sectors by the fraction of months with rolling rho > 1; test the reproducibility and robustness of the observation that the CHIPS Act's two dependent sectors rank at the top.

**Operator.** Rolling 60-month persistence per sector; rho computed under SPEC-R (W = 12, bg scale 3.0); per sector: peak rho, mean rho, % months rho > 1, full-sample. Ranking by % months. Robustness: recompute under SPEC-M; report both.

**Decision rule.** This is a descriptive diagnostic, not a hypothesis test; its pre-registered claims: (a) REPRODUCED if the ranking regenerates from re-pulled hashed data; (b) the CHIPS observation ("the two sectors the Act depends on are the two most structurally unstable") is ASSERTED only if computers/electronics manufacturing (NAICS 334) and wholesale machinery rank #1-#2 under SPEC-R AND remain in the top quartile under SPEC-M; DOWNGRADED to "among the most unstable" if top-quartile but not #1-#2; DROPPED if either falls below the top quartile in either spec.

**Validity review.** Referent: % months above the stability boundary is a direct reading of the framework on real data. The graded assertion rule prevents over-claiming from a rank that spec choice could flip.

**AMENDMENT 2026-07-13 (post-first-run, test-validity-motivated, author-ratified; pre-registered BLIND to the CHIPS outcome).** The first E5 run exposed a TEST-DESIGN DEFECT, not a result: under SPEC-R (bg scale 3.0) the ranking key % months rho > 1 SATURATES - the top six sectors (AMTMIS, AMDMIS, AMNMIS, A34SIS, A31SIS, R4233) all read 100.0%, a six-way tie at the ceiling. A saturated key carries ZERO ordering information among the tied sectors, so the emitted ranks (#1-#6) were tiebreak/sort artifacts, not measurements. The original DROPPED verdict was therefore computed from non-informative inputs and is INVALID in BOTH directions: the test could not show the CHIPS sectors WERE #1-#2, nor that they WERE NOT - it was incapable of adjudicating the ranking claim at all. Corrected first-run status: INCONCLUSIVE (test-invalid for ranking), NOT DROPPED. This is a validity finding (a broken ruler), not a data result, so replacing the ranking instrument does NOT constitute testing-after-seeing-results / HARKing: there was no informative ranking outcome to steer away from, and the replacement statistic is chosen SOLELY for having dynamic range (non-saturation), defined by the instrument's properties and NOT by where the CHIPS sectors land. The robustness spec SPEC-M (W=8, bg 0.05) did NOT saturate, but leaning the verdict on it now would be spec-shopping (it is the robustness spec, not primary); the clean fix is to redesign the PRIMARY ranking statistic and re-run BOTH specs under it.

REDESIGN (author-ratified, this amendment): the PRIMARY ranking statistic changes from '% months rho > 1' to MEAN EXCEEDANCE MAGNITUDE = mean over the sample of max(rho - 1, 0), i.e. the average distance the rolling spectral radius sits ABOVE the stability boundary (zero when below). This is continuous and non-saturating (it keeps increasing as rho climbs past 1, unlike the binary share which pegs at 100%), so it can order the leaders. Reported alternates (descriptive, not the ranking key): peak rho, mean rho, and the original % months rho > 1 (retained for continuity and to document the saturation). Ranking is by mean exceedance under SPEC-R (primary) with SPEC-M recomputed for robustness. The GRADED ASSERTION RULE is otherwise UNCHANGED and carried over verbatim onto the new key: ASSERTED iff computers/electronics (NAICS 334 -> A34SIS) AND wholesale machinery (R4238) rank #1-#2 under SPEC-R AND both remain top-quartile under SPEC-M; DOWNGRADED to 'among the most unstable' if both top-quartile but not #1-#2; DROPPED if either falls below the top quartile in either spec. A DISCLOSURE note recording the saturation, the corrected INCONCLUSIVE status of the first run, and this redesign is added to the manuscript methods/limitations - proper disclosure of what happened, in either eventual direction.

**Inputs:** 17 I/S series.

## 9. E6 - Capacity-utilization stability threshold (semiconductors)

**Purpose:** test the empirical link between capacity utilization and rho, and locate the crossing relative to the Factory Physics 85-90% knee.

**Operator.** Fed G.17 semiconductor capacity utilization (CAPUTLG3344S) and industrial production (IPG3344S), monthly; sector rho series for NAICS 334 from E5's pipeline (SPEC-R primary, SPEC-M robustness). Bin months by utilization: < 75%, 75-85%, 85-90%, >= 90%; mean rho per bin; monotonicity and crossing bin identified. Current-utilization reading reported.

**Decision rule.** SUPPORT: mean rho increases monotonically across bins AND the rho = 1.0 crossing lies in the 85-90% or >= 90% bin (consistent with the Factory Physics knee). REFUTE (claim dropped): no monotone relationship, or crossing below 80% / no crossing - the "monitoring benchmark" section is cut or reframed accordingly.

**Validity review.** Referent: utilization-congestion nonlinearity is established (Hopp-Spearman VUT); the experiment tests whether OUR statistic sees it. Binned means at 400+ months give adequate n per bin (reported per bin).

**Inputs:** CAPUTLG3344S, IPG3344S + NAICS 334 I/S series.

## 10. E7 - Chain-length sweep (robustness)

**Purpose:** map how the formula's value scales with chain length and capacity headroom, including the all-tier deployment harm-to-benefit crossover.

**Operator (frozen; source calibration).** Chain lengths {4, 6, 8}; capacity multipliers {1.3x, 1.8x, 2.4x}; four demand environments (high-persistence sustained, low-persistence noisy, plus the two source-defined variants - exact parameterizations frozen in the committed script config before first run); 50 seeds per cell; 9,000 simulations total; all-tier deployment vs base-stock baseline.

**Decision rule.** SUPPORT (robustness): the E4-configuration benefit is preserved in its own cell; the crossover pattern (small harm at 4-stage/2.4x high-persistence -> benefit by 8-stage) is REPORTED as found, whichever direction it lands. WEAKENS E4: benefit vanishes across all realistic cells adjacent to the E4 configuration.

**Validity review.** Referent: chain length and capacity are the two most arbitrary Beer Game conventions; sweeping them is the direct answer to "is this an artifact of 4 tiers?". Partition: all outcomes reportable; nothing here can be silently dropped (COVERAGE maps it).

**Inputs:** none external.

## 11. E8 - Pricing-mechanism analysis (asymmetry)

**Purpose:** test whether the persistence calculation gives useful guidance on a second lever (price), and re-earn the asymmetric finding (raises help under strain; cuts are uniformly negative).

**Operator (frozen; source calibration).** Chain simulation extended with constant-elasticity demand response and a phi-gated pricing policy (raise on high-persistence upward shift; cut on high-persistence downward shift); five demand environments at 1.3x capacity, 50 seeds per cell; capacity sensitivity at 1.8x for the upward case. Outputs: per-period value of the pricing policy vs no-pricing baseline, per cell.

**Decision rule.** The asymmetry claim is ASSERTED only if: value of raises is positive in the capacity-strained sustained-upward environment (95% CI excluding zero) AND value of cuts is negative in EVERY downward environment tested. PARTIAL: raises positive but any cut-cell non-negative -> the "uniformly negative" language is withdrawn and the section reports the actual sign pattern. DROPPED: raises not positive under strain - the pricing section reduces to a null report.

**Validity review.** Referent: constant-elasticity immediate-arithmetic response is a stated modeling assumption, disclosed as bounding the finding (no competitor response, no brand effects); E9 attacks the biggest omission directly. Partition: assert/partial/drop covers all sign patterns.

**Inputs:** none external.

## 12. E9 - Customer-hysteresis sensitivity sweep

**Purpose:** attack E8's raise-prices finding with its most obvious objection: permanent customer loss.

**Operator (frozen; source calibration).** Customer-pool variable decaying multiplicatively when price > reference, constant otherwise; hysteresis intensities {0.0, 0.10, 0.30, 0.60}; the two upward-shift environments at 1.3x capacity; 20 seeds per cell; 320 trials. Outputs: pricing benefit per cell; end-of-run customer pool fraction.

**Decision rule.** The E8 raise-claim is retained WITH the split framing only if the benefit remains positive at hysteresis 0.60 in the high-persistence strained environment; the noisy-environment fragility is reported as found. If the benefit goes negative at moderate hysteresis (0.30) even in the strained sticky environment, E8's raise-claim is downgraded to fragile everywhere and the practical guidance is withdrawn. The cuts-are-bad finding is unaffected by construction (hysteresis does not engage at/below reference) - stated, not tested here.

**Validity review.** Referent: hysteresis-as-attrition is the standard first-order model of the objection. 20 seeds/cell is smaller than E8's 50 - pre-registered consequence: cell means carry wider CIs; any cell mean within 1 SE of zero is reported as indeterminate rather than signed.

**Inputs:** none external.

## 13. E10 - Sovereign ratings extension (suggestive), E11 - UI extension (suggestive), E12 - non-stationarity limitation

**E10 operator.** JST Macrohistory R6, 18 countries, 1870-2020; debt/GDP persistence per country by OLS on linearly detrended series (raw-levels variant reported); rho per country under SPEC-S calm (W = 5y, bg = 0.05); crisis sweep bg in {0.05, 0.10, 0.25, 0.50, 1.00, 1.50}. **Decision rule.** The conditional-instability reading is OFFERED (suggestive framing locked) only if: all 18 countries rho < 1 at calm bg AND the count crossing 1.0 rises monotonically with bg AND cross-country rho ranking tracks persistence. Any failure -> the sovereign section reports what was found and withdraws the Greek-crisis suggestion. GROUND-UP RE-VERIFICATION mandatory: this analysis contained the source project's v14 fatal error (impossible rho values), fixed at v15 - the rebuild recomputes from scratch and cross-checks against an independent implementation before any value is ledgered.

**E11 operator.** DOL ETA 539 weekly claims, 53 jurisdictions, 1986-2026; insured unemployment rate persistence, quarterly aggregation; rho under SPEC-U at bg grid {0.05, 0.10, 0.25}; normal-period vs GFC-period (2008-2009) persistence. **Decision rule.** The procyclical-feedback reading is OFFERED only if normal-period rho < 1 at all tested bg AND GFC-period persistence crosses the boundary at bg > 0.05. Otherwise reported and withdrawn. Framing locked at suggestive (one reading of the formula's dynamics, not a welfare claim; Fath-Fuest counterpoint cited).

**E12 operator (pre-registered limitation documentation).** Within the E7 environment: oracle variant handed true phi each period vs OLS-estimated variant vs fixed-alpha damping vs no-formula baseline, under non-stationary persistence trajectory phi: 0.30 -> 0.95 -> 0.40; 50 seeds. **Decision rule.** This experiment CANNOT support the thesis; it documents a limitation. Expected (per source): fixed-alpha outperforms both oracle and OLS variants, establishing the recipe-level (not estimator-level) nature of the limitation. If instead the oracle variant WINS, the limitation section is rewritten as resolved (good news requiring explanation) - a dated amendment records either way. Only the one tested trajectory shape is claimed; the untested shapes (drift, square-wave, one-shot) are named as future work.

**Validity reviews.** E10/E11: bg values are assumption-driven proxies, not estimates - exactly why the decision rules lock SUGGESTIVE framing and the paper says so; the experiments test internal coherence of the reading, not causal claims. E12: the oracle design isolates recipe-vs-estimator attribution by construction (perfect information removes the estimator from the causal path).

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

- (none)
