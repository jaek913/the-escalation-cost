# The Escalation Cost

## Intensity, Duration, and the Growing Damage of Regime Change

Jae Kim (ORCID 0009-0005-3260-7880) - jae@laggingtruth.com

<!-- Rendered numbers: every double-braced LB-id token below is substituted by the committed renderer (analysis/render_paper.py) from analysis/claims.lock. No figure is retyped by hand. -->

## Abstract

Institutions steer feedback systems off trailing averages of persistent variables, and after a regime change the estimator lags reality. This paper prices that lag. We prove that blind-period damage is bounded by a compound expression D = (rho_2/rho_1)^tau - intensity raised to duration - computable from quantities institutions already estimate; derive the unique optimal measurement window W* in closed form; and establish the adaptation-stability identity linking the two. The bound is validated on a 34-year rolling out-of-sample panel of seventeen U.S. inventory-to-sales series (pooled Spearman {{LB-E1-panel-spearman}}, panel p {{LB-E1-panel-p}}), corroborated on the 2008 crisis episode, and boundary-tested on COVID. Simulation studies map where acting on the diagnostic helps and where it harms: value is conditional on capacity strain, asymmetric between price raises and cuts, robust to permanent customer attrition in genuinely shifted regimes yet harmful in noisy ones, and - under drifting persistence - beyond rescue by any estimator, including a perfect one. The theorem converts steady-state stability analysis into a computable transient-cost diagnostic; its limits are stated and tested.

**Keywords:** regime change; adaptation lag; spectral radius; bullwhip; measurement window; transient cost

**JEL:** C61; C63; E32; L60; M11

## 1 Introduction

Every institution that steers a system steers it off a measurement, and every measurement of a persistent variable is a trailing average of some length. A central bank reads inflation over a window. A manufacturer sets inventory policy off recent demand. A rating agency assesses debt sustainability from years of fiscal data. Each of these windows is a choice, and each is usually made on grounds of statistical precision alone: longer windows give cleaner estimates, so longer is treated as safer.

That reasoning holds exactly as long as the world stays in one regime. When the underlying persistence changes - when demand that used to revert starts to compound, when a fiscal position that used to stabilize starts to run - the trailing average keeps reporting the old regime for a while. During that stretch the institution is not making a small error. It is applying a control rule calibrated to conditions that no longer exist, to a system whose deviations are now amplifying rather than decaying. The loop pays for the lag, and the payment is not proportional to it [@Minsky-1986; @Hopp-Spearman-2008].

This paper prices that payment. The result is a bound: damage during the blind period is the intensity of the new instability raised to the power of the institution's own adaptation time. Intensity and duration compound rather than add, so the cost of a slow measurement rises exponentially in exactly the situations where the measurement is most likely to be slow - and both inputs are quantities institutions already estimate, which makes the bound a diagnostic rather than a metaphor. Two corollaries follow directly: there is a unique optimal window that balances estimation precision against adaptation speed and it is available in closed form, and the safe operating point under regime-change risk sits strictly below the stability limit that steady-state analysis would license.

The gap this fills is specific. The control-theoretic literature answers when a loop is stable in steady state, and answers it well; the empirical bullwhip literature measures amplification as it occurs; the adaptive-control literature bounds transient behavior for a controller that knows it is adapting. None of them prices what an institution loses in the interval between a regime changing and its own estimator noticing [@Disney-Towill-2002; @Dejonckheere-2003; @Li-Dorfler-2024; @Leng-2025; @Spiegler-2016].

The contribution is therefore a computable bound on that transient cost, its optimal-window corollary, an identity unifying them across domains, and - equally - a program of pre-registered empirical and simulation tests that map where the result holds and where it does not. That second half is not a formality. The tests reported here include a rolling out-of-sample validation the framework passes, two domain extensions whose pre-registered readings were withdrawn when their preconditions failed, a capacity-threshold hypothesis that proved unadjudicable, a simulation result showing the framework's own remedy causes harm under conditions the theory does not cover, and a monitoring record showing that the paper's own instability dashboard confirms regime shifts rather than anticipating them. Each of those outcomes is reported at the strength the evidence supports, because a diagnostic whose failure modes are undocumented is not a diagnostic.

## 2 Related Work

Six literatures bear on this result. The first establishes the stability conditions this paper takes as given; the second supplies the empirical phenomenon; the third and fourth ground the applications; the fifth supplies the institutional frame; the sixth contains the nearest formal relatives. Across all six, the recurring pattern is that the transient - the interval during which a system's own measurement is wrong about which regime it is in - is either assumed away or treated as a nuisance rather than priced.

### 2.1 Control-Theoretic Stability

This is the literature the paper stands on rather than argues with. The transfer-function and eigenvalue traditions establish when supply loops are stable in steady state, and they establish it well: given a demand process and a replenishment rule, the analysis says whether the loop amplifies or damps [@Disney-Towill-2002; @Dejonckheere-2003; @Dejonckheere-2004; @Disney-2008; @Disney-Towill-2003; @Disney-2004-golden; @Hosoda-Disney-2006; @Li-2023; @Lin-2020; @Ouyang-Daganzo-2006; @Spiegler-2016; @Helbing-2004; @Gaalman-2022; @Warburton-Disney-2007]. The companion-matrix construction this paper uses is taken from that tradition and is cited, not re-proved.

The closest method precedents share the move of treating the loop's own parameters as the object of analysis: closed-loop production-inventory analysis under i.i.d. demand [@Boute-2006], ARMA-demand eigenvalue work [@Gaalman-Disney-2009], stability-region inversions that solve for the admissible parameter set rather than testing one policy [@Warburton-2004; @Wang-2013], and behavioral stability regions that ask which regions human orderers actually occupy [@Udenio-2017].

What the tradition assumes away is the thing this paper prices, and the assumption is specific enough to name. A number of the foundational closed-form bullwhip results - the z-transform framework and its smoothing-policy extensions, and the golden-ratio gain [@Disney-Towill-2002; @Disney-Towill-2003; @Dejonckheere-2003; @Dejonckheere-2004; @Disney-2004-golden] - were derived under independently and identically distributed demand. Under i.i.d. demand the spectral radius sits below one for any reasonable ordering policy, so the instability mechanism studied here does not arise at all. Bullwhip under i.i.d. demand is a VARIANCE-AMPLIFICATION phenomenon: does order variance exceed demand variance? What this paper studies is a STABILITY-TRANSITION phenomenon: does the system cross the boundary past which perturbations compound rather than decay? The second question requires persistent demand, which the panel in Section 7.1 finds in real sectors and which the i.i.d. analyses do not model. That is the gap, stated precisely - not that prior work was wrong, but that it was answering a different question in a demand environment where this one cannot be posed.

That characterization applies to the foundational analytical results and NOT to the tradition as a whole, a distinction worth making explicitly. A substantial body of work in the same school analyses transient and nonlinear dynamics directly - describing-function and step-response analysis of grocery supply-chain resilience, and frequency-response analysis of delivery-time dynamics in assemble-to-order systems [@Spiegler-2016; @Lin-2020]. The contribution here is therefore not the analysis of supply-chain transients as such, which is well established and built upon, but a closed-form damage bound tying a backward-looking estimator's adaptation time to a regime transition.

Four bodies of work sit close enough to require explicit differentiation rather than a citation. The nearest is the closed-loop production-inventory analysis of smoothing replenishment under endogenous lead times [@Boute-2006], which shares this paper's central concern - the coupling between the ordering decision and the production system - and motivated the construction used here. It differs in three respects that matter: its demand is i.i.d., so the persistence driving this mechanism is absent by construction; its apparatus is a queueing and matrix-analytic model of endogenous lead times rather than a companion-matrix eigenvalue analysis; and the questions taken up here - what happens when persistence changes between regimes, estimating the spectral radius from rolling empirical data as a monitoring statistic, and the damage bound itself - fall outside the scope that work sets. The relationship is an extension of that modelling tradition, and dialogue with its authors about how they see the connection would be welcome.

The golden-ratio gain [@Disney-2004-golden] minimizes steady-state combined order and inventory variance under i.i.d. demand. The safety factor derived here ({{LB-T3-kstar-mfg-argmin}} at manufacturing parameters) minimizes expected total cost INCLUDING regime-transition damage under high persistence that can shift between regimes. These answer different optimization problems in non-overlapping demand environments rather than competing on the same one: under i.i.d. demand this framework reduces to standard stability analysis, where the golden ratio may well be the right answer; under persistent demand with regime changes, it was not derived for that setting.

The Lambert W function appears in both this paper and the delay-differential analysis of continuous-time supply chains with pure time delays [@Warburton-Disney-2007], but for different purposes - there to solve the delay equations, here to derive the optimal measurement window. The shared use of one widely applicable function reflects its breadth across optimization contexts rather than overlapping intellectual content.

The closest mathematical relatives are the switched-linear-systems transient bounds, which establish that cumulative deviation grows at most as the joint spectral radius raised to the elapsed time [@Jungers-2009; @Plischke-Wirth-2008]. The damage bound is superficially similar and differs on three axes: those bounds hold for ARBITRARY switching, while the transition here follows a specific trajectory dictated by the trailing estimator's convergence, with the exponent a function of the measurement window rather than a free parameter; their matrices are abstract, while these are parameterized by observable quantities with explicit formulas connecting the spectral radius to them; and that work sits in pure-mathematics venues without a supply-chain application. The mathematical kinship is real and the practical overlap limited. Oscillatory instability in material-flow networks has also been examined from a statistical-physics standpoint [@Helbing-2004], documenting the phenomenon without supplying the parameterized criterion this framework needs.

Two recent results come closest in aim and are positioned individually: transient bullwhip analyzed through robust control [@Li-Dorfler-2024], which bounds transient behavior but for a controller with known dynamics, and persistence-driven network amplification [@Leng-2025], which makes persistence the driver but not the measurement of it. Neither prices the estimator's blind period after a regime change. Two further contrasts are complementary rather than competing: statistical-process-control monitoring [@Costantino-2014] is built to detect THAT order variance has risen, where diagnosing why, supplying a principled ordering constraint, and pricing the damage accumulated during the detection delay are aims this framework adds; and deep reinforcement learning [@Gijsbrechts-2022] can outperform base-stock policies in specific simulated environments while providing no closed-form stability bound, no interpretable constraint, and no regime-transition prediction - so the natural division is that the spectral radius supplies the constraint and a learned policy optimizes within it.

### 2.2 Empirical Bullwhip

Firm- and industry-level measurements establish the phenomenon our panel rides on [@Bray-Mendelson-2012; @Bray-Mendelson-2015; @Cachon-2007; @Shan-2014; @Dooley-2010; @Saricioglu-2025], with SPC-style monitoring as a method contrast [@Costantino-2014]. This work documents that amplification exists, varies across firms and sectors, and intensifies in crises. What it does not supply is a pre-crisis quantity that orders sectors by how much amplification they are about to suffer - which is precisely what the damage bound proposes and Section 6 tests out of sample.

### 2.3 Semiconductor Dynamics

Sector-specific volatility and planning literature ground the CHIPS application [@Anderson-2000; @Monch-2011; @Nepal-2012; @Hopp-Spearman-2008]. Semiconductors are the natural stress case for a measurement-lag argument: fabrication lead times run months, capacity is lumpy and capital-intensive so it cannot be adjusted incrementally, and end demand swings hard enough that the persistence of any given quarter is a poor guide to the next. An industry with long lead times and expensive capacity is an industry whose control loop has both a long effective window and a strong incentive to react hard once it does react - the two ingredients the damage bound multiplies together.

That literature also supplies the specific intuition this paper puts to a direct test: that a stability knee should appear as utilization approaches its ceiling, since a system running near capacity has no slack to absorb a disturbance. Section 8.2 tests it and does not confirm it - not because the intuition is refuted, but because the sector never occupies the stable regime the test needed as a contrast. The honest reading is reported there as an inconclusive instrument rather than as a negative result.

### 2.4 Complexity and Resilience

Complexity-performance and network-risk results motivate the persistence channel [@Bozarth-2009; @Choi-2001; @Novak-Eppinger-2001; @Serdarasan-2013; @Osadchiy-2016; @Graves-Tomlin-2003; @Tomlin-2006]. Their common finding is that structure matters independently of scale: products with many interdependent components, supply bases with many tiers, and networks with dense interconnection all propagate a disturbance through more paths and hold it longer than a simpler system would.

Translated into this paper's vocabulary, that is a mechanism for high persistence - complexity is one of the reasons a sector's phi sits where it does. The translation matters because it connects two literatures that rarely cite each other: the complexity tradition explains WHY some sectors are structurally slow to shed a shock, and the control tradition explains WHAT a slow-shedding sector does to a feedback loop. This paper joins them at the persistence parameter, which is why the instability ranking of Section 8.1 and the complexity literature's usual suspects are substantially the same sectors, reached from different directions. That convergence is offered as a coherence check, not as a tested claim: no experiment here measures complexity or estimates its effect on persistence.

### 2.5 Minsky in Operations

Stability breeding instability, drift toward boundaries, capability traps, and quality erosion supply the institutional frame [@Minsky-1986; @Rasmussen-1997; @Dekker-2011; @Repenning-Sterman-2001; @Repenning-Sterman-2002; @Oliva-Sterman-2001]. This tradition explains why regime changes in the dangerous direction are not rare accidents but the expected consequence of a quiet period: calm conditions invite the very leverage, tightening, and margin-thinning that raise persistence. The measurement problem this paper prices is therefore structural rather than incidental - the transition is most likely to arrive exactly when the institution's long measurement window feels most justified.

### 2.6 Adaptation Rates and Transient Response

Adaptive-control transient bounds are the nearest formal relatives of the blind-period cost [@Datta-Ioannou-1994; @Krstic-Kokotovic-1993; @Zang-Bitmead-1994; @Gibson-2013; @Haykin-1996]. Those results bound what happens while an adaptive controller converges, which is structurally the same question asked of a controller that is not designed to adapt at all - the ordinary institutional case, where the window is a fixed policy choice rather than a tuned gain. The joint-spectral-radius literature supplies the correct caution for products of differing matrices, which Appendix G.0 uses to scope the paper's per-step reading precisely rather than assume it away [@Jungers-2009; @Plischke-Wirth-2008].

## 3 The Framework in Brief

Three ingredients carry the whole argument, and two of them are inherited rather than re-proved here.

The first is the loop. An institution measuring over a window W and feeding back at rate bg produces a closed loop whose linearization is a W x W companion matrix; its spectral radius rho decides stability. When rho is below one, deviations decay; above one, they compound. This is a verified input from the companion work, cited not re-proved [@Kim-MeasurementTrap].

The second is the lag. A trailing estimator of window W does not learn a new persistence regime instantly; it converges over an adaptation time tau(W) that is proportional to the window. That interval - during which the institution is steering by a description of a regime it has already left - is the blind period [@Kim-AdaptationRate].

The third is the composition, and it is this paper's contribution: what the blind period costs. Because deviations compound at the new regime's rate for the whole of it, the cost is the new intensity raised to the duration, and because the duration is set by the window the institution chose, the cost is a consequence of a measurement decision rather than of the shock alone. Two scope conditions govern throughout: stability is read from the companion-matrix spectral radius under linearization (S-1), and the managed variable follows an AR(1) with a single persistence parameter per regime (S-2).

## 4 The Measurement Damage Theorem

### 4.1 Setup

An institution manages a variable it cannot observe without delay. The managed variable y_t follows AR(1) dynamics with persistence phi, and the institution estimates the state it is reacting to with a trailing average of window W - the last W observations, equally weighted. A feedback policy then adjusts the system at rate bg on the gap between that estimate and a target. Linearizing the resulting closed loop gives a W x W companion matrix A(phi, W, bg): the persistence and feedback structure occupy its first row, an identity shift sits below, and its spectral radius rho(A) decides whether deviations decay or compound [@Kim-MeasurementTrap; @Dejonckheere-2003].

<!-- anchor: EQ-1 -->
EQ-1 defines the managed variable, trailing estimator, and companion matrix A(phi, W, bg). Scope conditions S-1 and S-2 bind here.

The window is the decision variable, and it is the source of the tension the rest of this section resolves. A long window estimates persistence precisely but adapts slowly; a short window adapts quickly but estimates noisily. When persistence is stable, only the first consideration matters and longer is better without limit. When persistence changes, the second consideration acquires a price - and Section 4.3 shows that price is finite, computable, and minimized at a unique interior window. Two restrictions carry through: stability is read from the linearized companion matrix rather than from the full nonlinear system (S-1), and the managed variable follows an AR(1) with a single persistence parameter per regime (S-2). Appendix G.0 states the full assumption set (A1 through A6), including the dominant-mode reading of damage that Remark G.0.1 scopes explicitly and Lemma G.1 replaces with a matrix-general bound.

### 4.2 Theorem 1: The Compound Damage Bound

When true persistence steps from phi_1 to phi_2 at some moment, a trailing estimator does not notice immediately. For a stretch of time it continues to report the old regime, and the policy keeps applying a rule calibrated to conditions that no longer hold. This is the blind period, and its length is the estimator's adaptation time tau(W) = kappa * W, proportional to the window (A5). The theorem prices what happens inside it.

<!-- anchor: THM-1 -->
THM-1 (Compound Damage Bound): blind-period damage is bounded by D = (rho_2/rho_1)^tau.
<!-- anchor: EQ-2 -->
EQ-2 states the bound. The structure is the paper's central claim in one line: damage is not additive in the delay, it is exponential in it, with the base set by how much more unstable the new regime is (rho_2/rho_1) and the exponent set by how long the institution stays blind (tau). Intensity and duration multiply rather than add, so a modest increase in instability paired with a long measurement window produces damage that neither factor predicts alone. Both inputs are quantities institutions already estimate, which is what makes the bound a diagnostic rather than an abstraction. S-3 restricts the domain to step-change regime transitions; compound multi-channel shocks are outside the model. The full written proof is P-THM-1 in Appendix G; the machine legs are the symbolic step-check ({{LB-T1-bound-symbolic}}) and the numeric stress grid (in-domain cells {{LB-T1-bound-numeric-indomain}}, counterexamples {{LB-T1-bound-numeric-counterexamples}}, all-pass {{LB-T1-bound-numeric-allpass}}).

### 4.3 Theorem 2: The Optimal Measurement Window

The trade-off is now explicit and has two opposing arms. Lengthening the window lowers estimation error - the asymptotic variance of the AR(1) estimate falls like (1 - phi^2)/W - while raising the exponential damage term, because a longer window means a longer blind period. Minimizing the sum of the two costs gives a first-order condition with a transcendental solution, and that solution is exactly the Lambert W function's domain.

<!-- anchor: THM-2 -->
THM-2: a unique interior optimal window W* exists in closed form via the Lambert W function [@Warburton-Disney-2007].
<!-- anchor: EQ-3 -->
EQ-3 states the closed form. The optimum is interior and unique under strict convexity of the loss (proved in Appendix G.3), which matters practically: there is one right window, not a range of defensible ones, and it can be computed from parameters an institution can estimate rather than chosen by convention. Written proof P-THM-2 in Appendix G; machine legs {{LB-T2-wstar-symbolic}}, brute-force agreement {{LB-T2-wstar-numeric-match}} (match rate {{LB-T2-wstar-numeric-matchrate}}), unimodality failures {{LB-T2-wstar-numeric-unimodal-failures}}.

### 4.4 Theorem 3: The Adaptation-Stability Identity

The first two theorems are stated for a supply chain, but nothing in their derivation is about inventory. What the derivation uses is that some quantity compounds at a rate set by the regime in force, and that the regime in force is whatever the institution's measurement says it is. Any domain with those two features inherits the result.

<!-- anchor: THM-3 -->
THM-3 (Adaptation-Stability Identity): total damage is governed by intensity x duration across domains.
<!-- anchor: EQ-4 -->
EQ-4 states the identity. This is what licenses Sections 7 through 9 to apply one framework to inventories, semiconductor capacity, sovereign debt, and unemployment insurance without re-deriving anything: the domains differ in what compounds and how the feedback is implemented, not in the structure of the cost. Written proof P-THM-3 in Appendix G; machine legs {{LB-THM3-symbolic}}, dual-path identity checks {{LB-THM3-numeric-checked}}, numeric leg pass {{LB-THM3-numeric}}.

### 4.5 Comparative Statics

How should the optimal window move when conditions change? Implicit differentiation of the first-order condition answers this cleanly, since strict convexity fixes the denominator's sign and every comparative static reduces to the sign of one partial derivative. The full re-derivation is Appendix G.4; the results are three confirmations and one correction.

Higher instability intensity shortens the window. Raising rho_2 raises the damage term at every window length, so the optimum moves left: when the new regime is more explosive, the institution can afford less blindness. Larger expected regime changes shorten it too. A bigger Delta_phi raises kappa and so lengthens the blind period for any given window, which the optimum offsets by shrinking W. Dearer estimation error lengthens it, symmetrically: as the cost of acting on a noisy estimate rises relative to the cost of acting late, the optimum buys precision with time.

The fourth static reverses the direction claimed by the source this rebuild replaces, and the reversal is forced by the model's own cost function. Holding regime-change intensity fixed, higher steady-state persistence favors a SHORTER window, not a longer one. The reason is the estimation-cost term itself: the asymptotic variance of the AR(1) estimator is (1 - phi^2)/W, which FALLS as phi approaches one. Under this variance model, highly persistent series are estimated more precisely per observation, not less, so persistence relieves estimation pressure rather than adding to it - and relieved pressure means the optimum spends fewer periods blind. The source's verbal justification ("coefficients near 1.0 require more data") contradicts the formula the source itself adopts; the correction was pre-registered before the rebuild's experiments ran. Including the indirect channel does not rescue the original sign: higher phi also raises rho_2 (A3), and that effect pushes the same direction, so the total derivative is unambiguously negative. Restoring the source's intuition would require a different estimation-cost model - one in which the difficulty of the estimation task rises with persistence, as it does for a unit-root boundary test - and that is a modeling choice outside the pinned cost function, not adopted here. No experiment in this paper consumes the sign of dW*/dphi, so the correction changes exposition rather than any operator or result.

Machine verification: symbolic legs {{LB-T2-statics-symbolic}}; numeric monotonicity counters {{LB-T2-statics-numeric-monophi-fail}} (phi) and {{LB-T2-statics-numeric-monobg-fail}} (bg) failures.

### 4.6 The pi^2/2 Speed Limit and Optimal Safety Factor

The stability boundary itself is not this paper's result; it is the foundation's, and it takes a compact form. A single loop is stable when the product of the estimator's amplification and the feedback aggressiveness stays below a fixed constant - the pi^2/2 speed limit. Read as engineering advice it says something simple: there is a maximum rate at which a system can chase a measurement it takes time to form, and exceeding it converts correction into oscillation.

<!-- anchor: EQ-5 -->
EQ-5 restates the single-loop criterion S(phi, W) * bg < pi^2/2 from the foundation [@Kim-MeasurementTrap].

The question this paper adds is where inside that region an institution should actually sit. The boundary marks where stability is lost under CURRENT conditions; it says nothing about how much room to leave for conditions changing. If persistence can step upward, an operating point that is merely inside the boundary today can be outside it tomorrow, and the blind period guarantees the institution keeps steering as though it were still inside. The safety factor answers how much margin that risk is worth.

<!-- anchor: EQ-6 -->
EQ-6 gives the optimal safety factor k*. Under regime-change risk the optimal operating point sits below the limit: mfg-parameter argmin {{LB-T3-kstar-mfg-argmin}}, in-band {{LB-T3-kstar-inband}}, all-below-one {{LB-T3-kstar-allbelow1}}, verdict {{LB-T3-kstar-verdict}} (proposition-level: numeric legs here; the written proof with labeled approximations is P-THM-3's companion obligation in Appendix G).

### 4.7 Connection to the Adaptation Tax

The damage bound supplies the transition-cost foundation for the adaptation-tax framework [@Kim-AdaptationTax]. That framework asks what an institution pays to move between operating regimes; this theorem prices one specific component of that bill - the cost incurred while the institution's own measurement still describes the regime it has already left. The two results compose rather than compete: the adaptation tax counts the cost of changing, and the damage bound counts the cost of not yet knowing that change is required.

## 5 Methods

This section states the operators the experiments actually ran. Every specification here was frozen in the pre-registered design document and committed before the first hashed-data run; where a rule changed, the change is a dated amendment disclosed in place rather than a silent edit, and no operator was chosen after seeing a result.

### 5.1 Managed Variable and Data

The managed variable is the inventory-to-sales ratio: monthly, seasonally adjusted, per sector. It is the quantity firms actually control through ordering decisions, and it is stationary, which the persistence estimator requires. The panel is seventeen US Census series - seven manufacturing, seven wholesale, three retail - held fixed from the design stage; the frozen member map, every series identifier, and each file's hash are recorded in the data dictionary (Table TBL-A), and one aggregate carries a dated correction to a source mislabel with the superseded series retained as an audit trail. Coverage runs from January 1992 to the pull date. Cross-domain extensions use the Jorda-Schularick-Taylor macrohistory panel (eighteen countries, annual) and US Department of Labor unemployment-insurance claims; semiconductor work uses the Federal Reserve capacity-utilization series.

The data floor is a scope condition, not a preference (S-4): persistence estimation requires monthly frequency and at least thirty-six observations, sixty preferred. A twenty-observation quarterly sample cannot distinguish a persistence of 0.95 from one of 0.50, so quarterly filing data is excluded by design rather than accepted with a caveat.

### 5.2 Persistence, the Loop, and Damage

Persistence phi is the AR(1) coefficient, estimated by ordinary least squares of the series on its own lag with an intercept. OLS was pre-registered as the sole estimator. The alternative considered was Yule-Walker, and the comparison is reported rather than buried: on synthetic AR(1) histories at high true persistence, Yule-Walker is the more downward-biased of the two, so OLS was retained. That comparison is re-earned in this paper's own verification suite and is labeled a diagnostic, not a selectable specification - a specification the analyst may switch after seeing results is a specification the analyst is fishing with.

The closed loop follows the construction of the companion work, used and not re-proved: a trailing-average estimator of window W feeding a proportional feedback policy of aggressiveness bg yields a W x W companion matrix A(phi, W, bg), whose spectral radius rho decides stability (S-1). Adaptation time tau is the structural function of W carried from the companion work on trailing-average adaptation, with its constant frozen in the analysis scripts. Predicted damage is D = (rho_2/rho_1)^tau, computed with rho_1 at pre-transition persistence and rho_2 at post-transition persistence, both evaluated at the system's own (W, bg).

### 5.3 The Two Named Specifications

Two real-data specifications were named in advance and both are reported wherever both apply: SPEC-M, the monitoring specification (W = 8 months, bg = 0.05), and SPEC-R, the ranking specification (W = 12 months, bg scale 3.0). Neither was selected after the fact. Three further specifications govern their own simulations - the Beer Game harness, the sovereign panel (five-year window, calm feedback swept upward for the crisis branch), and the unemployment-insurance reading - and are stated where they are used.

Reporting both specifications is what makes Section 8.1's spec-conditionality visible rather than concealed: results that hold under one and not the other are reported as exactly that.

### 5.4 The Primary Test and Its Amended Rule

The falsifier is the rolling out-of-sample panel validation (Section 6.3). At each month and sector, phi is estimated on the trailing sixty months, regime change is detected from the trailing twelve, tau follows from the window, and D is computed under SPEC-M using backward-looking data only. The outcome is the sector's excess absolute I/S deviation over the following twelve months, measured against its own trailing baseline, with the deviation definition frozen in the script before the first real run.

The decision rule was amended once, before any hashed data was touched, and the amendment is disclosed because concealing it would misrepresent the test's strength. The pre-registered rule required a majority of regime-oscillating sectors to clear a per-sector significance bar. The mechanism-validation suite measured that rule at the real sample size and found it broken in the supporting direction: the block-bootstrap null placed the bar near a rank correlation of 0.30 while the operator's own detection noise capped even strong planted true effects well below it - measured power approximately zero. A rule that cannot detect a planted true effect is a rubber stamp, and discovering this before the run is precisely what the pre-run validation exists for.

The replacement rule, ratified and frozen before the run, moves the verdict to the panel level: the statistic is the mean Spearman correlation across regime-oscillating sectors; the null is a joint circular block bootstrap in which one set of twenty-four-month block indices is applied to every oscillating sector simultaneously, preserving the cross-sector dependence that a per-sector majority rule ignores, with D held fixed and two thousand resamples. Support requires at least two oscillating sectors, a positive pooled mean, and a one-sided p below 0.01. The per-sector table (Table TBL-2) is retained as descriptive reporting and no longer carries the verdict. Verdict-level false support measured zero at the null. A pass under this rule is strong evidence; a failure is reported as indistinguishable from noise at this data resolution, not as disproof.

Sector classification is part of the operator, not a post-hoc convenience: sectors whose rolling rho crosses the boundary in both directions are regime-oscillating and carry the test; chronically-unstable sectors are boundary-condition cases reported separately, per the theorem's stated domain.

### 5.5 Episodes, Ranking, and Monitoring

The two episode tests share one operator and differ only in dates. For each sector, phi_1 is estimated over a pre-episode window and phi_2 over the episode itself, D follows, and the realized outcome is the excess deviation over the episode's peak window; the association is Spearman across the seventeen sectors, with a component bake-off reporting crisis rho alone and absolute change in persistence alone alongside the combined quantity. The global financial crisis uses 2003-2006 against 2008-2009, with outcomes over 2007-2010. COVID uses 2017-2019 against 2020-2021, with outcomes over 2020-2022, and was pre-registered as an expected null with its polarity stated explicitly: a non-significant correlation together with persistence falling in most sectors confirms the boundary, while a strongly positive result would have been reported as a problem for the mechanism rather than a win (L-01). Episode tests are seventeen observations and are labeled corroborating; they cannot carry falsification, which Section 6.3 owns.

The cross-sector ranking (Table TBL-4) orders sectors by mean exceedance - the average of max(rho - 1, 0) - after the originally registered ranking key, the share of months above the boundary, was found to saturate at its ceiling and tie the leaders. That re-instrumentation was chosen for dynamic range, blind to where any sector lands, and pre-registered before the re-run; a metric that cannot separate the leaders produces no ordering in either direction, so the earlier reading was recorded as uninformative rather than as a result. The monitoring record (Section 7.4) applies the same rolling construction at both specifications across the full sample, marks upward boundary crossings as a below-to-above transition sustained three months, and reports status and first crossing within twenty-four months either side of each episode onset.

### 5.6 Simulations, Seeds, and Disclosure

The simulation studies use paired designs: within a run, every algorithm faces identical demand sequences, seeds are recorded, and run counts were fixed in advance. The Beer Game comparison (Table TBL-3) runs four algorithms against one frozen calibration with no parameter search on the demand process. The chain-length study reports its full grid - three chain lengths by three capacity levels by four demand environments, at fifty seeds - as the experiment rather than as a search, and every cell is reported including the unresolved ones. The pricing and hysteresis studies likewise report all cells. Simulation verdicts bind the model, and generalization to the world is a separate and weaker claim (S-5).

The anti-fishing disclosure is the pair of counts, not either alone: the design document stated in advance how many specifications would be tried, and the totals actually run match those counts. Any specification beyond them would have required a dated amendment before the run, tested against the question of whether the same change would have been made had it pushed the result the other way.

Every load-bearing number in this paper is generated by a committed script from hashed inputs, recorded in a machine-checked ledger, and substituted into the text by a committed renderer; no figure is retyped by hand. The verification apparatus, including the ledger's coverage and the checks that guard it, is described in Appendix B.

## 6 Empirical Validation

### 6.1 GFC Episode

Pre-crisis predicted damage ranking aligns with realized crisis damage (corroborating; L-06 states the limit) [@Udenio-2015; @Dooley-2010]. This is an episode association by construction - the crisis estimation window is contemporaneous with part of the realized window - and is never an out-of-sample prediction; Section 6.3 owns prediction. Combined D: Spearman {{LB-E2-gfc-spearman}}, permutation p {{LB-E2-gfc-p}}, n {{LB-E2-gfc-n}}, verdict {{LB-E2-gfc-verdict}}; component bake-off rho_crisis {{LB-E2-components-rho-crisis}}, |delta phi| {{LB-E2-components-absdphi}}, combined-beats-components {{LB-E2-components-combined-ge}}. Table TBL-1 reports the full panel.

<!-- anchor: TBL-1 -->

*Table TBL-1. GFC episode (2008-09): episode-level association between predicted D and realized inventory/sales deviation, with the component bake-off. The committed episode artifact carries episode statistics and components; per-sector regime detail is in Table TBL-2.*

| Statistic | Value |
| --- | --- |
| Sectors (n) | {{LB-E2-gfc-n}} |
| Spearman, predicted D vs realized deviation | {{LB-E2-gfc-spearman}} |
| One-sided p | {{LB-E2-gfc-p}} |
| Verdict (pre-registered rule) | {{LB-E2-gfc-verdict}} |
| Component alone: crisis rho (Spearman) | {{LB-E2-components-rho-crisis}} |
| Component alone: abs delta phi (Spearman) | {{LB-E2-components-absdphi}} |
| Combined D at least matches each component | {{LB-E2-components-combined-ge}} |


### 6.2 COVID Episode

COVID was pre-registered as an expected null, and the reason matters more than the result. The theorem prices a step change in the dangerous direction: persistence rises, the loop that was decaying starts compounding, and the estimator's lag becomes expensive. COVID was not that shock. Demand collapsed and rebounded across multiple channels at once, and in most sectors measured persistence FELL rather than rose - a compound multi-channel disturbance sitting squarely outside the step-change model (L-01) [@Saricioglu-2025]. A framework that predicted damage rankings here would be a framework detecting crises in general rather than the specific mechanism it claims, so the null is the outcome that supports the theory and a positive result would have undermined it. Result: Spearman {{LB-E3-covid-spearman}}, p {{LB-E3-covid-p}}, n {{LB-E3-covid-n}}, verdict {{LB-E3-covid-verdict}}; persistence dropped in {{LB-E3-persistence-direction-count}} of 17 sectors (majority {{LB-E3-persistence-direction-majority}}) - the falsifiable boundary direction confirmed. This is the paper's cleanest demonstration that the diagnostic is scoped rather than universal: it declines to fire on the most famous supply-chain disruption in living memory, because that disruption is not the kind of event it prices.

### 6.3 Rolling 34-Year Validation

The primary falsifier: rolling out-of-sample D predicts subsequent inventory-to-sales deviation at the panel level across regime-oscillating sectors (amended rule B, pooled statistic) [@Cachon-2007]. Result: pooled mean Spearman {{LB-E1-panel-spearman}}, joint block-bootstrap panel p {{LB-E1-panel-p}} over {{LB-E1-panel-n-oscillating}} oscillating sectors ({{LB-E1-panel-n-chronic}} chronic-boundary), verdict {{LB-E1-panel-verdict}}; per-sector range {{LB-E1-range-min}} to {{LB-E1-range-max}} (descriptive). The estimator choice is justified by the supplementary OLS-vs-YW comparison (OLS bias {{LB-T1-estimator-ols}} vs Yule-Walker bias {{LB-T1-estimator-yw}}; OLS less biased: {{LB-T1-estimator-ols-less-biased}}; labeled not-a-theorem). Table TBL-2 reports per-sector detail.

<!-- anchor: TBL-2 -->

*Table TBL-2. Rolling 34-year out-of-sample validation, per sector: full-sample regime class, Spearman between trailing D and forward deviation, and the descriptive one-sided block-bootstrap p (alpha 0.05 reference; the verdict is panel-level, not per-sector). Panel result: {{LB-E1-panel-n-oscillating}} oscillating sectors ({{LB-E1-panel-n-chronic}} chronic-boundary), pooled mean Spearman {{LB-E1-panel-spearman}}, joint panel p {{LB-E1-panel-p}}, verdict {{LB-E1-panel-verdict}}; per-sector Spearman range {{LB-E1-range-min}} to {{LB-E1-range-max}} (descriptive). Estimator footnote: OLS AR(1) bias {{LB-T1-estimator-ols}} vs Yule-Walker {{LB-T1-estimator-yw}}; OLS less biased: {{LB-T1-estimator-ols-less-biased}} (supplementary, not-a-theorem).*

| Sector | Regime class | Spearman | p (descriptive) |
| --- | --- | --- | --- |
| {{LB-E1-tbl2-r01-sector}} | {{LB-E1-tbl2-r01-class}} | {{LB-E1-tbl2-r01-spearman}} | {{LB-E1-tbl2-r01-p}} |
| {{LB-E1-tbl2-r02-sector}} | {{LB-E1-tbl2-r02-class}} | {{LB-E1-tbl2-r02-spearman}} | {{LB-E1-tbl2-r02-p}} |
| {{LB-E1-tbl2-r03-sector}} | {{LB-E1-tbl2-r03-class}} | {{LB-E1-tbl2-r03-spearman}} | {{LB-E1-tbl2-r03-p}} |
| {{LB-E1-tbl2-r04-sector}} | {{LB-E1-tbl2-r04-class}} | {{LB-E1-tbl2-r04-spearman}} | {{LB-E1-tbl2-r04-p}} |
| {{LB-E1-tbl2-r05-sector}} | {{LB-E1-tbl2-r05-class}} | {{LB-E1-tbl2-r05-spearman}} | {{LB-E1-tbl2-r05-p}} |
| {{LB-E1-tbl2-r06-sector}} | {{LB-E1-tbl2-r06-class}} | {{LB-E1-tbl2-r06-spearman}} | {{LB-E1-tbl2-r06-p}} |
| {{LB-E1-tbl2-r07-sector}} | {{LB-E1-tbl2-r07-class}} | {{LB-E1-tbl2-r07-spearman}} | {{LB-E1-tbl2-r07-p}} |
| {{LB-E1-tbl2-r08-sector}} | {{LB-E1-tbl2-r08-class}} | {{LB-E1-tbl2-r08-spearman}} | {{LB-E1-tbl2-r08-p}} |
| {{LB-E1-tbl2-r09-sector}} | {{LB-E1-tbl2-r09-class}} | {{LB-E1-tbl2-r09-spearman}} | {{LB-E1-tbl2-r09-p}} |
| {{LB-E1-tbl2-r10-sector}} | {{LB-E1-tbl2-r10-class}} | {{LB-E1-tbl2-r10-spearman}} | {{LB-E1-tbl2-r10-p}} |
| {{LB-E1-tbl2-r11-sector}} | {{LB-E1-tbl2-r11-class}} | {{LB-E1-tbl2-r11-spearman}} | {{LB-E1-tbl2-r11-p}} |
| {{LB-E1-tbl2-r12-sector}} | {{LB-E1-tbl2-r12-class}} | {{LB-E1-tbl2-r12-spearman}} | {{LB-E1-tbl2-r12-p}} |
| {{LB-E1-tbl2-r13-sector}} | {{LB-E1-tbl2-r13-class}} | {{LB-E1-tbl2-r13-spearman}} | {{LB-E1-tbl2-r13-p}} |
| {{LB-E1-tbl2-r14-sector}} | {{LB-E1-tbl2-r14-class}} | {{LB-E1-tbl2-r14-spearman}} | {{LB-E1-tbl2-r14-p}} |
| {{LB-E1-tbl2-r15-sector}} | {{LB-E1-tbl2-r15-class}} | {{LB-E1-tbl2-r15-spearman}} | {{LB-E1-tbl2-r15-p}} |
| {{LB-E1-tbl2-r16-sector}} | {{LB-E1-tbl2-r16-class}} | {{LB-E1-tbl2-r16-spearman}} | {{LB-E1-tbl2-r16-p}} |
| {{LB-E1-tbl2-r17-sector}} | {{LB-E1-tbl2-r17-class}} | {{LB-E1-tbl2-r17-spearman}} | {{LB-E1-tbl2-r17-p}} |


### 6.4 Beer Game Monte Carlo

Acting on the diagnostic saves cost within this experiment's own construction (L-03 binds; the source's ERP figure is not carried) [@Oroojlooyjadid-2022]. Base-stock comparator {{LB-E4-erp}}; phi-gated spectral tool {{LB-E4-tool}} (relative reduction {{LB-E4-tool-relreduction}}, paired p {{LB-E4-tool-p}}, verdict {{LB-E4-tool-verdict}}); full theorem {{LB-E4-full}}; win rate {{LB-E4-winrate}}; engagement boundary {{LB-E4-tool-phi-engagement}} (a property of this construction). Table TBL-3 reports costs by algorithm.

<!-- anchor: TBL-3 -->

*Table TBL-3. Beer Game Monte Carlo, mean cost by algorithm with the paired comparison - a property of E4's own construction, model-bound per the audit (the source-fidelity claim is withdrawn; no external benchmark figure is carried).*

| Statistic | Value |
| --- | --- |
| Mean cost, self-calibrating base-stock (ERP-style baseline) | {{LB-E4-erp}} |
| Mean cost, phi-gated spectral damping (the tool) | {{LB-E4-tool}} |
| Mean cost, full theorem policy | {{LB-E4-full}} |
| Paired p, tool vs baseline | {{LB-E4-tool-p}} |
| Relative cost reduction, tool vs baseline | {{LB-E4-tool-relreduction}} |
| Verdict (pre-registered rule) | {{LB-E4-tool-verdict}} |
| Engagement persistence (phi at which the gate engages; a property of this construction) | {{LB-E4-tool-phi-engagement}} |
| Pairwise win rate, full theorem vs spectral | {{LB-E4-winrate}} |


## 7 Supply Chain Application

### 7.1 Bullwhip Instability Finding

The classical bullwhip literature explains amplification through informational and incentive channels: demand signal processing, order batching, rationing games, price promotions [@Lee-1997a; @Lee-1997b; @Chen-2000]. The measurement channel adds a structural one that operates even when every informational pathology has been eliminated. If measured persistence is high enough, a standard order-up-to policy driven by a trailing estimate is not merely amplifying - it is operating at or past its own stability boundary, and the amplification is a property of the control loop rather than of anyone's behavior. That is what the panel shows: manufacturing-aggregate mean rho {{LB-E5-persistence-mfg-meanrho-R}} (SPEC-R) and {{LB-E5-persistence-mfg-meanrho-M}} (SPEC-M). Under the primary specification the boundary is not a line these sectors occasionally cross; it is a line they operate above, which is the finding that shapes everything in Section 8.

### 7.2 Spectral Radius Ordering Tool

The practical form of the result is an ordering rule: estimate demand persistence from data a firm already has, compute the spectral radius its current window and feedback rate imply, and read off whether the loop sits below the boundary, above it, or close enough that a regime change would push it over. The rule inverts the same stability geometry as the region-inversion and eigenvalue precedents, but takes an estimated persistence as its input rather than a design parameter [@Warburton-2004; @Wang-2013; @Udenio-2017; @Gaalman-Disney-2009; @Boute-2006].

The input requirement is the binding constraint in practice, and it is stated as a scope condition rather than a caveat. S-4 sets the data floor: monthly frequency with at least 36 observations, 60 preferred. Below that floor the persistence estimate carries more sampling error than the boundary comparison can absorb, and the tool returns a number with no informational content. Quarterly filing data is insufficient - a limitation with immediate consequences for who can use this and on what data, taken up next.

### 7.3 Firm-Level Bookend

The data floor has a sharp institutional edge. The richest publicly available firm-level operating data - quarterly filings - cannot support the estimate the tool requires: a decade of quarterly observations yields roughly forty points, and the persistence estimate at that sample size is too noisy to place a firm relative to the boundary with any confidence. The consequence is a genuine limit on the diagnostic's reach rather than a temporary data-collection problem. Firms can run this analysis internally on their own monthly or weekly series; outside analysts working from public filings generally cannot, which is why every empirical result in this paper is sector-level rather than firm-level (S-4). (Conditional on the deferred EDGAR entry; any quoted figure will be ledgered.)

### 7.4 Cross-Sector Evidence

The rolling monitoring record is backward-looking and weaker than Section 6.3, and says so: it documents what a boundary dashboard would have displayed around the two crisis onsets, not lead-time predictivity (Section 6.3 carries the out-of-sample claim). The committed record is honest about direction: the monitor is reactive. Around the 2008-09 onset, under the crossing-informative specification, no sector sat above the boundary beforehand and none crossed before the onset ({{LB-E5-monitor-specm-gfc-precede-count}} pre-onset crossings); {{LB-E5-monitor-specm-gfc-crossing-count}} sectors crossed in the window, clustered two to five months after the onset - the manufacturing aggregate's status was {{LB-E5-monitor-specm-mfg-gfc-status}} with first crossing {{LB-E5-monitor-specm-mfg-gfc-first-crossing}}. Around the 2020-03 onset, {{LB-E5-monitor-specm-covid-crossing-count}} sectors crossed, of which {{LB-E5-monitor-specm-covid-precede-count}} nominally preceded the onset by one to two months (within monthly-data noise, not offered as warning); the manufacturing aggregate's status was {{LB-E5-monitor-specm-mfg-covid-status}} with first crossing {{LB-E5-monitor-specm-mfg-covid-first-crossing}}. Under the primary specification the boundary saturates as disclosed in advance: {{LB-E5-monitor-specr-gfc-above-throughout-count}} of seventeen sectors sat above the boundary throughout the GFC window and {{LB-E5-monitor-specr-covid-above-throughout-count}} throughout the COVID window, so episode-specific crossing information lives at the crossing-informative specification - the spec-conditionality of Section 8.1 again. Two characterizations follow. First, the sectors that cross in either crisis window are exactly the nine boundary-oscillating sectors of the Section 6.3 classification, and the sectors that never cross are exactly the never-crossing class: the panel's boundary-crossing action over thirty-four years concentrates in these two crisis windows (in part reflecting that the full-sample classification contains these episodes). Second, and on-theme: the instability monitor is itself a lagging measurement - it confirms regime shifts with a two-to-five-month lag rather than predicting them, which is this paper's thesis applied to its own dashboard.

### 7.5 Boundary Conditions

A diagnostic that is only ever tested where it works has not been tested. The four simulation studies in Appendix F were built to find the edges of this one, and they found four, each of which constrains the advice the paper is entitled to give [@Boute-2022].

The chain-length result is conditional, not universal. The source this rebuild replaces reported a crossover at long chains where the tool turns from harmful to beneficial; re-run at five times the seed count, that crossover holds only with capacity headroom, and in the tight-capacity cells the tool remains harmful at every chain length tested. More than half the source's grid was unresolved at its seed count, so what looked like a clean transition was a reading taken through noise. Pricing value behaves as a cliff rather than a slope: it is large where capacity strain is moderate and turns net-negative above a strain threshold, so a firm that adopts the raise rule without knowing which side of that cliff it occupies may be buying the harm rather than the benefit.

The pricing result is asymmetric, and the asymmetry is the practical content. On the raise side the benefit is real where capacity is strained. On the cut side it is not: recommending a price cut in response to a demand decrease produced negative value in every environment tested - low-persistence {{LB-E8-down-low_phi_shift_down-mean}}, mid-persistence {{LB-E8-down-mid_phi_shift_down-mean}}, persistent level shift {{LB-E8-down-level_shift_down_persistent-mean}}. Under the immediate-arithmetic demand model this study assumes, the defensible reading is narrow and one-directional: the persistence calculation offers operationally meaningful guidance on when NOT to cut prices, and no comparable licence to cut them.

The hysteresis result splits, and the split is the finding: the raise strategy survives permanent customer attrition in genuinely shifted, persistent regimes, and fails in noisy ones where the estimator's own variance drives the policy on and off. The mechanism behind the robust half is worth stating, because it explains a result that otherwise looks implausible. At the heaviest attrition tested the policy permanently loses a large fraction of the customer base and the benefit still holds, because the two effects are not commensurate: when capacity is genuinely strained, the stockout costs avoided by raising price exceed the revenue lost to departing customers by a margin wide enough to absorb substantial attrition. Where capacity is loose, that margin is thin, the same attrition dominates, and the policy turns harmful.

The fourth boundary is the sharpest, and the honest way to state it is as a comparison rather than a failure. Under drifting persistence the recipe is beaten by the crudest available alternative: a FIXED damping coefficient - no estimator, no persistence calculation, no recipe at all - outperforms both the estimator-driven policy and an oracle handed the true parameter at every step (paired contrasts {{LB-E12-oracle-legb-L8x18-fixedvsoracle}} and {{LB-E12-oracle-legb-L8x24-fixedvsoracle}} against the oracle, {{LB-E12-oracle-legb-L8x18-fixedvsols}} and {{LB-E12-oracle-legb-L8x24-fixedvsols}} against the estimator). That the oracle also loses is what makes the diagnosis specific: THE LIMITATION IS IN THE RECIPE, NOT THE ESTIMATOR. A policy that mapped persistence to damping under a stationarity assumption returns a coefficient optimal for the persistence value it was handed, not for the trajectory of values the system will actually traverse. If the remedy failed because measurement was noisy, better measurement would fix it; it does not, and no amount of estimator precision reaches a parameter that will not hold still (S-8, L-04).

The scope of that limitation is itself unresolved, and naming what was not tested is more useful than a general caveat: one trajectory shape was examined, and slow drift, square-wave oscillation, and sudden one-shot jumps were not. Whether the recipe-level failure reproduces across those shapes is open, and a recipe taking both the level of persistence and its rate of change as inputs - drawing on the companion work on adaptation rates and on trajectory detection - is the natural route to one that survives drift. That is identified as a direction, not claimed as a result.

Appendix F carries the four studies in full and Table TBL-7 reports every cell, including the unresolved ones. Scope conditions S-3 and S-5 and limits L-01 and L-03 bind here: these are simulation results, they bind the model rather than the world, and the generalization to deployed systems is a separate and weaker claim.

## 8 The CHIPS Act

### 8.1 Most Unstable Sectors

The graded pre-registered claim was DROPPED with a limited-resolution caveat [@Monch-2011]: on the valid mean-exceedance instrument the CHIPS-dependent sectors sit in the top-instability cluster but not distinguishably at its peak, and rank is spec-sensitive. Ranks: R4238 {{LB-E5-chips-rank-R-R4238}} (SPEC-R) / {{LB-E5-chips-rank-M-R4238}} (SPEC-M); A34SIS {{LB-E5-chips-rank-R-A34SIS}} / {{LB-E5-chips-rank-M-A34SIS}}; verdict {{LB-E5-chips-verdict}}. Table TBL-4 carries the full ranking.

<!-- anchor: TBL-4 -->

*Table TBL-4. Seventeen-sector cross-section, ranked by SPEC-R mean exceedance (the amended primary key). Share is the fraction of months rho > 1 under SPEC-R - near one for most sectors, the saturation record. Episode columns are the SPEC-M monitoring record (Section 7.4): status in the onset +/- 24-month window and the first upward-crossing month ("none" where no crossing occurred). CHIPS footnote: ranks R4238 {{LB-E5-chips-rank-R-R4238}} (SPEC-R) / {{LB-E5-chips-rank-M-R4238}} (SPEC-M), A34SIS {{LB-E5-chips-rank-R-A34SIS}} / {{LB-E5-chips-rank-M-A34SIS}}; graded verdict {{LB-E5-chips-verdict}}. Persistence footnote: manufacturing-aggregate mean rho {{LB-E5-persistence-mfg-meanrho-R}} (SPEC-R) / {{LB-E5-persistence-mfg-meanrho-M}} (SPEC-M).*

| Rank | Sector | Mean exceedance | Share > 1 | GFC (SPEC-M) | GFC first crossing | COVID (SPEC-M) | COVID first crossing |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | {{LB-E5-ranking-r01-sector}} | {{LB-E5-ranking-r01-meanexc}} | {{LB-E5-tbl4-r01-share}} | {{LB-E5-tbl4-r01-gfc-status}} | {{LB-E5-tbl4-r01-gfc-first}} | {{LB-E5-tbl4-r01-covid-status}} | {{LB-E5-tbl4-r01-covid-first}} |
| 2 | {{LB-E5-ranking-r02-sector}} | {{LB-E5-ranking-r02-meanexc}} | {{LB-E5-tbl4-r02-share}} | {{LB-E5-tbl4-r02-gfc-status}} | {{LB-E5-tbl4-r02-gfc-first}} | {{LB-E5-tbl4-r02-covid-status}} | {{LB-E5-tbl4-r02-covid-first}} |
| 3 | {{LB-E5-ranking-r03-sector}} | {{LB-E5-ranking-r03-meanexc}} | {{LB-E5-tbl4-r03-share}} | {{LB-E5-tbl4-r03-gfc-status}} | {{LB-E5-tbl4-r03-gfc-first}} | {{LB-E5-tbl4-r03-covid-status}} | {{LB-E5-tbl4-r03-covid-first}} |
| 4 | {{LB-E5-ranking-r04-sector}} | {{LB-E5-ranking-r04-meanexc}} | {{LB-E5-tbl4-r04-share}} | {{LB-E5-tbl4-r04-gfc-status}} | {{LB-E5-tbl4-r04-gfc-first}} | {{LB-E5-tbl4-r04-covid-status}} | {{LB-E5-tbl4-r04-covid-first}} |
| 5 | {{LB-E5-ranking-r05-sector}} | {{LB-E5-ranking-r05-meanexc}} | {{LB-E5-tbl4-r05-share}} | {{LB-E5-tbl4-r05-gfc-status}} | {{LB-E5-tbl4-r05-gfc-first}} | {{LB-E5-tbl4-r05-covid-status}} | {{LB-E5-tbl4-r05-covid-first}} |
| 6 | {{LB-E5-ranking-r06-sector}} | {{LB-E5-ranking-r06-meanexc}} | {{LB-E5-tbl4-r06-share}} | {{LB-E5-tbl4-r06-gfc-status}} | {{LB-E5-tbl4-r06-gfc-first}} | {{LB-E5-tbl4-r06-covid-status}} | {{LB-E5-tbl4-r06-covid-first}} |
| 7 | {{LB-E5-ranking-r07-sector}} | {{LB-E5-ranking-r07-meanexc}} | {{LB-E5-tbl4-r07-share}} | {{LB-E5-tbl4-r07-gfc-status}} | {{LB-E5-tbl4-r07-gfc-first}} | {{LB-E5-tbl4-r07-covid-status}} | {{LB-E5-tbl4-r07-covid-first}} |
| 8 | {{LB-E5-ranking-r08-sector}} | {{LB-E5-ranking-r08-meanexc}} | {{LB-E5-tbl4-r08-share}} | {{LB-E5-tbl4-r08-gfc-status}} | {{LB-E5-tbl4-r08-gfc-first}} | {{LB-E5-tbl4-r08-covid-status}} | {{LB-E5-tbl4-r08-covid-first}} |
| 9 | {{LB-E5-ranking-r09-sector}} | {{LB-E5-ranking-r09-meanexc}} | {{LB-E5-tbl4-r09-share}} | {{LB-E5-tbl4-r09-gfc-status}} | {{LB-E5-tbl4-r09-gfc-first}} | {{LB-E5-tbl4-r09-covid-status}} | {{LB-E5-tbl4-r09-covid-first}} |
| 10 | {{LB-E5-ranking-r10-sector}} | {{LB-E5-ranking-r10-meanexc}} | {{LB-E5-tbl4-r10-share}} | {{LB-E5-tbl4-r10-gfc-status}} | {{LB-E5-tbl4-r10-gfc-first}} | {{LB-E5-tbl4-r10-covid-status}} | {{LB-E5-tbl4-r10-covid-first}} |
| 11 | {{LB-E5-ranking-r11-sector}} | {{LB-E5-ranking-r11-meanexc}} | {{LB-E5-tbl4-r11-share}} | {{LB-E5-tbl4-r11-gfc-status}} | {{LB-E5-tbl4-r11-gfc-first}} | {{LB-E5-tbl4-r11-covid-status}} | {{LB-E5-tbl4-r11-covid-first}} |
| 12 | {{LB-E5-ranking-r12-sector}} | {{LB-E5-ranking-r12-meanexc}} | {{LB-E5-tbl4-r12-share}} | {{LB-E5-tbl4-r12-gfc-status}} | {{LB-E5-tbl4-r12-gfc-first}} | {{LB-E5-tbl4-r12-covid-status}} | {{LB-E5-tbl4-r12-covid-first}} |
| 13 | {{LB-E5-ranking-r13-sector}} | {{LB-E5-ranking-r13-meanexc}} | {{LB-E5-tbl4-r13-share}} | {{LB-E5-tbl4-r13-gfc-status}} | {{LB-E5-tbl4-r13-gfc-first}} | {{LB-E5-tbl4-r13-covid-status}} | {{LB-E5-tbl4-r13-covid-first}} |
| 14 | {{LB-E5-ranking-r14-sector}} | {{LB-E5-ranking-r14-meanexc}} | {{LB-E5-tbl4-r14-share}} | {{LB-E5-tbl4-r14-gfc-status}} | {{LB-E5-tbl4-r14-gfc-first}} | {{LB-E5-tbl4-r14-covid-status}} | {{LB-E5-tbl4-r14-covid-first}} |
| 15 | {{LB-E5-ranking-r15-sector}} | {{LB-E5-ranking-r15-meanexc}} | {{LB-E5-tbl4-r15-share}} | {{LB-E5-tbl4-r15-gfc-status}} | {{LB-E5-tbl4-r15-gfc-first}} | {{LB-E5-tbl4-r15-covid-status}} | {{LB-E5-tbl4-r15-covid-first}} |
| 16 | {{LB-E5-ranking-r16-sector}} | {{LB-E5-ranking-r16-meanexc}} | {{LB-E5-tbl4-r16-share}} | {{LB-E5-tbl4-r16-gfc-status}} | {{LB-E5-tbl4-r16-gfc-first}} | {{LB-E5-tbl4-r16-covid-status}} | {{LB-E5-tbl4-r16-covid-first}} |
| 17 | {{LB-E5-ranking-r17-sector}} | {{LB-E5-ranking-r17-meanexc}} | {{LB-E5-tbl4-r17-share}} | {{LB-E5-tbl4-r17-gfc-status}} | {{LB-E5-tbl4-r17-gfc-first}} | {{LB-E5-tbl4-r17-covid-status}} | {{LB-E5-tbl4-r17-covid-first}} |


### 8.2 Capacity Utilization Threshold

The pre-registered hypothesis was a knee: as utilization climbs toward capacity, slack disappears, and the loop should cross from stable to unstable somewhere around the 85-to-90 percent band. It is a reasonable expectation and it is the one the planning literature would predict [@Hopp-Spearman-2008; @Nepal-2012].

It could not be adjudicated, and the reason matters more than the outcome. NAICS 334 runs persistently above the instability boundary at every utilization level - chronically unstable rather than utilization-triggered - so the stable side of the proposed knee is never occupied in this sample. A test that needs a contrast between two regimes cannot deliver a verdict when the data only ever visits one of them: it could not have produced support no matter what the truth was, which makes it non-severe by construction rather than negative in result. Reporting it as a refutation would be a category error in the opposite direction, manufacturing a finding out of an instrument's blind spot. The honest status is inconclusive, and the empirical demonstration of L-02 is exactly this: chronically-unstable sectors require steady-state analysis, not threshold-crossing analysis. Bin means {{LB-E6-threshold-bin1-lt75-mean}} / {{LB-E6-threshold-bin2-75-85-mean}} / {{LB-E6-threshold-bin3-85-90-mean}} / {{LB-E6-threshold-bin4-ge90-mean}} (n {{LB-E6-threshold-bin1-lt75-n}} / {{LB-E6-threshold-bin2-75-85-n}} / {{LB-E6-threshold-bin3-85-90-n}} / {{LB-E6-threshold-bin4-ge90-n}}); the pre-registered rule's outcome {{LB-E6-threshold-rule-outcome}} is reported alongside, not as the finding. Current utilization {{LB-E6-current-utilization}} ({{LB-E6-current-month}}), context only. Table TBL-6 shows the flat above-boundary band.

<!-- anchor: TBL-6 -->

*Table TBL-6. Semiconductor (NAICS 334) mean rho by capacity-utilization bin - an estimate/characterization, not a threshold-crossing table: the band sits entirely above the boundary at every utilization level, so no capacity knee is detectable in this statistic and NO verdict is attached (the pre-registered rule's outcome, {{LB-E6-threshold-rule-outcome}}, is reported alongside, not as the finding). Current reading, as context only: utilization {{LB-E6-current-utilization}} ({{LB-E6-current-month}}).*

| Utilization bin (%) | Mean rho | n (months) |
| --- | --- | --- |
| below 75 | {{LB-E6-threshold-bin1-lt75-mean}} | {{LB-E6-threshold-bin1-lt75-n}} |
| 75 to 85 | {{LB-E6-threshold-bin2-75-85-mean}} | {{LB-E6-threshold-bin2-75-85-n}} |
| 85 to 90 | {{LB-E6-threshold-bin3-85-90-mean}} | {{LB-E6-threshold-bin3-85-90-n}} |
| 90 and above | {{LB-E6-threshold-bin4-ge90-mean}} | {{LB-E6-threshold-bin4-ge90-n}} |


### 8.3 Complexity Drives Persistence

Why should some sectors carry structurally higher persistence than others? The complexity literature supplies the mechanism: products with many interdependent components, networks with many tiers, and supply bases with dense interconnection propagate a disturbance through more paths and hold it longer [@Bozarth-2009; @Novak-Eppinger-2001; @Choi-2001; @Serdarasan-2013; @Anderson-2000; @Ning-2023]. In this paper's terms, complexity is a mechanism for persistence, and persistence is the input to the damage bound - which is why the sectors this framework ranks as structurally unstable and the sectors that literature identifies as structurally complex are substantially the same sectors, arrived at from different directions. The connection is offered as a coherence check on the ranking, not as a tested causal claim; no experiment here estimates complexity or its effect on rho.

### 8.4 Werner-CHIPS Nexus

One financing question follows naturally and is raised here as exploration rather than result. If a supplier ecosystem's instability is structural, stabilizing it requires investment in the tiers that carry the persistence, not only in the visible final-assembly stage - and the composition of credit, not merely its quantity, determines whether such investment happens. The directed-credit tradition argues exactly this, that where newly created credit is channeled shapes real outcomes in ways aggregate monetary measures conceal [@Werner-1997; @Werner-2005; @Werner-2014a; @Werner-2014b], and recent work on industrial-policy financing raises the same composition question for semiconductor programs specifically [@Alfaro-2025; @Ahn-Tan-2025]. Whether that channel operates as the tradition claims is well outside anything this paper tests; the nexus is flagged as a direction, explicitly labeled exploratory, and carries no ledgered quantity.

## 9 Cross-Domain Extensions

Suggestive readings only; S-7 states that feedback strengths are assumption-driven proxies, and L-05 bounds every claim in this section.

### 9.1 Sovereign Ratings

The pre-registered conditional-instability reading fired WITHDRAWN: the stationarity precondition fails at the extreme [@Ferri-1999]. Characterization: {{LB-E10-calm-n-stationary}} of 18 countries in a tight near-unit band (phi {{LB-E10-calm-phi-min}} to {{LB-E10-calm-phi-max}}, calm rho {{LB-E10-calm-rho-min}} to {{LB-E10-calm-rho-max}}, all below 1); explosive {{LB-E10-calm-explosive}}; dual-implementation guard {{LB-E10-calm-guard-dualimpl}}; the crossing sweep is the withdrawn branch ({{LB-E10-crisis-reading}}). Table TBL-5 carries the country panel.

<!-- anchor: TBL-5 -->

*Table TBL-5. Sovereign debt panel (18 countries, JST): detrended AR(1) persistence, calm-regime rho, and pair counts - presented as a characterization with the withdrawn reading, not as a crossing table. Stationary countries: {{LB-E10-calm-n-stationary}} of 18, phi range {{LB-E10-calm-phi-min}} to {{LB-E10-calm-phi-max}}, calm rho range {{LB-E10-calm-rho-min}} to {{LB-E10-calm-rho-max}}; explosive detrended estimates: {{LB-E10-calm-explosive}}. Dual-implementation guard: max disagreement {{LB-E10-calm-guard-dualimpl}}. Crisis branch: {{LB-E10-crisis-reading}}.*

| Country | phi (detrended) | rho (calm) | n pairs |
| --- | --- | --- | --- |
| {{LB-E10-tbl5-r01-country}} | {{LB-E10-tbl5-r01-phi}} | {{LB-E10-tbl5-r01-rho}} | {{LB-E10-tbl5-r01-npairs}} |
| {{LB-E10-tbl5-r02-country}} | {{LB-E10-tbl5-r02-phi}} | {{LB-E10-tbl5-r02-rho}} | {{LB-E10-tbl5-r02-npairs}} |
| {{LB-E10-tbl5-r03-country}} | {{LB-E10-tbl5-r03-phi}} | {{LB-E10-tbl5-r03-rho}} | {{LB-E10-tbl5-r03-npairs}} |
| {{LB-E10-tbl5-r04-country}} | {{LB-E10-tbl5-r04-phi}} | {{LB-E10-tbl5-r04-rho}} | {{LB-E10-tbl5-r04-npairs}} |
| {{LB-E10-tbl5-r05-country}} | {{LB-E10-tbl5-r05-phi}} | {{LB-E10-tbl5-r05-rho}} | {{LB-E10-tbl5-r05-npairs}} |
| {{LB-E10-tbl5-r06-country}} | {{LB-E10-tbl5-r06-phi}} | {{LB-E10-tbl5-r06-rho}} | {{LB-E10-tbl5-r06-npairs}} |
| {{LB-E10-tbl5-r07-country}} | {{LB-E10-tbl5-r07-phi}} | {{LB-E10-tbl5-r07-rho}} | {{LB-E10-tbl5-r07-npairs}} |
| {{LB-E10-tbl5-r08-country}} | {{LB-E10-tbl5-r08-phi}} | {{LB-E10-tbl5-r08-rho}} | {{LB-E10-tbl5-r08-npairs}} |
| {{LB-E10-tbl5-r09-country}} | {{LB-E10-tbl5-r09-phi}} | {{LB-E10-tbl5-r09-rho}} | {{LB-E10-tbl5-r09-npairs}} |
| {{LB-E10-tbl5-r10-country}} | {{LB-E10-tbl5-r10-phi}} | {{LB-E10-tbl5-r10-rho}} | {{LB-E10-tbl5-r10-npairs}} |
| {{LB-E10-tbl5-r11-country}} | {{LB-E10-tbl5-r11-phi}} | {{LB-E10-tbl5-r11-rho}} | {{LB-E10-tbl5-r11-npairs}} |
| {{LB-E10-tbl5-r12-country}} | {{LB-E10-tbl5-r12-phi}} | {{LB-E10-tbl5-r12-rho}} | {{LB-E10-tbl5-r12-npairs}} |
| {{LB-E10-tbl5-r13-country}} | {{LB-E10-tbl5-r13-phi}} | {{LB-E10-tbl5-r13-rho}} | {{LB-E10-tbl5-r13-npairs}} |
| {{LB-E10-tbl5-r14-country}} | {{LB-E10-tbl5-r14-phi}} | {{LB-E10-tbl5-r14-rho}} | {{LB-E10-tbl5-r14-npairs}} |
| {{LB-E10-tbl5-r15-country}} | {{LB-E10-tbl5-r15-phi}} | {{LB-E10-tbl5-r15-rho}} | {{LB-E10-tbl5-r15-npairs}} |
| {{LB-E10-tbl5-r16-country}} | {{LB-E10-tbl5-r16-phi}} | {{LB-E10-tbl5-r16-rho}} | {{LB-E10-tbl5-r16-npairs}} |
| {{LB-E10-tbl5-r17-country}} | {{LB-E10-tbl5-r17-phi}} | {{LB-E10-tbl5-r17-rho}} | {{LB-E10-tbl5-r17-npairs}} |
| {{LB-E10-tbl5-r18-country}} | {{LB-E10-tbl5-r18-phi}} | {{LB-E10-tbl5-r18-rho}} | {{LB-E10-tbl5-r18-npairs}} |


### 9.2 Unemployment Insurance

The pre-registered procyclical-feedback reading fired WITHDRAWN [@Anderson-Meyer-1994; @Woodbury-2004]. Characterization: pooled normal-period phi {{LB-E11-normal-phi}} (n {{LB-E11-normal-n}}), rho {{LB-E11-normal-rho-min}} to {{LB-E11-normal-rho-max}} across all nine combinations, all below 1; jurisdictions {{LB-E11-normal-jur-phi-min}} to {{LB-E11-normal-jur-phi-max}} (median {{LB-E11-normal-jur-phi-median}}); pooled GFC phi {{LB-E11-gfc-phi}} (n {{LB-E11-gfc-n}}) sits far below the boundary corner {{LB-E11-gfc-corner}} and is statistically indistinguishable from normal; reading {{LB-E11-gfc-reading}} - consistent with the cited counterpoint [@Fath-Fuest-2002] and rhyming with the COVID finding: crises in these systems arrive as level shocks, not persistence explosions.

## 10 Implications for Institutional Design

### 10.1 Three-Parameter Audit

Stripped to essentials, the diagnostic asks an institution three questions. How persistent is the variable you are steering (phi)? How long is the window you steer by (W)? How hard do you push on the gap (bg)? Those three numbers determine the spectral radius, the spectral radius determines whether deviations decay or compound, and the pair (rho, tau) determines what a regime change costs while your measurement catches up. EQ-2 and EQ-5 are the instruments: the first prices the blind period, the second says whether the loop is stable at all.

The audit's value is that all three parameters are observable to the institution itself, and two of them are policy choices. An organization that cannot change how persistent its environment is can still change how long it looks and how hard it reacts - and the framework says precisely which of those levers is worth pulling in which conditions. This is also why the audit belongs in the safety-boundary tradition rather than the forecasting one: the question is not what will happen, but how far the current operating point sits from a boundary past which the institution's own control actions amplify rather than dampen [@Rasmussen-1997; @Dekker-2011].

### 10.2 Reverse-Engineering Principle

The bound runs in both directions. Forward, it prices damage from known loop parameters. Backward, an observed damage pattern constrains the parameters that could have produced it: a deviation that persisted for a known number of periods and grew by a known factor implies a range of (rho, tau) pairs, and tau implies a measurement window. An institution that does not know its own effective window - a common situation, since windows are often embedded in inherited procedures, vendor defaults, and reporting cadences rather than chosen deliberately - can therefore infer it from its own crisis history.

The inference is coarse and this paper does not test it; it is stated as a principle the identity licenses, not as a validated method. But it points at the practical failure the framework is ultimately about. Institutions rarely decide their measurement windows. They inherit them, and then discover during a regime change what the inheritance costs.

### 10.3 Domain Interventions

Ranking interventions by which parameter they move clarifies why some familiar remedies underperform. Interventions that shorten the window (faster reporting, higher-frequency data, nowcasting) attack tau directly and pay off exponentially, because tau sits in the exponent. Interventions that reduce feedback aggressiveness (damping, smoothing, rate limits) lower rho and can move a loop back inside the stability boundary, but they trade responsiveness for stability and Section 7.5 states the conditions under which that trade is worth making. Interventions that reduce underlying persistence (supply-base simplification, buffer capacity, demand pooling) are the most durable and the slowest to implement, since they change the environment rather than the controller.

Two cautions carry from this paper's own results and are not optional. First, the ordering above assumes the regime change is of the kind the theorem prices; the COVID episode shows that compound shocks in the opposite direction are outside it. Second, the simulation studies in Appendix F show that the framework's own remedy - adapting the damping to estimated persistence - is harmful in conditions the theory does not cover, specifically when persistence itself is drifting rather than stepping (S-8). An institution that adopts the diagnostic without adopting its scope conditions has bought a tool that will fire confidently in exactly the circumstances where it is wrong.

## 11 Forward Prediction: Self-Service Diagnostic

This section states the paper's two dated, falsifiable forward predictions - standing claims about post-publication outcomes, the one validator that routes around both author and reviewer. Every protocol constant below is a ledger row emitted by the committed registration generator (verification path: the same machinery that polices every other number in this paper); registration date {{LB-FP-diagnostic-registered}}, carry-forward horizon {{LB-FP-diagnostic-horizon}}.

### 11.1 The Predictions

PREDICTION A (self-service diagnostic; carried from the pinned source, locked April 2026, restated and re-registered at this rebuild's commit). Any firm can compute the closed-loop spectral radius rho from three quantities it already has: its estimated demand persistence phi (estimator {{LB-FP-diagnostic-estimator}} - the paper's pre-registered choice, Section 6.3), its measurement window W, and its feedback gain, via the companion-matrix construction of EQ-1. The standing claim: rho above the threshold {{LB-FP-diagnostic-threshold}} implies the firm's response to its next demand shock AMPLIFIES (bullwhip); rho below it implies the response DECAYS. A public calculator implements the computation at {{LB-FP-diagnostic-calculator-url}}.

PREDICTION B (sector-level two-class bet; new at this rebuild, registered at publication). The paper's committed rolling construction (Section 6.3) partitions the seventeen-sector panel into {{LB-FP-diagnostic-n-flagged}} boundary-crossing ("oscillating") sectors and {{LB-FP-diagnostic-n-decay}} never-crossing sectors; the class lists are extracted mechanically from the committed output and registered verbatim (flagged: {{LB-FP-diagnostic-flagged-sectors}}; never-crossing: {{LB-FP-diagnostic-decay-sectors}}). The standing claim: at the trigger event, the flagged class shows amplifying inventory/sales responses exceeding the never-crossing class under the registered metric and test. Honesty note, registered as part of the claim: under this committed construction the CHIPS-dependent computers/electronics sector sits in the NEVER-CROSSING class while wholesale machinery sits in the flagged class - an earlier informal sketch that named both CHIPS sectors as flagged is superseded by the committed classification, and the spec-sensitivity of such flags is itself one of this paper's findings (Section 8.1).

### 11.2 Protocol

A forward prediction is only as good as the ambiguity it removes in advance. Someone checking this claim years from now must be able to compute the answer without asking the author what was meant, which means every degree of freedom - when the clock starts, what is measured, over what window, against what baseline, and by which test - is fixed here rather than chosen later. Each constant below is a ledger row generated by a committed script and re-verified on every run, so the registration cannot drift even by accident.

Trigger: {{LB-FP-diagnostic-trigger}}. Metric: peak absolute deviation of log inventory/sales from its pre-onset baseline mean within {{LB-FP-diagnostic-metric-window-months}} months of onset, normalized by the pre-onset {{LB-FP-diagnostic-baseline-months}}-month baseline standard deviation, per sector, from the same public monthly series the paper uses (Appendix A). Test: {{LB-FP-diagnostic-test}} at alpha {{LB-FP-diagnostic-alpha}}.

Three choices deserve their reasons on the record. The metric is normalized by each sector's own pre-onset variability rather than compared in raw units, because sectors differ by an order of magnitude in how much their inventory ratios ordinarily move, and an unnormalized comparison would rank them by volatility rather than by the effect the prediction is about. The test is rank-based rather than parametric, because with class sizes in single digits no distributional assumption is credible and a rank test needs none. And the onset date is taken from an external authority rather than chosen by inspection, which removes the one degree of freedom most easily abused after the fact.

### 11.3 Registration

Both predictions are registered publicly at the review stage alongside this paper's release, and scored publicly as data accrues; the registered constants above are byte-verified against the committed generator on every verification run.

Public registration is the point rather than a formality. Every other check in this paper - the ledger, the code-integrity review, the machine-verified proofs, the adversarial read - is a check the author commissioned and could in principle have shaped. A dated claim about events that have not happened yet is the one validator that routes around both the author and the reviewer, because the world scores it and neither party gets a say. That is also why the constants are ledgered rather than typed: a registration whose terms can be quietly edited after the fact is not a registration, and tying every number to a committed generator makes the edit visible if anyone attempts it.

The sector classification these predictions rest on was fixed by an earlier experiment and is reproduced from that experiment's committed output, not re-derived here. Its membership is public in Table TBL-2, so the two classes can be read off before any trigger occurs rather than assembled afterward.

### 11.4 Falsification Conditions

Prediction A is falsified by systematic decay in above-threshold systems or amplification in below-threshold systems under the stated computation. Prediction B is falsified if, at the trigger event, the flagged class does NOT exceed the never-crossing class under the registered metric and test - a genuine two-sided exposure, since the never-crossing class is non-empty and includes a CHIPS-dependent sector. If no qualifying trigger occurs before {{LB-FP-diagnostic-horizon}}, the bet is untestable and carries forward, re-registered, dated.

Two outcomes are explicitly NOT falsifications, and saying so now prevents the boundary being redrawn later. A trigger event in which both classes deviate substantially, with the flagged class higher, supports the prediction even if the absolute magnitudes are large everywhere - the claim is comparative, not about levels. Conversely, a quiet period in which neither class moves is uninformative rather than confirming: the prediction earns nothing from an absence of stress, and a scorer should record it as untested rather than as a pass. The honest failure mode for a comparative claim is a coin-flip result under stress, and that is the one the test above is built to detect.

## 12 Conclusion

An institution that measures a persistent variable over a window and steers on the result is exposed to a cost it usually does not price. When the underlying regime shifts, its estimator keeps describing the world that has gone, and for the length of that blind period the institution applies a rule calibrated to conditions that no longer hold, to a system whose deviations are now compounding. C-01: blind-period damage is governed by intensity x duration, D = (rho_2/rho_1)^tau, computable from quantities institutions already estimate. That the two factors multiply rather than add is the whole content of the warning - a modest rise in instability paired with a long measurement window produces a cost neither factor predicts alone.

Two consequences follow directly. C-02: a unique optimal measurement window W* exists in closed form, so the length of a trailing average is a solvable question rather than a matter of convention. C-03: under regime-change risk the optimal operating point sits below the pi^2/2 limit, because a boundary computed for today's conditions offers no protection against tomorrow's if the institution will be blind while they change.

The empirical record is mixed in the way an honest record usually is. The rolling out-of-sample panel test - the pre-registered falsifier, and the only experiment entitled to that word - passed. The global financial crisis corroborated it; COVID did not, and was not expected to. C-04: acting on the diagnostic reduces cost against a rational self-calibrating base-stock baseline within the simulated environment. C-05: the CHIPS-dependent sectors are among the more structurally unstable, though not the two most, with measurement-sensitive ranking. C-06: semiconductor instability is structural rather than utilization-triggered, so a utilization tripwire is not an available monitoring benchmark.

The boundaries are stated with the same weight as the results, because a diagnostic whose failure modes are undocumented is not a diagnostic. L-01: compound shocks are excluded - the theorem prices a step change in the dangerous direction, and COVID was not one. L-02: chronically-unstable sectors need steady-state analysis rather than threshold-crossing analysis. L-03: simulation binds the model, and generalization to deployed systems is a separate, weaker claim. L-04: recipe-level non-stationarity is unresolved, with one trajectory shape tested - and an oracle given the true parameter does not rescue it, which forecloses better estimation as the fix. L-05: the cross-domain readings are suggestive only; two pre-registered extensions were withdrawn when their preconditions failed. L-06: the GFC episode is corroborating only. L-07: the pricing result is bounded by the immediate-arithmetic demand model.

Two further boundaries belong here rather than in a footnote, because they concern the paper's own instruments. The capacity-threshold test could not adjudicate its hypothesis in either direction and is reported as inconclusive rather than as a null. And the rolling monitoring record shows the paper's own instability dashboard confirming regime shifts two to five months after they begin rather than anticipating them - the thesis applied to its own apparatus. A framework that prices the cost of lagging measurement should expect to find that its own measurement lags, and saying so is not a concession but the argument working correctly.

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

Data sources and identifiers mirror the committed data registry; Table TBL-A lists them. Two points govern how that table should be read.

First, the registry rather than this table is authoritative. data/SOURCES.md is generated by the pull script and never hand-edited; it carries each file's exact identifier, byte count, SHA256, store path, and the per-source tolerance a replicator's own pull may differ within. Table TBL-A is a human-readable summary of that file and cannot override it. Where the two ever disagree, the registry is correct and the table is a defect.

Second, raw data is not committed. The repository's data layer is documentation: the pull script, the registry, and the hashes. The bytes themselves live in a project-local store outside the repository, because some are large and some carry licence terms that forbid redistribution. A replicator re-pulls from the named sources and checks their own files against the recorded hashes; for revisable series - and several here are revisable - a later pull will legitimately differ, which is why the registry records a tolerance per source rather than demanding bit-identity. Reproducibility is anchored to the pinned snapshot, not to a live re-fetch.

<!-- anchor: TBL-A -->
*Table TBL-A. Data sources and identifiers (provenance summary; the authoritative per-file registry - exact identifiers, byte counts, SHA256 hashes, store paths, and replicator tolerances - is the generated data/SOURCES.md, which this table mirrors and never supersedes).*

| Source group | Provider / identifier | Frequency | Used by |
| --- | --- | --- | --- |
| 17-member inventory/sales panel (7 manufacturing, 7 wholesale, 3 retail; frozen member map) | FRED (US Census / Fed), series ids per the frozen map in data/SOURCES.md | monthly, SA | E1, E2, E3, E5, monitoring record |
| Auxiliary series (audit-trail chemical products, aerospace inventories/shipments pair, three non-member wholesale lines) | FRED, per manifest | monthly, SA | audit / aux per manifest |
| Semiconductor capacity utilization | FRED CAPUTLG3344S | monthly, SA | E6 |
| Sovereign macrohistory panel (18 countries, 1870-2020) | Jorda-Schularick-Taylor Macrohistory, Release 6 | annual | E10 |
| Unemployment-insurance claims, all jurisdictions | US DOL ETA 539 | weekly | E11 |
| Source simulation sweep (9,000 trials; fixed in-house artifact) | aggregated chain-length sweep, source Phase 2.6 record | fixed artifact | E7 regression record; E12 leg B |

## Appendix B: Validation and Robustness

Theorem machine-check detail (both legs per theorem, per the two-row rule) and estimator robustness supporting Section 4 and Section 6.3.

The two-row rule is the reason this table has the shape it does. Each theorem is checked twice by independent means: a symbolic step-check that re-derives the result in a computer algebra system and confirms each step follows, and a numeric stress test that evaluates the claim across a grid of parameter values and hunts for counterexamples. The two legs fail differently - a symbolic check catches an algebraic slip that numerics would average over, and a numeric check catches a claim that is formally derivable but false outside the region the derivation implicitly assumed - so each is registered as its own ledger row. A theorem cannot report a pass with a leg missing, because a missing row is a missing number and the gate refuses it.

Neither leg replaces the written proof. Both supplement it, and the written proofs live in Appendix G with the three-way record - written proof, symbolic leg, numeric leg, and the result of each - committed to the verification directory, whose existence the gate asserts on every run. The distinction matters because machine checks are only as good as the statement handed to them: they verify that a proposition holds, never that it is the proposition the paper needed. That judgement stays with the reader, which is why the proofs are printed in full rather than summarized.

One entry in the table is deliberately asymmetric. The safety-factor result is a proposition supported by numeric legs with its written companion carrying labeled approximations, not a theorem with a symbolic step-check; it is recorded that way rather than promoted to match its neighbours. The estimator comparison is likewise labeled a supplementary diagnostic and marked not-a-theorem, exempting it from the symbolic row by design rather than by omission.

*Machine verification of the formal results (both legs per theorem, per the two-row rule; the written proofs are Appendix G).*

| Result | Symbolic leg | Numeric leg |
| --- | --- | --- |
| THM-1 (boundary bound) | {{LB-T1-bound-symbolic}} | all-pass {{LB-T1-bound-numeric-allpass}}, counterexamples {{LB-T1-bound-numeric-counterexamples}}, in-domain {{LB-T1-bound-numeric-indomain}} |
| THM-2 (closed-form W*) | {{LB-T2-wstar-symbolic}} | brute-force match {{LB-T2-wstar-numeric-match}} at rate {{LB-T2-wstar-numeric-matchrate}}, unimodality failures {{LB-T2-wstar-numeric-unimodal-failures}} |
| THM-2 comparative statics (corrected re-derivation) | {{LB-T2-statics-symbolic}} | monotonicity failures: phi {{LB-T2-statics-numeric-monophi-fail}}, bg {{LB-T2-statics-numeric-monobg-fail}} |
| THM-3 (adaptation-stability identity) | {{LB-THM3-symbolic}} | pass {{LB-THM3-numeric}}, dual-path checks {{LB-THM3-numeric-checked}} |
| Proposition k* (safety factor; numeric legs, written companion in Appendix G) | - | mfg argmin {{LB-T3-kstar-mfg-argmin}}, in-band {{LB-T3-kstar-inband}}, all-below-one {{LB-T3-kstar-allbelow1}}, verdict {{LB-T3-kstar-verdict}} |
| Estimator comparison (supplementary, not-a-theorem) | - | OLS bias {{LB-T1-estimator-ols}} vs Yule-Walker {{LB-T1-estimator-yw}}; OLS less biased {{LB-T1-estimator-ols-less-biased}} |


## Appendix C: Companion Matrix Spectral Radii by Domain

Cross-domain rho computations supporting Table TBL-4 and Table TBL-5. The construction is identical in every domain and only the inputs change: an estimated persistence, a window, and an assumed feedback strength generate a companion matrix whose spectral radius is computed directly. Two features of these computations require emphasis because they bound how the cross-domain numbers may be read.

The feedback strengths are assumption-driven proxies rather than estimates (S-7). Persistence is estimated from data in every domain, but bg - how hard the institution pushes on the measured gap - is not identified from the series, so the cross-domain radii are reported across a grid of feedback strengths rather than at a single fitted value. Consequently a cross-domain rho is a conditional statement of the form "at this feedback strength, this loop would sit here relative to the boundary," never a measurement of where an institution actually sits. The sovereign and unemployment-insurance readings in Section 9 are governed by this scope condition, and both pre-registered crossing claims were withdrawn when their preconditions failed, which is the honest consequence of taking the condition seriously rather than treating the grid as a set of estimates.

## Appendix D: Mitigation Effectiveness

Mitigation effectiveness under the damped policies, supporting Section 7.5. The relevant comparison is not whether a damped policy outperforms an undamped one on average, but whether it does so in the specific configuration an institution occupies - because the simulation studies establish that the answer changes sign across that space. Damping helps decisively in genuinely shifted, persistent regimes; it costs little in stationary conditions where the gate rarely engages; and it inflicts real harm in noisy environments where the estimator's own variance drives the gate on and off, and in drifting-persistence environments where no estimate of a stable parameter exists to gate on (S-8). The mitigation question is therefore inseparable from the diagnostic question: the value of acting depends on the same persistence structure the diagnostic is measuring, which is why this paper reports where the remedy fails at equal length to where it works.

## Appendix E: Beer Game Simulation Parameters

The frozen calibration behind Table TBL-3. The environment is a linear single-echelon core with the stated extensions and synthetic AR(1) demand, and the calibration was fixed before the comparison ran (S-5). The comparator deserves explicit note: the baseline is a self-calibrating base-stock policy, not a naive or deliberately weakened rule, because a diagnostic that only beats a straw policy demonstrates nothing about its value. The reported cost reduction is a property of this construction and this construction only. It is not a claim about deployed systems, and the audit that closed this experiment removed an inherited comparison to an external benchmark figure that could not be traced to its source (L-03).

## Appendix F: Additional Simulation Studies

Four studies map where the diagnostic's remedy helps and where it hurts: the chain-length sweep, the pricing analysis (S-6 states the pricing model scope; L-07 the limit), the hysteresis sweep, and the recipe-level non-stationarity analysis. Table TBL-7 carries every cell, including the unresolved ones.

These are reported as a series of bounded findings rather than as a single sweeping claim: each maps a region where the remedy helps or hurts, and none generalizes past the region it maps. Three conventions apply throughout and are worth stating once. Every comparison is paired: within a run, each algorithm faces the identical demand sequence, so a difference between algorithms is never a difference between draws. Every grid is reported in full rather than filtered to its significant cells - a grid reported selectively is a search presented as an experiment, and the counts of harm, benefit, and unresolved cells are themselves findings. And resolution is reported explicitly: a cell whose confidence interval spans zero is marked unresolved rather than assigned to whichever side its point estimate happens to fall on. That last convention is what exposed the source's headline chain-length crossover as a reading taken through noise, and it is applied here to this paper's own cells with equal force.

These are simulations. Their verdicts bind the model that produced them, and the step from model to deployed system is a separate and weaker claim (S-5, L-03).

<!-- anchor: TBL-7 -->

*Table TBL-7. The four Appendix F simulation studies, presented as their honest headlines: a capacity-conditional gradient map (not an unconditional crossover), a value cliff with withdrawn attribution, a resolved robust/fragile split, and the recipe-level non-stationarity result. Full grids with CIs and resolution flags live in the committed outputs.*

**Panel A - chain-length x capacity gradient (E7; ar1_high, tool-vs-disabled cost delta; positive = harm).** Grid counts: {{LB-E7-gradient-n-resolved}} of 36 cells resolved ({{LB-E7-gradient-n-harm}} harm, {{LB-E7-gradient-n-benefit}} benefit, {{LB-E7-gradient-n-unresolved}} unresolved).

| Capacity | L = 4 | L = 6 | L = 8 |
| --- | --- | --- | --- |
| 1.3x | {{LB-E7-gradient-cap13-ar1high-L4}} | {{LB-E7-gradient-cap13-ar1high-L6}} | {{LB-E7-gradient-cap13-ar1high-L8}} |
| 2.4x | {{LB-E7-gradient-cap24-ar1high-L4}} (resolved: {{LB-E7-gradient-cap24-ar1high-L4-resolved}}) | {{LB-E7-gradient-cap24-ar1high-L6}} (resolved: {{LB-E7-gradient-cap24-ar1high-L6-resolved}}) | {{LB-E7-gradient-cap24-ar1high-L8}} (resolved: {{LB-E7-gradient-cap24-ar1high-L8-resolved}}) |

**Panel B - resolution vs the source's 50-seed record (ar1_high x 2.4x; a regression check, not a calibration).**

| Cell | Ours (250 seeds) | Source (50 seeds) | Source inside our CI |
| --- | --- | --- | --- |
| L = 4 | {{LB-E7-calibration-L4-ours}} | {{LB-E7-calibration-L4-source}} | {{LB-E7-calibration-L4-source-in-ci}} |
| L = 6 | {{LB-E7-calibration-L6-ours}} | {{LB-E7-calibration-L6-source}} | {{LB-E7-calibration-L6-source-in-ci}} |
| L = 8 | {{LB-E7-calibration-L8-ours}} | {{LB-E7-calibration-L8-source}} | {{LB-E7-calibration-L8-source-in-ci}} |

**Panel C - pricing asymmetry (E8).** Raise side: claim A benefit {{LB-E8-up-claima-mean}} (CI {{LB-E8-up-claima-cipct-lo}} to {{LB-E8-up-claima-cipct-hi}} percent of the reacting-at-all benefit); claim B (formula attribution) {{LB-E8-up-claimb-mean}} at {{LB-E8-up-claimb-sigma}} sigma, verdict {{LB-E8-up-claimb-verdict}}; mean benefit by capacity {{LB-E8-up-cap18x-mean}} (1.8x) / {{LB-E8-up-cap24x-mean}} (2.4x) / {{LB-E8-up-cap30x-mean}} (3.0x). Cut side (mean, sigma): low-phi {{LB-E8-down-low_phi_shift_down-mean}} ({{LB-E8-down-low_phi_shift_down-sigma}}); mid-phi {{LB-E8-down-mid_phi_shift_down-mean}} ({{LB-E8-down-mid_phi_shift_down-sigma}}); persistent level shift {{LB-E8-down-level_shift_down_persistent-mean}} ({{LB-E8-down-level_shift_down_persistent-sigma}}).

**Panel D - hysteresis split (E9; raise benefit vs hysteresis intensity h; verdict {{LB-E9-verdict}}; fidelity {{LB-E9-fidelity-tier}}, max relative diff {{LB-E9-fidelity-maxreldiff}}).**

| h | Sticky environment (benefit, sigma) | Noisy environment (benefit, sigma) |
| --- | --- | --- |
| 0.0 | {{LB-E9-robust-h000-benefit}} ({{LB-E9-robust-h000-sigma}}) | {{LB-E9-fragile-h000-benefit}} ({{LB-E9-fragile-h000-sigma}}) |
| 0.1 | {{LB-E9-robust-h010-benefit}} ({{LB-E9-robust-h010-sigma}}) | {{LB-E9-fragile-h010-benefit}} ({{LB-E9-fragile-h010-sigma}}) |
| 0.3 | {{LB-E9-robust-h030-benefit}} ({{LB-E9-robust-h030-sigma}}) | {{LB-E9-fragile-h030-benefit}} ({{LB-E9-fragile-h030-sigma}}) |
| 0.6 | {{LB-E9-robust-h060-benefit}} ({{LB-E9-robust-h060-sigma}}) | {{LB-E9-fragile-h060-benefit}} ({{LB-E9-fragile-h060-sigma}}) |

**Panel E - recipe-level non-stationarity (E12; verdict {{LB-E12-oracle-verdict}}).** Oracle handed true phi: resolved harm in all nine drift cells: {{LB-E12-oracle-harm-all-drift}}; oracle mean delta {{LB-E12-oracle-L4x13-mean}} (L4 x 1.3x) and {{LB-E12-oracle-L8x24-mean}} (L8 x 2.4x); fixed-alpha at the long-chain locus {{LB-E12-oracle-fixed-L8x18-mean}} (L8 x 1.8x) / {{LB-E12-oracle-fixed-L8x24-mean}} (L8 x 2.4x). Paired 50-seed contrasts (leg B): fixed-vs-oracle {{LB-E12-oracle-legb-L8x18-fixedvsoracle}} / {{LB-E12-oracle-legb-L8x24-fixedvsoracle}}; fixed-vs-OLS {{LB-E12-oracle-legb-L8x18-fixedvsols}} / {{LB-E12-oracle-legb-L8x24-fixedvsols}}. Perfect-information paradox: oracle resolved-worse than the noisy OLS estimator in {{LB-E12-oracle-paradox-count}} of 9 drift cells; stationary-control inertness check {{LB-E12-oracle-winscheck}}.


## Appendix G: Proofs

Full written proofs for the paper's theorem-bearing claims, upgraded from the source's sketches per the theory-with-proofs archetype; where rigor forced a sharper statement than the sketch, the change is marked SHARPENED. Each theorem carries three verification legs - the written proof below, a symbolic step-check, and a numeric stress test - and the per-theorem results of all three are recorded in verification/proof_threeway.md.

### G.0 Standing Assumptions and Notation

(A1) DYNAMICS. The managed variable y_t follows AR(1) dynamics with persistence
phi in (0, 1): y_t = phi * y_{t-1} + epsilon_t, with epsilon_t zero-mean noise.
At t = 0 the true persistence steps from phi_1 to phi_2 with phi_2 > phi_1
(the dangerous direction).

(A2) CLOSED LOOP. A trailing-average estimator of window W >= 2 computes
y_bar_t = (1/W) * sum_{j=0}^{W-1} y_{t-j}; a feedback policy adjusts the system at
rate beta*gamma > 0 on the gap between y_bar_t and a target. The linearized closed
loop is the W x W companion matrix A(phi, W, beta*gamma) with the persistence and
feedback structure in its first row and an identity shift below. rho(A) denotes its
spectral radius. Write rho_1 = rho(A(phi_1, W, beta*gamma)) and
rho_2 = rho(A(phi_2, W, beta*gamma)).

(A3) MONOTONICITY. For fixed W and beta*gamma > 0, rho(A(phi, W, beta*gamma)) is
strictly increasing in phi. (Carried from the companion papers; verified numerically on the T1 grid - see the three-way record.)

(A4) DOMINANT-MODE DEVIATION (scope condition - SHARPENED from the sketch).
The damage state d_t >= 0 is the magnitude of the system deviation tracked along the
dominant mode of the closed loop: per cycle, the deviation is amplified by the
spectral radius of the matrix in force at that cycle, d_{t+1} = rho(A_t) * d_t,
where A_t is the closed-loop matrix under the policy in force at time t.
Remark G.0.1 states exactly what is and is not lost relative to full matrix
generality, and Lemma G.1 supplies the matrix-general bound.

(A5) ADAPTATION TIME. For the simple moving average, the estimator converges to
within detection tolerance epsilon of the new persistence in
tau(W) = W * (1 - epsilon/Delta_phi) periods, where Delta_phi = phi_2 - phi_1 > 0
and 0 < epsilon < Delta_phi, so kappa := 1 - epsilon/Delta_phi is in (0, 1) and
tau = kappa * W. (Carried from the trailing-average companions.)

(A6) REGIME CONFIGURATION. The old regime is stable and the new regime unstable:
rho_1 < 1 < rho_2. (Theorem 2 and the statics require only rho_2 > 1; Theorem 3
requires only rho_1 > 0.)

Remark G.0.1 (why A4 is stated, and what the matrix-general truth is). For a general
matrix A and a generic vector norm, ||A x|| <= rho(A) * ||x|| is FALSE; the spectral
radius controls asymptotic growth, not single-step growth (rho(A) <= ||A|| for every
induced norm, with a possibly large gap). The sketch's per-step inequality is
therefore not a theorem about arbitrary norms of the state; it is exact along the
dominant mode, which is what A4 tracks, and it is the standard Cardiff-school
linearized reading (amplification per cycle = spectral radius). Lemma G.1 gives the
rigorous matrix-general statement: the same exponential rate up to a constant. For a
time-varying product of DIFFERENT matrices (the adaptive-policy case), even the rate
statement requires care - the joint spectral radius of the family, not the maximum
individual spectral radius, governs worst-case products in general [@Jungers-2009]. Under A4 the scalar recursion sidesteps the JSR issue;
outside A4 the adaptive-policy bound in Theorem 1 is stated with the constant from
Lemma G.1 applied to the fixed-policy envelope. E1-E12 use D as an ordinal ranking
and threshold metric, which is invariant to the constant; the alignment review
(step 3) re-checks this experiment by experiment.

---

### G.1 Lemma (matrix-general growth bound)

LEMMA G.1. Let A be a W x W matrix. (i) For every eps > 0 there exists an induced
matrix norm ||.||_eps with ||A||_eps <= rho(A) + eps; hence for every t >= 0,
||A^t x|| <= C_eps * (rho(A) + eps)^t * ||x|| in any fixed norm, with C_eps >= 1
depending on A, eps, and the norm equivalence constants but not on t.
(ii) If A is diagonalizable with eigenvector matrix V, then
||A^t x||_2 <= cond(V) * rho(A)^t * ||x||_2, cond(V) = ||V||_2 * ||V^{-1}||_2.
(iii) In general ||A^t||_2 <= c * t^{m-1} * rho(A)^t for a constant c and m the size
of the largest Jordan block of a peripheral eigenvalue.

PROOF. (i) is the standard construction (Horn and Johnson, Lemma 5.6.10): take a
Schur or Jordan form A = P T P^{-1} and the scaled similarity D_delta =
diag(1, delta, ..., delta^{W-1}); the norm x |-> ||D_delta^{-1} P^{-1} x||_inf
induces a matrix norm equal to the inf-norm of D_delta^{-1} T D_delta, whose
off-diagonal mass shrinks like delta, so for delta small enough the induced norm is
<= rho(A) + eps. Norm equivalence on finite-dimensional spaces converts the bound to
any fixed norm at the cost of the constant C_eps. (ii) A^t = V Lambda^t V^{-1} with
||Lambda^t||_2 = rho(A)^t. (iii) is the Jordan-form growth bound: powers of a Jordan
block J of size m with eigenvalue lambda satisfy ||J^t|| <= C(m) * t^{m-1} *
|lambda|^t. QED.

LEMMA G.1b (Gain Envelope, in-domain - NEW at v0.2). Fix phi_2 in (0, 1), W, and
beta*gamma > 0 with rho_2 := rho(phi_2, W, beta*gamma) > 1. Then for every
beta*gamma' in [0, beta*gamma]: rho(phi_2, W, beta*gamma') <= rho_2.

STATUS AND JUSTIFICATION. rho is NOT globally monotone in the gain: at
beta*gamma' = 0 the loop is open and rho = phi_2 < 1; small positive feedback
DAMPS the persistence pole (rho dips below phi_2); large feedback destabilizes
(rho rises through 1). The map beta*gamma' |-> rho(phi_2, W, beta*gamma') is
empirically U-shaped on the verification grid. The lemma needs only the
weaker envelope statement: on [0, beta*gamma] the maximum is attained at an
endpoint, and since the left endpoint gives phi_2 < 1 < rho_2, the right
endpoint dominates. A violation would require an interior local maximum of
rho in the gain strictly exceeding rho_2 > 1; none exists on the verification
grid (T1 numeric leg: dense gain sweep per in-domain cell, zero violations).
The lemma is carried as NUMERICALLY VERIFIED on the theorem's verification
surface and is explicitly flagged for the Phase-5a proof-rigor pass (an
analytic proof from the characteristic polynomial lam^W - phi lam^{W-1} +
(bg/W) sum_{j<W} lam^j is a known open refinement; the theorem's scope is the
verified surface until then).

REMARK G.1b.1 (stabilizing-then-destabilizing feedback - new finding). The
U-shape is itself a substantive observation surfaced by this verification:
moderate measurement feedback is STABILIZING relative to the open loop
(rho below phi_2), and instability is a property of aggressive feedback, not
of feedback per se. This sharpens the paper's narrative and is recorded for
the manuscript's framework discussion; it changes no experiment operator
(alignment review, step 3, re-confirms).

---

<!-- anchor: P-THM-1 -->
### G.2 Theorem 1 (Compound Damage Bound)

STATEMENT (as proved). Let the regime change occur at t = 0 with initial deviation
d_0 > 0, and let the blind period be t = 0, 1, ..., tau - 1 (A5). Consider a policy
whose closed-loop matrix at time t during the blind period is
A_t = A(phi_2, W, beta*gamma_t), where beta*gamma_t <= beta*gamma is the (possibly
adaptively reduced) feedback in force.

(a) Under A4 (dominant-mode tracking), the deviation at the end of the blind period
satisfies
    d_tau = d_0 * product_{t=0}^{tau-1} rho(A_t) <= d_0 * rho_2^tau,
with equality iff the policy does not adapt (beta*gamma_t = beta*gamma for all t).

(b) Matrix-general version (SHARPENED): for the non-adaptive policy the state
satisfies x_tau = A_2^tau x_0 and, by Lemma G.1, ||x_tau|| <= C * rho_2^tau * ||x_0||
with C = cond(V) when A_2 is diagonalizable and C = C_eps (rate rho_2 + eps)
otherwise. The exponential RATE rho_2 is exact: lim_{t->inf} ||A_2^t||^{1/t} = rho_2
(Gelfand). For the adaptive time-varying case outside A4, the product of the family
{A_t} is governed by its joint spectral radius, and the bound is stated only through
the fixed-policy envelope A_2 with the constant of Lemma G.1.

(c) Substituting tau = kappa * W (A5) gives the window form
    D_SMA(W) := rho_2^{kappa * W},
strictly increasing and strictly log-linear (hence convex) in W.

PROOF. (a) During the blind period the estimator has not yet detected the change
(A5), so the persistence in force in the true dynamics is phi_2 while any adaptive
reduction acts only through beta*gamma_t <= beta*gamma. Fix t in {0, ..., tau-1}.
The matrix in force is A_t = A(phi_2, W, beta*gamma_t). Two facts bound rho(A_t):
(i) by construction rho(A_t) = rho(phi_2, W, beta*gamma_t); (ii) by the Gain-
Envelope Lemma G.1b (in-domain, rho_2 > 1 per A6), beta*gamma_t in
[0, beta*gamma] implies rho(A_t) <= rho(phi_2, W, beta*gamma) = rho_2. (The
v0.1 draft invoked global gain monotonicity here; that claim is FALSE - rho is
U-shaped in the gain - and the step now rests on G.1b.) Under A4,
d_{t+1} = rho(A_t) * d_t
with d_t >= 0, so by induction d_tau = d_0 * product_{t<tau} rho(A_t). Each factor
is <= rho_2, giving d_tau <= d_0 * rho_2^tau. If the policy does not adapt, every
factor equals rho_2 exactly and the bound is attained; the attainment direction
needs no strictness claim about intermediate gains (equality holds along the
non-adaptive path by construction, which is all the theorem's "achieved when
the policy does not adapt" asserts). (b) Immediate from Lemma G.1
applied to A_2, plus Gelfand's formula for the rate; the JSR caveat for time-varying
products is Remark G.0.1. (c) Substitute tau = kappa * W into rho_2^tau:
D_SMA(W) = exp(kappa * ln(rho_2) * W) with kappa * ln(rho_2) > 0 under A6, which is
strictly increasing, log-linear, and convex in W. QED.

NOTE FOR THE ALIGNMENT REVIEW (step 3). The sketch asserted the per-step inequality
for the raw deviation with no norm qualification; the proof shows it is exact under
A4 and holds matrix-generally at the same exponential rate up to a constant. Every
experiment that consumes D uses it ordinally (rankings, correlations) or as a
ratio threshold; constants cancel in the ratio of Theorem 3 and do not move ranks.
To be re-verified operator-by-operator in step 3.

---

<!-- anchor: P-THM-2 -->
### G.3 Theorem 2 (Optimal Measurement Window)

Cost model (as in the source): total expected loss
    L(W) = c_D * rho_2^{kappa * W} + c_E * (1 - phi^2) / W,   W in [1, infinity),
where c_D > 0 scales expected regime-change damage (it absorbs the regime-change
probability p and the unit damage cost), c_E > 0 scales estimation loss, and
(1 - phi^2)/W is the Cramer-Rao asymptotic variance rate for the AR(1) coefficient
from a window of W observations. Write a := kappa * ln(rho_2) > 0 (A5, A6).

STATEMENT (as proved - SHARPENED with an explicit interiority condition).
(i) L is strictly convex on (0, infinity).
(ii) If condition (C):  c_E * (1 - phi^2)  >  c_D * a * rho_2^{kappa}
holds, then L has a unique interior minimizer W* in (1, infinity), characterized by
the first-order condition
    (FOC)  c_D * a * exp(a * W)  =  c_E * (1 - phi^2) / W^2.
If (C) fails, L' >= 0 on [1, infinity) and the constrained optimum is the boundary
W* = 1.
(iii) Closed form: the interior W* is
    W* = (2/a) * W_L( (a/2) * sqrt( c_E * (1 - phi^2) / (c_D * a) ) ),
where W_L is the principal branch of the Lambert W function. (The source's
"(1/(kappa ln rho_2)) * W_L(kappa ln rho_2 * Q)" is the same family with the
parameter bundle Q left unspecified; the form above makes Q explicit. SHARPENED.)

PROOF. (i) rho_2^{kappa W} = exp(a W) is strictly convex in W (positive second
derivative a^2 exp(aW)); (1 - phi^2)/W has second derivative
2(1 - phi^2)/W^3 > 0 on W > 0; a positive combination of strictly convex functions
is strictly convex.
(ii) L'(W) = c_D * a * exp(a W) - c_E * (1 - phi^2)/W^2. As W -> infinity the first
term diverges and the second vanishes, so L'(W) -> +infinity; in particular L' > 0
for all large W. At the left end, L'(1) = c_D * a * exp(a) - c_E * (1 - phi^2)
= c_D * a * rho_2^{kappa} - c_E * (1 - phi^2), which is negative exactly under (C).
If (C) holds: L' is continuous, L'(1) < 0, L' > 0 for large W, so by the
intermediate value theorem a root exists in (1, infinity); strict convexity makes L'
strictly increasing, so the root is unique and is the global minimizer. If (C)
fails: L'(1) >= 0 and L' strictly increasing give L' >= 0 on [1, infinity), so L is
nondecreasing there and the constrained minimum sits at W = 1. (The source sketch's
"the estimation derivative is large and negative at W = 1" is a parameter claim,
not a theorem; (C) is the exact condition. SHARPENED.)
(iii) Rearrange (FOC): exp(a W) * W^2 = c_E (1 - phi^2) / (c_D a) =: B > 0.
Take square roots of both sides of W^2 exp(aW) = B:
W * exp(aW/2) = sqrt(B). Multiply both sides by a/2:
(aW/2) * exp(aW/2) = (a/2) * sqrt(B). By definition of the Lambert W function
(z = u e^u iff u = W_L(z), principal branch since both sides are positive),
aW/2 = W_L( (a/2) sqrt(B) ), i.e. W* = (2/a) * W_L( (a/2) sqrt(B) ). Substituting
B completes the form. Positivity of the argument puts us on the principal branch,
where W_L is single-valued, consistent with uniqueness in (ii). QED.

---

### G.4 Comparative Statics of W* (CORRECTED - replaces source Section 4.5)

Let G(W, theta) := L'(W) = c_D * a * exp(a W) - c_E * (1 - phi^2) / W^2, so the
interior optimum solves G(W*, theta) = 0, and by strict convexity
G_W = L''(W*) > 0. Implicit differentiation gives, for any parameter theta,
    dW*/dtheta = - G_theta / G_W,  so  sign(dW*/dtheta) = - sign(G_theta).

(a) theta = rho_2 (holding kappa, phi, costs fixed). a = kappa ln(rho_2) is
increasing in rho_2, and G depends on rho_2 only through the damage term
c_D * a * exp(a W), which is strictly increasing in a for W > 0 (both the
coefficient and the exponent rise). Hence G_{rho_2} > 0 and dW*/d(rho_2) < 0.
CONFIRMS the source: higher instability intensity favors shorter windows.

(b) theta = phi (holding rho_2 fixed; direct estimation-cost channel). phi enters G
only through -c_E (1 - phi^2)/W^2:
    G_phi = + 2 * c_E * phi / W^2 > 0,  hence  dW*/dphi < 0.
This REVERSES the source's claim (b) [dW*/dphi > 0, "coefficients near 1.0 require
more data"]. The reversal is forced by the model's own cost term: the Cramer-Rao
asymptotic variance of the AR(1) estimator is (1 - phi^2)/W, which FALLS as phi
rises toward 1 - high-persistence coefficients are, under this variance model,
estimated MORE precisely per observation, not less. The source's verbal
justification contradicts its own formula; this is the known defect pre-registered
as CORRECTED at OUTLINE node ARG-08. Under the stated cost model the correct
comparative static is: higher steady-state persistence REDUCES estimation pressure
and therefore favors SHORTER optimal windows, holding the regime-change intensity
fixed.

(b') Total effect of phi (decomposition). In the full model phi also moves rho_2
(A3: rho increasing in phi), so the TOTAL derivative is
    dW*/dphi |_total = dW*/dphi |_direct  +  dW*/d(rho_2) * d(rho_2)/dphi,
and BOTH terms are negative by (a) and (b): under this cost model the total effect
is unambiguously dW*/dphi < 0. Any restoration of the source's intuition would
require a different estimation-cost model (for example, one in which the QUANTITY
of interest is a level forecast or a unit-root boundary test, whose difficulty
rises with phi); that is a modeling choice outside the pinned cost function and is
NOT adopted here. Flagged for the manuscript's Section 4.5 prose and for the
alignment review: no experiment consumes the sign of dW*/dphi (checked in step 3),
so the correction changes exposition, not operators - to be re-verified.

(c) theta = Delta_phi (through kappa = 1 - epsilon/Delta_phi). dkappa/d(Delta_phi)
= epsilon / Delta_phi^2 > 0, and G depends on kappa through a = kappa ln(rho_2):
    G_kappa = c_D * ln(rho_2) * exp(a W) * (1 + a W) > 0,
hence dW*/dkappa < 0 and dW*/d(Delta_phi) = (dW*/dkappa)(dkappa/dDelta_phi) < 0.
CONFIRMS the source: larger expected regime changes favor shorter windows.

(d) theta = c_E / c_D (cost ratio; new, for completeness). Scaling c_E up raises
-G by c_E's term, i.e. G_{c_E} = -(1 - phi^2)/W^2 < 0, so dW*/dc_E > 0: dearer
estimation error favors longer windows. Symmetrically dW*/dc_D < 0. Matches the
economic reading of Theorem 2 and provides a sign check for the T2 numeric grid.

---

<!-- anchor: P-THM-3 -->
### G.5 Theorem 3 (The Adaptation-Stability Identity)

STATEMENT (as proved). Let the blind-period amplification of Theorem 1 (under A4,
non-adaptive envelope) be d_tau = d_0 * rho_2^tau, and let the counterfactual
deviation had the regime not changed be d_tau^0 = d_0 * rho_1^tau (the same
recursion under rho_1, with rho_1 > 0). Then the damage amplification FACTOR -
realized deviation relative to the no-regime-change counterfactual over the same
blind window - is exactly
    D(W) = d_tau / d_tau^0 = ( rho(phi_2, W, beta*gamma) /
                                rho(phi_1, W, beta*gamma) )^{tau(W)},
with both rho and tau functions of the single design parameter W. D(W) > 1 whenever
rho_2 > rho_1 and tau > 0; log D(W) = tau(W) * [ln rho_2(W) - ln rho_1(W)]
factorizes damage into DURATION (tau) times INTENSITY (the log spectral-radius
gap), which is the intensity-times-duration reading in the text.

PROOF. Both trajectories satisfy the A4 recursion from the same d_0 > 0: the
realized blind-period path compounds at rho_2 per cycle (Theorem 1a, non-adaptive
envelope, where the bound is attained), giving d_tau = d_0 rho_2^tau; the
counterfactual path compounds at rho_1 per cycle, giving d_tau^0 = d_0 rho_1^tau,
strictly positive since rho_1 > 0. The ratio is (rho_2/rho_1)^tau; d_0 cancels, so
the factor is initial-condition-free, and by Lemma G.1(b) any matrix-general
constants C are common to numerator and denominator's growth-rate reading at rate
level. Positivity/exceedance: rho_2 > rho_1 > 0 and tau > 0 give the ratio > 1.
Taking logs gives the stated factorization. Both arguments are functions of W alone
once (phi_1, phi_2, beta*gamma, epsilon) are fixed: rho_i = rho(phi_i, W,
beta*gamma) by A2 and tau = kappa W by A5. QED.

REMARK G.5.1 (bound vs identity). Theorem 1 is an upper BOUND on the realized
deviation (adaptive policies do strictly better); Theorem 3 is an exact IDENTITY
for the non-adaptive envelope's amplification factor - the quantity every
experiment ranks on. Under an adaptive policy the realized factor is <= D(W), so
D(W) retains its reading as the worst-case regime-change cost multiplier.

---

### G.6 Proposition (Optimal Safety Factor k*) - derivation with approximations
labeled

SETTING. The speed limit from the companion papers is S(phi, W) * beta*gamma =
pi^2/2, giving beta*gamma_max = (pi^2/2) / S(phi_hat, W), calibrated to the
ESTIMATED persistence phi_hat. During a blind period the true phi exceeds phi_hat,
so operating exactly at beta*gamma_max risks a breach. Choose an operating fraction
k in (0, 1]: beta*gamma_op = k * beta*gamma_max.

STATEMENT (approximation - stated as a Proposition, not a Theorem). Under (i)
first-order expansion of S in phi around phi_hat, (ii) Gaussian estimation error
phi - phi_hat ~ N(0, Var(phi_hat)) with the regime-change contribution entering as
an inflation of effective estimation risk proportional to p * W (probability p of a
change during a window of length W), and (iii) a breach-avoidance criterion that
holds the operating point at approximately two standard deviations of the induced
uncertainty in S * beta*gamma / (pi^2/2), the optimal fraction is approximately
    k* ~= 1 - (1/(pi^2/2)) * sqrt( 2 * p * W * Var(phi_hat) ),
matching the source's stated form. For typical manufacturing parameters
(phi ~ 0.96, W in [8, 12], regime changes every 5-7 years) this evaluates in the
0.85-0.95 range; the exact numbers are re-earned by the committed T3 grid, not
quoted from the source.

DERIVATION. Let u := S(phi, W) * beta*gamma_op / (pi^2/2) be the utilization of the
speed limit at the TRUE phi; stability requires u < 1. With beta*gamma_op =
k * (pi^2/2)/S(phi_hat, W), u = k * S(phi, W)/S(phi_hat, W). Expanding S to first
order in (phi - phi_hat) (approximation i): S(phi, W)/S(phi_hat, W) ~= 1 +
s_1 * (phi - phi_hat), with s_1 = (dS/dphi)/S evaluated at phi_hat. Under
(approximation ii) the term s_1 (phi - phi_hat) is Gaussian with variance
s_1^2 * Var_eff, Var_eff = 2 p W Var(phi_hat) collecting the estimation variance
inflated by the chance and length of a blind window (the factor 2pW is the source's
parameterization of that inflation and is retained as-is; it is a modeling
constant, not a derived quantity - labeled explicitly as such for the 5a review).
The breach-avoidance criterion (approximation iii) sets k so that u stays below 1
at the sqrt(Var_eff) scale normalized by the limit: k* = 1 - sqrt(Var_eff) /
(pi^2/2) after absorbing s_1 into the normalization of Var(phi_hat) (the source
states the formula with s_1 = 1, i.e., variance quoted directly in speed-limit
units; retained for continuity and flagged as a units convention). Substituting
Var_eff gives the stated k*. QED (as an approximation chain; each step labeled).

STATUS. G.6 is deliberately a PROPOSITION with an explicit approximation chain: the
source provides the formula with no derivation, and the three approximation steps
above are the minimal honest scaffold that produces it. The T3 grid (step 2)
verifies the practical content (argmin location and the 0.80-0.98 band) directly by
brute force, independent of the approximations. If the grid contradicts the
formula's location, the Proposition - not the grid - is amended, dated.

---
