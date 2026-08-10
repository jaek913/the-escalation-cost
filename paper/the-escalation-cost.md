---
title: |
  The Escalation Cost:\
  Intensity, Duration, and the Growing Damage of Regime Change
author: |
  Jae Kim\
  Independent Researcher\
  ORCID: [0009-0005-3260-7880](https://orcid.org/0009-0005-3260-7880)\
  jae@laggingtruth.com
date: |
  *This version: August 2026*\
  *Working paper --- preliminary; comments welcome.*\
  DOI: [10.5281/zenodo.21331771](https://doi.org/10.5281/zenodo.21331771)
license: "CC BY-NC-ND 4.0"
---

<!-- Rendered numbers: every double-braced LB-id token below is substituted by the committed renderer (analysis/render_paper.py) from analysis/claims.lock. No figure is retyped by hand. -->

## Abstract

Institutions steer feedback systems off trailing averages of persistent variables, and after a regime change the estimator lags reality. This paper prices that lag. Two established literatures each answer half the question - control-theoretic stability asks whether a loop is stable at its current parameters, and adaptive filtering asks how fast an estimator converges once those parameters move - and the cost of being wrong in between is what the result here combines them to compute. We prove that blind-period damage is bounded by a compound expression $D = (\rho_2/\rho_1)^{\tau}$ - intensity raised to duration - computable from quantities institutions already estimate; derive the unique optimal measurement window $W^{*}$ in closed form; and establish the adaptation-stability identity linking the two. The bound's damage ordering is validated on a 34-year rolling out-of-sample panel of seventeen U.S. inventory-to-sales series under a pre-registered panel-level test whose decision rule was amended, and the amendment disclosed, before any hashed data was touched (Section 6.3); it is corroborated on the 2008 crisis episode and boundary-tested on COVID, where the pre-registered expectation of a null was met. Simulation studies map where acting on the diagnostic helps and where it harms: value is conditional on capacity strain, asymmetric between price raises and cuts, robust to permanent customer attrition in genuinely shifted regimes yet harmful in noisy ones, and - under drifting persistence - beyond rescue by any estimator, including one handed the true parameter. Two pre-registered cross-domain extensions were WITHDRAWN when their preconditions failed, and a capacity-threshold test is reported as unadjudicable rather than negative. A dated, falsifiable forward prediction is registered publicly at release. The theorem converts steady-state stability analysis into a computable transient-cost diagnostic; the scope conditions and limits that bound it are stated, tested, and reported at the same weight as the results.

**Keywords:** regime change; adaptation lag; spectral radius; bullwhip; measurement window; transient cost

**JEL:** C61; C63; E32; L60; M11

## 1 Introduction

This result began as a special case. Companion work in this program examined a regulatory filter intended to stabilize credit cycles - a backward-looking smoother feeding a countercyclical policy response - and found that under empirically realistic dynamics it amplified the cycles it was built to damp [@Kim-MeasurementTrap]. The failure turned out not to be about banking. It was an instance of something more general: whenever a backward-looking measurement of a persistent variable drives a policy that feeds back into the variable being measured, the loop can become self-reinforcing rather than self-correcting, and whether it does is decided by three quantities an institution can measure - how persistent the variable is, how long the measurement window is, and how hard the policy pushes. This paper takes that mechanism seriously in its general form and asks what it costs.

Every institution that steers a system steers it off a measurement, and every measurement of a persistent variable is a trailing average of some length. A central bank reads inflation over a window. A manufacturer sets inventory policy off recent demand. A rating agency assesses debt sustainability from years of fiscal data. Each of these windows is a choice, and each is usually made on grounds of statistical precision alone: longer windows give cleaner estimates, so longer is treated as safer.

That reasoning holds exactly as long as the world stays in one regime. When the underlying persistence changes - when demand that used to revert starts to compound, when a fiscal position that used to stabilize starts to run - the trailing average keeps reporting the old regime for a while. During that stretch the institution is not making a small error. It is applying a control rule calibrated to conditions that no longer exist, to a system whose deviations are now amplifying rather than decaying. The loop pays for the lag, and the payment is not proportional to it [@Minsky-1986; @Hopp-Spearman-2008].

This paper prices that payment. The result is a bound: damage during the blind period is the intensity of the new instability raised to the power of the institution's own adaptation time. Intensity and duration compound rather than add, so the cost of a slow measurement rises exponentially in exactly the situations where the measurement is most likely to be slow - and both inputs are quantities institutions already estimate, which makes the bound a diagnostic rather than a metaphor. Two corollaries follow directly: there is a unique optimal window that balances estimation precision against adaptation speed and it is available in closed form, and the safe operating point under regime-change risk sits strictly below the stability limit that steady-state analysis would license.

The gap this fills is specific. The control-theoretic literature answers when a loop is stable in steady state, and answers it well; the empirical bullwhip literature measures amplification as it occurs; the adaptive-control literature bounds transient behavior for a controller that knows it is adapting. None of them prices what an institution loses in the interval between a regime changing and its own estimator noticing [@Disney-Towill-2002; @Dejonckheere-2003; @Li-Dorfler-2024; @Leng-2025; @Spiegler-2016].

The contribution is therefore a computable bound on that transient cost, its optimal-window corollary, an identity unifying them across domains, and - equally - a program of pre-registered empirical and simulation tests that map where the result holds and where it does not. That second half is not a formality. The tests reported here include a rolling out-of-sample validation the framework passes, two domain extensions whose pre-registered readings were withdrawn when their preconditions failed, a capacity-threshold hypothesis that proved unadjudicable, a simulation result showing the framework's own remedy causes harm under conditions the theory does not cover, and a monitoring record showing that the paper's own instability dashboard confirms regime shifts rather than anticipating them. Each of those outcomes is reported at the strength the evidence supports, because a diagnostic whose failure modes are undocumented is not a diagnostic. Correction would be welcome from readers who can point to closer precursors in literatures not surveyed completely here.

The paper proceeds as follows. Section 2 reviews the related literatures and locates the gap between steady-state stability analysis and transient regime-change cost. Section 3 states the framework in brief. Section 4 develops the measurement damage theorem, its optimal-window corollary, and the corrected comparative statics. Section 5 sets out the methods - the frozen operators, the two named specifications, and the pre-registered decision rules with their one disclosed amendment. Section 6 presents the empirical validation: the rolling out-of-sample panel test that carries falsification, and the two episode tests. Section 7 applies the framework to supply-chain ordering and maps, through four simulation studies, the conditions under which acting on the diagnostic helps and the conditions under which it harms. Section 8 develops the semiconductor and industrial-policy reading, including a capacity-threshold test that could not be adjudicated. Section 9 reports the two cross-domain extensions, both of whose pre-registered readings were withdrawn. Section 10 draws the institutional-design implications, Section 11 states and registers the forward predictions, and Section 12 concludes. Appendix G carries the written proofs; Appendices A through F carry the data registry, the machine-verification record, and the simulation detail.

## 2 Related Work

Six literatures bear on this result. The first establishes the stability conditions this paper takes as given; the second supplies the empirical phenomenon; the third and fourth ground the applications; the fifth supplies the institutional frame; the sixth contains the nearest formal relatives. Across all six, the recurring pattern is that the transient - the interval during which a system's own measurement is wrong about which regime it is in - is either assumed away or treated as a nuisance rather than priced.

### 2.1 Control-Theoretic Stability

This is the literature the paper stands on rather than argues with. The transfer-function and eigenvalue traditions establish when supply loops are stable in steady state, and they establish it well: given a demand process and a replenishment rule, the analysis says whether the loop amplifies or damps [@Disney-Towill-2002; @Dejonckheere-2003; @Dejonckheere-2004; @Disney-2008; @Disney-Towill-2003; @Disney-2004-golden; @Hosoda-Disney-2006; @Li-2023; @Lin-2020; @Ouyang-Daganzo-2006; @Spiegler-2016; @Helbing-2004; @Gaalman-2022; @Warburton-Disney-2007]. The companion-matrix construction this paper uses is taken from that tradition and is cited, not re-proved.

The closest method precedents share the move of treating the loop's own parameters as the object of analysis: closed-loop production-inventory analysis under i.i.d. demand [@Boute-2006], ARMA-demand eigenvalue work [@Gaalman-Disney-2009], stability-region inversions that solve for the admissible parameter set rather than testing one policy [@Warburton-2004; @Wang-2013], and behavioral stability regions that ask which regions human orderers actually occupy [@Udenio-2017].

What the tradition assumes away is the thing this paper prices, and the assumption is specific enough to name. A number of the foundational closed-form bullwhip results - the z-transform framework and its smoothing-policy extensions, and the golden-ratio gain [@Disney-Towill-2002; @Disney-Towill-2003; @Dejonckheere-2003; @Dejonckheere-2004; @Disney-2004-golden] - were derived under independently and identically distributed demand. Under i.i.d. demand the spectral radius sits below one for any reasonable ordering policy, so the instability mechanism studied here does not arise at all. Bullwhip under i.i.d. demand is a VARIANCE-AMPLIFICATION phenomenon: does order variance exceed demand variance? What this paper studies is a STABILITY-TRANSITION phenomenon: does the system cross the boundary past which perturbations compound rather than decay? The second question requires persistent demand, which the panel in Section 7.1 finds in real sectors and which the i.i.d. analyses do not model. That is the gap, stated precisely - not that prior work was wrong, but that it was answering a different question in a demand environment where this one cannot be posed.

That characterization applies to the foundational analytical results and NOT to the tradition as a whole, a distinction worth making explicitly. A substantial body of work in the same school analyses transient and nonlinear dynamics directly - describing-function and step-response analysis of grocery supply-chain resilience, and frequency-response analysis of delivery-time dynamics in assemble-to-order systems [@Spiegler-2016; @Lin-2020]. The contribution here is therefore not the analysis of supply-chain transients as such, which is well established and built upon, but a closed-form damage bound tying a backward-looking estimator's adaptation time to a regime transition.

Four bodies of work sit close enough to require explicit differentiation rather than a citation. The nearest is the closed-loop production-inventory analysis of smoothing replenishment under endogenous lead times [@Boute-2006], which shares this paper's central concern - the coupling between the ordering decision and the production system - and motivated the construction used here. It differs in three respects that matter: its demand is i.i.d., so the persistence driving this mechanism is absent by construction; its apparatus is a queueing and matrix-analytic model of endogenous lead times rather than a companion-matrix eigenvalue analysis; and the questions taken up here - what happens when persistence changes between regimes, estimating the spectral radius from rolling empirical data as a monitoring statistic, and the damage bound itself - fall outside the scope that work sets. The relationship is an extension of that modelling tradition, and dialogue with its authors about how they see the connection would be welcome.

The golden-ratio gain [@Disney-2004-golden] minimizes steady-state combined order and inventory variance under i.i.d. demand. The safety factor derived here ({{LB-T3-kstar-mfg-argmin}} at manufacturing parameters) minimizes expected total cost INCLUDING regime-transition damage under high persistence that can shift between regimes. These answer different optimization problems in non-overlapping demand environments rather than competing on the same one: under i.i.d. demand this framework reduces to standard stability analysis, where the golden ratio may well be the right answer; under persistent demand with regime changes, it was not derived for that setting.

The Lambert $W$ function appears in both this paper and the delay-differential analysis of continuous-time supply chains with pure time delays [@Warburton-Disney-2007], but for different purposes - there to solve the delay equations, here to derive the optimal measurement window. The shared use of one widely applicable function reflects its breadth across optimization contexts rather than overlapping intellectual content.

The closest mathematical relatives are the switched-linear-systems transient bounds, which establish that cumulative deviation grows at most as the joint spectral radius raised to the elapsed time [@Jungers-2009; @Plischke-Wirth-2008]. The damage bound is superficially similar and differs on three axes: those bounds hold for ARBITRARY switching, while the transition here follows a specific trajectory dictated by the trailing estimator's convergence, with the exponent a function of the measurement window rather than a free parameter; their matrices are abstract, while these are parameterized by observable quantities with explicit formulas connecting the spectral radius to them; and that work sits in pure-mathematics venues without a supply-chain application. The mathematical kinship is real and the practical overlap limited. Oscillatory instability in material-flow networks has also been examined from a statistical-physics standpoint [@Helbing-2004], documenting the phenomenon without supplying the parameterized criterion this framework needs.

Two recent results come closest in aim and are positioned individually: transient bullwhip analyzed through robust control [@Li-Dorfler-2024], which bounds transient behavior but for a controller with known dynamics, and persistence-driven network amplification [@Leng-2025], which makes persistence the driver but not the measurement of it. Neither prices the estimator's blind period after a regime change. Two further contrasts are complementary rather than competing: statistical-process-control monitoring [@Costantino-2014] is built to detect THAT order variance has risen, where diagnosing why, supplying a principled ordering constraint, and pricing the damage accumulated during the detection delay are aims this framework adds; and deep reinforcement learning [@Gijsbrechts-2022] can outperform base-stock policies in specific simulated environments while providing no closed-form stability bound, no interpretable constraint, and no regime-transition prediction - so the natural division is that the spectral radius supplies the constraint and a learned policy optimizes within it.

### 2.2 Empirical Bullwhip

Firm- and industry-level measurements establish the phenomenon our panel rides on [@Bray-Mendelson-2012; @Bray-Mendelson-2015; @Cachon-2007; @Shan-2014; @Dooley-2010; @Saricioglu-2025], with SPC-style monitoring as a method contrast [@Costantino-2014]. This work documents that amplification exists, varies across firms and sectors, and intensifies in crises. What it does not supply is a pre-crisis quantity that orders sectors by how much amplification they are about to suffer - which is precisely what the damage bound proposes and Section 6 tests out of sample.

One methodological choice separates this panel from that literature and should be stated where the literature is introduced rather than left to Methods. We condition on the *managed* variable - the inventory-to-sales ratio - rather than on demand levels, following the recommendation of [@Chen-2000]. The reason is that the I/S ratio behaves as a stationary series over this sample while demand levels do not: a levels series whose autoregressive coefficient sits at the edge of the unit circle cannot support a persistence estimate that means what this framework needs it to mean, because the quantity being estimated is distance to a stability boundary and a near-unit-root series is already at one for reasons that have nothing to do with the control loop. Estimating persistence on the managed variable is therefore not a convenience; it is what makes the spectral radius interpretable at all.

### 2.3 Semiconductor Dynamics

Sector-specific volatility and planning literature ground the CHIPS application [@Anderson-2000; @Monch-2011; @Nepal-2012; @Hopp-Spearman-2008]. Semiconductors are the natural stress case for a measurement-lag argument: fabrication lead times run months, capacity is lumpy and capital-intensive so it cannot be adjusted incrementally, and end demand swings hard enough that the persistence of any given quarter is a poor guide to the next. An industry with long lead times and expensive capacity is an industry whose control loop has both a long effective window and a strong incentive to react hard once it does react - the two ingredients the damage bound multiplies together.

That literature also supplies the specific intuition this paper puts to a direct test: that a stability knee should appear as utilization approaches its ceiling, since a system running near capacity has no slack to absorb a disturbance. Section 8.2 tests it and does not confirm it - not because the intuition is refuted, but because the sector never occupies the stable regime the test needed as a contrast. The honest reading is reported there as an inconclusive instrument rather than as a negative result.

### 2.4 Complexity and Resilience

Complexity-performance and network-risk results motivate the persistence channel [@Bozarth-2009; @Choi-2001; @Novak-Eppinger-2001; @Serdarasan-2013; @Osadchiy-2016; @Graves-Tomlin-2003; @Tomlin-2006]. Their common finding is that structure matters independently of scale: products with many interdependent components, supply bases with many tiers, and networks with dense interconnection all propagate a disturbance through more paths and hold it longer than a simpler system would.

A notational warning belongs here, because two of the quantities in play share a symbol. [@Osadchiy-2016] use $\rho$ to denote a systematic-risk correlation between nodes in a supply network. Throughout this paper $\rho$ denotes the spectral radius of the companion matrix of the control loop - the modulus of its largest eigenvalue, and the quantity whose distance from one is the whole subject of the damage bound. The two are unrelated: one is a correlation bounded in the usual way, the other a stability measure whose crossing of one marks a qualitative change in behaviour. A reader moving between that literature and this paper should not read the symbol as continuous across them.

Translated into this paper's vocabulary, that is a mechanism for high persistence - complexity is one of the reasons a sector's $\phi$ sits where it does. The translation matters because it connects two literatures that rarely cite each other: the complexity tradition explains WHY some sectors are structurally slow to shed a shock, and the control tradition explains WHAT a slow-shedding sector does to a feedback loop. This paper joins them at the persistence parameter, which is why the instability ranking of Section 8.1 and the complexity literature's usual suspects are substantially the same sectors, reached from different directions. That convergence is offered as a coherence check, not as a tested claim: no experiment here measures complexity or estimates its effect on persistence.

### 2.5 Minsky in Operations

Stability breeding instability, drift toward boundaries, capability traps, and quality erosion supply the institutional frame [@Minsky-1986; @Rasmussen-1997; @Dekker-2011; @Repenning-Sterman-2001; @Repenning-Sterman-2002; @Oliva-Sterman-2001]. This tradition explains why regime changes in the dangerous direction are not rare accidents but the expected consequence of a quiet period: calm conditions invite the very leverage, tightening, and margin-thinning that raise persistence. The measurement problem this paper prices is therefore structural rather than incidental - the transition is most likely to arrive exactly when the institution's long measurement window feels most justified.

What this paper adds to that tradition is measurement. The literature above documents that systems drift toward their boundaries and names the pressures that push them; it does not put a number on how far a given system currently sits from its boundary, nor on what crossing it costs. The spectral radius is offered here as a direct measurement of that distance, and the damage bound as a quantification of the cost once the boundary is crossed. That is the contribution being claimed - not the observation that drift happens, which is not ours.

### 2.6 Adaptation Rates and Transient Response

How quickly a smoothing estimator recovers from a structural break is long-settled: for a moving average of window $W$ the adaptation time after a step change is on the order of $W$ periods, and for an exponentially weighted average it scales inversely with the smoothing constant [@Haykin-1996]. The companion work on adaptation rates developed this specifically for trailing-average estimators embedded in economic measurement systems.

Adaptive-control transient bounds are the nearest formal relatives of the blind-period cost, deriving explicit bounds on transient performance as functions of the adaptation gain and showing that reference-model design can suppress the peaking that otherwise worsens as adaptation speeds up [@Krstic-Kokotovic-1993; @Datta-Ioannou-1994; @Zang-Bitmead-1994; @Gibson-2013]. NO NOVELTY IS CLAIMED for the general principle that adaptation speed trades against transient quality: that principle is well established in this literature and is cited here as acknowledged prior art.

The distinction to draw is one of object. Adaptive control studies a deliberately designed controller whose adaptation speed is a TUNABLE design gain. The adaptation time here is instead a structural, non-tunable property of a backward-looking trailing average: it is dictated by the window length rather than chosen. That difference is what makes the problem bite, because it closes the obvious escape. An operator cannot simply adapt faster to outrun the damage - the same window length that sets the adaptation time also sets the estimation accuracy, and buying speed spends precision. Resolving that tension is what the damage bound and its optimal-window corollary exist to do.

Two recent results approach the transient cost of supply-chain regime change closely enough to warrant individual positioning rather than a shared citation. The first defines a transient bullwhip measure carrying an explicit dependence on forecast error and computes worst-case order fluctuation under bounded errors through robust control [@Li-Dorfler-2024]; it shares the focus on the transient rather than the steady state and the insistence on treating forecast error as an explicit quantity, and differs in three respects - its measure is the output of a peak-gain optimization solved through bilinear matrix inequalities rather than a closed form, its forecast error is a bounded disturbance rather than the structural lag of a named estimator, and it studies a single vendor restabilizing around a steady state rather than a transition between persistence regimes. The second develops a closed-form general-equilibrium production-network model in which hump-shaped persistence profiles amplify along the chain while monotone-decay shocks do not, with an incomplete-information variant in which producers filter because they cannot distinguish the two [@Leng-2025]. Its use of a persistence distinction to drive amplification, solved in closed form and validated across manufacturing sectors, is close to this paper's concerns, and NO PRIORITY IS CLAIMED over the idea that shock persistence governs amplification. The differences are of object again: a general-equilibrium network of input-output-linked sectors against a backward-looking trailing estimator and the damage its lag produces; an impulse-response matrix series of sectoral revenue against a damage ratio; shocks fluctuating around a stable mean against a transition between two persistence regimes. All three lines are best read as complementary treatments of how forecast lag and shock persistence generate transient cost, and dialogue with both author groups would be welcome.

The joint-spectral-radius literature supplies the correct caution for products of differing matrices, which Appendix G.0 uses to scope the paper's per-step reading precisely rather than assume it away [@Jungers-2009; @Plischke-Wirth-2008].

## 3 The Framework in Brief

Three ingredients carry the whole argument, and two of them are inherited rather than re-proved here.

The first is the loop. An institution measuring over a window $W$ and feeding back at rate $bg$ produces a closed loop whose linearization is a $W \times W$ companion matrix; its spectral radius $\rho$ decides stability. When $\rho$ is below one, deviations decay; above one, they compound. This is a verified input from the companion work, cited not re-proved [@Kim-MeasurementTrap].

The second is the lag. A trailing estimator of window $W$ does not learn a new persistence regime instantly; it converges over an adaptation time $\tau(W)$ that is proportional to the window. That interval - during which the institution is steering by a description of a regime it has already left - is the blind period [@Kim-AdaptationRate].

The third is the composition, and it is this paper's contribution: what the blind period costs.

Stating it against the two literatures it draws on makes the contribution precise. The control-theoretic stability tradition asks whether a system is stable AT ITS CURRENT PARAMETERS. The adaptive-filtering and adaptation-rate tradition asks HOW QUICKLY an estimator converges after those parameters change. Both questions are well studied and neither is reopened here. What this paper has not found placed at the centre of either is the question between them: what is the total cost of being wrong during the convergence period? The damage bound answers it by combining $\rho$, which the stability literature supplies, with $\tau$, which the adaptation-rate literature supplies, into a single quantity.

Returning to the composition itself: because deviations compound at the new regime's rate for the whole of it, the cost is the new intensity raised to the duration, and because the duration is set by the window the institution chose, the cost is a consequence of a measurement decision rather than of the shock alone. Two scope conditions govern throughout: stability is read from the companion-matrix spectral radius under linearization (S-1), and the managed variable follows an AR(1) with a single persistence parameter per regime (S-2).

## 4 The Measurement Damage Theorem

### 4.1 Setup

An institution manages a variable it cannot observe without delay. The managed variable $y_t$ follows AR(1) dynamics with persistence $\phi$, and the institution estimates the state it is reacting to with a trailing average of window $W$ - the last $W$ observations, equally weighted. A feedback policy then adjusts the system at rate $bg$ on the gap between that estimate and a target. Linearizing the resulting closed loop gives a $W \times W$ companion matrix $A(\phi, W, bg)$: the persistence and feedback structure occupy its first row, an identity shift sits below, and its spectral radius $\rho(A)$ decides whether deviations decay or compound [@Kim-MeasurementTrap; @Dejonckheere-2003].

<!-- anchor: EQ-1 -->
EQ-1 defines the managed variable, trailing estimator, and companion matrix $A(\phi, W, bg)$. Scope conditions S-1 and S-2 bind here.

The window is the decision variable, and it is the source of the tension the rest of this section resolves. A long window estimates persistence precisely but adapts slowly; a short window adapts quickly but estimates noisily. When persistence is stable, only the first consideration matters and longer is better without limit. When persistence changes, the second consideration acquires a price - and Section 4.3 shows that price is finite, computable, and minimized at a unique interior window. Two restrictions carry through: stability is read from the linearized companion matrix rather than from the full nonlinear system (S-1), and the managed variable follows an AR(1) with a single persistence parameter per regime (S-2). Appendix G.0 states the full assumption set (A1 through A6), including the dominant-mode reading of damage that Remark G.0.1 scopes explicitly and Lemma G.1 replaces with a matrix-general bound.

### 4.2 Theorem 1: The Compound Damage Bound

When true persistence steps from $\phi_1$ to $\phi_2$ at some moment, a trailing estimator does not notice immediately. For a stretch of time it continues to report the old regime, and the policy keeps applying a rule calibrated to conditions that no longer hold. This is the blind period, and its length is the estimator's adaptation time $\tau(W) = \kappa W$, proportional to the window (A5). The theorem prices what happens inside it.

<!-- anchor: THM-1 -->
THM-1 (Compound Damage Bound): blind-period damage is bounded by

$$D = \left(\frac{\rho_2}{\rho_1}\right)^{\tau}.$$

<!-- anchor: EQ-2 -->
EQ-2 states the bound. The structure is the paper's central claim in one line: damage is not additive in the delay, it is exponential in it, with the base set by how much more unstable the new regime is ($\rho_2/\rho_1$) and the exponent set by how long the institution stays blind ($\tau$). Intensity and duration multiply rather than add, so a modest increase in instability paired with a long measurement window produces damage that neither factor predicts alone. Both inputs are quantities institutions already estimate, which is what makes the bound a diagnostic rather than an abstraction. S-3 restricts the domain to step-change regime transitions; compound multi-channel shocks are outside the model. The full written proof is P-THM-1 in Appendix G; the machine legs are the symbolic step-check ({{LB-T1-bound-symbolic}}) and the numeric stress grid (in-domain cells {{LB-T1-bound-numeric-indomain}}, counterexamples {{LB-T1-bound-numeric-counterexamples}}, all-pass {{LB-T1-bound-numeric-allpass}}).

### 4.3 Theorem 2: The Optimal Measurement Window

The trade-off is now explicit and has two opposing arms, and both are driven by the SAME parameter. Lengthening the window lowers estimation error - the asymptotic variance of the AR(1) estimate falls like $(1 - \phi^2)/W$ - while raising the exponential damage term, because the adaptation time is increasing in the window: a longer window means a longer blind period. That the two effects share one control is what makes this a genuine optimization rather than a preference. Minimizing the sum of the two costs gives a first-order condition with a transcendental solution, and that solution is exactly the Lambert $W$ function's domain.

<!-- anchor: THM-2 -->
THM-2: a unique interior optimal window $W^{*}$ exists in closed form via the Lambert $W$ function [@Warburton-Disney-2007].
<!-- anchor: EQ-3 -->
EQ-3 states the closed form. The optimum is interior and unique under strict convexity of the loss (proved in Appendix G.3), which matters practically: there is one right window, not a range of defensible ones, and it can be computed from parameters an institution can estimate rather than chosen by convention. Written proof P-THM-2 in Appendix G; machine legs {{LB-T2-wstar-symbolic}}, brute-force agreement {{LB-T2-wstar-numeric-match}} (match rate {{LB-T2-wstar-numeric-matchrate}}), unimodality failures {{LB-T2-wstar-numeric-unimodal-failures}}.

### 4.4 Theorem 3: The Adaptation-Stability Identity

The first two theorems are stated for a supply chain, but nothing in their derivation is about inventory. What the derivation uses is that some quantity compounds at a rate set by the regime in force, and that the regime in force is whatever the institution's measurement says it is. Any domain with those two features inherits the result.

<!-- anchor: THM-3 -->
THM-3 (Adaptation-Stability Identity): total damage is governed by intensity $\times$ duration across domains.
<!-- anchor: EQ-4 -->
EQ-4 states the identity. This is what licenses Sections 7 through 9 to apply one framework to inventories, semiconductor capacity, sovereign debt, and unemployment insurance without re-deriving anything: the domains differ in what compounds and how the feedback is implemented, not in the structure of the cost. Written proof P-THM-3 in Appendix G; machine legs {{LB-THM3-symbolic}}, dual-path identity checks {{LB-THM3-numeric-checked}}, numeric leg pass {{LB-THM3-numeric}}.

### 4.5 Comparative Statics

How should the optimal window move when conditions change? Implicit differentiation of the first-order condition answers this cleanly, since strict convexity fixes the denominator's sign and every comparative static reduces to the sign of one partial derivative. The full re-derivation is Appendix G.4; the results are three confirmations and one correction.

Higher instability intensity shortens the window. Raising $\rho_2$ raises the damage term at every window length, so the optimum moves left: when the new regime is more explosive, the institution can afford less blindness. Larger expected regime changes shorten it too. A bigger $\Delta\phi$ raises $\kappa$ and so lengthens the blind period for any given window, which the optimum offsets by shrinking $W$. Dearer estimation error lengthens it, symmetrically: as the cost of acting on a noisy estimate rises relative to the cost of acting late, the optimum buys precision with time.

The fourth static reverses the direction claimed by the source this rebuild replaces, and the reversal is forced by the model's own cost function. Holding regime-change intensity fixed, higher steady-state persistence favors a SHORTER window, not a longer one. The reason is the estimation-cost term itself: the asymptotic variance of the AR(1) estimator is $(1 - \phi^2)/W$, which FALLS as $\phi$ approaches one. Under this variance model, highly persistent series are estimated more precisely per observation, not less, so persistence relieves estimation pressure rather than adding to it - and relieved pressure means the optimum spends fewer periods blind. The source's verbal justification ("coefficients near 1.0 require more data") contradicts the formula the source itself adopts; the correction was pre-registered before the rebuild's experiments ran. Including the indirect channel does not rescue the original sign: higher $\phi$ also raises $\rho_2$ (A3), and that effect pushes the same direction, so the total derivative is unambiguously negative. Restoring the source's intuition would require a different estimation-cost model - one in which the difficulty of the estimation task rises with persistence, as it does for a unit-root boundary test - and that is a modeling choice outside the pinned cost function, not adopted here. No experiment in this paper consumes the sign of $dW^{*}/d\phi$, so the correction changes exposition rather than any operator or result.

Machine verification: symbolic legs {{LB-T2-statics-symbolic}}; numeric monotonicity counters {{LB-T2-statics-numeric-monophi-fail}} ($\phi$) and {{LB-T2-statics-numeric-monobg-fail}} ($bg$) failures.

### 4.6 The $\pi^2/2$ Speed Limit and Optimal Safety Factor

The stability boundary itself is not this paper's result; it is the foundation's, and it takes a compact form. A single loop is stable when the product of the estimator's amplification and the feedback aggressiveness stays below a fixed constant - the $\pi^2/2$ speed limit. Read as engineering advice it says something simple: there is a maximum rate at which a system can chase a measurement it takes time to form, and exceeding it converts correction into oscillation.

<!-- anchor: EQ-5 -->
EQ-5 restates the single-loop criterion $S(\phi, W) \cdot bg < \pi^2/2$ from the foundation [@Kim-MeasurementTrap].

Two derived quantities make the criterion operational. The stability margin $M = 1 - S(\phi, W) \cdot bg / (\pi^2/2)$ measures the fractional distance from the boundary - one at zero feedback, zero at the limit - and the maximum safe aggressiveness $bg_{\max} = (\pi^2/2) / S(\phi, W)$ is the same criterion solved for the feedback gain: the largest ordering aggressiveness the current persistence and window admit. Both are rearrangements of EQ-5 rather than new results, reported because they are the forms a practitioner reads off a dashboard - how much room is left, and how hard the system may push.

The question this paper adds is where inside that region an institution should actually sit. The boundary marks where stability is lost under CURRENT conditions; it says nothing about how much room to leave for conditions changing. If persistence can step upward, an operating point that is merely inside the boundary today can be outside it tomorrow, and the blind period guarantees the institution keeps steering as though it were still inside. The safety factor answers how much margin that risk is worth.

<!-- anchor: EQ-6 -->
EQ-6 gives the optimal safety factor $k^{*}$, approximately $1 - (1/(\pi^2/2))\sqrt{2 p W\,\mathrm{Var}(\hat{\phi})}$, where $p$ is the per-period regime-change probability and $\mathrm{Var}(\hat{\phi})$ the persistence-estimation variance. The structure of the expression carries the intuition: every quantity under the root is a source of blindness risk - likelier regime changes, longer windows, noisier estimates - and each pushes the safe operating point further below the limit. Under regime-change risk the optimal operating point sits below the limit: mfg-parameter argmin {{LB-T3-kstar-mfg-argmin}}, in-band {{LB-T3-kstar-inband}}, all-below-one {{LB-T3-kstar-allbelow1}}, verdict {{LB-T3-kstar-verdict}} (proposition-level: numeric legs here; the written proof with labeled approximations is P-THM-3's companion obligation in Appendix G).

### 4.7 Connection to the Adaptation Tax

The damage bound supplies the transition-cost foundation for the adaptation-tax framework [@Kim-AdaptationTax]. That framework asks what an institution pays to move between operating regimes; this theorem prices one specific component of that bill - the cost incurred while the institution's own measurement still describes the regime it has already left. The two results compose rather than compete: the adaptation tax counts the cost of changing, and the damage bound counts the cost of not yet knowing that change is required.

The identity supplies the arithmetic of that blind-period line item. If each period of blindness carries cost proportional to the prevailing excess deviation - unit carrying cost $c$ on an initial deviation $d_0$ - then the accumulated cost over the blind period is a finite geometric series in the per-period ratio $\rho_2/\rho_1$, and it sums in closed form to $C_{\mathrm{blind}} = c \cdot d_0 \cdot (D(W) - 1) / (\rho_2/\rho_1 - 1)$, with $D(W)$ the damage bound at window $W$. Nothing in the expression is new relative to EQ-1 and EQ-4 - it is the same compound damage read as a cost aggregate rather than a deviation ratio - which is exactly what makes it usable as the blind-period line in the adaptation-tax accounting.

## 5 Methods

This section states the operators the experiments actually ran. Every specification here was frozen in the pre-registered design document and committed before the first hashed-data run; where a rule changed, the change is a dated amendment disclosed in place rather than a silent edit, and no operator was chosen after seeing a result.

### 5.1 Managed Variable and Data

The managed variable is the inventory-to-sales ratio: monthly, seasonally adjusted, per sector. It is the quantity firms actually control through ordering decisions, and it is stationary, which the persistence estimator requires. The panel is seventeen US Census series - seven manufacturing, seven wholesale, three retail - held fixed from the design stage; the frozen member map, every series identifier, and each file's hash are recorded in the data dictionary (Table TBL-A), and one aggregate carries a dated correction to a source mislabel with the superseded series retained as an audit trail. Coverage runs from January 1992 to the pull date. Cross-domain extensions use the Jorda-Schularick-Taylor macrohistory panel (eighteen countries, annual) and US Department of Labor unemployment-insurance claims; semiconductor work uses the Federal Reserve capacity-utilization series.

The data floor is a scope condition, not a preference (S-4): persistence estimation requires monthly frequency and at least thirty-six observations, sixty preferred. A twenty-observation quarterly sample cannot distinguish a persistence of 0.95 from one of 0.50, so quarterly filing data is excluded by design rather than accepted with a caveat.

### 5.2 Persistence, the Loop, and Damage

Persistence $\phi$ is the AR(1) coefficient, estimated by ordinary least squares of the series on its own lag with an intercept. OLS was pre-registered as the sole estimator. The alternative considered was Yule-Walker, and the comparison is reported rather than buried: on synthetic AR(1) histories at high true persistence, Yule-Walker is the more downward-biased of the two, so OLS was retained. That comparison is re-earned in this paper's own verification suite and is labeled a diagnostic, not a selectable specification - a specification the analyst may switch after seeing results is a specification the analyst is fishing with.

One estimation choice is stated here rather than left implicit, because it invites an obvious objection and the answer is a position rather than an oversight. Persistence is estimated on the measured variable IN LEVELS, not on its differences. For variables that are stationary to begin with - the inventory-to-sales ratio, the insured unemployment rate - the level persistence is directly interpretable and is computed on linearly detrended series. For variables that may carry a unit root, such as debt-to-GDP ratios, differencing would remove precisely what the framework is trying to measure: the level persistence captures the trend-following behaviour that makes a trailing average lag reality, and that lag IS the mechanism. Differencing first would produce a well-behaved series describing a different system. Where unit-root concerns apply, results are reported on both the level series and a stationary transformation, and the boundary is visible in the results rather than hidden - the three sovereign countries whose detrended estimates come back above one (Section 9.1) are that boundary showing itself, not an anomaly. Suggestions on the right specification for any particular dataset would be welcome.

The closed loop follows the construction of the companion work, used and not re-proved: a trailing-average estimator of window $W$ feeding a proportional feedback policy of aggressiveness $bg$ yields a $W \times W$ companion matrix $A(\phi, W, bg)$, whose spectral radius $\rho$ decides stability (S-1). Adaptation time $\tau$ is the structural function of $W$ carried from the companion work on trailing-average adaptation, with its constant frozen in the analysis scripts. Predicted damage is $D = (\rho_2/\rho_1)^{\tau}$, computed with $\rho_1$ at pre-transition persistence and $\rho_2$ at post-transition persistence, both evaluated at the system's own $(W, bg)$.

### 5.3 The Two Named Specifications

Two real-data specifications were named in advance and both are reported wherever both apply: SPEC-M, the monitoring specification ($W = 8$ months, $bg = 0.05$), and SPEC-R, the ranking specification ($W = 12$ months, $bg$ scale 3.0). Neither was selected after the fact. Three further specifications govern their own simulations - the Beer Game harness, the sovereign panel (five-year window, calm feedback swept upward for the crisis branch), and the unemployment-insurance reading - and are stated where they are used.

Reporting both specifications is what makes Section 8.1's spec-conditionality visible rather than concealed: results that hold under one and not the other are reported as exactly that.

### 5.4 The Primary Test and Its Amended Rule

The falsifier is the rolling out-of-sample panel validation (Section 6.3). At each month and sector, $\phi$ is estimated on the trailing sixty months, regime change is detected from the trailing twelve, $\tau$ follows from the window, and $D$ is computed under SPEC-M using backward-looking data only. The outcome is the sector's excess absolute I/S deviation over the following twelve months, measured against its own trailing baseline, with the deviation definition frozen in the script before the first real run.

The decision rule was amended once, before any hashed data was touched, and the amendment is disclosed because concealing it would misrepresent the test's strength. The pre-registered rule required a majority of regime-oscillating sectors to clear a per-sector significance bar. The mechanism-validation suite measured that rule at the real sample size and found it broken in the supporting direction: the block-bootstrap null placed the bar near a rank correlation of 0.30 while the operator's own detection noise capped even strong planted true effects well below it - measured power approximately zero. A rule that cannot detect a planted true effect is a rubber stamp, and discovering this before the run is precisely what the pre-run validation exists for.

The replacement rule, ratified and frozen before the run, moves the verdict to the panel level: the statistic is the mean Spearman correlation across regime-oscillating sectors; the null is a joint circular block bootstrap in which one set of twenty-four-month block indices is applied to every oscillating sector simultaneously, preserving the cross-sector dependence that a per-sector majority rule ignores, with $D$ held fixed and two thousand resamples. Support requires at least two oscillating sectors, a positive pooled mean, and a one-sided p below 0.01. The per-sector table (Table TBL-2) is retained as descriptive reporting and no longer carries the verdict. Verdict-level false support measured zero at the null. A pass under this rule is strong evidence; a failure is reported as indistinguishable from noise at this data resolution, not as disproof.

Sector classification is part of the operator, not a post-hoc convenience: sectors whose rolling $\rho$ crosses the boundary in both directions are regime-oscillating and carry the test; chronically-unstable sectors are boundary-condition cases reported separately, per the theorem's stated domain. The classification is computed over the full sample - membership is not knowable in real time - and Section 6.3 states the scope this places on the out-of-sample label.

One apparent tension is addressed in writing rather than left silent. The falsifier's trailing persistence estimate uses twelve observations, and the crisis-episode estimates use twenty-four - all below the thirty-six-observation floor S-4 declares. S-4 governs level placement: locating a firm or sector relative to the boundary, where estimator bias of the size measured in the OLS comparison (Section 6.3) moves the answer. The trailing estimate feeds a ranked change detector instead - what the falsifier consumes is not where a sector sits but how its recent persistence moves against its own baseline and against other sectors' contemporaneous moves - and small-sample attenuation compresses those estimates toward zero, biasing the detector against firing rather than toward it. The floor binds the tool's placement use (Sections 7.2-7.3); the change signal operates below it by design, conservatively, and this paragraph is that disclosure.

A second, smaller boundary disclosure, self-found during the adversarial-review round: the rolling evaluation's final point computes its forward mean over the eleven months remaining in the series rather than the documented twelve. The joint panel alignment truncates every sector to the shortest series' evaluation span, which removes that point entirely for fourteen of seventeen sectors; it survives only as the last of 341 points in the three shortest series, exactly one of which is regime-oscillating and therefore contributes roughly one three-thousandth of the pooled falsifier evidence through an eleven-month rather than twelve-month mean, with no signed direction. The statistic is a rank correlation; the committed values are unaffected for all other sectors and points.

### 5.5 Episodes, Ranking, and Monitoring

The two episode tests share one operator and differ only in dates. For each sector, $\phi_1$ is estimated over a pre-episode window and $\phi_2$ over the episode itself, $D$ follows, and the realized outcome is the excess deviation over the episode's peak window; the association is Spearman across the seventeen sectors, with a component bake-off reporting crisis $\rho$ alone and absolute change in persistence alone alongside the combined quantity; per a dated DESIGN amendment adopted at adversarial review, the ordering comparison between the combined quantity and each component is reported as a paired permutation contrast - the same permuted outcome ranked against all three predictors per draw, preserving their covariance - with a pre-committed resolved-positive / resolved-negative / unresolved reading at 0.05, rather than as a bare point comparison. The global financial crisis uses 2003-2006 against 2008-2009, with outcomes over 2007-2010. COVID uses 2017-2019 against 2020-2021, with outcomes over 2020-2022, and was pre-registered as an expected null with its polarity stated explicitly: a non-significant correlation together with persistence falling in most sectors is consistent with the boundary, while a strongly positive result would have been reported as a problem for the mechanism rather than a win (L-01). Episode tests are seventeen observations and are labeled corroborating; they cannot carry falsification, which Section 6.3 owns.

The cross-sector ranking (Table TBL-4) orders sectors by mean exceedance - the average of $\max(\rho - 1, 0)$ - after the originally registered ranking key, the share of months above the boundary, was found to saturate at its ceiling and tie the leaders. That re-instrumentation was chosen for dynamic range, blind to where any sector lands, and pre-registered before the re-run; a metric that cannot separate the leaders produces no ordering in either direction, so the earlier reading was recorded as uninformative rather than as a result. The monitoring record (Section 7.4) applies the same rolling construction at both specifications across the full sample, marks upward boundary crossings as below-to-above transitions, recording for each sector both the first crossing and the first crossing sustained three months, and reports status and crossing dates within twenty-four months either side of each episode onset; Section 7.4 quotes the sustained figures as the record matching this definition, with the raw crossings reported beside them.

### 5.6 The Echelon Decomposition and Its Amended Reading

The echelon decomposition (Section 7.1) asks where along the goods chain variance amplification concentrates. The chain is four monthly series - retail sales, merchant wholesalers' sales, manufacturers' shipments, manufacturers' new orders - with a durable-goods arm replacing the final step as a by-product of the same operator, carrying no separate verdict. The observable is the month-over-month log difference, computed on the intersection of observation dates taken on levels first and differenced inside that intersection, so every column is aligned by construction. Log differences rather than raw differences because the four series grew at materially different rates over the sample; a ratio on raw differences would confound scale and growth with the amplification it is meant to isolate. The statistic is the ratio of variances between adjacent steps. The reporting commitment includes the compound product of the step ratios and the direct end-to-end ratio; their discrepancy is an algebraic identity - the ratios telescope - and is disclosed as an arithmetic confirmation carrying no information about the data, because a quantity reported under the heading of a consistency check reads like a check that could have failed.

Uncertainty comes from a stationary block bootstrap with geometric blocks of mean twelve months, ten thousand resamples, and 95 percent percentile intervals, resampled JOINTLY: one set of date blocks is applied to every series in the chain, preserving within-month co-movement. The validation suite includes a leg that deliberately breaks the joint resampling and confirms the correlation-preservation self-test fires while the telescoping identity stays blind to the same defect - which is why the identity is not used as a self-test. A COVID-excluded pass applies the identical operator to the sample with 2020-01 through 2021-12 removed. The experiment is classified as a descriptive structural characterization with no verdict; the pre-registered separation rule declared the chain DISTINGUISHED only if exactly one step's interval lower bound exceeded every other step's upper bound, and INCONCLUSIVE otherwise.

That rule was mis-calibrated, and unlike the amendment in Section 5.4 the defect was found after the single real run rather than before it. Non-overlap of two 95 percent intervals is approximately a 0.005-level criterion rather than the 0.05 the rule appeared to imply, and requiring it against every competing step is stricter still; more damagingly, the rule compared each step's marginal interval in isolation, discarding exactly the cross-series covariance the joint resampling had been chosen to preserve. Both defects were knowable in advance and neither was known in advance by this author. Two disclosed follow-ups respond to this. A post-hoc resolution characterization, labelled exploratory, measures the rule's detection probability at the coupling the data actually exhibits - necessary because the suite's synthetic resolution claim was measured in a regime the data never occupied and did not transfer. And one secondary analysis computes the correctly targeted statistic - the within-resample simultaneous contrast, with the per-resample argmax probabilities - under a reading committed in the design document before the analysis script existed, with the contrast rule's false-positive rate checked against a ceiling before its interval is read, reported whatever it returned, and labelled secondary and post-hoc wherever it appears. The pre-registered result remains primary. Numbers, intervals, and measured power all live in Section 7.1 through the ledger.

### 5.7 Simulations, Seeds, and Disclosure

The simulation studies use paired designs: within a run, every algorithm faces identical demand sequences, seeds are recorded, and run counts were fixed in advance. The Beer Game comparison (Table TBL-3) runs four algorithms against one frozen calibration with no parameter search on the demand process. The chain-length study reports its full grid - three chain lengths by three capacity levels by four demand environments, at 250 seeds, five times the source's fifty - as the experiment rather than as a search, and every cell is reported including the unresolved ones. The pricing and hysteresis studies likewise report all cells. One provenance distinction is stated rather than blurred: the pricing study is an analysis, not a run - it recomputes its claims from the source's own committed trial records (1,800 raw trials), because a re-execution was measured at roughly nineteen seconds per trial, about fifty-five hours for the grid, and rejected; the artifact is registered in data/SOURCES.md and carried in Table TBL-A. Simulation verdicts bind the model, and generalization to the world is a separate and weaker claim (S-5).

The anti-fishing disclosure is the pair of counts, not either alone: the design document stated in advance how many specifications would be tried, and the totals actually run match those counts. Any specification beyond them would have required a dated amendment before the run, tested against the question of whether the same change would have been made had it pushed the result the other way.

Every load-bearing number in this paper is generated by a committed script from hashed inputs, recorded in a machine-checked ledger, and substituted into the text by a committed renderer; no figure is retyped by hand. The verification apparatus, including the ledger's coverage and the checks that guard it, is described in Appendix B.

## 6 Empirical Validation

### 6.1 GFC Episode

Pre-crisis predicted damage ranking aligns with realized crisis damage (corroborating; L-06 states the limit) [@Udenio-2015; @Dooley-2010]. This is an episode association by construction - the crisis estimation window is contemporaneous with part of the realized window - and is never an out-of-sample prediction; Section 6.3 owns prediction. Combined $D$: Spearman {{LB-E2-gfc-spearman:.4f}}, permutation p {{LB-E2-gfc-p:.4f}}, n {{LB-E2-gfc-n}}, verdict {{LB-E2-gfc-verdict}}; component bake-off $\rho_{\mathrm{crisis}}$ {{LB-E2-components-rho-crisis:.4f}}, $\lvert\Delta\phi\rvert$ {{LB-E2-components-absdphi:.4f}}, combined-beats-components (point estimate) {{LB-E2-components-combined-ge}}. Under the amended ordering reading (Methods 5.5), the paired contrasts carry their own uncertainty: $D$ over $\rho_{\mathrm{crisis}}$ {{LB-E2-contrast-rho:.4f}} (one-sided permutation p {{LB-E2-contrast-rho-p:.4f}}, {{LB-E2-contrast-rho-reading}}); $D$ over $\lvert\Delta\phi\rvert$ {{LB-E2-contrast-dphi:.4f}} (p {{LB-E2-contrast-dphi-p:.4f}}, {{LB-E2-contrast-dphi-reading}}). Both are unresolved at n = 17 under the pre-committed 0.05 reading, so the ordering is reported as point-estimate-descriptive and the verdict's inferential weight rests on the association leg - with the substructure disclosed rather than averaged: the compound's edge over the level component alone is large (crisis $\rho$ alone anti-correlates with realized damage) and sits just outside the reading's threshold, while its edge over the change component alone is small. Table TBL-1 reports the full panel.

<!-- anchor: TBL-1 -->

*Table TBL-1. GFC episode (2008-09): episode-level association between predicted $D$ and realized inventory/sales deviation, with the component bake-off. Paired-contrast rows follow the dated F-07 amendment: same permuted outcome ranked against all three predictors per draw, one-sided p, pre-committed resolved/unresolved reading at 0.05. The committed episode artifact carries episode statistics and components; per-sector regime detail is in Table TBL-2.*

| Statistic | Value |
| --- | --- |
| Sectors (n) | {{LB-E2-gfc-n}} |
| Spearman, predicted $D$ vs realized deviation | {{LB-E2-gfc-spearman:.4f}} |
| One-sided p | {{LB-E2-gfc-p:.4f}} |
| Verdict (pre-registered rule) | {{LB-E2-gfc-verdict}} |
| Component alone: crisis $\rho$ (Spearman) | {{LB-E2-components-rho-crisis:.4f}} |
| Component alone: $\lvert\Delta\phi\rvert$ (Spearman) | {{LB-E2-components-absdphi:.4f}} |
| Combined $D$ at least matches each component (point estimate; paired contrasts unresolved) | {{LB-E2-components-combined-ge}} |
| Paired contrast: $D$ minus crisis $\rho$ | {{LB-E2-contrast-rho:.4f}} |
| Paired contrast p (one-sided) | {{LB-E2-contrast-rho-p:.4f}} |
| Paired contrast reading | {{LB-E2-contrast-rho-reading}} |
| Paired contrast: $D$ minus $\lvert\Delta\phi\rvert$ | {{LB-E2-contrast-dphi:.4f}} |
| Paired contrast p (one-sided) | {{LB-E2-contrast-dphi-p:.4f}} |
| Paired contrast reading | {{LB-E2-contrast-dphi-reading}} |


### 6.2 COVID Episode

COVID was pre-registered as an expected null, and the reason matters more than the result. The theorem prices a step change in the dangerous direction: persistence rises, the loop that was decaying starts compounding, and the estimator's lag becomes expensive. COVID was not that shock. Demand collapsed and rebounded across multiple channels at once, and in most sectors measured persistence FELL rather than rose - a compound multi-channel disturbance sitting squarely outside the step-change model (L-01) [@Saricioglu-2025]. A framework that predicted damage rankings here would be a framework detecting crises in general rather than the specific mechanism it claims, so the null is the outcome that supports the theory and a positive result would have undermined it. Result: Spearman {{LB-E3-covid-spearman:.4f}}, p {{LB-E3-covid-p:.4f}}, n {{LB-E3-covid-n}}, verdict {{LB-E3-covid-verdict}}; persistence dropped in {{LB-E3-persistence-direction-count}} of 17 sectors (majority {{LB-E3-persistence-direction-majority}}) - the falsifiable boundary direction confirmed. This is the paper's cleanest demonstration that the diagnostic is scoped rather than universal: it declines to fire on the most famous supply-chain disruption in living memory, because that disruption is not the kind of event it prices.

### 6.3 Rolling 34-Year Validation

The primary falsifier: rolling out-of-sample $D$ predicts subsequent inventory-to-sales deviation at the panel level across regime-oscillating sectors (amended rule B, pooled statistic) [@Cachon-2007]. Result: pooled mean Spearman {{LB-E1-panel-spearman:.4f}}, joint block-bootstrap panel p {{LB-E1-panel-p:.4f}} over {{LB-E1-panel-n-oscillating}} oscillating sectors ({{LB-E1-panel-n-chronic}} chronic-boundary), verdict {{LB-E1-panel-verdict}}; per-sector range {{LB-E1-range-min:.4f}} to {{LB-E1-range-max:.4f}} (descriptive). The estimator choice is justified by the supplementary OLS-vs-YW comparison (OLS mean estimate {{LB-T1-estimator-ols:.4f}} vs Yule-Walker mean estimate {{LB-T1-estimator-yw:.4f}}, both against true $\phi$ 0.95 at n = 40, so the higher mean is the less downward-biased; OLS less biased: {{LB-T1-estimator-ols-less-biased}}; labeled not-a-theorem). Table TBL-2 reports per-sector detail.

Two scope statements accompany this result, both a matter of what the test can and cannot have measured. First, because the window $W$ is constant across the panel, $\tau$ is a single positive constant, and a rank statistic is invariant to any monotone transform: the rolling test is rank-identical to a test on the spectral-radius ratio alone, so what it validates is the intensity ordering the bound implies, not the exponent - the compounding itself receives no empirical test from this panel, and a test of the exponent would require cross-sectional variation in $W$ that these series do not provide. Second, the sector classification that selects which series carry the test is a full-sample operator: the out-of-sample property holds within each selected sector's time series, not at the level of panel membership, and a real-time user at the sample's start could not have known which sectors would classify as oscillating. The registered prediction in Section 11.3 fixes its membership prospectively for exactly this reason.

<!-- anchor: TBL-2 -->

*Table TBL-2. Rolling 34-year out-of-sample validation, per sector: full-sample regime class, Spearman between trailing $D$ and forward deviation, and the descriptive one-sided block-bootstrap p ($\alpha$ 0.05 reference; the verdict is panel-level, not per-sector). Panel result: {{LB-E1-panel-n-oscillating}} oscillating sectors ({{LB-E1-panel-n-chronic}} chronic-boundary), pooled mean Spearman {{LB-E1-panel-spearman:.4f}}, joint panel p {{LB-E1-panel-p:.4f}}, verdict {{LB-E1-panel-verdict}}; per-sector Spearman range {{LB-E1-range-min:.4f}} to {{LB-E1-range-max:.4f}} (descriptive). Estimator footnote: OLS AR(1) mean estimate {{LB-T1-estimator-ols:.4f}} vs Yule-Walker {{LB-T1-estimator-yw:.4f}} (true $\phi$ 0.95, n 40); OLS less biased: {{LB-T1-estimator-ols-less-biased}} (supplementary, not-a-theorem).*

| Sector | Regime class | Spearman | p (descriptive) |
| --- | --- | --- | --- |
| {{LB-E1-tbl2-r01-sector}} | {{LB-E1-tbl2-r01-class}} | {{LB-E1-tbl2-r01-spearman:.4f}} | {{LB-E1-tbl2-r01-p:.4f}} |
| {{LB-E1-tbl2-r02-sector}} | {{LB-E1-tbl2-r02-class}} | {{LB-E1-tbl2-r02-spearman:.4f}} | {{LB-E1-tbl2-r02-p:.4f}} |
| {{LB-E1-tbl2-r03-sector}} | {{LB-E1-tbl2-r03-class}} | {{LB-E1-tbl2-r03-spearman:.4f}} | {{LB-E1-tbl2-r03-p:.4f}} |
| {{LB-E1-tbl2-r04-sector}} | {{LB-E1-tbl2-r04-class}} | {{LB-E1-tbl2-r04-spearman:.4f}} | {{LB-E1-tbl2-r04-p:.4f}} |
| {{LB-E1-tbl2-r05-sector}} | {{LB-E1-tbl2-r05-class}} | {{LB-E1-tbl2-r05-spearman:.4f}} | {{LB-E1-tbl2-r05-p:.4f}} |
| {{LB-E1-tbl2-r06-sector}} | {{LB-E1-tbl2-r06-class}} | {{LB-E1-tbl2-r06-spearman:.4f}} | {{LB-E1-tbl2-r06-p:.4f}} |
| {{LB-E1-tbl2-r07-sector}} | {{LB-E1-tbl2-r07-class}} | {{LB-E1-tbl2-r07-spearman:.4f}} | {{LB-E1-tbl2-r07-p:.4f}} |
| {{LB-E1-tbl2-r08-sector}} | {{LB-E1-tbl2-r08-class}} | {{LB-E1-tbl2-r08-spearman:.4f}} | {{LB-E1-tbl2-r08-p:.4f}} |
| {{LB-E1-tbl2-r09-sector}} | {{LB-E1-tbl2-r09-class}} | {{LB-E1-tbl2-r09-spearman:.4f}} | {{LB-E1-tbl2-r09-p:.4f}} |
| {{LB-E1-tbl2-r10-sector}} | {{LB-E1-tbl2-r10-class}} | {{LB-E1-tbl2-r10-spearman:.4f}} | {{LB-E1-tbl2-r10-p:.4f}} |
| {{LB-E1-tbl2-r11-sector}} | {{LB-E1-tbl2-r11-class}} | {{LB-E1-tbl2-r11-spearman:.4f}} | {{LB-E1-tbl2-r11-p:.4f}} |
| {{LB-E1-tbl2-r12-sector}} | {{LB-E1-tbl2-r12-class}} | {{LB-E1-tbl2-r12-spearman:.4f}} | {{LB-E1-tbl2-r12-p:.4f}} |
| {{LB-E1-tbl2-r13-sector}} | {{LB-E1-tbl2-r13-class}} | {{LB-E1-tbl2-r13-spearman:.4f}} | {{LB-E1-tbl2-r13-p:.4f}} |
| {{LB-E1-tbl2-r14-sector}} | {{LB-E1-tbl2-r14-class}} | {{LB-E1-tbl2-r14-spearman:.4f}} | {{LB-E1-tbl2-r14-p:.4f}} |
| {{LB-E1-tbl2-r15-sector}} | {{LB-E1-tbl2-r15-class}} | {{LB-E1-tbl2-r15-spearman:.4f}} | {{LB-E1-tbl2-r15-p:.4f}} |
| {{LB-E1-tbl2-r16-sector}} | {{LB-E1-tbl2-r16-class}} | {{LB-E1-tbl2-r16-spearman:.4f}} | {{LB-E1-tbl2-r16-p:.4f}} |
| {{LB-E1-tbl2-r17-sector}} | {{LB-E1-tbl2-r17-class}} | {{LB-E1-tbl2-r17-spearman:.4f}} | {{LB-E1-tbl2-r17-p:.4f}} |


### 6.4 Beer Game Monte Carlo

Acting on the diagnostic saves cost within this experiment's own construction (L-03 binds; the source's ERP figure is not carried) [@Oroojlooyjadid-2022]. Base-stock comparator {{LB-E4-erp:.4f}}; $\phi$-gated spectral tool {{LB-E4-tool:.4f}} (relative reduction {{LB-E4-tool-relreduction:.4f}}, paired p {{LB-E4-tool-p:.4f}}, verdict {{LB-E4-tool-verdict}}); full theorem {{LB-E4-full:.4f}}; win rate {{LB-E4-winrate}}; engagement boundary {{LB-E4-tool-phi-engagement:.4f}} (a property of this construction). Table TBL-3 reports costs by algorithm.

<!-- anchor: TBL-3 -->

*Table TBL-3. Beer Game Monte Carlo, mean cost by algorithm with the paired comparison - a property of E4's own construction, model-bound per the audit (the source-fidelity claim is withdrawn; no external benchmark figure is carried).*

| Statistic | Value |
| --- | --- |
| Mean cost, self-calibrating base-stock (ERP-style baseline) | {{LB-E4-erp:.4f}} |
| Mean cost, $\phi$-gated spectral damping (the tool) | {{LB-E4-tool:.4f}} |
| Mean cost, full theorem policy | {{LB-E4-full:.4f}} |
| Paired p, tool vs baseline | {{LB-E4-tool-p:.4f}} |
| Relative cost reduction, tool vs baseline | {{LB-E4-tool-relreduction:.4f}} |
| Verdict (pre-registered rule) | {{LB-E4-tool-verdict}} |
| Engagement persistence ($\phi$ at which the gate engages; a property of this construction) | {{LB-E4-tool-phi-engagement:.4f}} |
| Pairwise win rate, full theorem vs spectral | {{LB-E4-winrate}} |


## 7 Supply Chain Application

### 7.1 Bullwhip Instability Finding

The classical bullwhip literature explains amplification through informational and incentive channels: demand signal processing, order batching, rationing games, price promotions [@Lee-1997a; @Lee-1997b; @Chen-2000]. The measurement channel adds a structural one that operates even when every informational pathology has been eliminated. If measured persistence is high enough, a standard order-up-to policy driven by a trailing estimate is not merely amplifying - it is operating at or past its own stability boundary, and the amplification is a property of the control loop rather than of anyone's behavior. That is what the panel shows: manufacturing-aggregate mean $\rho$ {{LB-E5-persistence-mfg-meanrho-R:.4f}} (SPEC-R) and {{LB-E5-persistence-mfg-meanrho-M:.4f}} (SPEC-M). Under SPEC-R the boundary is not a line these sectors occasionally cross; it is a line they operate above, which is the finding that shapes everything in Section 8.

**Where the amplification concentrates.** The claim above says the loop is unstable; it does not say *where* along the chain the instability does its work. That is a separate question, and it is the one place in this paper where the mechanism can be located in real data rather than inferred from association or simulation. We decompose the variance of monthly log changes along the goods chain - retail sales, merchant wholesalers' sales, manufacturers' shipments, manufacturers' new orders - and take the ratio of variances between adjacent steps, with uncertainty from a stationary block bootstrap resampled jointly across the chain so that within-month co-movement is preserved. The observable is the log difference rather than the raw difference because these four series grew at materially different rates over the sample, and a ratio on raw differences would confound scale and growth with the amplification it is meant to isolate. The realised common window is {{LB-E14-chain-full-n}} monthly changes; excluding 2020-01 through 2021-12 leaves {{LB-E14-chain-excl-n}}. Full detail is in Table TBL-8.

<!-- anchor: TBL-8 -->

*Table TBL-8. Echelon variance decomposition: adjacent-step variance ratios on monthly log changes, with 95 percent stationary-block-bootstrap intervals resampled jointly across the chain. A ratio above 1 means variance grows across that step. The durable-goods arm replaces the final step with durable-goods new orders and is a by-product of the same operator, carrying no separate verdict. The secondary panel below reports the post-hoc contrast and is labelled as such.*

| Step | Full sample (n = {{LB-E14-chain-full-n}}) | Excluding COVID (n = {{LB-E14-chain-excl-n}}) | Durable-goods arm (n = {{LB-E14-arm-n}}) |
| --- | --- | --- | --- |
| retail to wholesale | {{LB-E14-chain-full-s1-ratio:.4f}} [{{LB-E14-chain-full-s1-lo:.4f}}, {{LB-E14-chain-full-s1-hi:.4f}}] | {{LB-E14-chain-excl-s1-ratio:.4f}} [{{LB-E14-chain-excl-s1-lo:.4f}}, {{LB-E14-chain-excl-s1-hi:.4f}}] | {{LB-E14-arm-s1-ratio:.4f}} [{{LB-E14-arm-s1-lo:.4f}}, {{LB-E14-arm-s1-hi:.4f}}] |
| wholesale to shipments | {{LB-E14-chain-full-s2-ratio:.4f}} [{{LB-E14-chain-full-s2-lo:.4f}}, {{LB-E14-chain-full-s2-hi:.4f}}] | {{LB-E14-chain-excl-s2-ratio:.4f}} [{{LB-E14-chain-excl-s2-lo:.4f}}, {{LB-E14-chain-excl-s2-hi:.4f}}] | {{LB-E14-arm-s2-ratio:.4f}} [{{LB-E14-arm-s2-lo:.4f}}, {{LB-E14-arm-s2-hi:.4f}}] |
| shipments to new orders | {{LB-E14-chain-full-s3-ratio:.4f}} [{{LB-E14-chain-full-s3-lo:.4f}}, {{LB-E14-chain-full-s3-hi:.4f}}] | {{LB-E14-chain-excl-s3-ratio:.4f}} [{{LB-E14-chain-excl-s3-lo:.4f}}, {{LB-E14-chain-excl-s3-hi:.4f}}] | {{LB-E14-arm-s3-ratio:.4f}} [{{LB-E14-arm-s3-lo:.4f}}, {{LB-E14-arm-s3-hi:.4f}}] |
| compound product of steps | {{LB-E14-chain-full-compound:.4f}} | {{LB-E14-chain-excl-compound:.4f}} | {{LB-E14-arm-compound:.4f}} |
| direct end-to-end ratio | {{LB-E14-chain-full-e2e:.4f}} | {{LB-E14-chain-excl-e2e:.4f}} | {{LB-E14-arm-e2e:.4f}} |
| discrepancy, compound minus end-to-end | {{LB-E14-chain-full-identity:.2e}} | {{LB-E14-chain-excl-identity:.2e}} | - |
| pre-registered rule | {{LB-E14-chain-full-result}} | {{LB-E14-chain-excl-result}} | {{LB-E14-arm-result}} |

The ordering step is the largest in every configuration and its interval excludes 1 in every configuration. One step *attenuates*: variance shrinks from wholesale sales to manufacturers' shipments, so the chain is not monotonically amplifying and the aggregate bullwhip is not the sum of uniform stagewise growth. Excluding the pandemic window strengthens the concentration rather than weakening it, which is the one place this paper speaks directly to the question of whether the pattern is structural or crisis-driven, and it points to structural.

We report the compound product and the direct end-to-end ratio because the pre-registration commits us to both, and we report their discrepancy for the same reason - but that discrepancy is an algebraic identity, not evidence. The step ratios telescope, so on a common sample the two quantities are the same number and their difference is zero by construction. It confirms that the arithmetic is arithmetic and tells us nothing whatever about supply chains. We state this because a quantity reported under the heading of an internal-consistency check reads, to a reader, exactly like a check that could have failed.

**The pre-registered rule did not fire, and on the full sample it could not have.** Our registered decision rule declared separation only when one step's interval lower bound cleared every other step's interval upper bound; on the registered chain it returned {{LB-E14-chain-full-result}} on the full sample and {{LB-E14-chain-excl-result}} excluding COVID. Two things must be said about that, and the first is uncomfortable. Measured afterwards, in an exploratory characterization at the coupling the data actually exhibits, the detection probability of that rule at the effect size we observed on the full sample was {{LB-E14-severity-full-power-at-full-effect:.2f}}; at the COVID-excluded effect size it was {{LB-E14-severity-excl-power-at-excl-effect:.2f}}. The full-sample verdict therefore carries no information: it is the outcome the rule would have produced whether or not a concentration of that magnitude is real. The smallest ordering-step ratio the rule resolves at 80 percent recovery is {{LB-E14-severity-full-r3-at-80:.1f}} on the full sample, above the {{LB-E14-chain-full-s3-ratio:.2f}} measured there; excluding COVID it is {{LB-E14-severity-excl-r3-at-80:.1f}}, just below the {{LB-E14-chain-excl-s3-ratio:.2f}} measured on that configuration. Reassuringly, the same characterization puts the rule's false-positive rate at {{LB-E14-severity-full-fpr:.2f}} and {{LB-E14-severity-excl-fpr:.2f}} when no concentration is planted, so its error runs in one direction only: it does not manufacture structure, and on the full sample it lacked the power to detect a concentration of the magnitude actually measured. The excluded-sample non-detection is not excused by power: at that configuration's measured effect the rule detects with probability {{LB-E14-severity-excl-power-at-excl-effect:.2f}}, yet the observed intervals missed separation by a hair - the ordering step's lower bound of {{LB-E14-chain-excl-s3-lo:.2f}} against the runner-up step's upper bound of {{LB-E14-chain-excl-s1-hi:.2f}}; the simultaneous contrast below resolves what the mis-specified rule could not. For completeness the cross-configuration cells are {{LB-E14-severity-full-power-at-excl-effect:.2f}} and {{LB-E14-severity-excl-power-at-full-effect:.2f}}.

The second thing is that the rule was mis-specified in a way that was knowable in advance and was not known in advance by this author. Non-overlap of two 95 percent intervals is approximately a 0.005-level criterion rather than a 0.05-level one, and requiring it against every competing step is stricter still; more importantly, the design had already chosen joint resampling precisely to preserve the covariance between step ratios, and then discarded that covariance by comparing each step's interval in isolation. We record this as a defect in our own pre-registration rather than as a property of the data.

**Secondary analysis, specified after the result and labelled accordingly.** Because the defect is result-independent, we report one secondary analysis on the correctly targeted statistic, with its reading committed in writing before the analysis was run and reported here whatever it returned. Within each bootstrap resample we compute the contrast between the largest step and each other step, taking the minimum so the comparison is simultaneous, and we report the proportion of resamples in which each step is the largest. The pre-committed admissibility condition was that the contrast rule's false-positive rate must not exceed 0.05; measured at realised coupling it is {{LB-E14-contrast-fpr-worst:.2f}} - a rate conditioned on the contrast separating the ordering step specifically, and therefore a lower bound on the whole rule's false-positive rate; the mechanism suite's check applies the unconditioned select-then-contrast version - so the rule fires more often on true effects without firing more often on none, and the outcome recorded is {{LB-E14-contrast-outcome}}.

*Table TBL-8, secondary panel (POST-HOC, SECONDARY). The simultaneous contrast and argmax probabilities described above, reported alongside the pre-registered result and never in place of it.*

| Configuration | Simultaneous contrast [95 pct] | P(ordering step largest) | P(middle step largest) | Power at that configuration's observed effect |
| --- | --- | --- | --- | --- |
| Full sample | {{LB-E14-contrast-full-point:.4f}} [{{LB-E14-contrast-full-lo:.4f}}, {{LB-E14-contrast-full-hi:.4f}}] | {{LB-E14-contrast-full-argmax-top:.4f}} | {{LB-E14-contrast-full-argmax-mid:.4f}} | {{LB-E14-contrast-power-full:.2f}} |
| Excluding COVID | {{LB-E14-contrast-excl-point:.4f}} [{{LB-E14-contrast-excl-lo:.4f}}, {{LB-E14-contrast-excl-hi:.4f}}] | {{LB-E14-contrast-excl-argmax-top:.4f}} | {{LB-E14-contrast-excl-argmax-mid:.4f}} | {{LB-E14-contrast-power-excl:.2f}} |
| Durable-goods arm | {{LB-E14-contrast-arm-point:.4f}} [{{LB-E14-contrast-arm-lo:.4f}}, {{LB-E14-contrast-arm-hi:.4f}}] | {{LB-E14-contrast-arm-argmax-top:.4f}} | {{LB-E14-contrast-arm-argmax-mid:.4f}} | not characterized |

Under this statistic the ordering step separates in all three configurations, and the middle step is never the largest in any resample of any configuration. All power and false-positive rates reported here are proportions over {{LB-E14-contrast-power-reps}} replications at realised coupling, so a rate of 1.00 means every replication rather than certainty, and a rate of 0.00 means none rather than impossibility. The honest weighting is this: the COVID-excluded reading is the sound one, with measured power at its observed effect of {{LB-E14-contrast-power-excl:.2f}}; the full-sample reading fired at a configuration whose measured power is only {{LB-E14-contrast-power-full:.2f}}, and a single result obtained where the rule fires roughly a third of the time is fragile and should not be presented as strong. The durable-goods arm separated under both the pre-registered rule and the contrast, but its coupling regime was never power-characterized, so no power figure attaches to it and it rests on the pre-registered rule's zero false-positive rate.

The claim we are willing to defend, therefore, is that amplification **concentrates at the ordering step** - not that we have proven it.

One external corroboration is worth recording, because it was not available to this analysis and was not used in designing it. The pinned source document reports its own layer-by-layer decomposition of the same chain, computed years earlier on a shorter sample by a different construction. Its ordering is the same as ours: a retail-to-wholesale step near unity, a middle step *below* unity, and the large step at manufacturing orders - with a total close to what we obtain. We did not calibrate to those figures and do not quote them as evidence; the point is that an independent construction on different data recovers the same shape, including the attenuating middle step, which is the feature most likely to be dismissed as noise in a single sample. The correspondence supports the decomposition's stability without adding a claim of its own.

And the scope condition (S-1) binds with full force here: this analysis locates *where* amplification concentrates. It does not establish that the measurement mechanism *caused* the concentration. Concentration at the point where firms convert observed demand into orders is consistent with the mechanism this paper models, and it does not exclude the batching, rationing, and promotional channels the classical literature describes.

### 7.2 Spectral Radius Ordering Tool

The practical form of the result is an ordering rule: estimate demand persistence from data a firm already has, compute the spectral radius its current window and feedback rate imply, and read off whether the loop sits below the boundary, above it, or close enough that a regime change would push it over. The rule inverts the same stability geometry as the region-inversion and eigenvalue precedents, but takes an estimated persistence as its input rather than a design parameter [@Warburton-2004; @Wang-2013; @Udenio-2017; @Gaalman-Disney-2009; @Boute-2006].

Two properties of that rule are worth stating plainly, because both answer objections a practitioner will raise.

The first is why a spectral radius rather than the familiar variance-amplification ratio [@Chen-2000]. The two measure related but distinct things, and the distinction decides behaviour. Two systems can share an identical amplification ratio and behave oppositely: one whose spectral radius sits just below one will self-correct, while one just above will self-amplify. A variance ratio cannot separate those cases, because it reports how much the signal grew and not whether the loop that grew it is convergent. That is the whole reason this framework measures what it measures.

The second is why the rule can depend on demand persistence at all when the stability-region inversions it resembles cannot [@Warburton-2004; @Wang-2013; @Udenio-2017]. In the linear order-up-to formulations those results analyse, the closed-loop eigenvalues depend only on feedback gains and lead times, so their admissible regions are necessarily independent of how persistent demand happens to be. The construction here augments the state: the AR(1) demand process is embedded directly into the closed-loop companion matrix, which is what allows an estimated persistence to enter the constraint. The closest precedent found for an eigenvalue analysis driven by the demand process's own autocorrelation is the ARMA-demand eigenvalue work [@Gaalman-Disney-2009], with the closed-loop production-inventory modelling of [@Boute-2006] related in spirit though built on a queueing apparatus under i.i.d. demand. The framing as a practitioner rule taking OBSERVED persistence as its input is, as far as has been found, novel within this tradition - and correction would be welcome if closer prior work exists.

One operational consequence follows and is easy to miss. The window is not always an available lever. At the persistence levels the manufacturing panel actually exhibits, shortening the measurement window does not bring the loop back inside the boundary - the persistence is too high for a window-based fix - and only reducing feedback aggressiveness moves the spectral radius meaningfully. An institution that responds to a boundary warning by measuring faster may find it has spent effort on the lever that does not move.

The input requirement is the binding constraint in practice, and it is stated as a scope condition rather than a caveat. S-4 sets the data floor: monthly frequency with at least 36 observations, 60 preferred. Below that floor the persistence estimate carries more sampling error than the boundary comparison can absorb, and the tool returns a number with no informational content. Quarterly filing data is insufficient - a limitation with immediate consequences for who can use this and on what data, taken up next.

### 7.3 Firm-Level Bookend

The data floor has a sharp institutional edge. The richest publicly available firm-level operating data - quarterly filings - cannot support the estimate the tool requires: a decade of quarterly observations yields roughly forty points, and the persistence estimate at that sample size is too noisy to place a firm relative to the boundary with any confidence. The consequence is a genuine limit on the diagnostic's reach rather than a temporary data-collection problem. Firms can run this analysis internally on their own monthly or weekly series; outside analysts working from public filings generally cannot, which is why every empirical result in this paper is sector-level rather than firm-level (S-4). (Conditional on the deferred EDGAR entry; any quoted figure will be ledgered.)

### 7.4 Cross-Sector Evidence

The rolling monitoring record is backward-looking and weaker than Section 6.3, and says so: it documents what a boundary dashboard would have displayed around the two crisis onsets, not lead-time predictivity (Section 6.3 carries the out-of-sample claim). The committed record is honest about direction: the monitor is reactive. Around the 2008-09 onset, under the crossing-informative specification, no sector sat above the boundary beforehand, and under the sustained three-month definition of Section 5.5, {{LB-E5-monitor-specm-gfc-sustained-count}} sectors crossed in the window with {{LB-E5-monitor-specm-gfc-sustained-precede-count}} sustained crossings preceding the onset; the manufacturing aggregate's status was {{LB-E5-monitor-specm-mfg-gfc-status}} with first sustained crossing {{LB-E5-monitor-specm-mfg-gfc-sustained}}. Counting raw first crossings without the sustain requirement gives {{LB-E5-monitor-specm-gfc-crossing-count}} crossing sectors ({{LB-E5-monitor-specm-gfc-precede-count}} pre-onset; manufacturing first raw crossing {{LB-E5-monitor-specm-mfg-gfc-first-crossing}}), clustered two to five months after the onset. Around the 2020-03 onset the sustained record is {{LB-E5-monitor-specm-covid-sustained-count}} crossing sectors with {{LB-E5-monitor-specm-covid-sustained-precede-count}} sustained crossings preceding the onset - the raw crossings that nominally preceded it do not survive the sustain requirement, so under the stated definition no crossing preceded either onset; the raw count is {{LB-E5-monitor-specm-covid-crossing-count}} sectors, of which {{LB-E5-monitor-specm-covid-precede-count}} nominally preceded the onset by one to two months (within monthly-data noise, not offered as warning); the manufacturing aggregate's status was {{LB-E5-monitor-specm-mfg-covid-status}} with first sustained crossing {{LB-E5-monitor-specm-mfg-covid-sustained}} (first raw crossing {{LB-E5-monitor-specm-mfg-covid-first-crossing}}). Under the primary specification the boundary saturates as disclosed in advance: {{LB-E5-monitor-specr-gfc-above-throughout-count}} of seventeen sectors sat above the boundary throughout the GFC window and {{LB-E5-monitor-specr-covid-above-throughout-count}} throughout the COVID window, so episode-specific crossing information lives at the crossing-informative specification - the spec-conditionality of Section 8.1 again. Two characterizations follow. First, the sectors that cross in either crisis window are exactly the nine boundary-oscillating sectors of the Section 6.3 classification, and the sectors that never cross are exactly the never-crossing class: the panel's boundary-crossing action over thirty-four years concentrates in these two crisis windows (in part reflecting that the full-sample classification contains these episodes). Second, and on-theme: the instability monitor is itself a lagging measurement - it confirms regime shifts with a two-to-five-month lag rather than predicting them, which is this paper's thesis applied to its own dashboard.

### 7.5 Boundary Conditions

A diagnostic that is only ever tested where it works has not been tested. The four simulation studies in Appendix F were built to find the edges of this one, and they found four, each of which constrains the advice the paper is entitled to give [@Boute-2022].

The chain-length result is conditional, not universal. The source this rebuild replaces reported a crossover at long chains where the tool turns from harmful to beneficial; re-run at five times the seed count, that crossover holds only with capacity headroom, and in the tight-capacity cells the tool remains harmful at every chain length tested. More than half the source's grid was unresolved at its seed count, so what looked like a clean transition was a reading taken through noise. Pricing value behaves as a cliff rather than a slope: it is large where capacity strain is moderate and turns net-negative above a strain threshold, so a firm that adopts the raise rule without knowing which side of that cliff it occupies may be buying the harm rather than the benefit.

The pricing result is asymmetric, and the asymmetry is the practical content. On the raise side the benefit is real where capacity is strained. On the cut side it is not: recommending a price cut in response to a demand decrease produced negative value in every environment tested - low-persistence {{LB-E8-down-low_phi_shift_down-mean:.4f}}, mid-persistence {{LB-E8-down-mid_phi_shift_down-mean:.4f}}, persistent level shift {{LB-E8-down-level_shift_down_persistent-mean:.4f}}. Under the immediate-arithmetic demand model this study assumes, the defensible reading is narrow and one-directional: the persistence calculation offers operationally meaningful guidance on when NOT to cut prices, and no comparable licence to cut them.

The hysteresis result splits, and the split is the finding: the raise strategy survives permanent customer attrition in genuinely shifted, persistent regimes, and fails in noisy ones where the estimator's own variance drives the policy on and off. The mechanism behind the robust half is worth stating, because it explains a result that otherwise looks implausible. At the heaviest attrition tested the policy permanently loses a large fraction of the customer base and the benefit still holds, because the two effects are not commensurate: when capacity is genuinely strained, the stockout costs avoided by raising price exceed the revenue lost to departing customers by a margin wide enough to absorb substantial attrition. Where capacity is loose, that margin is thin, the same attrition dominates, and the policy turns harmful.

The fourth boundary is the sharpest, and the honest way to state it is as a comparison rather than a failure. Under drifting persistence the recipe is beaten by the crudest available alternative: a FIXED damping coefficient - no estimator, no persistence calculation, no recipe at all - outperforms both the estimator-driven policy and an oracle handed the true parameter at every step (paired contrasts {{LB-E12-oracle-legb-L8x18-fixedvsoracle:.4f}} and {{LB-E12-oracle-legb-L8x24-fixedvsoracle:.4f}} against the oracle, {{LB-E12-oracle-legb-L8x18-fixedvsols:.4f}} and {{LB-E12-oracle-legb-L8x24-fixedvsols:.4f}} against the estimator). That the oracle also loses is what makes the diagnosis specific: THE LIMITATION IS IN THE RECIPE, NOT THE ESTIMATOR. A policy that mapped persistence to damping under a stationarity assumption returns a coefficient optimal for the persistence value it was handed, not for the trajectory of values the system will actually traverse. If the remedy failed because measurement was noisy, better measurement would fix it; it does not, and no amount of estimator precision reaches a parameter that will not hold still (S-8, L-04).

The scope of that limitation is itself unresolved, and naming what was not tested is more useful than a general caveat: one trajectory shape was examined, and slow drift, square-wave oscillation, and sudden one-shot jumps were not. Whether the recipe-level failure reproduces across those shapes is open, and a recipe taking both the level of persistence and its rate of change as inputs - drawing on the companion work on adaptation rates and on trajectory detection - is the natural route to one that survives drift. That is identified as a direction, not claimed as a result.

Appendix F carries the four studies in full and Table TBL-7 reports every cell, including the unresolved ones. Scope conditions S-3 and S-5 and limits L-01 and L-03 bind here: these are simulation results, they bind the model rather than the world, and the generalization to deployed systems is a separate and weaker claim.

## 8 The CHIPS Act

### 8.1 Most Unstable Sectors

The graded pre-registered claim was DROPPED with a limited-resolution caveat [@Monch-2011]: on the valid mean-exceedance instrument the CHIPS-dependent sectors sit in the top-instability cluster but not distinguishably at its peak, and rank is spec-sensitive. Ranks: R4238 {{LB-E5-chips-rank-R-R4238}} (SPEC-R) / {{LB-E5-chips-rank-M-R4238}} (SPEC-M); A34SIS {{LB-E5-chips-rank-R-A34SIS}} / {{LB-E5-chips-rank-M-A34SIS}} - though under SPEC-M the A34SIS position is properly tied-last rather than ranked: its mean exceedance is {{LB-E5-specm-a34sis-exceedance}}, inside a {{LB-E5-specm-zero-exceedance-count}}-way tie at exactly zero where the instrument floors and cannot order, and the printed rank within that tie is a sort artifact; verdict {{LB-E5-chips-verdict}}. Table TBL-4 carries the full ranking.

<!-- anchor: TBL-4 -->

*Table TBL-4. Seventeen-sector cross-section, ranked by SPEC-R mean exceedance (the amended primary key). Share is the fraction of months $\rho > 1$ under SPEC-R - near one for most sectors, the saturation record. Under SPEC-M the same instrument floors instead: {{LB-E5-specm-zero-exceedance-count}} of seventeen sectors tie at exactly zero mean exceedance, so SPEC-M orders only the crossing sectors and the ranking claim of Section 8.1 is a SPEC-R claim (C-05). Episode columns are the SPEC-M monitoring record (Section 7.4): status in the onset +/- 24-month window and the first upward-crossing month ("none" where no crossing occurred). CHIPS footnote: ranks R4238 {{LB-E5-chips-rank-R-R4238}} (SPEC-R) / {{LB-E5-chips-rank-M-R4238}} (SPEC-M), A34SIS {{LB-E5-chips-rank-R-A34SIS}} / {{LB-E5-chips-rank-M-A34SIS}}; graded verdict {{LB-E5-chips-verdict}}. Persistence footnote: manufacturing-aggregate mean $\rho$ {{LB-E5-persistence-mfg-meanrho-R:.4f}} (SPEC-R) / {{LB-E5-persistence-mfg-meanrho-M:.4f}} (SPEC-M).*

| Rank | Sector | Mean exceedance | Share > 1 | GFC (SPEC-M) | GFC first crossing | COVID (SPEC-M) | COVID first crossing |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | {{LB-E5-ranking-r01-sector}} | {{LB-E5-ranking-r01-meanexc:.4f}} | {{LB-E5-tbl4-r01-share}} | {{LB-E5-tbl4-r01-gfc-status}} | {{LB-E5-tbl4-r01-gfc-first}} | {{LB-E5-tbl4-r01-covid-status}} | {{LB-E5-tbl4-r01-covid-first}} |
| 2 | {{LB-E5-ranking-r02-sector}} | {{LB-E5-ranking-r02-meanexc:.4f}} | {{LB-E5-tbl4-r02-share}} | {{LB-E5-tbl4-r02-gfc-status}} | {{LB-E5-tbl4-r02-gfc-first}} | {{LB-E5-tbl4-r02-covid-status}} | {{LB-E5-tbl4-r02-covid-first}} |
| 3 | {{LB-E5-ranking-r03-sector}} | {{LB-E5-ranking-r03-meanexc:.4f}} | {{LB-E5-tbl4-r03-share}} | {{LB-E5-tbl4-r03-gfc-status}} | {{LB-E5-tbl4-r03-gfc-first}} | {{LB-E5-tbl4-r03-covid-status}} | {{LB-E5-tbl4-r03-covid-first}} |
| 4 | {{LB-E5-ranking-r04-sector}} | {{LB-E5-ranking-r04-meanexc:.4f}} | {{LB-E5-tbl4-r04-share}} | {{LB-E5-tbl4-r04-gfc-status}} | {{LB-E5-tbl4-r04-gfc-first}} | {{LB-E5-tbl4-r04-covid-status}} | {{LB-E5-tbl4-r04-covid-first}} |
| 5 | {{LB-E5-ranking-r05-sector}} | {{LB-E5-ranking-r05-meanexc:.4f}} | {{LB-E5-tbl4-r05-share}} | {{LB-E5-tbl4-r05-gfc-status}} | {{LB-E5-tbl4-r05-gfc-first}} | {{LB-E5-tbl4-r05-covid-status}} | {{LB-E5-tbl4-r05-covid-first}} |
| 6 | {{LB-E5-ranking-r06-sector}} | {{LB-E5-ranking-r06-meanexc:.4f}} | {{LB-E5-tbl4-r06-share}} | {{LB-E5-tbl4-r06-gfc-status}} | {{LB-E5-tbl4-r06-gfc-first}} | {{LB-E5-tbl4-r06-covid-status}} | {{LB-E5-tbl4-r06-covid-first}} |
| 7 | {{LB-E5-ranking-r07-sector}} | {{LB-E5-ranking-r07-meanexc:.4f}} | {{LB-E5-tbl4-r07-share}} | {{LB-E5-tbl4-r07-gfc-status}} | {{LB-E5-tbl4-r07-gfc-first}} | {{LB-E5-tbl4-r07-covid-status}} | {{LB-E5-tbl4-r07-covid-first}} |
| 8 | {{LB-E5-ranking-r08-sector}} | {{LB-E5-ranking-r08-meanexc:.4f}} | {{LB-E5-tbl4-r08-share}} | {{LB-E5-tbl4-r08-gfc-status}} | {{LB-E5-tbl4-r08-gfc-first}} | {{LB-E5-tbl4-r08-covid-status}} | {{LB-E5-tbl4-r08-covid-first}} |
| 9 | {{LB-E5-ranking-r09-sector}} | {{LB-E5-ranking-r09-meanexc:.4f}} | {{LB-E5-tbl4-r09-share:.4f}} | {{LB-E5-tbl4-r09-gfc-status}} | {{LB-E5-tbl4-r09-gfc-first}} | {{LB-E5-tbl4-r09-covid-status}} | {{LB-E5-tbl4-r09-covid-first}} |
| 10 | {{LB-E5-ranking-r10-sector}} | {{LB-E5-ranking-r10-meanexc:.4f}} | {{LB-E5-tbl4-r10-share}} | {{LB-E5-tbl4-r10-gfc-status}} | {{LB-E5-tbl4-r10-gfc-first}} | {{LB-E5-tbl4-r10-covid-status}} | {{LB-E5-tbl4-r10-covid-first}} |
| 11 | {{LB-E5-ranking-r11-sector}} | {{LB-E5-ranking-r11-meanexc:.4f}} | {{LB-E5-tbl4-r11-share:.4f}} | {{LB-E5-tbl4-r11-gfc-status}} | {{LB-E5-tbl4-r11-gfc-first}} | {{LB-E5-tbl4-r11-covid-status}} | {{LB-E5-tbl4-r11-covid-first}} |
| 12 | {{LB-E5-ranking-r12-sector}} | {{LB-E5-ranking-r12-meanexc:.4f}} | {{LB-E5-tbl4-r12-share:.4f}} | {{LB-E5-tbl4-r12-gfc-status}} | {{LB-E5-tbl4-r12-gfc-first}} | {{LB-E5-tbl4-r12-covid-status}} | {{LB-E5-tbl4-r12-covid-first}} |
| 13 | {{LB-E5-ranking-r13-sector}} | {{LB-E5-ranking-r13-meanexc:.4f}} | {{LB-E5-tbl4-r13-share}} | {{LB-E5-tbl4-r13-gfc-status}} | {{LB-E5-tbl4-r13-gfc-first}} | {{LB-E5-tbl4-r13-covid-status}} | {{LB-E5-tbl4-r13-covid-first}} |
| 14 | {{LB-E5-ranking-r14-sector}} | {{LB-E5-ranking-r14-meanexc:.4f}} | {{LB-E5-tbl4-r14-share:.4f}} | {{LB-E5-tbl4-r14-gfc-status}} | {{LB-E5-tbl4-r14-gfc-first}} | {{LB-E5-tbl4-r14-covid-status}} | {{LB-E5-tbl4-r14-covid-first}} |
| 15 | {{LB-E5-ranking-r15-sector}} | {{LB-E5-ranking-r15-meanexc:.4f}} | {{LB-E5-tbl4-r15-share:.4f}} | {{LB-E5-tbl4-r15-gfc-status}} | {{LB-E5-tbl4-r15-gfc-first}} | {{LB-E5-tbl4-r15-covid-status}} | {{LB-E5-tbl4-r15-covid-first}} |
| 16 | {{LB-E5-ranking-r16-sector}} | {{LB-E5-ranking-r16-meanexc:.4f}} | {{LB-E5-tbl4-r16-share:.4f}} | {{LB-E5-tbl4-r16-gfc-status}} | {{LB-E5-tbl4-r16-gfc-first}} | {{LB-E5-tbl4-r16-covid-status}} | {{LB-E5-tbl4-r16-covid-first}} |
| 17 | {{LB-E5-ranking-r17-sector}} | {{LB-E5-ranking-r17-meanexc:.4f}} | {{LB-E5-tbl4-r17-share:.4f}} | {{LB-E5-tbl4-r17-gfc-status}} | {{LB-E5-tbl4-r17-gfc-first}} | {{LB-E5-tbl4-r17-covid-status}} | {{LB-E5-tbl4-r17-covid-first}} |


### 8.2 Capacity Utilization Threshold

The pre-registered hypothesis was a knee: as utilization climbs toward capacity, slack disappears, and the loop should cross from stable to unstable somewhere around the 85-to-90 percent band. It is a reasonable expectation and it is the one the planning literature would predict [@Hopp-Spearman-2008; @Nepal-2012].

It could not be adjudicated, and the reason matters more than the outcome. NAICS 334 runs persistently above the instability boundary at every utilization level under SPEC-R, and persistently below it at every level under SPEC-M ({{LB-E6-specm-bin1-lt75-mean:.4f}} to {{LB-E6-specm-bin4-ge90-mean:.4f}} across the bins) - the specifications disagree on which side of the boundary the sector occupies, while agreeing on the point that decides the test: utilization never moves the sector across the boundary within this sample, so the contrast between regimes that the pre-registered knee test requires is never occupied under either reading. A test that needs a contrast between two regimes cannot deliver a verdict when the data only ever visits one of them: it could not have produced support no matter what the truth was, which makes it non-severe by construction rather than negative in result. Reporting it as a refutation would be a category error in the opposite direction, manufacturing a finding out of an instrument's blind spot. The honest status is inconclusive, and the empirical demonstration of L-02 is exactly this: chronically-unstable sectors require steady-state analysis, not threshold-crossing analysis. Bin means {{LB-E6-threshold-bin1-lt75-mean:.4f}} / {{LB-E6-threshold-bin2-75-85-mean:.4f}} / {{LB-E6-threshold-bin3-85-90-mean:.4f}} / {{LB-E6-threshold-bin4-ge90-mean:.4f}} (n {{LB-E6-threshold-bin1-lt75-n}} / {{LB-E6-threshold-bin2-75-85-n}} / {{LB-E6-threshold-bin3-85-90-n}} / {{LB-E6-threshold-bin4-ge90-n}}); the pre-registered rule's outcome {{LB-E6-threshold-rule-outcome}} is reported alongside, not as the finding. Current utilization {{LB-E6-current-utilization}} ({{LB-E6-current-month}}), context only. Table TBL-6 shows the flat above-boundary band.

<!-- anchor: TBL-6 -->

*Table TBL-6. Semiconductor (NAICS 334) mean $\rho$ by capacity-utilization bin - an estimate/characterization, not a threshold-crossing table: the SPEC-R band sits entirely above the boundary at every utilization level, so no capacity knee is detectable in this statistic and NO verdict is attached (the pre-registered rule's outcome, {{LB-E6-threshold-rule-outcome}}, is reported alongside, not as the finding). Under the robustness specification SPEC-M the same bins sit entirely BELOW the boundary at every level (monotone check {{LB-E6-specm-monotone}}; crossing bin {{LB-E6-specm-crossing-bin}}): the two specifications disagree on which side of the boundary the sector occupies while agreeing that utilization never moves it across. Current reading, as context only: utilization {{LB-E6-current-utilization}} ({{LB-E6-current-month}}).*

| Utilization bin (%) | Mean $\rho$ (SPEC-R) | Mean $\rho$ (SPEC-M) | n (months) |
| --- | --- | --- | --- |
| below 75 | {{LB-E6-threshold-bin1-lt75-mean:.4f}} | {{LB-E6-specm-bin1-lt75-mean:.4f}} | {{LB-E6-threshold-bin1-lt75-n}} |
| 75 to 85 | {{LB-E6-threshold-bin2-75-85-mean:.4f}} | {{LB-E6-specm-bin2-75-85-mean:.4f}} | {{LB-E6-threshold-bin2-75-85-n}} |
| 85 to 90 | {{LB-E6-threshold-bin3-85-90-mean:.4f}} | {{LB-E6-specm-bin3-85-90-mean:.4f}} | {{LB-E6-threshold-bin3-85-90-n}} |
| 90 and above | {{LB-E6-threshold-bin4-ge90-mean:.4f}} | {{LB-E6-specm-bin4-ge90-mean:.4f}} | {{LB-E6-threshold-bin4-ge90-n}} |


### 8.3 Complexity Drives Persistence

Why should some sectors carry structurally higher persistence than others? The complexity literature supplies the mechanism: products with many interdependent components, networks with many tiers, and supply bases with dense interconnection propagate a disturbance through more paths and hold it longer [@Bozarth-2009; @Novak-Eppinger-2001; @Choi-2001; @Serdarasan-2013; @Anderson-2000; @Ning-2023]. In this paper's terms, complexity is a mechanism for persistence, and persistence is the input to the damage bound - which is why the sectors this framework ranks as structurally unstable and the sectors that literature identifies as structurally complex are substantially the same sectors, arrived at from different directions. The connection is offered as a coherence check on the ranking, not as a tested causal claim; no experiment here estimates complexity or its effect on $\rho$.

### 8.4 Werner-CHIPS Nexus

One financing question follows naturally and is raised here as exploration rather than result. If a supplier ecosystem's instability is structural, stabilizing it requires investment in the tiers that carry the persistence, not only in the visible final-assembly stage - and the composition of credit, not merely its quantity, determines whether such investment happens. The directed-credit tradition argues exactly this, that where newly created credit is channeled shapes real outcomes in ways aggregate monetary measures conceal [@Werner-1997; @Werner-2005; @Werner-2014a; @Werner-2014b], and recent work on supply-chain finance and reconfiguration raises a related composition question - that bank credit relationships and diversification choices shape which supplier links firms can form and where [@Alfaro-2025; @Ahn-Tan-2025]. Whether that channel operates as the tradition claims is well outside anything this paper tests; the nexus is flagged as a direction, explicitly labeled exploratory, and carries no ledgered quantity.

## 9 Cross-Domain Extensions

Suggestive readings only; S-7 states that feedback strengths are assumption-driven proxies, and L-05 bounds every claim in this section.

### 9.1 Sovereign Ratings

The pre-registered conditional-instability reading fired WITHDRAWN: the stationarity precondition fails at the extreme [@Ferri-1999]. Characterization: {{LB-E10-calm-n-stationary}} of 18 countries in a tight near-unit band ($\phi$ {{LB-E10-calm-phi-min:.4f}} to {{LB-E10-calm-phi-max:.4f}}, calm $\rho$ {{LB-E10-calm-rho-min:.4f}} to {{LB-E10-calm-rho-max:.4f}}, all below 1); explosive {{LB-E10-calm-explosive}}; on the raw-levels leg the registration also committed to, {{LB-E10-levels-n-below1}} of 18 remain below one and the explosive set grows to {{LB-E10-levels-explosive}} - the United States joins on levels, so the detrending choice moves one country across the line while the withdrawn reading survives either way; dual-implementation guard {{LB-E10-calm-guard-dualimpl}}; the crossing sweep is the withdrawn branch ({{LB-E10-crisis-reading}}). Table TBL-5 carries the country panel.

<!-- anchor: TBL-5 -->

*Table TBL-5. Sovereign debt panel (18 countries, JST): detrended AR(1) persistence, calm-regime $\rho$, and pair counts - presented as a characterization with the withdrawn reading, not as a crossing table. Stationary countries: {{LB-E10-calm-n-stationary}} of 18, $\phi$ range {{LB-E10-calm-phi-min:.4f}} to {{LB-E10-calm-phi-max:.4f}}, calm $\rho$ range {{LB-E10-calm-rho-min:.4f}} to {{LB-E10-calm-rho-max:.4f}}; explosive detrended estimates: {{LB-E10-calm-explosive}}. Raw-levels leg (the dual-detrending commitment of Section 5.2): {{LB-E10-levels-n-below1}} of 18 remain below one on raw levels; explosive on levels: {{LB-E10-levels-explosive}}. Dual-implementation guard: max disagreement {{LB-E10-calm-guard-dualimpl}}. Crisis branch: {{LB-E10-crisis-reading}}.*

| Country | $\phi$ (detrended) | $\phi$ (raw levels) | $\rho$ (calm) | n pairs |
| --- | --- | --- | --- | --- |
| {{LB-E10-tbl5-r01-country}} | {{LB-E10-tbl5-r01-phi:.4f}} | {{LB-E10-tbl5-r01-phiraw:.4f}} | {{LB-E10-tbl5-r01-rho:.4f}} | {{LB-E10-tbl5-r01-npairs}} |
| {{LB-E10-tbl5-r02-country}} | {{LB-E10-tbl5-r02-phi:.4f}} | {{LB-E10-tbl5-r02-phiraw:.4f}} | {{LB-E10-tbl5-r02-rho:.4f}} | {{LB-E10-tbl5-r02-npairs}} |
| {{LB-E10-tbl5-r03-country}} | {{LB-E10-tbl5-r03-phi:.4f}} | {{LB-E10-tbl5-r03-phiraw:.4f}} | {{LB-E10-tbl5-r03-rho:.4f}} | {{LB-E10-tbl5-r03-npairs}} |
| {{LB-E10-tbl5-r04-country}} | {{LB-E10-tbl5-r04-phi:.4f}} | {{LB-E10-tbl5-r04-phiraw:.4f}} | {{LB-E10-tbl5-r04-rho:.4f}} | {{LB-E10-tbl5-r04-npairs}} |
| {{LB-E10-tbl5-r05-country}} | {{LB-E10-tbl5-r05-phi:.4f}} | {{LB-E10-tbl5-r05-phiraw:.4f}} | {{LB-E10-tbl5-r05-rho:.4f}} | {{LB-E10-tbl5-r05-npairs}} |
| {{LB-E10-tbl5-r06-country}} | {{LB-E10-tbl5-r06-phi:.4f}} | {{LB-E10-tbl5-r06-phiraw:.4f}} | {{LB-E10-tbl5-r06-rho:.4f}} | {{LB-E10-tbl5-r06-npairs}} |
| {{LB-E10-tbl5-r07-country}} | {{LB-E10-tbl5-r07-phi:.4f}} | {{LB-E10-tbl5-r07-phiraw:.4f}} | {{LB-E10-tbl5-r07-rho}} | {{LB-E10-tbl5-r07-npairs}} |
| {{LB-E10-tbl5-r08-country}} | {{LB-E10-tbl5-r08-phi:.4f}} | {{LB-E10-tbl5-r08-phiraw:.4f}} | {{LB-E10-tbl5-r08-rho:.4f}} | {{LB-E10-tbl5-r08-npairs}} |
| {{LB-E10-tbl5-r09-country}} | {{LB-E10-tbl5-r09-phi:.4f}} | {{LB-E10-tbl5-r09-phiraw:.4f}} | {{LB-E10-tbl5-r09-rho:.4f}} | {{LB-E10-tbl5-r09-npairs}} |
| {{LB-E10-tbl5-r10-country}} | {{LB-E10-tbl5-r10-phi:.4f}} | {{LB-E10-tbl5-r10-phiraw:.4f}} | {{LB-E10-tbl5-r10-rho}} | {{LB-E10-tbl5-r10-npairs}} |
| {{LB-E10-tbl5-r11-country}} | {{LB-E10-tbl5-r11-phi:.4f}} | {{LB-E10-tbl5-r11-phiraw:.4f}} | {{LB-E10-tbl5-r11-rho:.4f}} | {{LB-E10-tbl5-r11-npairs}} |
| {{LB-E10-tbl5-r12-country}} | {{LB-E10-tbl5-r12-phi:.4f}} | {{LB-E10-tbl5-r12-phiraw:.4f}} | {{LB-E10-tbl5-r12-rho:.4f}} | {{LB-E10-tbl5-r12-npairs}} |
| {{LB-E10-tbl5-r13-country}} | {{LB-E10-tbl5-r13-phi:.4f}} | {{LB-E10-tbl5-r13-phiraw:.4f}} | {{LB-E10-tbl5-r13-rho}} | {{LB-E10-tbl5-r13-npairs}} |
| {{LB-E10-tbl5-r14-country}} | {{LB-E10-tbl5-r14-phi:.4f}} | {{LB-E10-tbl5-r14-phiraw:.4f}} | {{LB-E10-tbl5-r14-rho:.4f}} | {{LB-E10-tbl5-r14-npairs}} |
| {{LB-E10-tbl5-r15-country}} | {{LB-E10-tbl5-r15-phi:.4f}} | {{LB-E10-tbl5-r15-phiraw:.4f}} | {{LB-E10-tbl5-r15-rho:.4f}} | {{LB-E10-tbl5-r15-npairs}} |
| {{LB-E10-tbl5-r16-country}} | {{LB-E10-tbl5-r16-phi:.4f}} | {{LB-E10-tbl5-r16-phiraw:.4f}} | {{LB-E10-tbl5-r16-rho:.4f}} | {{LB-E10-tbl5-r16-npairs}} |
| {{LB-E10-tbl5-r17-country}} | {{LB-E10-tbl5-r17-phi:.4f}} | {{LB-E10-tbl5-r17-phiraw:.4f}} | {{LB-E10-tbl5-r17-rho:.4f}} | {{LB-E10-tbl5-r17-npairs}} |
| {{LB-E10-tbl5-r18-country}} | {{LB-E10-tbl5-r18-phi:.4f}} | {{LB-E10-tbl5-r18-phiraw:.4f}} | {{LB-E10-tbl5-r18-rho:.4f}} | {{LB-E10-tbl5-r18-npairs}} |


### 9.2 Unemployment Insurance

The pre-registered procyclical-feedback reading fired WITHDRAWN [@Anderson-Meyer-1994; @Woodbury-2004]. The mechanism those studies describe is what the pre-registration expected to find: incomplete experience rating distorts layoff behaviour, and unemployment-insurance tax schedules automatically shift and steepen over the business cycle, so the marginal tax cost of a layoff rises precisely during a recession. That is a feedback channel of exactly the shape this framework measures. The data did not support the reading, and the theoretical literature is in any case not unanimous that experience rating is straightforwardly stabilizing - under implicit-contract wage rigidity its introduction can raise long-term employment and welfare [@Fath-Fuest-2002]. Characterization: pooled normal-period $\phi$ {{LB-E11-normal-phi:.4f}} (n {{LB-E11-normal-n}}), $\rho$ {{LB-E11-normal-rho-min:.4f}} to {{LB-E11-normal-rho-max:.4f}} across all nine combinations, all below 1; jurisdictions {{LB-E11-normal-jur-phi-min:.4f}} to {{LB-E11-normal-jur-phi-max:.4f}} (median {{LB-E11-normal-jur-phi-median:.4f}}); pooled GFC $\phi$ {{LB-E11-gfc-phi:.4f}} (n {{LB-E11-gfc-n}}) sits far below the boundary corner {{LB-E11-gfc-corner}} and beside the normal-period pooled estimate {{LB-E11-normal-phi:.4f}} - a descriptive comparison, with no formal difference test computed or claimed, and the normal window, excluding only the GFC, contains the 2020 claims shock; reading {{LB-E11-gfc-reading}} - consistent with the cited counterpoint and rhyming with the COVID finding: crises in these systems arrive as level shocks, not persistence explosions.

## 10 Implications for Institutional Design

### 10.1 Three-Parameter Audit

Stripped to essentials, the diagnostic asks an institution three questions. How persistent is the variable you are steering ($\phi$)? How long is the window you steer by ($W$)? How hard do you push on the gap ($bg$)? Those three numbers determine the spectral radius, the spectral radius determines whether deviations decay or compound, and the pair $(\rho, \tau)$ determines what a regime change costs while your measurement catches up. EQ-2 and EQ-5 are the instruments: the first prices the blind period, the second says whether the loop is stable at all.

The audit's value is that all three parameters are observable to the institution itself, and two of them are policy choices. An organization that cannot change how persistent its environment is can still change how long it looks and how hard it reacts - and the framework says precisely which of those levers is worth pulling in which conditions. This is also why the audit belongs in the safety-boundary tradition rather than the forecasting one: the question is not what will happen, but how far the current operating point sits from a boundary past which the institution's own control actions amplify rather than dampen [@Rasmussen-1997; @Dekker-2011].

### 10.2 Reverse-Engineering Principle

The bound runs in both directions. Forward, it prices damage from known loop parameters. Backward, an observed damage pattern constrains the parameters that could have produced it: a deviation that persisted for a known number of periods and grew by a known factor implies a range of $(\rho, \tau)$ pairs, and $\tau$ implies a measurement window. An institution that does not know its own effective window - a common situation, since windows are often embedded in inherited procedures, vendor defaults, and reporting cadences rather than chosen deliberately - can therefore infer it from its own crisis history.

The inference is coarse and this paper does not test it; it is stated as a principle the identity licenses, not as a validated method. But it points at the practical failure the framework is ultimately about. Institutions rarely decide their measurement windows. They inherit them, and then discover during a regime change what the inheritance costs.

### 10.3 Domain Interventions

Ranking interventions by which parameter they move clarifies why some familiar remedies underperform. Interventions that shorten the window (faster reporting, higher-frequency data, nowcasting) attack $\tau$ directly and pay off exponentially, because $\tau$ sits in the exponent. Interventions that reduce feedback aggressiveness (damping, smoothing, rate limits) lower $\rho$ and can move a loop back inside the stability boundary, but they trade responsiveness for stability and Section 7.5 states the conditions under which that trade is worth making. Interventions that reduce underlying persistence (supply-base simplification, buffer capacity, demand pooling) are the most durable and the slowest to implement, since they change the environment rather than the controller.

Two cautions carry from this paper's own results and are not optional. First, the ordering above assumes the regime change is of the kind the theorem prices; the COVID episode illustrates that compound shocks in the opposite direction are outside it. Second, the simulation studies in Appendix F show that the framework's own remedy - adapting the damping to estimated persistence - is harmful in conditions the theory does not cover, specifically when persistence itself is drifting rather than stepping (S-8). An institution that adopts the diagnostic without adopting its scope conditions has bought a tool that will fire confidently in exactly the circumstances where it is wrong.

## 11 Forward Prediction: Self-Service Diagnostic

This section states the paper's two dated, falsifiable forward predictions - standing claims about post-publication outcomes, the one validator that routes around both author and reviewer. Every protocol constant below is a ledger row emitted by the committed registration generator (verification path: the same machinery that polices every other number in this paper); registration date {{LB-FP-diagnostic-registered}}, carry-forward horizon {{LB-FP-diagnostic-horizon}}.

### 11.1 The Predictions

PREDICTION A (self-service diagnostic; carried from the pinned source, locked April 2026, restated and re-registered at this rebuild's commit). Any firm can compute the closed-loop spectral radius $\rho$ from three quantities it already has: its estimated demand persistence $\phi$ (estimator {{LB-FP-diagnostic-estimator}} - the paper's pre-registered choice, Section 6.3), its measurement window $W$, and its feedback gain, via the companion-matrix construction of EQ-1. The standing claim: $\rho$ above the threshold {{LB-FP-diagnostic-threshold}} implies the firm's response to its next demand shock AMPLIFIES (bullwhip); $\rho$ below it implies the response DECAYS. A public calculator implementing the computation will be provided at {{LB-FP-diagnostic-calculator-url}} in the near future.

PREDICTION B (sector-level two-class bet; new at this rebuild, registered at publication). The paper's committed rolling construction (Section 6.3) partitions the seventeen-sector panel into {{LB-FP-diagnostic-n-flagged}} boundary-crossing ("oscillating") sectors and {{LB-FP-diagnostic-n-decay}} never-crossing sectors; the class lists are extracted mechanically from the committed output and registered verbatim (flagged: {{LB-FP-diagnostic-flagged-sectors}}; never-crossing: {{LB-FP-diagnostic-decay-sectors}}). The standing claim: at the trigger event, the flagged class shows amplifying inventory/sales responses exceeding the never-crossing class under the registered metric and test. Honesty note, registered as part of the claim: under this committed construction the CHIPS-dependent computers/electronics sector sits in the NEVER-CROSSING class while wholesale machinery sits in the flagged class - an earlier informal sketch that named both CHIPS sectors as flagged is superseded by the committed classification, and the spec-sensitivity of such flags is itself one of this paper's findings (Section 8.1).

### 11.2 Protocol

A forward prediction is only as good as the ambiguity it removes in advance. Someone checking this claim years from now must be able to compute the answer without asking the author what was meant, which means every degree of freedom - when the clock starts, what is measured, over what window, against what baseline, and by which test - is fixed here rather than chosen later. Each constant below is a ledger row generated by a committed script and re-verified on every run, so the registration cannot drift even by accident.

Trigger: {{LB-FP-diagnostic-trigger}}. Metric: peak absolute deviation of log inventory/sales from its pre-onset baseline mean within {{LB-FP-diagnostic-metric-window-months}} months of onset, normalized by the pre-onset {{LB-FP-diagnostic-baseline-months}}-month baseline standard deviation, per sector, from the same public monthly series the paper uses (Appendix A). Test: {{LB-FP-diagnostic-test}} at $\alpha$ {{LB-FP-diagnostic-alpha}}.

Three choices deserve their reasons on the record. The metric is normalized by each sector's own pre-onset variability rather than compared in raw units, because sectors differ by an order of magnitude in how much their inventory ratios ordinarily move, and an unnormalized comparison would rank them by volatility rather than by the effect the prediction is about. The test is rank-based rather than parametric, because with class sizes in single digits no distributional assumption is credible and a rank test needs none. And the onset date is taken from an external authority rather than chosen by inspection, which removes the one degree of freedom most easily abused after the fact.

### 11.3 Registration

Both predictions are registered publicly at the review stage alongside this paper's release, and scored publicly as data accrues; the registered constants above are byte-verified against the committed generator on every verification run.

Public registration is the point rather than a formality. Every other check in this paper - the ledger, the code-integrity review, the machine-verified proofs, the adversarial read - is a check the author commissioned and could in principle have shaped. A dated claim about events that have not happened yet is the one validator that routes around both the author and the reviewer, because the world scores it and neither party gets a say. That is also why the constants are ledgered rather than typed: a registration whose terms can be quietly edited after the fact is not a registration, and tying every number to a committed generator makes the edit visible if anyone attempts it.

The sector classification these predictions rest on was fixed by an earlier experiment and is reproduced from that experiment's committed output, not re-derived here. Its membership is public in Table TBL-2, so the two classes can be read off before any trigger occurs rather than assembled afterward.

### 11.4 Falsification Conditions

Prediction A is falsified by systematic decay in above-threshold systems or amplification in below-threshold systems under the stated computation. Prediction B is falsified if, at the trigger event, the flagged class does NOT exceed the never-crossing class under the registered metric and test - a genuine two-sided exposure, since the never-crossing class is non-empty and includes a CHIPS-dependent sector. If no qualifying trigger occurs before {{LB-FP-diagnostic-horizon}}, the bet is untestable and carries forward, re-registered, dated.

Two outcomes are explicitly NOT falsifications, and saying so now prevents the boundary being redrawn later. A trigger event in which both classes deviate substantially, with the flagged class higher, supports the prediction even if the absolute magnitudes are large everywhere - the claim is comparative, not about levels. Conversely, a quiet period in which neither class moves is uninformative rather than confirming: the prediction earns nothing from an absence of stress, and a scorer should record it as untested rather than as a pass. The honest failure mode for a comparative claim is a coin-flip result under stress, and that is the one the test above is built to detect.

## 12 Conclusion

An institution that measures a persistent variable over a window and steers on the result is exposed to a cost it usually does not price. When the underlying regime shifts, its estimator keeps describing the world that has gone, and for the length of that blind period the institution applies a rule calibrated to conditions that no longer hold, to a system whose deviations are now compounding. C-01: blind-period damage is governed by intensity $\times$ duration, $D = (\rho_2/\rho_1)^{\tau}$, computable from quantities institutions already estimate. That the two factors multiply rather than add is the whole content of the warning - a modest rise in instability paired with a long measurement window produces a cost neither factor predicts alone.

Two consequences follow directly. C-02: a unique optimal measurement window $W^{*}$ exists in closed form, so the length of a trailing average is a solvable question rather than a matter of convention. C-03: under regime-change risk the optimal operating point sits below the $\pi^2/2$ limit, because a boundary computed for today's conditions offers no protection against tomorrow's if the institution will be blind while they change.

The empirical record is mixed in the way an honest record usually is. The rolling out-of-sample panel test - the pre-registered falsifier, and the only experiment entitled to that word - passed. The global financial crisis corroborated it; COVID did not, and was not expected to. C-04: acting on the diagnostic reduces cost against a rational self-calibrating base-stock baseline within the simulated environment. C-05: under SPEC-R the CHIPS-dependent sectors are among the more structurally unstable, though not the two most, with measurement-sensitive ranking; under SPEC-M the exceedance instrument floors at zero for {{LB-E5-specm-zero-exceedance-count}} sectors and cannot order within that tie, so the ranking claim is a SPEC-R claim and its spec-sensitivity is part of the finding. C-06: under SPEC-R the semiconductor sector sits above the instability boundary at every utilization level, and under SPEC-M below it at every level - which side is spec-dependent, but under neither reading does utilization move the sector across the boundary, so a utilization tripwire is not an available monitoring benchmark under either specification.

One result arrived last and is summarized with its full chain of custody visible. The echelon decomposition asked WHERE amplification enters the retail-to-manufacturing chain. The pre-registered rule returned inconclusive on both samples, and a post-hoc characterization showed that verdict to be non-severe: the rule could not have fired at the effect the data exhibits - a defect in our own registration, knowable in advance and not known. The secondary contrast, its reading committed before its script existed, locates the growth at the step where manufacturers convert observed sales into orders, with one middle handoff attenuating rather than amplifying, and excluding the pandemic window strengthens the pattern - structure, not crisis. The finding is a where, not a why; the pre-registered inconclusive remains the primary result standing beside it.

The boundaries are stated with the same weight as the results, because a diagnostic whose failure modes are undocumented is not a diagnostic. L-01: compound shocks are excluded - the theorem prices a step change in the dangerous direction, and COVID was not one. L-02: chronically-unstable sectors need steady-state analysis rather than threshold-crossing analysis, and the reason is mechanical - a transition detector has no clean stable-to-unstable signal to trigger on when the system never occupies the stable side. L-03: simulation binds the model, and generalization to deployed systems is a separate, weaker claim. L-04: recipe-level non-stationarity is unresolved, with one trajectory shape tested - and an oracle given the true parameter does not rescue it, which forecloses better estimation as the fix. L-05: the cross-domain readings are suggestive only; two pre-registered extensions were withdrawn when their preconditions failed. L-06: the GFC episode is corroborating only. L-07: the pricing result is bounded by the immediate-arithmetic demand model.

It is worth being explicit about what is and is not new here, because a claim that is narrow is easier to check. NOT NEW, and credited to the literatures this paper builds on and cites: the control-theoretic analysis of supply-chain stability; the analysis of transient and nonlinear supply-chain dynamics; the long-established trade-off between adaptation speed and transient quality; and the role of shock persistence in supply-chain amplification. What is offered as this paper's contribution is the specific combination - a closed-form damage bound tying a backward-looking estimator's STRUCTURAL, non-tunable adaptation time to a regime-transition stability ratio; the framing of the cost as a TRANSITION BETWEEN PERSISTENCE REGIMES rather than as disturbance rejection or steady-state variance amplification; and the validation of the resulting metric across seventeen sectors and thirty-four years of monthly data. Extension of the same structure to other domains was attempted and is reported at the strength it earned, which in two cases was withdrawal. These are offered as contributions to be tested and refined rather than as final results.

Two further boundaries belong here rather than in a footnote, because they concern the paper's own instruments. The capacity-threshold test could not adjudicate its hypothesis in either direction and is reported as inconclusive rather than as a null. And the rolling monitoring record shows the paper's own instability dashboard confirming regime shifts two to five months after they begin rather than anticipating them - the thesis applied to its own apparatus. A framework that prices the cost of lagging measurement should expect to find that its own measurement lags, and saying so is not a concession but the argument working correctly.

What the result adds to an institution's view of itself is therefore narrow and, if it holds, useful: not merely how close to the boundary it is operating, but how much crossing might cost, and how long it would go on not knowing.

## Disclosure

This research was conducted with extensive AI collaboration. The cross-disciplinary framing that motivates this work - treating the transient cost of regime change as a measurable property of the adaptation lag between a shifted process and the trailing measurements that track it - emerged from iterative dialogue between the author and large language model AI systems, drawing on disciplines outside the author's formal training. AI was used for literature search across these disciplines, for implementation of the analysis pipeline, and for drafting and revision of analytical arguments. The research questions, the choice of methodology, the pre-registered specifications, the adjudication of results, the interpretation of empirical findings, and all final editorial judgments are the author's own. The paper's formal results are proved by hand in the proofs appendix, and the written proofs are supplemented by machine verification - both legs per theorem - executed by committed scripts with every outcome reported through the claims ledger; the empirical claims across the registered experiments were each rebuilt from the documented methodology and matched, and every analysis was run locally by the author and verified by hash. As the certification step of this work, the manuscript underwent a capped adversarial review by a memory-isolated AI session under a fix-or-rebut protocol, working from a single curated package of committed artifacts and recomputing the full claims ledger before reviewing. The full record - eighteen confirmed findings, sixteen fixed and two rebutted in writing, one cured by a pre-registered amendment whose unresolved result is reported in Section 6.1 exactly as the frozen rule dictates, and one boundary defect in the primary falsifier self-found and disclosed during the round (Section 5.4) - closed with a delta-verification round over the corrected package, the enlarged ledger recomputed with zero mismatches and a byte-identical render, and is committed verbatim in the repository (`verification/`: the reviewer's findings, the finding-by-finding adjudication, and the certification). Author and reviewer are the same model family, so this catches oversight but not shared blind spots; the results have not yet been independently verified by a domain expert. Citation keys are machine-tied both ways between the body and the reference list - every citation used is defined and every definition is used - and the tie was verified in both review rounds. The entire empirical battery was built under a written research-to-publication standard: analysis scripts were committed before results were accepted, every input file is pinned by a SHA-256 content hash, every load-bearing number is registered in a machine-checked ledger (`claims.lock`) and rendered into the manuscript by a committed script, and an automated checker (`verify.py`) regenerates and re-verifies every value on demand and is itself run against deliberately broken fixtures it must fail. The operative amendments to the pre-registered specification are disclosed as dated amendments at the points where their results appear. The author takes full responsibility for the contents of this paper, including any errors that may have originated from AI assistance.

## References


[@Ahn-Tan-2025]: Ahn, J. & Tan, B. J. (2025). Supply chain diversification and resilience. IMF Working Paper 2025/102.
[@Alfaro-2025]: Alfaro, L., Brussevich, M., Minoiu, C. & Presbitero, A. (2025). Bank financing of global supply chains. NBER Working Paper 33754.
[@Anderson-2000]: Anderson, E., Fine, C. & Parker, G. (2000). Upstream volatility in the supply chain: the machine tool industry as a case study. Production and Operations Management, 9(3), 239–261.
[@Anderson-Meyer-1994]: Anderson, P. & Meyer, B. (1994). The effects of unemployment insurance taxes and benefits on layoffs using firm and individual data. NBER Working Paper 4960.
[@Boute-2006]: Boute, R., Disney, S., Lambrecht, M. & Van Houdt, B. (2007). An integrated production and inventory model to dampen upstream demand variability in the supply chain. European Journal of Operational Research, 178(1), 121–142.
[@Boute-2022]: Boute, R., Disney, S., Gijsbrechts, J. & Van Mieghem, J. (2022). Dual sourcing and smoothing under non-stationary demand time series: re-shoring with SpeedFactories. Management Science, 68(2), 1039–1057.
[@Bozarth-2009]: Bozarth, C., Warsing, D., Flynn, B. & Flynn, E. (2009). The impact of supply chain complexity on manufacturing plant performance. Journal of Operations Management, 27(1), 78–93.
[@Bray-Mendelson-2012]: Bray, R. & Mendelson, H. (2012). Information transmission and the bullwhip effect: an empirical investigation. Management Science, 58(5), 860–875.
[@Bray-Mendelson-2015]: Bray, R. & Mendelson, H. (2015). Production smoothing and the bullwhip effect. Manufacturing & Service Operations Management, 17(2), 208–220.
[@Cachon-2007]: Cachon, G., Randall, T. & Schmidt, G. (2007). In search of the bullwhip effect. Manufacturing & Service Operations Management, 9(4), 457–479.
[@Chen-2000]: Chen, F., Drezner, Z., Ryan, J. & Simchi-Levi, D. (2000). Quantifying the bullwhip effect in a simple supply chain: the impact of forecasting, lead times, and information. Management Science, 46(3), 436–443.
[@Choi-2001]: Choi, T., Dooley, K. & Rungtusanatham, M. (2001). Supply networks and complex adaptive systems: control versus emergence. Journal of Operations Management, 19(3), 351–366.
[@Costantino-2014]: Costantino, F., Di Gravio, G., Shaban, A. & Tronci, M. (2014). SPC-based inventory control policy to improve supply chain dynamics. International Journal of Engineering & Technology, 6, 418–426.
[@Datta-Ioannou-1994]: Datta, A. & Ioannou, P. (1994). Performance analysis and improvement in model reference adaptive control. IEEE Transactions on Automatic Control, 39(12), 2370–2381.
[@Dejonckheere-2003]: Dejonckheere, J., Disney, S., Lambrecht, M. & Towill, D. (2003). Measuring and avoiding the bullwhip effect: a control theoretic approach. European Journal of Operational Research, 147(3), 567–590.
[@Dejonckheere-2004]: Dejonckheere, J., Disney, S., Lambrecht, M. & Towill, D. (2004). The impact of information enrichment on the bullwhip effect in supply chains: a control engineering perspective. European Journal of Operational Research, 153(3), 727–750.
[@Dekker-2011]: Dekker, S. (2011). Drift into Failure: From Hunting Broken Components to Understanding Complex Systems. Ashgate.
[@Disney-2004-golden]: Disney, S., Towill, D. & Van de Velde, W. (2004). Variance amplification and the golden ratio in production and inventory control. International Journal of Production Economics, 90(3), 295–309.
[@Disney-2008]: Disney, S. (2008). Supply chain aperiodicity, bullwhip and stability analysis with Jury's inners. IMA Journal of Management Mathematics, 19(2), 101–116.
[@Disney-Towill-2002]: Disney, S. & Towill, D. (2002). A discrete linear control theory model to determine the dynamic stability of vendor managed inventory supply chains. International Journal of Production Research, 40(1), 179–204.
[@Disney-Towill-2003]: Disney, S. & Towill, D. (2003). On the bullwhip and inventory variance produced by an ordering policy. Omega, 31(3), 157–167.
[@Dooley-2010]: Dooley, K., Yan, T., Mohan, S. & Gopalakrishnan, M. (2010). Inventory management and the bullwhip effect during the 2007–2009 recession: evidence from the manufacturing sector. Journal of Supply Chain Management, 46(1), 12–18.
[@Fath-Fuest-2002]: Fath, J. & Fuest, C. (2005). Experience rating of unemployment insurance in the US: a model for Europe? CESifo DICE Report, 3(2), 45–50.
[@Ferri-1999]: Ferri, G., Liu, L.-G. & Stiglitz, J. (1999). The procyclical role of rating agencies: evidence from the East Asian crisis. Economic Notes, 28(3), 335–355.
[@Gaalman-2022]: Gaalman, G., Disney, S. & Wang, X. (2022). When bullwhip increases in the lead time: an eigenvalue analysis of ARMA demand. International Journal of Production Economics, 250, 108623.
[@Gaalman-Disney-2009]: Gaalman, G. & Disney, S. (2009). On bullwhip in a family of order-up-to policies with ARMA(2,2) demand and arbitrary lead-times. International Journal of Production Economics, 121(2), 454–463.
[@Gibson-2013]: Gibson, T., Annaswamy, A. & Lavretsky, E. (2013). On adaptive control with closed-loop reference models: transients, oscillations, and peaking. IEEE Access.
[@Gijsbrechts-2022]: Gijsbrechts, J., Boute, R., Van Mieghem, J. & Zhang, D. (2022). Can deep reinforcement learning improve inventory management? Performance on lost sales, dual-sourcing, and multi-echelon problems. Manufacturing & Service Operations Management, 24(3), 1349–1368.
[@Graves-Tomlin-2003]: Graves, S. & Tomlin, B. (2003). Process flexibility in supply chains. Management Science, 49(7), 907–919.
[@Haykin-1996]: Haykin, S. (1996). Adaptive Filter Theory (3rd ed.). Prentice Hall.
[@Helbing-2004]: Helbing, D., Lammer, S., Witt, U. & Brenner, T. (2004). Network-induced oscillatory behavior in material flow networks and irregular business cycles. Physical Review E, 70(5), 056118.
[@Hopp-Spearman-2008]: Hopp, W. & Spearman, M. (2008). Factory Physics (3rd ed.). Waveland.
[@Hosoda-Disney-2006]: Hosoda, T. & Disney, S. (2006). On variance amplification in a three-echelon supply chain with minimum mean square error forecasting. Omega, 34(4), 344–358.
[@Jungers-2009]: Jungers, R. (2009). The Joint Spectral Radius: Theory and Applications. Lecture Notes in Control and Information Sciences 385. Springer.
[@Kim-AdaptationRate]: Kim, J. (2026a). The Adaptation Rate of Trailing Averages. Zenodo (companion, cited by title).
[@Kim-AdaptationTax]: Kim, J. (2026b). The Adaptation Tax. Zenodo (companion, cited by title).
[@Kim-MeasurementTrap]: Kim, J. (2026c). The Measurement Trap. Zenodo (companion, cited by title).
[@Krstic-Kokotovic-1993]: Krstic, M., Kokotovic, P. & Kanellakopoulos, I. (1993). Transient-performance improvement with a new class of adaptive controllers. Systems & Control Letters, 21(6), 451–461.
[@Lee-1997a]: Lee, H., Padmanabhan, V. & Whang, S. (1997a). Information distortion in a supply chain: the bullwhip effect. Management Science, 43(4), 546–558.
[@Lee-1997b]: Lee, H., Padmanabhan, V. & Whang, S. (1997b). The bullwhip effect in supply chains. Sloan Management Review, 38(3), 93–102.
[@Leng-2025]: Leng, Y., Liu, E., Ren, Y. & Tsyvinski, A. (2025). The bullwhip: time-to-build and sectoral fluctuations. NBER Working Paper 33638.
[@Li-2023]: Li, Q., Gaalman, G. & Disney, S. (2023). On the equivalence of the proportional and damped trend order-up-to policies: an eigenvalue analysis. International Journal of Production Economics, 265, 109005.
[@Li-Dorfler-2024]: Li, S. H. Q. & Dorfler, F. (2024). Mitigating transient bullwhip effects under imperfect demand forecasts. arXiv:2404.01090.
[@Lin-2020]: Lin, J., Naim, M. & Spiegler, V. (2020). Delivery time dynamics in an assemble-to-order inventory and order based production control system. International Journal of Production Economics, 223, 107531.
[@Minsky-1986]: Minsky, H. (1986). Stabilizing an Unstable Economy. Yale University Press.
[@Monch-2011]: Monch, L., Fowler, J., Dauzere-Peres, S., Mason, S. & Rose, O. (2011). A survey of problems, solution techniques, and future challenges in scheduling semiconductor manufacturing operations. Journal of Scheduling, 14(6), 583–599.
[@Nepal-2012]: Nepal, B., Murat, A. & Chinnam, R. (2012). The bullwhip effect in capacitated supply chains with consideration for product life-cycle aspects. International Journal of Production Economics, 136(2), 318–331.
[@Ning-2023]: Ning, A., Tziantzioulis, G. & Wentzlaff, D. (2023). Supply chain aware computer architecture. ISCA.
[@Novak-Eppinger-2001]: Novak, S. & Eppinger, S. (2001). Sourcing by design: product complexity and the supply chain. Management Science, 47(1), 189–204.
[@Oliva-Sterman-2001]: Oliva, R. & Sterman, J. (2001). Cutting corners and working overtime: quality erosion in the service industry. Management Science, 47(7), 894–914.
[@Oroojlooyjadid-2022]: Oroojlooyjadid, A., Nazari, M., Snyder, L. & Takac, M. (2022). A deep Q-network for the beer game: deep reinforcement learning for inventory optimization. Manufacturing & Service Operations Management, 24.
[@Osadchiy-2016]: Osadchiy, N., Gaur, V. & Seshadri, S. (2016). Systematic risk in supply chain networks. Management Science, 62(6), 1755–1777.
[@Ouyang-Daganzo-2006]: Ouyang, Y. & Daganzo, C. (2006). Characterization of the bullwhip effect in linear, time-invariant supply chains: some formulae and tests. Management Science, 52(10), 1544–1556.
[@Plischke-Wirth-2008]: Plischke, E. & Wirth, F. (2008). Duality results for the joint spectral radius and transient behavior. Linear Algebra and its Applications, 428(10), 2368–2384.
[@Rasmussen-1997]: Rasmussen, J. (1997). Risk management in a dynamic society: a modelling problem. Safety Science, 27(2–3), 183–213.
[@Repenning-Sterman-2001]: Repenning, N. & Sterman, J. (2001). Nobody ever gets credit for fixing problems that never happened: creating and sustaining process improvement. California Management Review, 43(4), 64–88.
[@Repenning-Sterman-2002]: Repenning, N. & Sterman, J. (2002). Capability traps and self-confirming attribution errors in the dynamics of process improvement. Administrative Science Quarterly, 47(2), 265–295.
[@Saricioglu-2025]: Saricioglu, A., Erol Genevois, M. & Cedolin, M. (2025). Impact of COVID-19 on the bullwhip effect across U.S. industries. International Journal of Industrial Engineering: Theory, Applications and Practice, 32(3), 751–769.
[@Serdarasan-2013]: Serdarasan, S. (2013). A review of supply chain complexity drivers. Computers & Industrial Engineering, 66(3), 533–540.
[@Shan-2014]: Shan, J., Yang, S., Yang, S. & Zhang, J. (2014). An empirical study of the bullwhip effect in China. Production and Operations Management, 23(4), 537–551.
[@Spiegler-2016]: Spiegler, V., Potter, A., Naim, M. & Towill, D. (2016). The value of nonlinear control theory in investigating the underlying dynamics and resilience of a grocery supply chain. International Journal of Production Research, 54(1), 265–286.
[@Tomlin-2006]: Tomlin, B. (2006). On the value of mitigation and contingency strategies for managing supply chain disruption risks. Management Science, 52(5), 639–657.
[@Udenio-2015]: Udenio, M., Fransoo, J. & Peels, R. (2015). Destocking, the bullwhip effect, and the credit crisis: empirical modeling of supply chain dynamics. International Journal of Production Economics, 160, 34–46.
[@Udenio-2017]: Udenio, M., Vatamidou, E., Fransoo, J. & Dellaert, N. (2017). Behavioral causes of the bullwhip effect: an analysis using linear control theory. IISE Transactions, 49(10), 980–1000.
[@Wang-2013]: Wang, X., Disney, S. & Wang, J. (2012). Stability analysis of constrained inventory systems with transportation delay. European Journal of Operational Research, 223(1), 86–95.
[@Warburton-2004]: Warburton, R., Disney, S., Towill, D. & Hodgson, J. (2004). Further insights into 'the stability of supply chains'. International Journal of Production Research, 42(3), 639–648.
[@Warburton-Disney-2007]: Warburton, R. & Disney, S. (2007). Order and inventory variance amplification: the equivalence of discrete and continuous time analyses. International Journal of Production Economics, 110(1–2), 128–137.
[@Werner-1997]: Werner, R. (1997). Towards a new monetary paradigm: a quantity theorem of disaggregated credit, with evidence from Japan. Kredit und Kapital, 30(2), 276–309.
[@Werner-2005]: Werner, R. (2005). New Paradigm in Macroeconomics: Solving the Riddle of Japanese Macroeconomic Performance. Palgrave Macmillan.
[@Werner-2014a]: Werner, R. (2014a). Can banks individually create money out of nothing? The theories and the empirical evidence. International Review of Financial Analysis, 36, 1–19.
[@Werner-2014b]: Werner, R. (2014b). How do banks create money, and why can other firms not do the same? An explanation for the coexistence of lending and deposit-taking. International Review of Financial Analysis, 36, 71–77.
[@Woodbury-2004]: Woodbury, S. (2004). Layoffs and experience rating of the unemployment insurance payroll tax: panel data analysis of employers in three states. W.E. Upjohn Institute for Employment Research.
[@Zang-Bitmead-1994]: Zang, Z. & Bitmead, R. (1994). Transient bounds for adaptive control systems. IEEE Transactions on Automatic Control, 39(1), 171–175.


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
| Pricing-mechanism trial records (phase27_* artifacts; 1,800 raw trials, fixed in-house) | Source-committed artifact; registry, byte counts, and SHA256 in data/SOURCES.md | per-trial records | E8 (analysis, not re-execution) |
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
| THM-2 (closed-form $W^{*}$) | {{LB-T2-wstar-symbolic}} | brute-force match {{LB-T2-wstar-numeric-match}} at rate {{LB-T2-wstar-numeric-matchrate}}, unimodality failures {{LB-T2-wstar-numeric-unimodal-failures}} |
| THM-2 comparative statics (corrected re-derivation) | {{LB-T2-statics-symbolic}} | monotonicity failures: $\phi$ {{LB-T2-statics-numeric-monophi-fail}}, $bg$ {{LB-T2-statics-numeric-monobg-fail}} |
| THM-3 (adaptation-stability identity) | {{LB-THM3-symbolic}} | pass {{LB-THM3-numeric}}, dual-path checks {{LB-THM3-numeric-checked}} |
| Proposition $k^{*}$ (safety factor; numeric legs, written companion in Appendix G) | - | mfg argmin {{LB-T3-kstar-mfg-argmin}}, in-band {{LB-T3-kstar-inband}}, all-below-one {{LB-T3-kstar-allbelow1}}, verdict {{LB-T3-kstar-verdict}} |
| Estimator comparison (supplementary, not-a-theorem) | - | OLS mean estimate {{LB-T1-estimator-ols:.4f}} vs Yule-Walker {{LB-T1-estimator-yw:.4f}} (true $\phi$ 0.95, n 40); OLS less biased {{LB-T1-estimator-ols-less-biased}} |


## Appendix C: Companion Matrix Spectral Radii by Domain

Cross-domain $\rho$ computations supporting Table TBL-4 and Table TBL-5. The construction is identical in every domain and only the inputs change: an estimated persistence, a window, and an assumed feedback strength generate a companion matrix whose spectral radius is computed directly. Two features of these computations require emphasis because they bound how the cross-domain numbers may be read.

The feedback strengths are assumption-driven proxies rather than estimates (S-7). Persistence is estimated from data in every domain, but $bg$ - how hard the institution pushes on the measured gap - is not identified from the series, so the cross-domain radii are reported across a grid of feedback strengths rather than at a single fitted value. Consequently a cross-domain $\rho$ is a conditional statement of the form "at this feedback strength, this loop would sit here relative to the boundary," never a measurement of where an institution actually sits. The sovereign and unemployment-insurance readings in Section 9 are governed by this scope condition, and both pre-registered crossing claims were withdrawn when their preconditions failed, which is the honest consequence of taking the condition seriously rather than treating the grid as a set of estimates.

## Appendix D: Mitigation Effectiveness

Mitigation effectiveness under the damped policies, supporting Section 7.5. The relevant comparison is not whether a damped policy outperforms an undamped one on average, but whether it does so in the specific configuration an institution occupies - because the simulation studies establish that the answer changes sign across that space. Damping helps decisively in genuinely shifted, persistent regimes; it costs little in stationary conditions where the gate rarely engages; and it inflicts real harm in noisy environments where the estimator's own variance drives the gate on and off, and in drifting-persistence environments where no estimate of a stable parameter exists to gate on (S-8). The mitigation question is therefore inseparable from the diagnostic question: the value of acting depends on the same persistence structure the diagnostic is measuring, which is why this paper reports where the remedy fails at equal length to where it works.

## Appendix E: Beer Game Simulation Parameters

The frozen calibration behind Table TBL-3. The environment is a linear single-echelon core with the stated extensions and synthetic AR(1) demand, and the calibration was fixed before the comparison ran (S-5). The comparator deserves explicit note: the baseline is a self-calibrating base-stock policy, not a naive or deliberately weakened rule, because a diagnostic that only beats a straw policy demonstrates nothing about its value. The reported cost reduction is a property of this construction and this construction only. It is not a claim about deployed systems, and the audit that closed this experiment removed an inherited comparison to an external benchmark figure that could not be traced to its source (L-03).

## Appendix F: Additional Simulation Studies

Four studies map where the diagnostic's remedy helps and where it hurts: the chain-length sweep, the pricing analysis - a recomputation from the source's committed trial records rather than a run by this paper's code (Section 5.7; S-6 states the pricing model scope; L-07 the limit) - the hysteresis sweep, and the recipe-level non-stationarity analysis. Table TBL-7 carries every cell, including the unresolved ones.

These are reported as a series of bounded findings rather than as a single sweeping claim: each maps a region where the remedy helps or hurts, and none generalizes past the region it maps. Three conventions apply throughout and are worth stating once. Every comparison is paired: within a run, each algorithm faces the identical demand sequence, so a difference between algorithms is never a difference between draws. Every grid is reported in full rather than filtered to its significant cells - a grid reported selectively is a search presented as an experiment, and the counts of harm, benefit, and unresolved cells are themselves findings. And resolution is reported explicitly: a cell whose confidence interval spans zero is marked unresolved rather than assigned to whichever side its point estimate happens to fall on. That last convention is what exposed the source's headline chain-length crossover as a reading taken through noise, and it is applied here to this paper's own cells with equal force.

These are simulations. Their verdicts bind the model that produced them, and the step from model to deployed system is a separate and weaker claim (S-5, L-03).

<!-- anchor: TBL-7 -->

*Table TBL-7. The four Appendix F simulation studies, presented as their honest headlines: a capacity-conditional gradient map (not an unconditional crossover), a value cliff with withdrawn attribution, a resolved robust/fragile split, and the recipe-level non-stationarity result. Full grids with CIs and resolution flags live in the committed outputs.*

**Panel A - chain-length $\times$ capacity gradient (E7; ar1_high, tool-vs-disabled cost delta; positive = harm).** Grid counts: {{LB-E7-gradient-n-resolved}} of 36 cells resolved ({{LB-E7-gradient-n-harm}} harm, {{LB-E7-gradient-n-benefit}} benefit, {{LB-E7-gradient-n-unresolved}} unresolved).

| Capacity | L = 4 | L = 6 | L = 8 |
| --- | --- | --- | --- |
| 1.3x | {{LB-E7-gradient-cap13-ar1high-L4:.4f}} | {{LB-E7-gradient-cap13-ar1high-L6:.4f}} | {{LB-E7-gradient-cap13-ar1high-L8:.4f}} |
| 2.4x | {{LB-E7-gradient-cap24-ar1high-L4:.4f}} (resolved: {{LB-E7-gradient-cap24-ar1high-L4-resolved}}) | {{LB-E7-gradient-cap24-ar1high-L6:.4f}} (resolved: {{LB-E7-gradient-cap24-ar1high-L6-resolved}}) | {{LB-E7-gradient-cap24-ar1high-L8:.4f}} (resolved: {{LB-E7-gradient-cap24-ar1high-L8-resolved}}) |

**Panel B - resolution vs the source's 50-seed record (ar1_high $\times$ 2.4x; a regression check, not a calibration; the source's fifty seeds are the first fifty of this paper's 250, so the containment column measures what the added two hundred seeds moved, not agreement between independent runs).**

| Cell | Ours (250 seeds) | Source (50 seeds) | Source inside our CI |
| --- | --- | --- | --- |
| L = 4 | {{LB-E7-calibration-L4-ours:.4f}} | {{LB-E7-calibration-L4-source}} | {{LB-E7-calibration-L4-source-in-ci}} |
| L = 6 | {{LB-E7-calibration-L6-ours:.4f}} | {{LB-E7-calibration-L6-source}} | {{LB-E7-calibration-L6-source-in-ci}} |
| L = 8 | {{LB-E7-calibration-L8-ours:.4f}} | {{LB-E7-calibration-L8-source}} | {{LB-E7-calibration-L8-source-in-ci}} |

**Panel C - pricing asymmetry (E8; an analysis of the source's committed trial records, Section 5.7).** Throughout Panels C and D the parenthetical $\sigma$ is the t-statistic (effect divided by its standard error), not a dispersion - unsigned in Panel C, signed in Panel D, each following its script's committed convention. Raise side: claim A benefit {{LB-E8-up-claima-mean:.4f}} (CI {{LB-E8-up-claima-cipct-lo:.4f}} to {{LB-E8-up-claima-cipct-hi:.4f}} percent of the reacting-at-all benefit); claim B (formula attribution) {{LB-E8-up-claimb-mean:.4f}} at {{LB-E8-up-claimb-sigma:.4f}} $\sigma$, verdict {{LB-E8-up-claimb-verdict}}; mean benefit by capacity {{LB-E8-up-cap18x-mean:.4f}} (1.8x) / {{LB-E8-up-cap24x-mean:.4f}} (2.4x) / {{LB-E8-up-cap30x-mean:.4f}} (3.0x). Cut side (mean, $\sigma$): low-$\phi$ {{LB-E8-down-low_phi_shift_down-mean:.4f}} ({{LB-E8-down-low_phi_shift_down-sigma:.4f}}); mid-$\phi$ {{LB-E8-down-mid_phi_shift_down-mean:.4f}} ({{LB-E8-down-mid_phi_shift_down-sigma:.4f}}); persistent level shift {{LB-E8-down-level_shift_down_persistent-mean:.4f}} ({{LB-E8-down-level_shift_down_persistent-sigma:.4f}}).

**Panel D - hysteresis split (E9; raise benefit vs hysteresis intensity $h$; verdict {{LB-E9-verdict}}; fidelity {{LB-E9-fidelity-tier}}, max relative diff {{LB-E9-fidelity-maxreldiff}} - the exact tier records bit-identical reproduction of the source's committed trial streams at the source's own seeds through the vendored closure, not an independent replication).**

| $h$ | Sticky environment (benefit, $\sigma$) | Noisy environment (benefit, $\sigma$) |
| --- | --- | --- |
| 0.0 | {{LB-E9-robust-h000-benefit:.4f}} ({{LB-E9-robust-h000-sigma:.4f}}) | {{LB-E9-fragile-h000-benefit:.4f}} ({{LB-E9-fragile-h000-sigma:.4f}}) |
| 0.1 | {{LB-E9-robust-h010-benefit:.4f}} ({{LB-E9-robust-h010-sigma:.4f}}) | {{LB-E9-fragile-h010-benefit:.4f}} ({{LB-E9-fragile-h010-sigma:.4f}}) |
| 0.3 | {{LB-E9-robust-h030-benefit:.4f}} ({{LB-E9-robust-h030-sigma:.4f}}) | {{LB-E9-fragile-h030-benefit:.4f}} ({{LB-E9-fragile-h030-sigma:.4f}}) |
| 0.6 | {{LB-E9-robust-h060-benefit:.4f}} ({{LB-E9-robust-h060-sigma:.4f}}) | {{LB-E9-fragile-h060-benefit:.4f}} ({{LB-E9-fragile-h060-sigma:.4f}}) |

**Panel E - recipe-level non-stationarity (E12; verdict {{LB-E12-oracle-verdict}}).** Oracle handed true $\phi$: resolved harm in all nine drift cells: {{LB-E12-oracle-harm-all-drift}}; oracle mean delta {{LB-E12-oracle-L4x13-mean:.4f}} (L4 $\times$ 1.3x) and {{LB-E12-oracle-L8x24-mean:.4f}} (L8 $\times$ 2.4x); fixed-$\alpha$ at the long-chain locus {{LB-E12-oracle-fixed-L8x18-mean:.4f}} (L8 $\times$ 1.8x) / {{LB-E12-oracle-fixed-L8x24-mean:.4f}} (L8 $\times$ 2.4x). Paired 50-seed contrasts (leg B): fixed-vs-oracle {{LB-E12-oracle-legb-L8x18-fixedvsoracle:.4f}} / {{LB-E12-oracle-legb-L8x24-fixedvsoracle:.4f}}; fixed-vs-OLS {{LB-E12-oracle-legb-L8x18-fixedvsols:.4f}} / {{LB-E12-oracle-legb-L8x24-fixedvsols:.4f}}. Leg A's ordering conjunct, frozen before the run, is decided by disjoint marginal intervals on a paired design - the construction Section 5.6 diagnoses for the echelon rule; it is retained as frozen because its direction is conservative (disjoint marginals are strictly harder to satisfy than a paired contrast, so the rule cannot manufacture a false positive), and the claim Section 7.5 carries quotes these paired leg-B contrasts, the correctly targeted statistic. Perfect-information paradox: oracle resolved-worse than the noisy OLS estimator in {{LB-E12-oracle-paradox-count}} of 9 drift cells; stationary-control inertness check {{LB-E12-oracle-winscheck}}.


## Appendix G: Proofs

Full written proofs for the paper's theorem-bearing claims, upgraded from the source's sketches per the theory-with-proofs archetype; where rigor forced a sharper statement than the sketch, the change is marked SHARPENED. Each theorem carries three verification legs - the written proof below, a symbolic step-check, and a numeric stress test - and the per-theorem results of all three are recorded in verification/proof_threeway.md.

### G.0 Standing Assumptions and Notation

(A1) DYNAMICS. The managed variable $y_t$ follows AR(1) dynamics with persistence
$\phi \in (0, 1)$: $y_t = \phi y_{t-1} + \epsilon_t$, with $\epsilon_t$ zero-mean noise.
At $t = 0$ the true persistence steps from $\phi_1$ to $\phi_2$ with $\phi_2 > \phi_1$
(the dangerous direction).

(A2) CLOSED LOOP. A trailing-average estimator of window $W \geq 2$ computes
$\bar{y}_t = (1/W)\sum_{j=0}^{W-1} y_{t-j}$; a feedback policy adjusts the system at
rate $\beta\gamma > 0$ on the gap between $\bar{y}_t$ and a target. The linearized closed
loop is the $W \times W$ companion matrix $A(\phi, W, \beta\gamma)$ with the persistence and
feedback structure in its first row and an identity shift below. $\rho(A)$ denotes its
spectral radius. Write $\rho_1 = \rho(A(\phi_1, W, \beta\gamma))$ and
$\rho_2 = \rho(A(\phi_2, W, \beta\gamma))$.

(A3) MONOTONICITY. For fixed $W$ and $\beta\gamma > 0$, $\rho(A(\phi, W, \beta\gamma))$ is
strictly increasing in $\phi$. (Carried from the companion papers; verified numerically on the T1 grid - see the three-way record.)

(A4) DOMINANT-MODE DEVIATION (scope condition - SHARPENED from the sketch).
The damage state $d_t \geq 0$ is the magnitude of the system deviation tracked along the
dominant mode of the closed loop: per cycle, the deviation is amplified by the
spectral radius of the matrix in force at that cycle, $d_{t+1} = \rho(A_t) d_t$,
where $A_t$ is the closed-loop matrix under the policy in force at time $t$.
Remark G.0.1 states exactly what is and is not lost relative to full matrix
generality, and Lemma G.1 supplies the matrix-general bound.

(A5) ADAPTATION TIME. For the simple moving average, the estimator converges to
within detection tolerance $\epsilon$ of the new persistence in
$\tau(W) = W(1 - \epsilon/\Delta\phi)$ periods, where $\Delta\phi = \phi_2 - \phi_1 > 0$
and $0 < \epsilon < \Delta\phi$, so $\kappa := 1 - \epsilon/\Delta\phi$ is in $(0, 1)$ and
$\tau = \kappa W$. (Carried from the trailing-average companions.)

(A6) REGIME CONFIGURATION. The old regime is stable and the new regime unstable:
$\rho_1 < 1 < \rho_2$. (Theorem 2 and the statics require only $\rho_2 > 1$; Theorem 3
requires only $\rho_1 > 0$.)

Remark G.0.1 (why A4 is stated, and what the matrix-general truth is). For a general
matrix $A$ and a generic vector norm, $\|A x\| \leq \rho(A)\|x\|$ is FALSE; the spectral
radius controls asymptotic growth, not single-step growth ($\rho(A) \leq \|A\|$ for every
induced norm, with a possibly large gap). The sketch's per-step inequality is
therefore not a theorem about arbitrary norms of the state; it is exact along the
dominant mode, which is what A4 tracks, and it is the standard Cardiff-school
linearized reading (amplification per cycle = spectral radius). Lemma G.1 gives the
rigorous matrix-general statement: the same exponential rate up to a constant. For a
time-varying product of DIFFERENT matrices (the adaptive-policy case), even the rate
statement requires care - the joint spectral radius of the family, not the maximum
individual spectral radius, governs worst-case products in general [@Jungers-2009]. Under A4 the scalar recursion sidesteps the JSR issue;
outside A4 the adaptive-policy bound in Theorem 1 is stated with the constant from
Lemma G.1 applied to the fixed-policy envelope. E1-E12 use $D$ as an ordinal ranking
and threshold metric, which is invariant to the constant; the alignment review
(step 3) re-checks this experiment by experiment.

---

### G.1 Lemma (matrix-general growth bound)

LEMMA G.1. Let $A$ be a $W \times W$ matrix. (i) For every $\epsilon > 0$ there exists an induced
matrix norm $\|\cdot\|_\epsilon$ with $\|A\|_\epsilon \leq \rho(A) + \epsilon$; hence for every $t \geq 0$,
$\|A^t x\| \leq C_\epsilon (\rho(A) + \epsilon)^t \|x\|$ in any fixed norm, with $C_\epsilon \geq 1$
depending on $A$, $\epsilon$, and the norm equivalence constants but not on $t$.
(ii) If $A$ is diagonalizable with eigenvector matrix $V$, then
$\|A^t x\|_2 \leq \mathrm{cond}(V) \rho(A)^t \|x\|_2$, $\mathrm{cond}(V) = \|V\|_2 \|V^{-1}\|_2$.
(iii) In general $\|A^t\|_2 \leq c\, t^{m-1} \rho(A)^t$ for a constant $c$ and $m$ the size
of the largest Jordan block of a peripheral eigenvalue.

PROOF. (i) is the standard construction (Horn and Johnson, Lemma 5.6.10): take a
Schur or Jordan form $A = P T P^{-1}$ and the scaled similarity $D_\delta =$
$\mathrm{diag}(1, \delta, \ldots, \delta^{W-1})$; the norm $x \mapsto \|D_\delta^{-1} P^{-1} x\|_\infty$
induces a matrix norm equal to the inf-norm of $D_\delta^{-1} T D_\delta$, whose
off-diagonal mass shrinks like $\delta$, so for $\delta$ small enough the induced norm is
$\leq \rho(A) + \epsilon$. Norm equivalence on finite-dimensional spaces converts the bound to
any fixed norm at the cost of the constant $C_\epsilon$. (ii) $A^t = V \Lambda^t V^{-1}$ with
$\|\Lambda^t\|_2 = \rho(A)^t$. (iii) is the Jordan-form growth bound: powers of a Jordan
block $J$ of size $m$ with eigenvalue $\lambda$ satisfy $\|J^t\| \leq C(m)\, t^{m-1}$
$|\lambda|^t$. QED.

LEMMA G.1b (Gain Envelope, in-domain - NEW at v0.2). Fix $\phi_2 \in (0, 1)$, $W$, and
$\beta\gamma > 0$ with $\rho_2 := \rho(\phi_2, W, \beta\gamma) > 1$. Then for every
$\beta\gamma' \in [0, \beta\gamma]$: $\rho(\phi_2, W, \beta\gamma') \leq \rho_2$.

STATUS AND JUSTIFICATION. $\rho$ is NOT globally monotone in the gain: at
$\beta\gamma' = 0$ the loop is open and $\rho = \phi_2 < 1$; small positive feedback
DAMPS the persistence pole ($\rho$ dips below $\phi_2$); large feedback destabilizes
($\rho$ rises through 1). The map $\beta\gamma' \mapsto \rho(\phi_2, W, \beta\gamma')$ is
empirically U-shaped on the verification grid. The lemma needs only the
weaker envelope statement: on $[0, \beta\gamma]$ the maximum is attained at an
endpoint, and since the left endpoint gives $\phi_2 < 1 < \rho_2$, the right
endpoint dominates. A violation would require an interior local maximum of
$\rho$ in the gain strictly exceeding $\rho_2 > 1$; none exists on the verification
grid (T1 numeric leg: dense gain sweep per in-domain cell, zero violations).
The lemma is carried as NUMERICALLY VERIFIED on the theorem's verification
surface and is explicitly flagged for the Phase-5a proof-rigor pass (an
analytic proof from the characteristic polynomial $\lambda^W - \phi\lambda^{W-1} +$
$(bg/W)\sum_{j<W}\lambda^j$ is a known open refinement; the theorem's scope is the
verified surface until then).

REMARK G.1b.1 (stabilizing-then-destabilizing feedback - new finding). The
U-shape is itself a substantive observation surfaced by this verification:
moderate measurement feedback is STABILIZING relative to the open loop
($\rho$ below $\phi_2$), and instability is a property of aggressive feedback, not
of feedback per se. This sharpens the paper's narrative and is recorded for
the manuscript's framework discussion; it changes no experiment operator
(alignment review, step 3, re-confirms).

---

<!-- anchor: P-THM-1 -->
### G.2 Theorem 1 (Compound Damage Bound)

STATEMENT (as proved). Let the regime change occur at $t = 0$ with initial deviation
$d_0 > 0$, and let the blind period be $t = 0, 1, \ldots, \tau - 1$ (A5). Consider a policy
whose closed-loop matrix at time $t$ during the blind period is
$A_t = A(\phi_2, W, \beta\gamma_t)$, where $\beta\gamma_t \leq \beta\gamma$ is the (possibly
adaptively reduced) feedback in force.

(a) Under A4 (dominant-mode tracking), the deviation at the end of the blind period
satisfies
    $d_\tau = d_0 \prod_{t=0}^{\tau-1} \rho(A_t) \leq d_0 \rho_2^{\tau}$,
with equality iff the policy does not adapt ($\beta\gamma_t = \beta\gamma$ for all $t$).

(b) Matrix-general version (SHARPENED): for the non-adaptive policy the state
satisfies $x_\tau = A_2^{\tau} x_0$ and, by Lemma G.1, $\|x_\tau\| \leq C \rho_2^{\tau} \|x_0\|$
with $C = \mathrm{cond}(V)$ when $A_2$ is diagonalizable and $C = C_\epsilon$ (rate $\rho_2 + \epsilon$)
otherwise. The exponential RATE $\rho_2$ is exact: $\lim_{t\to\infty} \|A_2^t\|^{1/t} = \rho_2$
(Gelfand). For the adaptive time-varying case outside A4, the product of the family
$\{A_t\}$ is governed by its joint spectral radius, and the bound is stated only through
the fixed-policy envelope $A_2$ with the constant of Lemma G.1.

(c) Substituting $\tau = \kappa W$ (A5) gives the window form
    $D_{\mathrm{SMA}}(W) := \rho_2^{\kappa W}$,
strictly increasing and strictly log-linear (hence convex) in $W$.

PROOF. (a) During the blind period the estimator has not yet detected the change
(A5), so the persistence in force in the true dynamics is $\phi_2$ while any adaptive
reduction acts only through $\beta\gamma_t \leq \beta\gamma$. Fix $t \in \{0, \ldots, \tau-1\}$.
The matrix in force is $A_t = A(\phi_2, W, \beta\gamma_t)$. Two facts bound $\rho(A_t)$:
(i) by construction $\rho(A_t) = \rho(\phi_2, W, \beta\gamma_t)$; (ii) by the Gain-
Envelope Lemma G.1b (in-domain, $\rho_2 > 1$ per A6), $\beta\gamma_t \in$
$[0, \beta\gamma]$ implies $\rho(A_t) \leq \rho(\phi_2, W, \beta\gamma) = \rho_2$. (The
v0.1 draft invoked global gain monotonicity here; that claim is FALSE - $\rho$ is
U-shaped in the gain - and the step now rests on G.1b.) Under A4,
$d_{t+1} = \rho(A_t) d_t$
with $d_t \geq 0$, so by induction $d_\tau = d_0 \prod_{t<\tau} \rho(A_t)$. Each factor
is $\leq \rho_2$, giving $d_\tau \leq d_0 \rho_2^{\tau}$. If the policy does not adapt, every
factor equals $\rho_2$ exactly and the bound is attained; the attainment direction
needs no strictness claim about intermediate gains (equality holds along the
non-adaptive path by construction, which is all the theorem's "achieved when
the policy does not adapt" asserts). (b) Immediate from Lemma G.1
applied to $A_2$, plus Gelfand's formula for the rate; the JSR caveat for time-varying
products is Remark G.0.1. (c) Substitute $\tau = \kappa W$ into $\rho_2^{\tau}$:
$D_{\mathrm{SMA}}(W) = \exp(\kappa \ln(\rho_2) W)$ with $\kappa \ln(\rho_2) > 0$ under A6, which is
strictly increasing, log-linear, and convex in $W$. QED.

NOTE FOR THE ALIGNMENT REVIEW (step 3). The sketch asserted the per-step inequality
for the raw deviation with no norm qualification; the proof shows it is exact under
A4 and holds matrix-generally at the same exponential rate up to a constant. Every
experiment that consumes $D$ uses it ordinally (rankings, correlations) or as a
ratio threshold; constants cancel in the ratio of Theorem 3 and do not move ranks.
To be re-verified operator-by-operator in step 3.

---

<!-- anchor: P-THM-2 -->
### G.3 Theorem 2 (Optimal Measurement Window)

Cost model (as in the source): total expected loss
    $L(W) = c_D \rho_2^{\kappa W} + c_E (1 - \phi^2)/W$,   $W \in [1, \infty)$,
where $c_D > 0$ scales expected regime-change damage (it absorbs the regime-change
probability $p$ and the unit damage cost), $c_E > 0$ scales estimation loss, and
$(1 - \phi^2)/W$ is the Cramer-Rao asymptotic variance rate for the AR(1) coefficient
from a window of $W$ observations. Write $a := \kappa \ln(\rho_2) > 0$ (A5, A6).

STATEMENT (as proved - SHARPENED with an explicit interiority condition).
(i) $L$ is strictly convex on $(0, \infty)$.
(ii) If condition (C):  $c_E (1 - \phi^2) > c_D\, a\, \rho_2^{\kappa}$
holds, then $L$ has a unique interior minimizer $W^{*} \in (1, \infty)$, characterized by
the first-order condition
    (FOC)  $c_D\, a \exp(a W) = c_E (1 - \phi^2)/W^2$.
If (C) fails, $L' \geq 0$ on $[1, \infty)$ and the constrained optimum is the boundary
$W^{*} = 1$.
(iii) Closed form: the interior $W^{*}$ is
    $W^{*} = (2/a) W_L((a/2)\sqrt{c_E (1 - \phi^2)/(c_D\, a)})$,
where $W_L$ is the principal branch of the Lambert $W$ function. (The source's
"(1/(kappa ln rho_2)) * W_L(kappa ln rho_2 * Q)" is the same family with the
parameter bundle $Q$ left unspecified; the form above makes $Q$ explicit. SHARPENED.)

PROOF. (i) $\rho_2^{\kappa W} = \exp(a W)$ is strictly convex in $W$ (positive second
derivative $a^2 \exp(a W)$); $(1 - \phi^2)/W$ has second derivative
$2(1 - \phi^2)/W^3 > 0$ on $W > 0$; a positive combination of strictly convex functions
is strictly convex.
(ii) $L'(W) = c_D\, a \exp(a W) - c_E (1 - \phi^2)/W^2$. As $W \to \infty$ the first
term diverges and the second vanishes, so $L'(W) \to +\infty$; in particular $L' > 0$
for all large $W$. At the left end, $L'(1) = c_D\, a \exp(a) - c_E (1 - \phi^2)$
$= c_D\, a\, \rho_2^{\kappa} - c_E (1 - \phi^2)$, which is negative exactly under (C).
If (C) holds: $L'$ is continuous, $L'(1) < 0$, $L' > 0$ for large $W$, so by the
intermediate value theorem a root exists in $(1, \infty)$; strict convexity makes $L'$
strictly increasing, so the root is unique and is the global minimizer. If (C)
fails: $L'(1) \geq 0$ and $L'$ strictly increasing give $L' \geq 0$ on $[1, \infty)$, so $L$ is
nondecreasing there and the constrained minimum sits at $W = 1$. (The source sketch's
"the estimation derivative is large and negative at W = 1" is a parameter claim,
not a theorem; (C) is the exact condition. SHARPENED.)
(iii) Rearrange (FOC): $\exp(a W) W^2 = c_E (1 - \phi^2)/(c_D a) =: B > 0$.
Take square roots of both sides of $W^2 \exp(a W) = B$:
$W \exp(a W/2) = \sqrt{B}$. Multiply both sides by $a/2$:
$(a W/2) \exp(a W/2) = (a/2)\sqrt{B}$. By definition of the Lambert $W$ function
($z = u e^u$ iff $u = W_L(z)$, principal branch since both sides are positive),
$a W/2 = W_L((a/2)\sqrt{B})$, i.e. $W^{*} = (2/a) W_L((a/2)\sqrt{B})$. Substituting
$B$ completes the form. Positivity of the argument puts us on the principal branch,
where $W_L$ is single-valued, consistent with uniqueness in (ii). QED.

---

### G.4 Comparative Statics of $W^{*}$ (CORRECTED - replaces source Section 4.5)

Let $G(W, \theta) := L'(W) = c_D\, a \exp(a W) - c_E (1 - \phi^2)/W^2$, so the
interior optimum solves $G(W^{*}, \theta) = 0$, and by strict convexity
$G_W = L''(W^{*}) > 0$. Implicit differentiation gives, for any parameter $\theta$,
    $dW^{*}/d\theta = -G_\theta/G_W$,  so  $\mathrm{sign}(dW^{*}/d\theta) = -\mathrm{sign}(G_\theta)$.

(a) $\theta = \rho_2$ (holding $\kappa$, $\phi$, costs fixed). $a = \kappa \ln(\rho_2)$ is
increasing in $\rho_2$, and $G$ depends on $\rho_2$ only through the damage term
$c_D\, a \exp(a W)$, which is strictly increasing in $a$ for $W > 0$ (both the
coefficient and the exponent rise). Hence $G_{\rho_2} > 0$ and $dW^{*}/d\rho_2 < 0$.
CONFIRMS the source: higher instability intensity favors shorter windows.

(b) $\theta = \phi$ (holding $\rho_2$ fixed; direct estimation-cost channel). $\phi$ enters $G$
only through $-c_E (1 - \phi^2)/W^2$:
    $G_\phi = +2 c_E \phi/W^2 > 0$,  hence  $dW^{*}/d\phi < 0$.
This REVERSES the source's claim (b) [$dW^{*}/d\phi > 0$, "coefficients near 1.0 require
more data"]. The reversal is forced by the model's own cost term: the Cramer-Rao
asymptotic variance of the AR(1) estimator is $(1 - \phi^2)/W$, which FALLS as $\phi$
rises toward 1 - high-persistence coefficients are, under this variance model,
estimated MORE precisely per observation, not less. The source's verbal
justification contradicts its own formula; this is the known defect pre-registered
as CORRECTED at OUTLINE node ARG-08. Under the stated cost model the correct
comparative static is: higher steady-state persistence REDUCES estimation pressure
and therefore favors SHORTER optimal windows, holding the regime-change intensity
fixed.

(b') Total effect of $\phi$ (decomposition). In the full model $\phi$ also moves $\rho_2$
(A3: $\rho$ increasing in $\phi$), so the TOTAL derivative is
    $dW^{*}/d\phi\,|_{\mathrm{total}} = dW^{*}/d\phi\,|_{\mathrm{direct}} + (dW^{*}/d\rho_2)(d\rho_2/d\phi)$,
and BOTH terms are negative by (a) and (b): under this cost model the total effect
is unambiguously $dW^{*}/d\phi < 0$. Any restoration of the source's intuition would
require a different estimation-cost model (for example, one in which the QUANTITY
of interest is a level forecast or a unit-root boundary test, whose difficulty
rises with $\phi$); that is a modeling choice outside the pinned cost function and is
NOT adopted here. Flagged for the manuscript's Section 4.5 prose and for the
alignment review: no experiment consumes the sign of $dW^{*}/d\phi$ (checked in step 3),
so the correction changes exposition, not operators - to be re-verified.

(c) $\theta = \Delta\phi$ (through $\kappa = 1 - \epsilon/\Delta\phi$). $d\kappa/d\Delta\phi$
$= \epsilon/\Delta\phi^2 > 0$, and $G$ depends on $\kappa$ through $a = \kappa \ln(\rho_2)$:
    $G_\kappa = c_D \ln(\rho_2) \exp(a W)(1 + a W) > 0$,
hence $dW^{*}/d\kappa < 0$ and $dW^{*}/d\Delta\phi = (dW^{*}/d\kappa)(d\kappa/d\Delta\phi) < 0$.
CONFIRMS the source: larger expected regime changes favor shorter windows.

(d) $\theta = c_E/c_D$ (cost ratio; new, for completeness). Scaling $c_E$ up raises
$-G$ by $c_E$'s term, i.e. $G_{c_E} = -(1 - \phi^2)/W^2 < 0$, so $dW^{*}/dc_E > 0$: dearer
estimation error favors longer windows. Symmetrically $dW^{*}/dc_D < 0$. Matches the
economic reading of Theorem 2 and provides a sign check for the T2 numeric grid.

---

<!-- anchor: P-THM-3 -->
### G.5 Theorem 3 (The Adaptation-Stability Identity)

STATEMENT (as proved). Let the blind-period amplification of Theorem 1 (under A4,
non-adaptive envelope) be $d_\tau = d_0 \rho_2^{\tau}$, and let the counterfactual
deviation had the regime not changed be $d_\tau^0 = d_0 \rho_1^{\tau}$ (the same
recursion under $\rho_1$, with $\rho_1 > 0$). Then the damage amplification FACTOR -
realized deviation relative to the no-regime-change counterfactual over the same
blind window - is exactly
    $D(W) = d_\tau / d_\tau^0 =$
    $(\rho(\phi_2, W, \beta\gamma) / \rho(\phi_1, W, \beta\gamma))^{\tau(W)}$,
with both $\rho$ and $\tau$ functions of the single design parameter $W$. $D(W) > 1$ whenever
$\rho_2 > \rho_1$ and $\tau > 0$; $\log D(W) = \tau(W)[\ln \rho_2(W) - \ln \rho_1(W)]$
factorizes damage into DURATION ($\tau$) times INTENSITY (the log spectral-radius
gap), which is the intensity-times-duration reading in the text.

PROOF. Both trajectories satisfy the A4 recursion from the same $d_0 > 0$: the
realized blind-period path compounds at $\rho_2$ per cycle (Theorem 1a, non-adaptive
envelope, where the bound is attained), giving $d_\tau = d_0 \rho_2^{\tau}$; the
counterfactual path compounds at $\rho_1$ per cycle, giving $d_\tau^0 = d_0 \rho_1^{\tau}$,
strictly positive since $\rho_1 > 0$. The ratio is $(\rho_2/\rho_1)^{\tau}$; $d_0$ cancels, so
the factor is initial-condition-free, and by Lemma G.1(b) any matrix-general
constants $C$ are common to numerator and denominator's growth-rate reading at rate
level. Positivity/exceedance: $\rho_2 > \rho_1 > 0$ and $\tau > 0$ give the ratio $> 1$.
Taking logs gives the stated factorization. Both arguments are functions of $W$ alone
once $(\phi_1, \phi_2, \beta\gamma, \epsilon)$ are fixed: $\rho_i =$
$\rho(\phi_i, W, \beta\gamma)$ by A2 and $\tau = \kappa W$ by A5. QED.

REMARK G.5.1 (bound vs identity). Theorem 1 is an upper BOUND on the realized
deviation (adaptive policies do strictly better); Theorem 3 is an exact IDENTITY
for the non-adaptive envelope's amplification factor - the quantity every
experiment ranks on. Under an adaptive policy the realized factor is $\leq D(W)$, so
$D(W)$ retains its reading as the worst-case regime-change cost multiplier.

---

### G.6 Proposition (Optimal Safety Factor $k^{*}$) - derivation with approximations
labeled

SETTING. The speed limit from the companion papers is $S(\phi, W)\, \beta\gamma = \pi^2/2$,
giving $\beta\gamma_{\max} = (\pi^2/2)/S(\hat{\phi}, W)$, calibrated to the
ESTIMATED persistence $\hat{\phi}$. During a blind period the true $\phi$ exceeds $\hat{\phi}$,
so operating exactly at $\beta\gamma_{\max}$ risks a breach. Choose an operating fraction
$k \in (0, 1]$: $\beta\gamma_{\mathrm{op}} = k\, \beta\gamma_{\max}$.

STATEMENT (approximation - stated as a Proposition, not a Theorem). Under (i)
first-order expansion of $S$ in $\phi$ around $\hat{\phi}$, (ii) Gaussian estimation error
$\phi - \hat{\phi} \sim N(0, \mathrm{Var}(\hat{\phi}))$ with the regime-change contribution entering as
an inflation of effective estimation risk proportional to $p W$ (probability $p$ of a
change during a window of length $W$), and (iii) a breach-avoidance criterion that
holds the operating point at approximately two standard deviations of the induced
uncertainty in $S \beta\gamma/(\pi^2/2)$, the optimal fraction is approximately
    $k^{*} \approx 1 - (1/(\pi^2/2))\sqrt{2 p W\,\mathrm{Var}(\hat{\phi})}$,
matching the source's stated form. For typical manufacturing parameters
($\phi \approx 0.96$, $W \in [8, 12]$, regime changes every 5-7 years) this evaluates in the
0.85-0.95 range; the exact numbers are re-earned by the committed T3 grid, not
quoted from the source.

DERIVATION. Let $u := S(\phi, W)\, \beta\gamma_{\mathrm{op}}/(\pi^2/2)$ be the utilization of the
speed limit at the TRUE $\phi$; stability requires $u < 1$. With $\beta\gamma_{\mathrm{op}} =$
$k (\pi^2/2)/S(\hat{\phi}, W)$, $u = k\, S(\phi, W)/S(\hat{\phi}, W)$. Expanding $S$ to first
order in $(\phi - \hat{\phi})$ (approximation i): $S(\phi, W)/S(\hat{\phi}, W) \approx 1 +$
$s_1 (\phi - \hat{\phi})$, with $s_1 = (dS/d\phi)/S$ evaluated at $\hat{\phi}$. Under
(approximation ii) the term $s_1 (\phi - \hat{\phi})$ is Gaussian with variance
$s_1^2 \mathrm{Var}_{\mathrm{eff}}$, $\mathrm{Var}_{\mathrm{eff}} = 2 p W \mathrm{Var}(\hat{\phi})$ collecting the estimation variance
inflated by the chance and length of a blind window (the factor $2 p W$ is the source's
parameterization of that inflation and is retained as-is; it is a modeling
constant, not a derived quantity - labeled explicitly as such for the 5a review).
The breach-avoidance criterion (approximation iii) sets $k$ so that $u$ stays below 1
at the $\sqrt{\mathrm{Var}_{\mathrm{eff}}}$ scale normalized by the limit: $k^{*} = 1 - \sqrt{\mathrm{Var}_{\mathrm{eff}}}/$
$(\pi^2/2)$ after absorbing $s_1$ into the normalization of $\mathrm{Var}(\hat{\phi})$ (the source
states the formula with $s_1 = 1$, i.e., variance quoted directly in speed-limit
units; retained for continuity and flagged as a units convention). Substituting
$\mathrm{Var}_{\mathrm{eff}}$ gives the stated $k^{*}$. QED (as an approximation chain; each step labeled).

STATUS. G.6 is deliberately a PROPOSITION with an explicit approximation chain: the
source provides the formula with no derivation, and the three approximation steps
above are the minimal honest scaffold that produces it. The T3 grid (step 2)
verifies the practical content (argmin location and the 0.80-0.98 band) directly by
brute force, independent of the approximations. If the grid contradicts the
formula's location, the Proposition - not the grid - is amended, dated.

---

(c) 2026 Jae Kim. This paper is licensed under Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0). You may share it with attribution, for non-commercial purposes, without modification. The accompanying plain-English companion is released under CC BY-NC 4.0, and the analysis and verification code is released separately under the MIT License; see the repository LICENSE.
