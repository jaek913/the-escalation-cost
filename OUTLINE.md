# OUTLINE.md - Paper Roadmap: The Escalation Cost

## Metadata

- **Paper:** The Escalation Cost: Intensity, Duration, and the Growing Damage of Regime Change
- **Archetype:** theory-with-proofs (empirics co-primary; author-ratified 2026-07-13)
- **Source pin (rebuild):** C:\Users\jaek9\Documents\LaggingTruth\05-13-2026\Paper 9\Paper9_The_General_Measurement_Trap_v16.md, MD5 93135760b92cc195da36eb3c2b785ded, SHA256 c4fee62f2b48f8f5a84cf22f5b3d01fe139cc59810db9f11e29d800ed7c648a5
- **Standard:** v1.9.5 (template v1.8)
- **Outline version:** v0.2 - 2026-07-13
- **Status:** draft

## Changelog

- v0.2 2026-07-13 - E1 (primary falsifier) RESULT LANDED: SUPPORT. Rule amended pre-run (dated DESIGN Section 4 amendment, author-ratified rule B: pooled panel statistic replaces per-sector majority after the v1.9.5 suite measured ~0 power in the original rule; falsifier is now panel-level). ARG-13 and LB-E1 nodes updated to DONE/SUPPORT with the pooled figure. Sector-composition note: primary metals = A31SIS per the 2026-07-13 data-layer amendment (source A25SIS mislabel corrected).

- v0.1 2026-07-13 - initial roadmap built from the pinned v16 source, restructured for the retitled standalone rebuild; experiment ids reference DESIGN.md (T1-T3, E1-E12).

## 1. IMRaD structural map (the skeleton)

Abstract -> 1 Introduction -> 2 Related Work (2.1 Control-Theoretic Stability, 2.2 Empirical Bullwhip, 2.3 Semiconductor Dynamics, 2.4 Complexity and Resilience, 2.5 Minsky in Operations, 2.6 Adaptation Rates and Transient Response) -> 3 The Framework in Brief -> 4 The Measurement Damage Theorem (4.1 Setup, 4.2 Theorem 1, 4.3 Theorem 2, 4.4 Theorem 3, 4.5 Comparative Statics, 4.6 The pi^2/2 Speed Limit and Optimal Safety Factor, 4.7 Connection to the Adaptation Tax) -> 5 Empirical Validation (5.1 GFC Episode, 5.2 COVID Episode, 5.3 Rolling 34-Year Validation, 5.4 Beer Game Monte Carlo) -> 6 Supply Chain Application (6.1 Bullwhip Instability Finding, 6.2 Spectral Radius Ordering Tool, 6.3 Firm-Level Bookend, 6.4 Cross-Sector Evidence, 6.5 Boundary Conditions) -> 7 The CHIPS Act (7.1 Most Unstable Sectors, 7.2 Capacity Utilization Threshold, 7.3 Complexity Drives Persistence, 7.4 Werner-CHIPS Nexus) -> 8 Cross-Domain Extensions (8.1 Sovereign Ratings, 8.2 Unemployment Insurance) -> 9 Implications for Institutional Design (9.1 Three-Parameter Audit, 9.2 Reverse-Engineering Principle, 9.3 Domain Interventions) -> 10 Forward Prediction: Self-Service Diagnostic (10.1-10.4) -> 11 Conclusion -> References -> Appendix A Data Sources -> Appendix B Validation and Robustness -> Appendix C Companion Matrix Spectral Radii by Domain -> Appendix D Mitigation Effectiveness -> Appendix E Beer Game Simulation Parameters -> Appendix F Additional Simulation Studies (chain-length sweep, recipe-level non-stationarity, pricing analysis, hysteresis sweep) -> Appendix G Proofs (NEW - full written proofs under theory-with-proofs).

Title/subtitle: CORRECTED - source title "The General Measurement Trap" retired; H1 = "The Escalation Cost", subtitle = "Intensity, Duration, and the Growing Damage of Regime Change"; the theorem keeps its name in the body. Standalone framing: no paper numbering; companions cited by title.

## 2. Argument chain (the spine)

| ID | Claim (one line) | Sect | Depends on | Support (LB-id / proof / cite key) | Status |
| --- | --- | --- | --- | --- | --- |
| ARG-01 | Institutions steer feedback off trailing averages of persistent variables; the estimator lags reality after a regime change | 1 | - | Minsky-1986, Hopp-Spearman-2008, framework cites | RETAINED |
| ARG-02 | The closed loop is a W x W companion matrix; spectral radius rho determines stability (verified input, cited not re-proved) | 3 | ARG-01 | Kim-MeasurementTrap (foundation), EQ-1 | RETAINED |
| ARG-03 | Prior literatures answer steady-state stability or optimal policy mix, not the transient cost of estimator lag during regime transition (the gap) | 1,2 | - | Disney-Towill-2002, Dejonckheere-2003, Li-Dorfler-2024, Leng-2025, Spiegler-2016 | RETAINED |
| ARG-04 | A trailing estimator of window W adapts to a new persistence regime over adaptation time tau(W): the blind period | 3,4.1 | ARG-02 | Kim-AdaptationRate (foundation), EQ-1 | RETAINED |
| ARG-05 | THM-1 (Compound Damage Bound): blind-period damage is bounded by D = (rho_2/rho_1)^tau | 4.2 | ARG-02, ARG-04 | P-THM-1, LB-T1-bound, EQ-2 | TRANSFORM (proof sketch -> full proof) |
| ARG-06 | THM-2: a unique interior optimal window W* exists, closed form via Lambert W | 4.3 | ARG-05 | P-THM-2, LB-T2-wstar, EQ-3 | TRANSFORM (proof sketch -> full proof) |
| ARG-07 | THM-3 (Adaptation-Stability Identity): total damage governed by intensity x duration across domains | 4.4 | ARG-05 | P-THM-3, EQ-4 | TRANSFORM (proof sketch -> full proof) |
| ARG-08 | Comparative statics of W*: signs of dW*/d(rho_2), dW*/d(phi), dW*/d(Delta_phi) | 4.5 | ARG-06 | P-THM-2 corollary, LB-T2-statics | CORRECTED (source 4.5 justification contradicted its own (1-phi^2)/W cost term - re-derived cleanly in rebuild) |
| ARG-09 | Operating below the pi^2/2 limit is optimal under regime-change risk; safety factor k* < 1 | 4.6 | ARG-05, ARG-02 | LB-T3-kstar, EQ-5, EQ-6, Kim-MeasurementTrap | TRANSFORM |
| ARG-10 | The damage bound gives the adaptation-tax framework its transition-cost foundation | 4.7 | ARG-05, ARG-07 | Kim-AdaptationTax (foundation) | TRANSFORM (de-seriesed cross-reference) |
| ARG-11 | GFC episode: pre-crisis predicted damage ranking aligns with realized crisis damage; combined D at least comparable to components (corroborating, n stated) | 5.1 | ARG-05 | LB-E2-gfc, LB-E2-components, TBL-1, Udenio-2015 | TRANSFORM |
| ARG-12 | COVID episode: null result, consistent with the theorem's stated domain (persistence dropped; compound shock outside step-change model) | 5.2 | ARG-05 | LB-E3-covid, LB-E3-persistence-direction | TRANSFORM |
| ARG-13 | PRIMARY (falsifier): rolling out-of-sample D predicts subsequent I/S deviation at the PANEL level across regime-oscillating sectors [amended rule B - pooled statistic, not per-sector majority]. RESULT 2026-07-13: SUPPORT, pooled mean Spearman +0.1505, joint block-bootstrap panel p = 0.0090 (< 0.01), 9 oscillating sectors, all 9 positive; verdict rests on the pooled statistic (per-sector inference noisy at this resolution). | 5.3 | ARG-05 | LB-E1-panel, LB-E1-range, TBL-2 | DONE (SUPPORT) |
| ARG-14 | Acting on the diagnostic saves cost: spectral-radius tool beats an ERP baseline in the Beer Game Monte Carlo; full theorem adds a further edge | 5.4 | ARG-09 | LB-E4-erp, LB-E4-tool, LB-E4-full, LB-E4-winrate, TBL-3, Oroojlooyjadid-2022 | TRANSFORM |
| ARG-15 | Measured sector I/S persistence is high enough that standard order-up-to policies sit at or over the stability boundary | 6.1 | ARG-02 | LB-E5-persistence, Lee-1997a, Chen-2000 | TRANSFORM |
| ARG-16 | The spectral-radius ordering tool is a practitioner rule taking observed demand persistence as input; novelty positioned against stability-region inversions and ARMA eigenvalue work | 6.2 | ARG-14, ARG-15 | Warburton-2004, Wang-2013, Udenio-2017, Gaalman-Disney-2009, Boute-2006 | RETAINED |
| ARG-17 | Firm-level bookend: the tool needs monthly n >= 36; quarterly filings are insufficient (data floor illustration) | 6.3 | ARG-16 | LB-E13-firm-bookend, S-4 | TRANSFORM |
| ARG-18 | Rolling 34-year monitoring narrative: rho crossings preceded the major disruptions (backward-looking; weaker than 5.3 and said so) | 6.4 | ARG-13 | LB-E5-monitor, TBL-4 | TRANSFORM |
| ARG-19 | Boundary conditions mapped: chain-length crossover, pricing asymmetry, hysteresis split, and the recipe-level non-stationarity limitation | 6.5, App F | ARG-14 | LB-E7-crossover, LB-E8-up, LB-E8-down, LB-E9-robust, LB-E9-fragile, LB-E12-oracle, TBL-7, Boute-2022 | TRANSFORM |
| ARG-20 | The two sectors the CHIPS Act depends on rank as the most structurally unstable in the panel (graded assertion per DESIGN E5) | 7.1 | ARG-15 | LB-E5-ranking, LB-E5-chips, TBL-4, Monch-2011 | TRANSFORM |
| ARG-21 | Capacity utilization and rho are empirically linked; the rho crossing sits at the Factory Physics knee; monitoring benchmark for the buildout | 7.2 | ARG-20 | LB-E6-threshold, LB-E6-current, TBL-6, Hopp-Spearman-2008 | TRANSFORM |
| ARG-22 | Product/network complexity drives persistence, connecting the complexity literature to the instability ranking | 7.3 | ARG-20 | Bozarth-2009, Novak-Eppinger-2001, Choi-2001, Serdarasan-2013, Anderson-2000, Ning-2023 | RETAINED |
| ARG-23 | Werner-CHIPS nexus: directed credit creation as a possible financing channel for supplier-ecosystem stability (exploratory) | 7.4 | ARG-20 | Werner-1997, Werner-2005, Werner-2014a, Werner-2014b, Alfaro-2025, Ahn-Tan-2025 | RETAINED |
| ARG-24 | Sovereign ratings: conditionally unstable - stable in calm, crossing under crisis-level feedback (suggestive) | 8.1 | ARG-07 | LB-E10-calm, LB-E10-crisis, TBL-5, Ferri-1999, JST data | TRANSFORM (ground-up re-verification mandatory - source v14 fatal-error site) |
| ARG-25 | UI experience rating: procyclical feedback reading - stable normally, boundary-crossing persistence in the GFC (suggestive, not a welfare claim) | 8.2 | ARG-07 | LB-E11-normal, LB-E11-gfc, Anderson-Meyer-1994, Woodbury-2004, Fath-Fuest-2002 | TRANSFORM |
| ARG-26 | Institutional design: the three-parameter audit (phi, W, beta*gamma) and reverse-engineering principle generalize the diagnostic | 9 | ARG-07, ARG-09 | EQ-2, EQ-5, Rasmussen-1997, Dekker-2011 | RETAINED |
| ARG-27 | Forward prediction: a self-service diagnostic - rho > 1 predicts amplifying response to the next shock, rho < 1 decaying; registered publicly at 5c | 10 | ARG-13, ARG-16 | LB-FP-diagnostic, replication protocol | TRANSFORM (re-identified for standalone registration) |
| ARG-28 | Conclusion: the theorem converts steady-state stability analysis into a computable transient-cost diagnostic; limits stated | 11 | all | C-01..C-06, L-01..L-07 | TRANSFORM |

## 3. Citations

Roles: prior-art / motivating-anomaly / method-precedent / corroboration / contrast / foundation (self-cite) / context. Every key below must appear in the manuscript; the reconciliation gate greps for each.

| Key | Reference (full entry -> References) | Role | Supports | Status |
| --- | --- | --- | --- | --- |
| Ahn-Tan-2025 | Ahn & Tan (2025), IMF WP 2025/102 | context (resilience/diversification) | ARG-23, 7.4 | RETAINED |
| Alfaro-2025 | Alfaro, Brussevich, Minoiu & Presbitero (2025), NBER | context (bank financing of supply chains) | ARG-23, 7.4 | RETAINED |
| Anderson-2000 | Anderson, Fine & Parker (2000) | prior-art (upstream volatility, machine tools) | ARG-22, 2.3/7.3 | RETAINED |
| Anderson-Meyer-1994 | Anderson & Meyer (1994) | prior-art (UI experience-rating layoff effects) | ARG-25, 8.2 | RETAINED |
| Boute-2022 | Boute, Disney, Gijsbrechts & Van Mieghem (2022) | contrast + future-work route (non-stationary demand policies) | ARG-19, 6.5/App F | RETAINED |
| Boute-2006 | Boute, Disney, Lambrecht & Van Houdt (2006) | closest method-precedent (closed-loop production-inventory; i.i.d. demand) - positioned in 2.1 | ARG-16, 2.1/6.2 | RETAINED |
| Bozarth-2009 | Bozarth, Warsing, Flynn & Flynn (2009) | prior-art (complexity-performance) | ARG-22, 2.4/7.3 | RETAINED |
| Bray-Mendelson-2012 | Bray & Mendelson (2012) | prior-art (empirical bullwhip, firm level) | 2.2 | RETAINED |
| Bray-Mendelson-2015 | Bray & Mendelson (2015) | prior-art (production smoothing) | 2.2 | RETAINED |
| Cachon-2007 | Cachon, Randall & Schmidt (2007) | prior-art (Census-industry bullwhip prevalence) | 2.2, method context for E1 panel | RETAINED |
| Chen-2000 | Chen, Drezner, Ryan & Simchi-Levi (2000) | prior-art (bullwhip quantification; managed-variable conditioning) | ARG-15, 2.1/6.1 | RETAINED |
| Choi-2001 | Choi, Dooley & Rungtusanatham (2001) | prior-art (supply networks as CAS) | ARG-22, 2.4 | RETAINED |
| Costantino-2014 | Costantino, Di Gravio, Shaban & Tronci (2014) | method-precedent (SPC monitoring of bullwhip) | 2.2/6.2 contrast | RETAINED |
| Datta-Ioannou-1994 | Datta & Ioannou (1994) | prior-art (adaptive-control transient bounds) | 2.6 | RETAINED |
| Dejonckheere-2003 | Dejonckheere, Disney, Lambrecht & Towill (2003) | prior-art (Cardiff transfer-function stability) | ARG-03, 2.1 | RETAINED |
| Dejonckheere-2004 | Dejonckheere et al. (2004) | prior-art (information enrichment) | 2.1 | RETAINED |
| Dekker-2011 | Dekker (2011) | corroboration (drift into failure) | ARG-26, 2.5/9 | RETAINED |
| Disney-2008 | Disney (2008) | prior-art (Jury inners stability) | 2.1 | RETAINED |
| Disney-Towill-2002 | Disney & Towill (2002) | prior-art (discrete transfer-function stability) | ARG-03, 2.1 | RETAINED |
| Disney-Towill-2003 | Disney & Towill (2003) | prior-art (bullwhip/inventory variance) | 2.1 | RETAINED |
| Disney-2004-golden | Disney, Towill & Van de Velde (2004) | prior-art (golden-ratio gain, i.i.d.) | 2.1 | RETAINED |
| Dooley-2010 | Dooley, Yan, Jones & Craighead (2010) | corroboration (2008 destocking, three echelons) | 2.2, 5.1 context | RETAINED |
| Fath-Fuest-2002 | Fath & Fuest (2002) | contrast (experience rating can raise welfare) | ARG-25, 8.2 balance | RETAINED |
| Ferri-1999 | Ferri, Liu & Stiglitz (1999) | motivating-anomaly (procyclical ratings, East Asia) | ARG-24, 8.1 | RETAINED |
| Gaalman-Disney-2009 | Gaalman & Disney (2009) | closest eigenvalue precedent (ARMA-demand) | ARG-16, 2.1/6.2 | RETAINED |
| Gaalman-2022 | Gaalman, Disney & Wang (2022) | prior-art (lead-time eigenvalue analysis) | 2.1 | RETAINED |
| Gibson-2013 | Gibson, Annaswamy & Lavretsky (2013) | prior-art (closed-loop reference-model adaptive control) | 2.6 | RETAINED |
| Gijsbrechts-2022 | Gijsbrechts, Boute, Van Mieghem & Zhang (2022) | contrast (deep RL for inventory) | 2.1/6.2 context | RETAINED |
| Graves-Tomlin-2003 | Graves & Tomlin (2003) | prior-art (process flexibility) | 2.4 | RETAINED |
| Haykin-1996 | Haykin (1996) | method-precedent (adaptive filtering; estimator adaptation) | 2.6 | RETAINED |
| Helbing-2004 | Helbing, Lammer, Witt & Brenner (2004) | prior-art (network oscillation, statistical physics) | 2.1/2.4 | RETAINED |
| Hopp-Spearman-2008 | Hopp & Spearman (2008), Factory Physics | prior-art (VUT knee 85-90%) | ARG-01, ARG-21, 2.3/7.2 | RETAINED |
| Hosoda-Disney-2006 | Hosoda & Disney (2006) | prior-art (three-echelon variance) | 2.1 | RETAINED |
| Jungers-2009 | Jungers (2009) | contrast (joint spectral radius transients; arbitrary switching) | 2.6 | RETAINED |
| Krstic-Kokotovic-1993 | Krstic & Kokotovic (1993) | prior-art (adaptive transient performance) | 2.6 | RETAINED |
| Lee-1997a | Lee, Padmanabhan & Whang (1997a) | prior-art (bullwhip coiners; information distortion) | ARG-15, 2.1/2.2 | RETAINED |
| Lee-1997b | Lee, Padmanabhan & Whang (1997b) | prior-art (bullwhip, Sloan) | 2.1/2.2 | RETAINED |
| Leng-2025 | Leng, Liu, Ren & Tsyvinski (2025), NBER WP 33638 | closest-cousin contrast (persistence-driven network amplification) - positioned explicitly | ARG-03, 2.1 | RETAINED |
| Li-2023 | Li, Gaalman & Disney (2023) | prior-art (proportional/damped-trend OUT equivalence) | 2.1 | RETAINED |
| Li-Dorfler-2024 | Li & Dorfler (2024) | closest-cousin contrast (transient bullwhip via robust control) - positioned explicitly | ARG-03, 2.1 | RETAINED |
| Lin-2020 | Lin, Naim & Spiegler (2020) | prior-art (delivery-time transients) | 2.1 | RETAINED |
| Minsky-1986 | Minsky (1986) | motivating framework (stability breeds instability) | ARG-01, 1/2.5 | RETAINED |
| Monch-2011 | Monch, Fowler & Dauzere-Peres (2011) | prior-art (semiconductor planning survey) | ARG-20, 2.3 | RETAINED |
| Nepal-2012 | Nepal, Murat & Chinnam (2012) | prior-art (capacitated bullwhip attenuation) | 2.3/7.2 | RETAINED |
| Ning-2023 | Ning, Tziantzioulis & Wentzlaff (2023) | context (chip agility; chiplets) | ARG-22, 7.3 | RETAINED |
| Novak-Eppinger-2001 | Novak & Eppinger (2001) | prior-art (product complexity sourcing) | ARG-22, 2.4/7.3 | RETAINED |
| Oliva-Sterman-2001 | Oliva & Sterman (2001) | prior-art (service erosion dynamics) | 2.5 | RETAINED |
| Oroojlooyjadid-2022 | Oroojlooyjadid, Nazari, Snyder & Takac (2022) | contrast (deep-Q Beer Game) | ARG-14, 5.4 context | RETAINED |
| Osadchiy-2016 | Osadchiy, Gaur & Seshadri (2016) | prior-art (systematic network risk) | 2.4 | RETAINED |
| Ouyang-Daganzo-2006 | Ouyang & Daganzo (2006) | prior-art (LTI bullwhip characterization) | ARG-03, 2.1 | RETAINED |
| Plischke-Wirth-2008 | Plischke & Wirth (2008) | contrast (JSR duality/transients; substitute for Jungers full text) | 2.6 | RETAINED |
| Rasmussen-1997 | Rasmussen (1997) | corroboration (drift toward boundaries) | ARG-26, 2.5/9 | RETAINED |
| Repenning-Sterman-2001 | Repenning & Sterman (2001) | prior-art (capability traps) | 2.5 | RETAINED |
| Repenning-Sterman-2002 | Repenning & Sterman (2002) | prior-art (self-confirming attribution) | 2.5 | RETAINED |
| Saricioglu-2025 | Saricioglu, Erol Genevois & Cedolin (2025) | corroboration (COVID bullwhip amplification) | 2.2, 5.2 context | RETAINED |
| Serdarasan-2013 | Serdarasan (2013) | prior-art (complexity drivers review) | ARG-22, 2.4 | RETAINED |
| Shan-2014 | Shan, Yang, Yang & Zhang (2014) | prior-art (China bullwhip replication) | 2.2 | RETAINED |
| Spiegler-2016 | Spiegler, Potter, Naim & Towill (2016) | prior-art (nonlinear control transients) | ARG-03, 2.1 | RETAINED |
| Tomlin-2006 | Tomlin (2006) | prior-art (mitigation/contingency) | 2.4 | RETAINED |
| Udenio-2015 | Udenio, Fransoo & Peels (2015) | corroboration (GFC destocking account) | ARG-11, 2.2/5.1 | RETAINED |
| Udenio-2017 | Udenio, Vatamidou, Fransoo & Dellaert (2017) | prior-art (behavioral stability regions) | ARG-16, 2.1/6.2 | RETAINED |
| Wang-2013 | Wang, Disney & Wang (2013) | prior-art (constrained-inventory stability regions) | ARG-16, 2.1/6.2 | RETAINED |
| Warburton-2004 | Warburton, Disney, Towill & Hodgson (2004) | prior-art (stability-region inversion) | ARG-16, 2.1/6.2 | RETAINED |
| Warburton-Disney-2007 | Warburton & Disney (2007) | prior-art (Lambert W for delays; discrete-continuous equivalence) | 2.1, 4.3 method context | RETAINED |
| Werner-1997 | Werner (1997) | foundation-adjacent (disaggregated credit quantity theorem) | ARG-23, 7.4 | RETAINED |
| Werner-2005 | Werner (2005) | prior-art (New Paradigm; credit creation) | ARG-23, 7.4 | RETAINED |
| Werner-2014a | Werner (2014a) | prior-art (banks create money - empirical test) | ARG-23, 7.4 | RETAINED |
| Werner-2014b | Werner (2014b) | prior-art (credit creation mechanism) | ARG-23, 7.4 | RETAINED |
| Woodbury-2004 | Woodbury (2004) | prior-art (UI schedule procyclicality - the mechanism our reading uses) | ARG-25, 8.2 | RETAINED |
| Zang-Bitmead-1994 | Zang & Bitmead (1994) | prior-art (adaptive transient bounds) | 2.6 | RETAINED |
| Kim-MeasurementTrap | Kim (2026), "The Measurement Trap" (companion, cited by title) | foundation (pi^2/2 criterion; companion-matrix stability) | ARG-02, ARG-09, 3/4.6 | TRANSFORM (de-seriesed; verify against companion's committed claims) |
| Kim-AdaptationRate | Kim (2026), trailing-average adaptation companion(s) (by title) | foundation (adaptation time tau) | ARG-04, 3/4.1 | TRANSFORM (de-seriesed; exact titles fixed at Phase 4) |
| Kim-AdaptationTax | Kim (2026), "The Adaptation Tax" (companion, by title) | foundation (adaptation-tax framework) | ARG-10, 4.7 | TRANSFORM (de-seriesed) |

## 4. Load-bearing findings (no values; ledger ids assigned at Phase 3)

| LB-id | Finding (one line, no value) | Supports | Status |
| --- | --- | --- | --- |
| LB-T1-bound | Numeric stress grid: realized blind-period damage respects the D bound in-domain | ARG-05 | TRANSFORM |
| LB-T2-wstar | Closed-form W* matches brute-force argmin; cost curve unimodal | ARG-06 | TRANSFORM |
| LB-T2-statics | Comparative-static signs of W* confirmed numerically | ARG-08 | CORRECTED (re-derivation) |
| LB-T3-kstar | Expected-cost argmin below the pi^2/2 limit; manufacturing-parameter k* range | ARG-09 | TRANSFORM |
| LB-E1-panel | Pooled mean Spearman over regime-oscillating sectors + joint block-bootstrap panel p (amended rule B). VALUE 2026-07-13: +0.1505, p = 0.0090, 9 oscillating sectors, 0 chronic. | ARG-13 | DONE |
| LB-E1-range | Per-sector Spearman range in the rolling test (descriptive, alpha 0.05 line). VALUE 2026-07-13: oscillating sectors +0.023 to +0.273 (strongest wholesale motor vehicles +0.273, primary metals A31SIS +0.232); never-crossing sectors near zero. | ARG-13 | DONE |
| LB-E2-gfc | GFC episode Spearman for combined D (with exact p, n) | ARG-11 | TRANSFORM |
| LB-E2-components | Component bake-off correlations (rho alone; delta-phi; tau) | ARG-11 | TRANSFORM |
| LB-E3-covid | COVID episode correlation (expected null) | ARG-12 | TRANSFORM |
| LB-E3-persistence-direction | Count of sectors where persistence dropped during COVID | ARG-12 | TRANSFORM |
| LB-E4-naive | Beer Game mean cost, naive policy | ARG-14 | TRANSFORM |
| LB-E4-erp | Beer Game mean cost, ERP baseline | ARG-14 | TRANSFORM |
| LB-E4-tool | Beer Game mean cost, spectral-radius tool + relative reduction vs ERP | ARG-14 | TRANSFORM |
| LB-E4-full | Beer Game mean cost, full theorem + increment | ARG-14 | TRANSFORM |
| LB-E4-winrate | Pairwise win rate, full theorem | ARG-14 | TRANSFORM |
| LB-E5-persistence | Sector I/S persistence estimates (mfg aggregate + detrended variant) | ARG-15 | TRANSFORM |
| LB-E5-ranking | 17-sector instability ranking (share of months rho > 1, both specs) | ARG-20 | TRANSFORM |
| LB-E5-chips | Rank positions of the two CHIPS-dependent sectors (graded assertion rule) | ARG-20 | TRANSFORM |
| LB-E5-monitor | Rolling rho monitoring series: boundary-crossing dates relative to GFC/COVID | ARG-18 | TRANSFORM |
| LB-E6-threshold | Mean rho by utilization bin; crossing bin | ARG-21 | TRANSFORM |
| LB-E6-current | Current utilization reading vs threshold | ARG-21 | TRANSFORM |
| LB-E7-crossover | Chain-length sweep: all-tier deployment harm-to-benefit crossover cells | ARG-19 | TRANSFORM |
| LB-E8-up | Pricing raise-value under strained sustained-upward environment (+ capacity sensitivity) | ARG-19 | TRANSFORM |
| LB-E8-down | Pricing cut-value across all downward environments | ARG-19 | TRANSFORM |
| LB-E9-robust | Hysteresis sweep: raise benefit vs hysteresis level, strained sticky environment | ARG-19 | TRANSFORM |
| LB-E9-fragile | Hysteresis sweep: raise benefit vs hysteresis level, noisy environment | ARG-19 | TRANSFORM |
| LB-E12-oracle | Oracle vs OLS vs fixed-alpha costs under the non-stationary trajectory | ARG-19 | TRANSFORM |
| LB-E10-calm | Sovereign: country rho values at calm feedback (all below boundary) | ARG-24 | TRANSFORM (ground-up re-verification) |
| LB-E10-crisis | Sovereign: boundary-crossing counts along the feedback sweep | ARG-24 | TRANSFORM (ground-up re-verification) |
| LB-E11-normal | UI: cross-state persistence and rho in normal conditions | ARG-25 | TRANSFORM |
| LB-E11-gfc | UI: GFC-period persistence vs boundary | ARG-25 | TRANSFORM |
| LB-E13-firm-bookend | Firm-level illustration: quarterly-n insufficiency for persistence estimation | ARG-17 | TRANSFORM (illustration; ledgered if any figure quoted) |
| LB-FP-diagnostic | Forward-prediction protocol constants (thresholds, window, reporting) | ARG-27 | TRANSFORM (finalized Phase 4, registered 5c) |

## 5. Figures, tables & equations

| ID | What it shows | Sect | Referenced by | Status |
| --- | --- | --- | --- | --- |
| EQ-1 | Setup: AR(1) managed variable, trailing estimator, companion matrix A(phi, W, bg) | 4.1 | ARG-02, ARG-04 | RETAINED |
| EQ-2 | The Measurement Damage Theorem: D = (rho_2/rho_1)^tau | 4.2 | ARG-05, ARG-26 | RETAINED |
| EQ-3 | Optimal window W* closed form (Lambert W) | 4.3 | ARG-06 | RETAINED |
| EQ-4 | Adaptation-Stability Identity | 4.4 | ARG-07 | RETAINED |
| EQ-5 | pi^2/2 single-loop criterion S(phi, W) * bg < pi^2/2 (foundation, restated) | 4.6 | ARG-09, ARG-26 | RETAINED |
| EQ-6 | Optimal safety factor k* expression | 4.6 | ARG-09 | RETAINED |
| THM-1 / P-THM-1 | Compound Damage Bound + full written proof | 4.2 / App G | ARG-05 | TRANSFORM (sketch -> full proof) |
| THM-2 / P-THM-2 | Optimal Measurement Window + full written proof | 4.3 / App G | ARG-06, ARG-08 | TRANSFORM (sketch -> full proof) |
| THM-3 / P-THM-3 | Adaptation-Stability Identity + full written proof | 4.4 / App G | ARG-07 | TRANSFORM (sketch -> full proof) |
| TBL-1 | GFC episode: predicted D ranking vs realized deviation, 17 sectors + component bake-off | 5.1 | ARG-11 | TRANSFORM |
| TBL-2 | Rolling validation: per-sector Spearman, significance, regime classification | 5.3 | ARG-13 | TRANSFORM |
| TBL-3 | Beer Game Monte Carlo: cost by algorithm, paired differences, win rates | 5.4 / App E | ARG-14 | TRANSFORM |
| TBL-4 | Cross-sector summary: peak/mean rho, share months rho > 1, both specs | 6.4 / 7.1 / App C | ARG-18, ARG-20 | TRANSFORM |
| TBL-5 | Sovereign: country persistence + rho at calm and swept feedback | 8.1 / App C | ARG-24 | TRANSFORM |
| TBL-6 | Utilization bins vs mean rho (semiconductors) | 7.2 | ARG-21 | TRANSFORM |
| TBL-7 | Additional simulation studies: chain-length grid, pricing cells, hysteresis cells, oracle comparison | App F | ARG-19 | TRANSFORM |
| TBL-A | Data sources and identifiers (mirrors SOURCES.md) | App A | all empirical ARGs | TRANSFORM |
| FIG (none) | The source carries no figures; any figure added in the rebuild enters as NEW via a dated outline amendment | - | - | RETAINED (as a rule) |

## 6. Assumptions & scope conditions (greppable S- anchors)

| ID | Statement | Where | Status |
| --- | --- | --- | --- |
| S-1 | Linearized closed-loop model; stability read from the companion-matrix spectral radius under linearization | 3 / 4.1 | RETAINED |
| S-2 | AR(1) demand/managed-variable model; single persistence parameter per regime | 4.1 / Methods | RETAINED |
| S-3 | Step-change regime transitions (Minsky tightening); compound multi-channel shocks are outside the model | 4.2 / 6.5 | RETAINED |
| S-4 | Data floor: monthly frequency, n >= 36 (60 preferred) for persistence estimation; quarterly filing data insufficient | 6.2 / 6.3 | RETAINED |
| S-5 | Simulation environment: linear single-echelon core with stated extensions; synthetic AR(1) demand | 5.4 / 6.5 / App E-F | RETAINED |
| S-6 | Pricing model: constant-elasticity, immediate-arithmetic response; no competitor/brand/reference-price dynamics (hysteresis modeled separately) | App F | RETAINED |
| S-7 | Cross-domain feedback strengths (bg) are assumption-driven proxies, not estimates; suggestive framing locked | 8.1 / 8.2 | RETAINED |
| S-8 | Recipe stationarity: the alpha-from-phi damping recipe assumes within-regime stationary persistence | 6.5 / App F | RETAINED |

## 7. Conclusions & limits-of-claim (greppable C- / L- anchors)

| ID | Conclusion or limit | Where | Status |
| --- | --- | --- | --- |
| C-01 | Blind-period damage is governed by intensity x duration, D = (rho_2/rho_1)^tau, computable from quantities institutions already estimate | 11 | RETAINED |
| C-02 | A unique optimal measurement window W* exists in closed form, resolving the accuracy-vs-adaptation-speed tension | 11 | RETAINED |
| C-03 | Under regime-change risk the optimal operating point sits below the pi^2/2 limit (safety factor k* < 1) | 11 | RETAINED |
| C-04 | Acting on the diagnostic reduces cost against a modern baseline in the simulated environment | 11 | TRANSFORM |
| C-05 | The CHIPS-dependent sectors rank at the top of the structural-instability panel (graded per E5 rule) | 11 | TRANSFORM |
| C-06 | Capacity utilization functions as an empirical stability threshold consistent with the Factory Physics knee | 11 | TRANSFORM |
| L-01 | Does NOT apply to compound shocks where persistence drops (COVID boundary condition) | 5.2 / 6.5 / 11 | RETAINED |
| L-02 | Chronically-unstable sectors need steady-state analysis; the transient theorem has no clean trigger there | 6.5 / 11 | RETAINED |
| L-03 | Simulation results establish behavior within the modeled environment only; no deployment-scale generalization claimed | 6.5 / 11 | RETAINED |
| L-04 | Recipe-level non-stationarity limitation: even with perfect persistence knowledge the damping recipe loses value under drifting persistence; unresolved here; one trajectory shape tested | 6.5 / App F / 11 | RETAINED |
| L-05 | Cross-domain extensions are suggestive readings, not causal or welfare claims | 8 / 11 | RETAINED |
| L-06 | The GFC episode test is corroborating only (single episode, small n, marginal significance) | 5.1 | RETAINED |
| L-07 | Pricing findings bounded by the immediate-arithmetic demand model; hysteresis addressed, competitor/brand effects not modeled | App F | RETAINED |

## Reconciliation (run before signing; re-run at Phase 4 open/close and Phase 5)

- [ ] Every ARG node has >= 1 support and a valid Depends-on (or "-" for a premise).
- [ ] Every citation key maps to >= 1 ARG node or section (no orphans either direction).
- [ ] Every load-bearing finding names a real LB-id in claims.lock; no values in this file.
- [ ] Every FIG-/TBL-/EQ- (and THM-/P-THM-) is present at its anchor AND referenced in the text.
- [ ] Every S- and C-/L- anchor appears in the manuscript.
- [ ] Every internal cross-reference resolves.
- [ ] Every node has a status; every DROPPED carries a valid reason (none yet).
- [ ] The IMRaD map matches the manuscript's actual section list.
- [ ] (Rebuild) every COVERAGE KEEP/TRANSFORM row maps to >= 1 node here.

## Author sign-off

> The roadmap captures the paper's full argument, every citation, every load-bearing finding, every figure/table/equation, the assumptions/scope, and the conclusions; every node has a status and (where applicable) a manuscript anchor; (rebuild) every COVERAGE keep maps to a node; no values are hard-coded. Accurate as of commit 7593a1ab0cdb01f73e42319c5d657ad1a7584e65, outline v0.1.

**Signed:** Jae Kim (ORCID 0009-0005-3260-7880) - **Date:** 2026-07-13
