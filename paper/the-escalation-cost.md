# The Escalation Cost

## Intensity, Duration, and the Growing Damage of Regime Change

Jae Kim (ORCID 0009-0005-3260-7880) - jae@laggingtruth.com

<!-- Rendered numbers: every {{LB-id}} token below is substituted by the committed renderer from analysis/claims.lock. No figure is retyped by hand. -->

## Abstract

Institutions steer feedback systems off trailing averages of persistent variables, and after a regime change the estimator lags reality. This paper prices that lag. We prove that blind-period damage is bounded by a compound expression D = (rho_2/rho_1)^tau - intensity raised to duration - computable from quantities institutions already estimate; derive the unique optimal measurement window W* in closed form; and establish the adaptation-stability identity linking the two. The bound is validated on a 34-year rolling out-of-sample panel of seventeen U.S. inventory-to-sales series (pooled Spearman {{LB-E1-panel-spearman}}, panel p {{LB-E1-panel-p}}), corroborated on the 2008 crisis episode, and boundary-tested on COVID. Simulation studies map where acting on the diagnostic helps and where it harms: value is conditional on capacity strain, asymmetric between price raises and cuts, robust to permanent customer attrition in genuinely shifted regimes yet harmful in noisy ones, and - under drifting persistence - beyond rescue by any estimator, including a perfect one. The theorem converts steady-state stability analysis into a computable transient-cost diagnostic; its limits are stated and tested.

**Keywords:** regime change; adaptation lag; spectral radius; bullwhip; measurement window; transient cost

**JEL:** C61; C63; E32; L60; M11

## 1 Introduction

Institutions steer feedback off trailing averages of persistent variables; after a regime change the estimator lags reality, and the loop pays for the lag [@Minsky-1986; @Hopp-Spearman-2008]. Prior literatures answer steady-state stability or optimal policy mix, not the transient cost of estimator lag during a regime transition - the gap this paper fills [@Disney-Towill-2002; @Dejonckheere-2003; @Li-Dorfler-2024; @Leng-2025; @Spiegler-2016]. Our contribution is a computable bound on that transient cost, its optimal-window corollary, an identity unifying them, and a program of pre-registered empirical and simulation tests that map the result's domain - including its failures - honestly.

## 2 Related Work

### 2.1 Control-Theoretic Stability

The transfer-function and eigenvalue traditions establish when supply loops are stable in steady state [@Disney-Towill-2002; @Dejonckheere-2003; @Dejonckheere-2004; @Disney-2008; @Disney-Towill-2003; @Disney-2004-golden; @Hosoda-Disney-2006; @Li-2023; @Lin-2020; @Ouyang-Daganzo-2006; @Spiegler-2016; @Helbing-2004; @Gaalman-2022; @Warburton-Disney-2007]. The closest method precedents are closed-loop production-inventory analysis under i.i.d. demand [@Boute-2006], ARMA-demand eigenvalue work [@Gaalman-Disney-2009], stability-region inversions [@Warburton-2004; @Wang-2013], and behavioral stability regions [@Udenio-2017]. Two closest cousins are positioned explicitly: transient bullwhip via robust control [@Li-Dorfler-2024] and persistence-driven network amplification [@Leng-2025]; neither prices the estimator's blind period after a regime change. Deep-RL policy work is a contrast, not a precedent [@Gijsbrechts-2022].

### 2.2 Empirical Bullwhip

Firm- and industry-level measurements establish the phenomenon our panel rides on [@Bray-Mendelson-2012; @Bray-Mendelson-2015; @Cachon-2007; @Shan-2014; @Dooley-2010; @Saricioglu-2025], with SPC-style monitoring as a method contrast [@Costantino-2014].

### 2.3 Semiconductor Dynamics

Sector-specific volatility and planning literature ground the CHIPS application [@Anderson-2000; @Monch-2011; @Nepal-2012; @Hopp-Spearman-2008].

### 2.4 Complexity and Resilience

Complexity-performance and network-risk results motivate the persistence channel [@Bozarth-2009; @Choi-2001; @Novak-Eppinger-2001; @Serdarasan-2013; @Osadchiy-2016; @Graves-Tomlin-2003; @Tomlin-2006].

### 2.5 Minsky in Operations

Stability breeding instability, drift toward boundaries, capability traps, and quality erosion supply the institutional frame [@Minsky-1986; @Rasmussen-1997; @Dekker-2011; @Repenning-Sterman-2001; @Repenning-Sterman-2002; @Oliva-Sterman-2001].

### 2.6 Adaptation Rates and Transient Response

Adaptive-control transient bounds are the nearest formal relatives of the blind-period cost [@Datta-Ioannou-1994; @Krstic-Kokotovic-1993; @Zang-Bitmead-1994; @Gibson-2013; @Haykin-1996; @Jungers-2009; @Plischke-Wirth-2008].

## 3 The Framework in Brief

The closed loop is a W x W companion matrix whose spectral radius rho determines stability; this is a verified input from the companion work, cited not re-proved [@Kim-MeasurementTrap]. A trailing estimator of window W adapts to a new persistence regime over adaptation time tau(W): the blind period [@Kim-AdaptationRate]. S-1 states the linearization scope: stability is read from the companion-matrix spectral radius under linearization. S-2 states the demand model: AR(1) with a single persistence parameter per regime.

## 4 The Measurement Damage Theorem

### 4.1 Setup

<!-- anchor: EQ-1 -->
EQ-1 defines the managed variable, trailing estimator, and companion matrix A(phi, W, bg). Scope conditions S-1 and S-2 bind here.

### 4.2 Theorem 1: The Compound Damage Bound

<!-- anchor: THM-1 -->
THM-1 (Compound Damage Bound): blind-period damage is bounded by D = (rho_2/rho_1)^tau.
<!-- anchor: EQ-2 -->
EQ-2 states the bound. S-3 restricts the domain to step-change regime transitions; compound multi-channel shocks are outside the model. The full written proof is P-THM-1 in Appendix G; the machine legs are the symbolic step-check ({{LB-T1-bound-symbolic}}) and the numeric stress grid (in-domain cells {{LB-T1-bound-numeric-indomain}}, counterexamples {{LB-T1-bound-numeric-counterexamples}}, all-pass {{LB-T1-bound-numeric-allpass}}).

### 4.3 Theorem 2: The Optimal Measurement Window

<!-- anchor: THM-2 -->
THM-2: a unique interior optimal window W* exists in closed form via the Lambert W function [@Warburton-Disney-2007].
<!-- anchor: EQ-3 -->
EQ-3 states the closed form. Written proof P-THM-2 in Appendix G; machine legs {{LB-T2-wstar-symbolic}}, brute-force agreement {{LB-T2-wstar-numeric-match}} (match rate {{LB-T2-wstar-numeric-matchrate}}), unimodality failures {{LB-T2-wstar-numeric-unimodal-failures}}.

### 4.4 Theorem 3: The Adaptation-Stability Identity

<!-- anchor: THM-3 -->
THM-3 (Adaptation-Stability Identity): total damage is governed by intensity x duration across domains.
<!-- anchor: EQ-4 -->
EQ-4 states the identity. Written proof P-THM-3 in Appendix G; machine legs {{LB-THM3-symbolic}}, dual-path identity checks {{LB-THM3-numeric-checked}}, numeric leg pass {{LB-THM3-numeric}}.

### 4.5 Comparative Statics

Signs of dW*/d(rho_2), dW*/d(phi), and dW*/d(Delta_phi), re-derived cleanly in this rebuild: symbolic legs {{LB-T2-statics-symbolic}}; numeric monotonicity counters {{LB-T2-statics-numeric-monophi-fail}} (phi) and {{LB-T2-statics-numeric-monobg-fail}} (bg) failures.

### 4.6 The pi^2/2 Speed Limit and Optimal Safety Factor

<!-- anchor: EQ-5 -->
EQ-5 restates the single-loop criterion S(phi, W) * bg < pi^2/2 from the foundation [@Kim-MeasurementTrap].
<!-- anchor: EQ-6 -->
EQ-6 gives the optimal safety factor k*. Under regime-change risk the optimal operating point sits below the limit: mfg-parameter argmin {{LB-T3-kstar-mfg-argmin}}, in-band {{LB-T3-kstar-inband}}, all-below-one {{LB-T3-kstar-allbelow1}}, verdict {{LB-T3-kstar-verdict}} (proposition-level: numeric legs here; the written proof with labeled approximations is P-THM-3's companion obligation in Appendix G).

### 4.7 Connection to the Adaptation Tax

The damage bound supplies the transition-cost foundation for the adaptation-tax framework [@Kim-AdaptationTax].

## 5 Empirical Validation

### 5.1 GFC Episode

Pre-crisis predicted damage ranking aligns with realized crisis damage (corroborating; L-06 states the limit) [@Udenio-2015; @Dooley-2010]. This is an episode association by construction - the crisis estimation window is contemporaneous with part of the realized window - and is never an out-of-sample prediction; Section 5.3 owns prediction. Combined D: Spearman {{LB-E2-gfc-spearman}}, permutation p {{LB-E2-gfc-p}}, n {{LB-E2-gfc-n}}, verdict {{LB-E2-gfc-verdict}}; component bake-off rho_crisis {{LB-E2-components-rho-crisis}}, |delta phi| {{LB-E2-components-absdphi}}, combined-beats-components {{LB-E2-components-combined-ge}}. Table TBL-1 reports the full panel.

<!-- anchor: TBL-1 -->

*TBL-1 token stub (GFC episode + components).*

- LB-E2-gfc: {{LB-E2-gfc-n}} {{LB-E2-gfc-p}} {{LB-E2-gfc-spearman}} {{LB-E2-gfc-verdict}}
- LB-E2-components: {{LB-E2-components-absdphi}} {{LB-E2-components-combined-ge}} {{LB-E2-components-rho-crisis}}


### 5.2 COVID Episode

The pre-registered expected null: a compound shock where persistence drops sits outside the step-change model (L-01) [@Saricioglu-2025]. Result: Spearman {{LB-E3-covid-spearman}}, p {{LB-E3-covid-p}}, n {{LB-E3-covid-n}}, verdict {{LB-E3-covid-verdict}}; persistence dropped in {{LB-E3-persistence-direction-count}} of 17 sectors (majority {{LB-E3-persistence-direction-majority}}) - the falsifiable boundary direction confirmed.

### 5.3 Rolling 34-Year Validation

The primary falsifier: rolling out-of-sample D predicts subsequent inventory-to-sales deviation at the panel level across regime-oscillating sectors (amended rule B, pooled statistic) [@Cachon-2007]. Result: pooled mean Spearman {{LB-E1-panel-spearman}}, joint block-bootstrap panel p {{LB-E1-panel-p}} over {{LB-E1-panel-n-oscillating}} oscillating sectors ({{LB-E1-panel-n-chronic}} chronic-boundary), verdict {{LB-E1-panel-verdict}}; per-sector range {{LB-E1-range-min}} to {{LB-E1-range-max}} (descriptive). The estimator choice is justified by the supplementary OLS-vs-YW comparison (OLS bias {{LB-T1-estimator-ols}} vs Yule-Walker bias {{LB-T1-estimator-yw}}; OLS less biased: {{LB-T1-estimator-ols-less-biased}}; labeled not-a-theorem). Table TBL-2 reports per-sector detail.

<!-- anchor: TBL-2 -->

*TBL-2 token stub (rolling validation).*

- LB-E1-panel: {{LB-E1-panel-n-chronic}} {{LB-E1-panel-n-oscillating}} {{LB-E1-panel-p}} {{LB-E1-panel-spearman}} {{LB-E1-panel-verdict}}
- LB-E1-range: {{LB-E1-range-max}} {{LB-E1-range-min}}
- LB-T1-estimator: {{LB-T1-estimator-ols}} {{LB-T1-estimator-ols-less-biased}} {{LB-T1-estimator-yw}}


### 5.4 Beer Game Monte Carlo

Acting on the diagnostic saves cost within this experiment's own construction (L-03 binds; the source's ERP figure is not carried) [@Oroojlooyjadid-2022]. Base-stock comparator {{LB-E4-erp}}; phi-gated spectral tool {{LB-E4-tool}} (relative reduction {{LB-E4-tool-relreduction}}, paired p {{LB-E4-tool-p}}, verdict {{LB-E4-tool-verdict}}); full theorem {{LB-E4-full}}; win rate {{LB-E4-winrate}}; engagement boundary {{LB-E4-tool-phi-engagement}} (a property of this construction). Table TBL-3 reports costs by algorithm.

<!-- anchor: TBL-3 -->

*TBL-3 token stub (Beer Game).*

- LB-E4-erp: {{LB-E4-erp}}
- LB-E4-tool: {{LB-E4-tool}} {{LB-E4-tool-p}} {{LB-E4-tool-phi-engagement}} {{LB-E4-tool-relreduction}} {{LB-E4-tool-verdict}}
- LB-E4-full: {{LB-E4-full}}
- LB-E4-winrate: {{LB-E4-winrate}}


## 6 Supply Chain Application

### 6.1 Bullwhip Instability Finding

Measured sector inventory-to-sales persistence is high enough that standard order-up-to policies sit at or over the stability boundary [@Lee-1997a; @Lee-1997b; @Chen-2000]: manufacturing-aggregate mean rho {{LB-E5-persistence-mfg-meanrho-R}} (SPEC-R) and {{LB-E5-persistence-mfg-meanrho-M}} (SPEC-M).

### 6.2 Spectral Radius Ordering Tool

The ordering tool is a practitioner rule taking observed demand persistence as input, positioned against stability-region inversions and eigenvalue precedents [@Warburton-2004; @Wang-2013; @Udenio-2017; @Gaalman-Disney-2009; @Boute-2006]. S-4 states the data floor: monthly frequency with n at least 36 (60 preferred); quarterly filing data is insufficient.

### 6.3 Firm-Level Bookend

The data-floor illustration (S-4): quarterly filings cannot support the persistence estimate the tool needs. (Conditional on the deferred EDGAR entry; any quoted figure will be ledgered.)

### 6.4 Cross-Sector Evidence

The rolling monitoring narrative is backward-looking and weaker than Section 5.3, and says so. Its boundary-crossing dates enter with Table TBL-4 when the table's generator commits its output (deferred by author ruling).

### 6.5 Boundary Conditions

Where the tool helps and where it harms is mapped, not assumed [@Boute-2022]. The chain-length crossover is conditional on capacity headroom; pricing value is a cliff in capacity strain and net-negative above it; the raise strategy is robust to permanent attrition only in genuinely shifted regimes; and under drifting persistence no estimator - including a perfect one - rescues the recipe (S-8, L-04). Appendix F carries the four studies; Table TBL-7 the cells. Scope conditions S-3, S-5 and limits L-01, L-03 bind here.

## 7 The CHIPS Act

### 7.1 Most Unstable Sectors

The graded pre-registered claim was DROPPED with a limited-resolution caveat [@Monch-2011]: on the valid mean-exceedance instrument the CHIPS-dependent sectors sit in the top-instability cluster but not distinguishably at its peak, and rank is spec-sensitive. Ranks: R4238 {{LB-E5-chips-rank-R-R4238}} (SPEC-R) / {{LB-E5-chips-rank-M-R4238}} (SPEC-M); A34SIS {{LB-E5-chips-rank-R-A34SIS}} / {{LB-E5-chips-rank-M-A34SIS}}; verdict {{LB-E5-chips-verdict}}. Table TBL-4 carries the full ranking.

<!-- anchor: TBL-4 -->

*TBL-4 token stub (instability ranking + persistence).*

- LB-E5-ranking: {{LB-E5-ranking-r01-meanexc}} {{LB-E5-ranking-r01-sector}} {{LB-E5-ranking-r02-meanexc}} {{LB-E5-ranking-r02-sector}} {{LB-E5-ranking-r03-meanexc}} {{LB-E5-ranking-r03-sector}} {{LB-E5-ranking-r04-meanexc}} {{LB-E5-ranking-r04-sector}} {{LB-E5-ranking-r05-meanexc}} {{LB-E5-ranking-r05-sector}} {{LB-E5-ranking-r06-meanexc}} {{LB-E5-ranking-r06-sector}} {{LB-E5-ranking-r07-meanexc}} {{LB-E5-ranking-r07-sector}} {{LB-E5-ranking-r08-meanexc}} {{LB-E5-ranking-r08-sector}} {{LB-E5-ranking-r09-meanexc}} {{LB-E5-ranking-r09-sector}} {{LB-E5-ranking-r10-meanexc}} {{LB-E5-ranking-r10-sector}} {{LB-E5-ranking-r11-meanexc}} {{LB-E5-ranking-r11-sector}} {{LB-E5-ranking-r12-meanexc}} {{LB-E5-ranking-r12-sector}} {{LB-E5-ranking-r13-meanexc}} {{LB-E5-ranking-r13-sector}} {{LB-E5-ranking-r14-meanexc}} {{LB-E5-ranking-r14-sector}} {{LB-E5-ranking-r15-meanexc}} {{LB-E5-ranking-r15-sector}} {{LB-E5-ranking-r16-meanexc}} {{LB-E5-ranking-r16-sector}} {{LB-E5-ranking-r17-meanexc}} {{LB-E5-ranking-r17-sector}}
- LB-E5-chips: {{LB-E5-chips-rank-M-A34SIS}} {{LB-E5-chips-rank-M-R4238}} {{LB-E5-chips-rank-R-A34SIS}} {{LB-E5-chips-rank-R-R4238}} {{LB-E5-chips-verdict}}
- LB-E5-persistence: {{LB-E5-persistence-mfg-meanrho-M}} {{LB-E5-persistence-mfg-meanrho-R}}


### 7.2 Capacity Utilization Threshold

The knee hypothesis could not be adjudicated: NAICS 334 runs persistently above the instability boundary at every utilization level - chronically unstable, not utilization-triggered - so no capacity knee is detectable in this statistic (the empirical demonstration of L-02) [@Hopp-Spearman-2008; @Nepal-2012]. Bin means {{LB-E6-threshold-bin1-lt75-mean}} / {{LB-E6-threshold-bin2-75-85-mean}} / {{LB-E6-threshold-bin3-85-90-mean}} / {{LB-E6-threshold-bin4-ge90-mean}} (n {{LB-E6-threshold-bin1-lt75-n}} / {{LB-E6-threshold-bin2-75-85-n}} / {{LB-E6-threshold-bin3-85-90-n}} / {{LB-E6-threshold-bin4-ge90-n}}); the pre-registered rule's outcome {{LB-E6-threshold-rule-outcome}} is reported alongside, not as the finding. Current utilization {{LB-E6-current-utilization}} ({{LB-E6-current-month}}), context only. Table TBL-6 shows the flat above-boundary band.

<!-- anchor: TBL-6 -->

*TBL-6 token stub (utilization bins).*

- LB-E6-threshold: {{LB-E6-threshold-bin1-lt75-mean}} {{LB-E6-threshold-bin1-lt75-n}} {{LB-E6-threshold-bin2-75-85-mean}} {{LB-E6-threshold-bin2-75-85-n}} {{LB-E6-threshold-bin3-85-90-mean}} {{LB-E6-threshold-bin3-85-90-n}} {{LB-E6-threshold-bin4-ge90-mean}} {{LB-E6-threshold-bin4-ge90-n}} {{LB-E6-threshold-rule-outcome}}
- LB-E6-current: {{LB-E6-current-month}} {{LB-E6-current-utilization}}


### 7.3 Complexity Drives Persistence

Product and network complexity drive persistence, connecting the complexity literature to the instability ranking [@Bozarth-2009; @Novak-Eppinger-2001; @Choi-2001; @Serdarasan-2013; @Anderson-2000; @Ning-2023].

### 7.4 Werner-CHIPS Nexus

Directed credit creation as a possible financing channel for supplier-ecosystem stability - exploratory, and labeled as such [@Werner-1997; @Werner-2005; @Werner-2014a; @Werner-2014b; @Alfaro-2025; @Ahn-Tan-2025].

## 8 Cross-Domain Extensions

Suggestive readings only; S-7 states that feedback strengths are assumption-driven proxies, and L-05 bounds every claim in this section.

### 8.1 Sovereign Ratings

The pre-registered conditional-instability reading fired WITHDRAWN: the stationarity precondition fails at the extreme [@Ferri-1999]. Characterization: {{LB-E10-calm-n-stationary}} of 18 countries in a tight near-unit band (phi {{LB-E10-calm-phi-min}} to {{LB-E10-calm-phi-max}}, calm rho {{LB-E10-calm-rho-min}} to {{LB-E10-calm-rho-max}}, all below 1); explosive {{LB-E10-calm-explosive}}; dual-implementation guard {{LB-E10-calm-guard-dualimpl}}; the crossing sweep is the withdrawn branch ({{LB-E10-crisis-reading}}). Table TBL-5 carries the country panel.

<!-- anchor: TBL-5 -->

*TBL-5 token stub (sovereign panel).*

- LB-E10-calm: {{LB-E10-calm-explosive}} {{LB-E10-calm-guard-dualimpl}} {{LB-E10-calm-n-stationary}} {{LB-E10-calm-phi-max}} {{LB-E10-calm-phi-min}} {{LB-E10-calm-rho-max}} {{LB-E10-calm-rho-min}}
- LB-E10-crisis: {{LB-E10-crisis-reading}}


### 8.2 Unemployment Insurance

The pre-registered procyclical-feedback reading fired WITHDRAWN [@Anderson-Meyer-1994; @Woodbury-2004]. Characterization: pooled normal-period phi {{LB-E11-normal-phi}} (n {{LB-E11-normal-n}}), rho {{LB-E11-normal-rho-min}} to {{LB-E11-normal-rho-max}} across all nine combinations, all below 1; jurisdictions {{LB-E11-normal-jur-phi-min}} to {{LB-E11-normal-jur-phi-max}} (median {{LB-E11-normal-jur-phi-median}}); pooled GFC phi {{LB-E11-gfc-phi}} (n {{LB-E11-gfc-n}}) sits far below the boundary corner {{LB-E11-gfc-corner}} and is statistically indistinguishable from normal; reading {{LB-E11-gfc-reading}} - consistent with the cited counterpoint [@Fath-Fuest-2002] and rhyming with the COVID finding: crises in these systems arrive as level shocks, not persistence explosions.

## 9 Implications for Institutional Design

### 9.1 Three-Parameter Audit

The three-parameter audit (phi, W, bg) generalizes the diagnostic; EQ-2 and EQ-5 are its instruments [@Rasmussen-1997; @Dekker-2011].

### 9.2 Reverse-Engineering Principle

Observed damage patterns imply the loop parameters that produced them.

### 9.3 Domain Interventions

Interventions ranked by which parameter they move.

## 10 Forward Prediction: Self-Service Diagnostic

### 10.1 The Prediction

A dated, falsifiable forward prediction is stated here for public registration: for systems whose measured rho exceeds 1, the response to the next demand shock amplifies; for rho below 1, it decays. Protocol constants are finalized in this phase and ledgered under the LB-FP-diagnostic family.

### 10.2 Protocol

Thresholds, window, and reporting per the replication protocol.

### 10.3 Registration

Registered publicly at the review stage.

### 10.4 Falsification Conditions

What outcome would falsify the prediction, stated in advance.

## 11 Conclusion

C-01: blind-period damage is governed by intensity x duration, D = (rho_2/rho_1)^tau, computable from quantities institutions already estimate. C-02: a unique optimal measurement window W* exists in closed form. C-03: under regime-change risk the optimal operating point sits below the pi^2/2 limit. C-04: acting on the diagnostic reduces cost against a rational self-calibrating base-stock baseline within the simulated environment. C-05: the CHIPS-dependent sectors are among the more structurally unstable, though not the two most, with measurement-sensitive ranking. C-06: semiconductor instability is structural rather than utilization-triggered, so a utilization tripwire is not an available monitoring benchmark. Limits: L-01 (compound shocks excluded), L-02 (chronically-unstable sectors need steady-state analysis), L-03 (simulation binds the model), L-04 (recipe-level non-stationarity unresolved; one trajectory shape tested), L-05 (cross-domain readings suggestive only), L-06 (GFC corroborating only), L-07 (pricing bounded by the immediate-arithmetic demand model).

## AI-Assistance Disclosure

This paper was produced with substantial AI assistance. Claude (Anthropic) served as research assistant and code author under the author's direction and the project's Research-to-Publication Standard: Claude drafted and edited analysis code, ran container-side quality assurance, performed the seven-class code-integrity review, drafted manuscript text from the author's pre-registered outline, and maintained the project's decision journal and verification artifacts. All experiments were pre-registered by the author; all analysis code, its integrity review (verification/cic_signoff.md), and the machine-checked claim ledger are committed alongside this manuscript; every load-bearing number is rendered from that ledger by a committed script. The author made all scientific decisions, ran all analyses locally, verified all results by hash, and takes full responsibility for the content. The adversarial pre-publication review is likewise performed by Claude in a separate, isolated session; this statement will be updated to mirror that review's record.

## References


[@Ahn-Tan-2025]: Ahn, J. & Tan, B. (2025). Supply chain resilience and diversification. IMF Working Paper 2025/102.
[@Alfaro-2025]: Alfaro, L., Brussevich, M., Minoiu, C. & Presbitero, A. (2025). Bank financing of global supply chains. NBER Working Paper.
[@Anderson-2000]: Anderson, E., Fine, C. & Parker, G. (2000). Upstream volatility in the supply chain: the machine tool industry. Production and Operations Management.
[@Anderson-Meyer-1994]: Anderson, P. & Meyer, B. (1994). The effects of unemployment insurance taxes and benefits on layoffs. NBER.
[@Boute-2006]: Boute, R., Disney, S., Lambrecht, M. & Van Houdt, B. (2006). An integrated production and inventory model to dampen upstream demand variability. European Journal of Operational Research.
[@Boute-2022]: Boute, R., Disney, S., Gijsbrechts, J. & Van Mieghem, J. (2022). Dual sourcing and smoothing under non-stationary demand. Management Science.
[@Bozarth-2009]: Bozarth, C., Warsing, D., Flynn, B. & Flynn, E. (2009). The impact of supply chain complexity on manufacturing plant performance. Journal of Operations Management.
[@Bray-Mendelson-2012]: Bray, R. & Mendelson, H. (2012). Information transmission and the bullwhip effect: an empirical investigation. Management Science.
[@Bray-Mendelson-2015]: Bray, R. & Mendelson, H. (2015). Production smoothing and the bullwhip effect. M&SOM.
[@Cachon-2007]: Cachon, G., Randall, T. & Schmidt, G. (2007). In search of the bullwhip effect. M&SOM.
[@Chen-2000]: Chen, F., Drezner, Z., Ryan, J. & Simchi-Levi, D. (2000). Quantifying the bullwhip effect in a simple supply chain. Management Science.
[@Choi-2001]: Choi, T., Dooley, K. & Rungtusanatham, M. (2001). Supply networks and complex adaptive systems. Journal of Operations Management.
[@Costantino-2014]: Costantino, F., Di Gravio, G., Shaban, A. & Tronci, M. (2014). SPC-based inventory control policy to improve supply chain dynamics. International Journal of Production Research.
[@Datta-Ioannou-1994]: Datta, A. & Ioannou, P. (1994). Performance analysis and improvement in model reference adaptive control. IEEE TAC.
[@Dejonckheere-2003]: Dejonckheere, J., Disney, S., Lambrecht, M. & Towill, D. (2003). Measuring and avoiding the bullwhip effect: a control theoretic approach. EJOR.
[@Dejonckheere-2004]: Dejonckheere, J., Disney, S., Lambrecht, M. & Towill, D. (2004). The impact of information enrichment on the bullwhip effect. EJOR.
[@Dekker-2011]: Dekker, S. (2011). Drift into Failure. Ashgate.
[@Disney-2004-golden]: Disney, S., Towill, D. & Van de Velde, W. (2004). Variance amplification and the golden ratio in production and inventory control. IJPE.
[@Disney-2008]: Disney, S. (2008). Supply chain aperiodicity, bullwhip and stability analysis with Jury's inners. IMA Journal of Management Mathematics.
[@Disney-Towill-2002]: Disney, S. & Towill, D. (2002). A discrete transfer function model to determine the dynamic stability of a vendor managed inventory supply chain. IJPR.
[@Disney-Towill-2003]: Disney, S. & Towill, D. (2003). On the bullwhip and inventory variance produced by an ordering policy. Omega.
[@Dooley-2010]: Dooley, K., Yan, T., Mohan, S. & Gopalakrishnan, M. (2010). Inventory management and the bullwhip effect during the 2007-2009 recession. Journal of Supply Chain Management.
[@Fath-Fuest-2002]: Fath, J. & Fuest, C. (2002). Experience rating of unemployment insurance in the US: a model for Europe? CESifo.
[@Ferri-1999]: Ferri, G., Liu, L.-G. & Stiglitz, J. (1999). The procyclical role of rating agencies: evidence from the East Asian crisis. Economic Notes.
[@Gaalman-2022]: Gaalman, G., Disney, S. & Wang, X. (2022). When bullwhip increases in the lead time. EJOR.
[@Gaalman-Disney-2009]: Gaalman, G. & Disney, S. (2009). On bullwhip in a family of order-up-to policies with ARMA(2,2) demand. IJPE.
[@Gibson-2013]: Gibson, T., Annaswamy, A. & Lavretsky, E. (2013). On adaptive control with closed-loop reference models. IEEE Access.
[@Gijsbrechts-2022]: Gijsbrechts, J., Boute, R., Van Mieghem, J. & Zhang, D. (2022). Can deep reinforcement learning improve inventory management? M&SOM.
[@Graves-Tomlin-2003]: Graves, S. & Tomlin, B. (2003). Process flexibility in supply chains. Management Science.
[@Haykin-1996]: Haykin, S. (1996). Adaptive Filter Theory. Prentice Hall.
[@Helbing-2004]: Helbing, D., Lammer, S., Witt, U. & Brenner, T. (2004). Network-induced oscillatory behavior in material flow networks. Physical Review E.
[@Hopp-Spearman-2008]: Hopp, W. & Spearman, M. (2008). Factory Physics (3rd ed.). Waveland.
[@Hosoda-Disney-2006]: Hosoda, T. & Disney, S. (2006). On variance amplification in a three-echelon supply chain. Omega.
[@Jungers-2009]: Jungers, R. (2009). The Joint Spectral Radius: Theory and Applications. Springer.
[@Kim-AdaptationRate]: Kim, J. (2026). The Adaptation Rate of Trailing Averages. Zenodo (companion, cited by title).
[@Kim-AdaptationTax]: Kim, J. (2026). The Adaptation Tax. Zenodo (companion, cited by title).
[@Kim-MeasurementTrap]: Kim, J. (2026). The Measurement Trap. Zenodo (companion, cited by title).
[@Krstic-Kokotovic-1993]: Krstic, M. & Kokotovic, P. (1993). Transient-performance improvement with a new class of adaptive controllers. Systems & Control Letters.
[@Lee-1997a]: Lee, H., Padmanabhan, V. & Whang, S. (1997a). Information distortion in a supply chain: the bullwhip effect. Management Science.
[@Lee-1997b]: Lee, H., Padmanabhan, V. & Whang, S. (1997b). The bullwhip effect in supply chains. Sloan Management Review.
[@Leng-2025]: Leng, K., Liu, Y., Ren, S. & Tsyvinski, A. (2025). Persistence-driven amplification in production networks. NBER Working Paper 33638.
[@Li-2023]: Li, Q., Gaalman, G. & Disney, S. (2023). On the equivalence of proportional and damped-trend order-up-to policies. IJPE.
[@Li-Dorfler-2024]: Li, Z. & Dorfler, F. (2024). Transient bullwhip via robust control. Working paper.
[@Lin-2020]: Lin, J., Naim, M. & Spiegler, V. (2020). Delivery-time dynamics in supply chains. IJPR.
[@Minsky-1986]: Minsky, H. (1986). Stabilizing an Unstable Economy. Yale University Press.
[@Monch-2011]: Monch, L., Fowler, J. & Dauzere-Peres, S. (2011). A survey of semiconductor supply chain planning. EJOR.
[@Nepal-2012]: Nepal, B., Murat, A. & Chinnam, R. (2012). The bullwhip effect in capacitated supply chains. IJPE.
[@Ning-2023]: Ning, Z., Tziantzioulis, G. & Wentzlaff, D. (2023). Supply chain aware computer architecture. ISCA.
[@Novak-Eppinger-2001]: Novak, S. & Eppinger, S. (2001). Sourcing by design: product complexity and the supply chain. Management Science.
[@Oliva-Sterman-2001]: Oliva, R. & Sterman, J. (2001). Cutting corners and working overtime: quality erosion in the service industry. Management Science.
[@Oroojlooyjadid-2022]: Oroojlooyjadid, A., Nazari, M., Snyder, L. & Takac, M. (2022). A deep Q-network for the beer game. M&SOM.
[@Osadchiy-2016]: Osadchiy, N., Gaur, V. & Seshadri, S. (2016). Systematic risk in supply chain networks. Management Science.
[@Ouyang-Daganzo-2006]: Ouyang, Y. & Daganzo, C. (2006). Characterization of the bullwhip effect in linear, time-invariant supply chains. Management Science.
[@Plischke-Wirth-2008]: Plischke, E. & Wirth, F. (2008). Duality results for the joint spectral radius and transient behavior. LAA.
[@Rasmussen-1997]: Rasmussen, J. (1997). Risk management in a dynamic society. Safety Science.
[@Repenning-Sterman-2001]: Repenning, N. & Sterman, J. (2001). Nobody ever gets credit for fixing problems that never happened. California Management Review.
[@Repenning-Sterman-2002]: Repenning, N. & Sterman, J. (2002). Capability traps and self-confirming attribution errors. Administrative Science Quarterly.
[@Saricioglu-2025]: Saricioglu, P., Erol Genevois, M. & Cedolin, M. (2025). Bullwhip amplification under COVID-19. Working paper.
[@Serdarasan-2013]: Serdarasan, S. (2013). A review of supply chain complexity drivers. Computers & Industrial Engineering.
[@Shan-2014]: Shan, J., Yang, S., Yang, S. & Zhang, J. (2014). An empirical study of the bullwhip effect in China. Production and Operations Management.
[@Spiegler-2016]: Spiegler, V., Potter, A., Naim, M. & Towill, D. (2016). The value of nonlinear control theory in investigating the underlying dynamics of a production and inventory system. IJPR.
[@Tomlin-2006]: Tomlin, B. (2006). On the value of mitigation and contingency strategies for managing supply chain disruption risks. Management Science.
[@Udenio-2015]: Udenio, M., Fransoo, J. & Peels, R. (2015). Destocking, the bullwhip effect, and the credit crisis. IJPE.
[@Udenio-2017]: Udenio, M., Vatamidou, E., Fransoo, J. & Dellaert, N. (2017). Behavioral causes of the bullwhip effect: an analysis using linear control theory. IISE Transactions.
[@Wang-2013]: Wang, X., Disney, S. & Wang, J. (2013). Stability analysis of constrained inventory systems. EJOR.
[@Warburton-2004]: Warburton, R., Disney, S., Towill, D. & Hodgson, J. (2004). Further insights into the stability of supply chains. IJPR.
[@Warburton-Disney-2007]: Warburton, R. & Disney, S. (2007). Order and inventory variance amplification: the equivalence of discrete and continuous time analyses. IJPE.
[@Werner-1997]: Werner, R. (1997). Towards a new monetary paradigm: a quantity theorem of disaggregated credit. Kredit und Kapital.
[@Werner-2005]: Werner, R. (2005). New Paradigm in Macroeconomics. Palgrave Macmillan.
[@Werner-2014a]: Werner, R. (2014a). Can banks individually create money out of nothing? The theories and the empirical evidence. IRFA.
[@Werner-2014b]: Werner, R. (2014b). How do banks create money, and why can other firms not do the same? IRFA.
[@Woodbury-2004]: Woodbury, S. (2004). Layoffs and experience rating of the unemployment insurance payroll tax. Upjohn Institute.
[@Zang-Bitmead-1994]: Zang, Z. & Bitmead, R. (1994). Transient bounds for adaptive control systems. IEEE TAC.


## Appendix A: Data Sources

Data sources and identifiers mirror the committed data registry; Table TBL-A lists them.

<!-- anchor: TBL-A -->
*TBL-A token stub: mirrors data/SOURCES.md (no ledger values).*

## Appendix B: Validation and Robustness

Theorem machine-check detail (both legs per theorem, per the two-row rule) and estimator robustness supporting Section 4 and Section 5.3.

*Theorem-leg token stub.*

- LB-T1-bound: {{LB-T1-bound-numeric-allpass}} {{LB-T1-bound-numeric-counterexamples}} {{LB-T1-bound-numeric-indomain}} {{LB-T1-bound-symbolic}}
- LB-T2-wstar: {{LB-T2-wstar-numeric-match}} {{LB-T2-wstar-numeric-matchrate}} {{LB-T2-wstar-numeric-unimodal-failures}} {{LB-T2-wstar-symbolic}}
- LB-T2-statics: {{LB-T2-statics-numeric-monobg-fail}} {{LB-T2-statics-numeric-monophi-fail}} {{LB-T2-statics-symbolic}}
- LB-T3-kstar: {{LB-T3-kstar-allbelow1}} {{LB-T3-kstar-inband}} {{LB-T3-kstar-mfg-argmin}} {{LB-T3-kstar-verdict}}
- LB-THM3: {{LB-THM3-numeric}} {{LB-THM3-numeric-checked}} {{LB-THM3-symbolic}}
- LB-T1-estimator: {{LB-T1-estimator-ols}} {{LB-T1-estimator-ols-less-biased}} {{LB-T1-estimator-yw}}


## Appendix C: Companion Matrix Spectral Radii by Domain

Cross-domain rho computations supporting Table TBL-4 and Table TBL-5.

## Appendix D: Mitigation Effectiveness

Mitigation effectiveness under the damped policies, supporting Section 6.5.

## Appendix E: Beer Game Simulation Parameters

The frozen calibration behind Table TBL-3 (S-5 states the simulation scope).

## Appendix F: Additional Simulation Studies

Four studies: the chain-length sweep, the pricing analysis (S-6 states the pricing model scope; L-07 the limit), the hysteresis sweep, and the recipe-level non-stationarity analysis. Table TBL-7 carries every cell.

<!-- anchor: TBL-7 -->

*TBL-7 token stub (chain-length / pricing / hysteresis / non-stationarity).*

- LB-E7-gradient: {{LB-E7-gradient-cap13-ar1high-L4}} {{LB-E7-gradient-cap13-ar1high-L6}} {{LB-E7-gradient-cap13-ar1high-L8}} {{LB-E7-gradient-cap24-ar1high-L4}} {{LB-E7-gradient-cap24-ar1high-L4-resolved}} {{LB-E7-gradient-cap24-ar1high-L6}} {{LB-E7-gradient-cap24-ar1high-L6-resolved}} {{LB-E7-gradient-cap24-ar1high-L8}} {{LB-E7-gradient-cap24-ar1high-L8-resolved}} {{LB-E7-gradient-n-benefit}} {{LB-E7-gradient-n-harm}} {{LB-E7-gradient-n-resolved}} {{LB-E7-gradient-n-unresolved}}
- LB-E7-calibration: {{LB-E7-calibration-L4-ours}} {{LB-E7-calibration-L4-source}} {{LB-E7-calibration-L4-source-in-ci}} {{LB-E7-calibration-L6-ours}} {{LB-E7-calibration-L6-source}} {{LB-E7-calibration-L6-source-in-ci}} {{LB-E7-calibration-L8-ours}} {{LB-E7-calibration-L8-source}} {{LB-E7-calibration-L8-source-in-ci}}
- LB-E8-up: {{LB-E8-up-cap18x-mean}} {{LB-E8-up-cap24x-mean}} {{LB-E8-up-cap30x-mean}} {{LB-E8-up-claima-cipct-hi}} {{LB-E8-up-claima-cipct-lo}} {{LB-E8-up-claima-mean}} {{LB-E8-up-claimb-mean}} {{LB-E8-up-claimb-sigma}} {{LB-E8-up-claimb-verdict}}
- LB-E8-down: {{LB-E8-down-level_shift_down_persistent-mean}} {{LB-E8-down-level_shift_down_persistent-sigma}} {{LB-E8-down-low_phi_shift_down-mean}} {{LB-E8-down-low_phi_shift_down-sigma}} {{LB-E8-down-mid_phi_shift_down-mean}} {{LB-E8-down-mid_phi_shift_down-sigma}}
- LB-E9-robust: {{LB-E9-robust-h000-benefit}} {{LB-E9-robust-h000-sigma}} {{LB-E9-robust-h010-benefit}} {{LB-E9-robust-h010-sigma}} {{LB-E9-robust-h030-benefit}} {{LB-E9-robust-h030-sigma}} {{LB-E9-robust-h060-benefit}} {{LB-E9-robust-h060-sigma}}
- LB-E9-fragile: {{LB-E9-fragile-h000-benefit}} {{LB-E9-fragile-h000-sigma}} {{LB-E9-fragile-h010-benefit}} {{LB-E9-fragile-h010-sigma}} {{LB-E9-fragile-h030-benefit}} {{LB-E9-fragile-h030-sigma}} {{LB-E9-fragile-h060-benefit}} {{LB-E9-fragile-h060-sigma}}
- LB-E9-verdict: {{LB-E9-verdict}}
- LB-E9-fidelity: {{LB-E9-fidelity-maxreldiff}} {{LB-E9-fidelity-tier}}
- LB-E12-oracle: {{LB-E12-oracle-L4x13-mean}} {{LB-E12-oracle-L8x24-mean}} {{LB-E12-oracle-fixed-L8x18-mean}} {{LB-E12-oracle-fixed-L8x24-mean}} {{LB-E12-oracle-harm-all-drift}} {{LB-E12-oracle-legb-L8x18-fixedvsols}} {{LB-E12-oracle-legb-L8x18-fixedvsoracle}} {{LB-E12-oracle-legb-L8x24-fixedvsols}} {{LB-E12-oracle-legb-L8x24-fixedvsoracle}} {{LB-E12-oracle-paradox-count}} {{LB-E12-oracle-verdict}} {{LB-E12-oracle-winscheck}}


## Appendix G: Proofs

<!-- anchor: P-THM-1 -->
P-THM-1: full written proof of THM-1 (the Compound Damage Bound).
<!-- anchor: P-THM-2 -->
P-THM-2: full written proof of THM-2 (the Optimal Measurement Window), with the comparative-statics corollary.
<!-- anchor: P-THM-3 -->
P-THM-3: full written proof of THM-3 (the Adaptation-Stability Identity), with the k* proposition's labeled approximations.
