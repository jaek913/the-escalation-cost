# Phase 5a Round-1 Findings - The Escalation Cost (reviewer document, verbatim)

Provenance: the reviewer's round-1 findings report, delivered in the isolated
claude.ai review session in response to the launch package (SHA256
39c79ea74608245e3be1f3570a9062c824a6d821b987c8c0787c1759d6ef6958), received
2026-07-26 and committed 2026-07-28 from the author's full-conversation
export with all messages expanded. Chat-interface artifacts removed; reviewer
prose untouched, including the reviewer's own disclosure that the session's
tool-use limit was reached partway through Pass 10.

---

# Adversarial Review Findings — "The Escalation Cost" (Phase 5a)

**Reviewer:** fresh isolated session. **Package SHA256 verified:** `39c79ea7…6ef6958` (matches the attestation). Mechanical gate output taken as the integrity attestation per the prompt.

**Note required by the Standard:** author and reviewer are both Claude, so this review catches oversight, not shared model blind spots.

**Status of this delivery:** I hit the session's tool-use limit partway through Pass 10. Passes 1–8 were run to completion on the material I had read; Pass 9 (proof rigor) was run on the full text of Appendix G; Pass 10 (methods-code fidelity) was run against E1, E2, E3, E4, E6, E14-echelon, E14-contrast, `theory_lib`, `build_claims`, and `render_paper`, but **not** against E5-monitor, E7, E9, E10, E11, E12, or the `analysis/suites/` directory. I flag the incomplete passes explicitly at the end rather than reporting them as clean.

---

## What the mechanical layer checks out on

Independently reproduced inside the package before any finding below:

- **Ledger ↔ outputs:** all 506 rows re-dug from the committed JSONs — 485 by `json_path`, 21 by re-executing the `DERIVED` lambdas in `build_claims.py`. **Zero mismatches.**
- **Renderer:** re-ran `render_paper.py`; output is **byte-identical** to the committed rendered manuscript. 593 occurrences / 506 distinct ids, every token has a row, every row is placed.
- **Citations:** all 73 OUTLINE citation keys appear in the reference list and are cited in the body; zero orphans; zero undefined keys.
- **Node tie:** S-1…S-8, L-01…L-07, C-01…C-06, all TBL/EQ/THM anchors present in the rendered manuscript.

---

## CONFIRMED FINDINGS

### F-01 — E8's numbers are a re-analysis of the source's own artifact, and the manuscript never says so
**Pass:** 10 (methods-code fidelity), with a Pass 8 component
**Location:** `analysis/e8_pricing.py` docstring + `INPUTS`; `data/SOURCES.md` lines 82–87, 96; manuscript §5.7, §7.5, Appendix F Panel C, Appendix A / TBL-A

**Claim as written.** §5.7: *"The simulation studies use paired designs: within a run, every algorithm faces identical demand sequences, seeds are recorded, and run counts were fixed in advance… The pricing and hysteresis studies likewise report all cells."* Appendix F introduces "four studies" including "the pricing analysis" alongside three studies this paper ran.

**What I found.** E8 is not a run. Its own header states: *"THIS IS AN ANALYSIS, NOT A RE-EXECUTION (16e). It reads the source's own committed artifact - 1,800 raw trial records - and computes the claims from it."* `SOURCES.md` line 96 confirms: *"E8 analyses it rather than re-running it… A re-run was measured and rejected: 19.04 s/trial => 55.5h."* The manuscript nowhere discloses this. §5.7's "within a run… seeds are recorded… run counts were fixed in advance" is a description of E4/E7/E9/E12 that does not hold for E8.

**Evidence.** The near-identity between the rebuilt figures and the source figures that COVERAGE.md dispositioned DROP is the observable tell:

| COVERAGE.md line 103 (source, DROPPED) | Rebuild (Panel C) |
|---|---|
| +$10,142 | 10141.857108768863 |
| −$2,315 | −2315.245864373627 |
| −$581 | −581.3646581811907 |
| −$1,238 | −1238.289061709133 |
| ~$845 at 1.8x | 842.1953341888299 (1.8x) |

Agreement to 4–5 significant figures across five independent quantities is not convergence of two constructions; it is the same trial records read twice. A reader of the manuscript alone has no way to know that.

**Second-review test.** I considered withdrawing this on the grounds that Appendix A's TBL-A discloses a source artifact. It does — but only the **Phase 2.6 chain sweep** ("Source simulation sweep (9,000 trials; fixed in-house artifact)… E7 regression record; E12 leg B"). The six `phase27_*` artifacts that carry **all** of E8 are registered in `SOURCES.md` but have **no row in TBL-A**. Appendix A states the governing rule itself: *"Where the two ever disagree, the registry is correct and the table is a defect."* By the paper's own rule this is a defect. CONFIRMED, and strengthened rather than withdrawn.

**Severity:** LOAD-BEARING. It affects Abstract ("Simulation studies map where acting on the diagnostic helps and where it harms: value is… asymmetric between price raises and cuts"), C-07-adjacent limit L-07, and ledger rows in the LB-E8 family.

**Proposed adjudication:** fix — add the TBL-A row for the `phase27_*` artifacts, and add one sentence to §5.7 and Appendix F stating that E8 is an analysis of the source's committed 50-seed records rather than a run by this paper's code, with the measured re-run cost as the reason. The substance survives; only the disclosure is missing.

---

### F-02 — COVERAGE.md's zero-drop checklist is contradicted by its own table
**Pass:** 8 (completeness)
**Location:** `COVERAGE.md` line 12 (header posture), line 103 (the DROP row), line 150, line 158 (checklist)

**Claim as written.** Line 12: *"Posture: ZERO-DROP. Every source element is KEEP or TRANSFORM."* Line 158: *"Every DROP carries a valid reason - vacuously true: ZERO drops."* Line 150: *"zero losses - no DROP rows owed."*

**What I found.** Line 103 is a DROP row: *"Pricing-mechanism ABSOLUTE DOLLAR LEVELS… | DROP - not replicable in prior form | ESCALATED 2026-07-15."* The escalation is dated after the header and checklist were written, and neither was updated. The checklist assertion is therefore false as committed, and it is the assertion a reviewer is directed to rely on.

**Second-review test.** The DROP's *reason* holds — the row documents a 39× spread across three mutually exclusive source values for the 1.8x cell and a direct v16-vs-draft conflict on the −$2,315 figure. This is a good-faith, well-evidenced disposition. The defect is purely that the summary claims zero drops while the ledger contains one. Confirmed as a bookkeeping defect, not a substantive coverage loss.

**Severity:** MINOR (COVERAGE.md is a verification artifact, not a manuscript claim; no ledger row or Abstract/Conclusion claim moves).

**Proposed adjudication:** fix — update lines 12, 150, and 158 to "one DROP, escalated 2026-07-15, reason at line 103."

---

### F-03 — E6's committed SPEC-M robustness result exists, is required by DESIGN, and is not reported
**Pass:** 8 (completeness) + 6 (interpretation overreach)
**Location:** `DESIGN.md` line 207 and line 975; `analysis/outputs/e6_capacity_threshold.json` → `robustness_spec_M`; manuscript §8.2, TBL-6, C-06

**Claim as written.** DESIGN line 207: E6's operator is *"NAICS 334 from E5's pipeline (SPEC-R primary, SPEC-M robustness)."* DESIGN line 975: the two named specs are *"both reported wherever both apply (E5, E6)."* Manuscript §5.3 restates the commitment: *"Two real-data specifications were named in advance and both are reported wherever both apply… results that hold under one and not the other are reported as exactly that."*

**What I found.** §8.2 and TBL-6 report SPEC-R only. The SPEC-M leg was computed and committed:

| bin | SPEC-R mean rho (reported) | SPEC-M mean rho (committed, unreported) |
|---|---|---|
| <75 | 1.049927 | 0.759914 |
| 75–85 | 1.065486 | 0.822648 |
| 85–90 | 1.064265 | 0.811749 |
| ≥90 | 1.078030 | 0.881278 |

Under SPEC-M, `crossing_bin: null`, and E1's committed classification puts A34SIS at `frac_months_above_1 = 0.0` — the sector never touches the boundary at any utilization level.

**Why this is more than an omission.** §8.2's load-bearing sentence is *"NAICS 334 runs persistently above the instability boundary at every utilization level - chronically unstable rather than utilization-triggered."* That is true under SPEC-R and exactly inverted under SPEC-M, where the sector is persistently **below** the boundary at every level. C-06 states the result unconditionally: *"semiconductor instability is structural rather than utilization-triggered."* The body does not support that at that strength; it supports "under SPEC-R, structural; under SPEC-M, absent."

The *unadjudicable* verdict survives either way — the test needs a two-regime contrast and gets one regime under both specs — so the honest headline is intact. What is not supported is the positive attribution of instability.

**Second-review test.** I checked whether a dated amendment removed the E6 SPEC-M reporting obligation. Section 16's amendment log and the E6 section (DESIGN 203–222) contain no such amendment; the obligation stands as written in two places. I also checked whether §8.1's general spec-sensitivity discussion covers it — it discusses *rank* sensitivity in the E5 ranking, not the sign of the boundary comparison in E6. CONFIRMED.

**Severity:** LOAD-BEARING (C-06; ledger rows LB-E6-bin-mean family; a DESIGN-mandated robustness leg).

**Proposed adjudication:** fix — add the SPEC-M column to TBL-6, and rewrite C-06 and the §8.2 sentence to condition on the specification, e.g. "under the ranking specification the sector sits above the boundary at every utilization level and under the monitoring specification below it at every level; either way the knee has no stable-side contrast to fire on."

---

### F-04 — E1's operator estimates persistence from 12 observations, in direct conflict with scope condition S-4
**Pass:** 4 (does the spec test the thesis)
**Location:** `analysis/e1_rolling_validation.py` `sector_series_stats` (`RECENT_WIN = 12`); `e2_gfc_episode.py` `CRISIS = 2008-01..2009-12`; `e3_covid_episode.py` `CRISIS = 2020-01..2021-12`; manuscript §5.1, §7.2, §7.3

**Claim as written.** §5.1: *"The data floor is a scope condition, not a preference (S-4): persistence estimation requires monthly frequency and at least thirty-six observations, sixty preferred. A twenty-observation quarterly sample cannot distinguish a persistence of 0.95 from one of 0.50."* §7.3 hardens it: *"a decade of quarterly observations yields roughly forty points, and the persistence estimate at that sample size is too noisy to place a firm relative to the boundary with any confidence."*

**What I found.** The primary falsifier's numerator is estimated from **twelve** observations:

```python
phi_r = ols_phi(y[t - RECENT_WIN:t])      # RECENT_WIN = 12
r_r   = rho(phi_r, W_SPEC, BG_SPEC)
d_vals.append((r_r / r_b) ** TAU ...)
```

E2's `phi2` uses 24 months; E3's `phi2` uses 24 months. All three are below the 36-observation floor S-4 declares binding, and 12 is below the 20-observation sample §5.1 names as the example of what cannot work.

The paper's own committed measurement of small-sample AR(1) bias is in the same experiment family: `t1_theorem_checks.ols_vs_yw` at n=40, true phi=0.95, returns `ols_mean = 0.8171` — a 14% downward bias at n=40. At n=12 the bias and variance are materially worse, and that estimate is the entire signal in D.

**Second-review test.** The strongest rebuttal I could construct: S-4 governs the *tool's* input requirement (§7.2/§7.3 — placing a firm relative to the boundary), whereas `phi_recent` is a *regime-change detector*, not a boundary placement, so the floor arguably does not bind it. I take that rebuttal seriously and it may be the right adjudication. But it is not what the manuscript says: §5.1 states S-4 as a property of "persistence estimation" without qualification, and §5.2 says *"Predicted damage is D = (rho_2/rho_1)^tau, computed with rho_1 at pre-transition persistence and rho_2 at post-transition persistence"* — i.e. `phi_recent` **is** a persistence estimate feeding a spectral radius. As committed, the paper asserts a floor and its primary experiment operates a third of the way below it, unremarked. CONFIRMED as a disclosure/consistency defect at minimum.

**Severity:** LOAD-BEARING (S-4 is a stated scope condition; the operator it conflicts with produces the Abstract's headline validation).

**Proposed adjudication:** rebut-with-reason, in writing, in §5.4 — state explicitly that S-4 governs level placement relative to the boundary and does not govern the trailing-12 change detector, and say why a 12-observation estimate is adequate for a *ranked* change signal when it is inadequate for a *level*. If that argument cannot be made, the alternative is to report the falsifier at a longer `RECENT_WIN` as a robustness leg. Either way the current silence is the defect.

---

### F-05 — The primary falsifier is invariant to the theorem's exponent, so it does not test the compound structure it is offered as validating
**Pass:** 4 (does the spec test the thesis)
**Location:** `e1_rolling_validation.py` frozen note 1 and `d_vals` construction; manuscript §6.3, §4.2, Abstract

**Claim as written.** Abstract: *"We prove that blind-period damage is bounded by a compound expression D = (rho_2/rho_1)^tau - intensity raised to duration… The bound is validated on a 34-year rolling out-of-sample panel."* §4.2: *"The structure is the paper's central claim in one line: damage is not additive in the delay, it is exponential in it."*

**What I found.** In E1, W is constant across every sector and month, so `TAU = KAPPA * W_SPEC = 6.0` is a single positive constant exponent applied to every observation. `D = (r_r/r_b)**TAU` is therefore a strictly monotone transform of the ratio `r_r/r_b`, and the statistic is Spearman — rank-invariant. The script states this itself: *"Spearman is rank-based, hence E1's statistic is provably invariant to the kappa choice."* E2's header states the same.

The consequence is not disclosed in the manuscript: **the exponential structure — the paper's stated central claim — receives no empirical test from the falsifier.** E1 tests whether the *ratio* `rho_recent/rho_baseline` ranks subsequent deviation. Any monotone function of that ratio, including the ratio itself, `log` of it, or the ratio raised to any positive power, would return the identical Spearman, identical p, identical verdict. What is validated is the *intensity* half; the *duration* half and the compounding are untouched.

**Second-review test.** I checked whether the manuscript scopes this anywhere. Remark G.0.1 says *"E1-E12 use D as an ordinal ranking and threshold metric, which is invariant to the constant"* — but that is about the Lemma G.1 constant `C`, not about `tau`, and it appears in a proof appendix rather than where the validation claim is made. §6.3 and the Abstract both present the panel test as validating "the bound." CONFIRMED.

**Severity:** LOAD-BEARING (Abstract sentence; C-01's empirical support).

**Proposed adjudication:** fix — one sentence in §6.3 stating that because W is constant across the panel, the rolling test is rank-identical to a test on the spectral-radius ratio alone, and that it therefore validates the intensity ordering rather than the exponent. This costs the paper little and closes a claim a referee will otherwise open. A genuine test of the exponent would require cross-sectional variation in W, which this panel does not have — worth stating as a limit.

---

### F-06 — Panel membership for the falsifier is selected using the full sample, including the forward windows
**Pass:** 1 (look-ahead)
**Location:** `e1_rolling_validation.py` `sector_series_stats` classification block; manuscript §5.4, §6.3, Abstract, §11.1 Prediction B

**Claim as written.** Abstract: *"validated on a 34-year rolling out-of-sample panel of seventeen U.S. inventory-to-sales series."* §5.4: *"Sector classification is part of the operator, not a post-hoc convenience."*

**What I found.** Each `(D_t, outcome_t)` pair is correctly out-of-sample — `D_t` uses `y[:t]`, `outcome_t` uses `y[t+1:t+13]`. But the *classification* that decides which sectors carry the verdict is computed over the whole `rho_roll` trajectory, which extends to `n` (past the last testable `t`, since `d_vals` stops at `n - FWD_WIN`):

```python
for t in range(BASE_WIN, n):
    ...
    rho_roll.append(r_b)
    if t + FWD_WIN > n: continue          # test pairs stop here; rho_roll does not
...
frac_above = float((rr > 1.0).mean())      # whole-sample
crossings_up / crossings_dn                # whole-sample
```

The verdict rests on 9 of 17 sectors chosen with knowledge of the entire trajectory. A practitioner in 1997 could not have known which nine. Selection materially changes the statistic: the nine selected sectors have Spearman +0.023 to +0.273, all positive; the eight excluded run −0.132 to +0.208, mixed.

**Second-review test — partial withdrawal.** I initially drafted this as invalidating the p-value. On focused re-examination it does **not**: the classification is a function of `rho` (the D-side) only, never of the outcome, and the joint block bootstrap scrambles the outcome with the selected set held fixed. Selection on D-side variability cannot manufacture a D-outcome association under that null. **The p = 0.0090 is valid as computed**, and I withdraw the inference-validity component.

What survives is narrower and still real: the *label* "out-of-sample," applied at the panel level, and the Abstract's "seventeen series," overstate what a real-time user could have run. §7.4 concedes the mechanism obliquely — *"in part reflecting that the full-sample classification contains these episodes"* — but §5.4, §6.3, and the Abstract do not. Prediction B inherits the same classification, and §11.3 handles it correctly (*"fixed by an earlier experiment… Its membership is public in Table TBL-2"*), which is the model §6.3 should follow.

**Severity:** LOAD-BEARING (Abstract wording; the "out-of-sample" characterization of the falsifier).

**Proposed adjudication:** fix — in §5.4 and §6.3, state that sector classification is a full-sample operator and that the out-of-sample property holds within each selected sector's time series rather than at the level of panel membership. Consider reporting the all-17 pooled mean as a descriptive robustness line so the selection's contribution is visible.

---

### F-07 — E2's "combined beats components" gate is a bare point-estimate comparison on a common sample
**Pass:** 3 (statistical inference validity — contrast rule)
**Location:** `e2_gfc_episode.py` `run_panel` → `combined_ge_components`; manuscript §6.1, TBL-1

**Claim as written.** TBL-1: *"Combined D at least matches each component | true."* §6.1 reports it as a component of the SUPPORT verdict.

**What I found.** The gate is `all(s_d >= v - 1e-9 for v in informative)` — a comparison of three Spearman coefficients estimated from the **same 17 sectors and the same realized outcomes**, decided on point estimates with no interval, no paired resample, and no test of the difference. The realized margin is 0.34559 vs 0.31618 = **0.0294** on n = 17.

The v1.9.11 contrast rule targets comparisons from a common resample decided by marginal-interval overlap. This is the same failure one step further out: it is decided by marginal *point estimates* with no uncertainty at all. The correctly targeted statistic is the same one E14 eventually adopts — the within-resample contrast `s_D − s_component` and its interval — and the machinery to compute it already exists in `boot_p`, which runs the resamples but discards everything except the marginal p for D.

**Second-review test.** Two possible rebuttals. (i) DESIGN Section 5 says *"differences not over-read"* — true, and the manuscript does not over-read the size of the gap. But the difference is nonetheless load-bearing: it is a conjunct of the frozen verdict rule, and flipping it flips SUPPORT to WEAKENS. A quantity that decides a verdict is not exempt from the contrast rule by being described as not-over-read. (ii) E2 is only corroborating and L-06 binds. True, and it lowers the stakes — but the verdict is still printed as SUPPORT in §6.1 and TBL-1. CONFIRMED, at reduced severity.

**Severity:** LOAD-BEARING by the stated criterion (ledger rows `LB-E2-combined-ge-components`, `LB-E2-spearman`, and a conjunct of a reported verdict), though the paper's own L-06 already caps what it may be used for.

**Proposed adjudication:** fix, cheaply — compute the paired contrast `s_D − s_{|Δφ|}` within the existing permutation resamples and report its interval next to the boolean. If the interval spans zero, report the conjunct as unresolved rather than `true`. This is the same repair E14 made and it should be applied consistently.

---

### F-08 — The contrast rule's reported false-positive rate measures a strictly narrower event than the rule the analyst would apply
**Pass:** 3 (statistical inference validity)
**Location:** `analysis/e14_contrast.py` `power_curve` → `contrast_fires(Xs, B_POWER, SEED + r, 2)`; manuscript §7.1, TBL-8 secondary panel

**Claim as written.** §7.1: *"The pre-committed admissibility condition was that the contrast rule's false-positive rate must not exceed 0.05; measured at realised coupling it is 0.00, so the rule fires more often on true effects without firing more often on none."* This is the DESIGN 22.3 outcome-C gate that decides whether the secondary contrast interval may be read at all.

**What I found.** `contrast_fires` requires **two** conditions: the interval excludes zero **and** `largest_step_index == want_index`. In the real run's `power_curve`, `want_index` is hard-coded to `2`. At the null cell `R3 = 1.0` (no planted concentration), the reported "false-positive rate" is therefore `P(interval excludes 0 AND the observed argmax happens to be step 3)`, not `P(the rule fires)`. With three steps and no planted effect the argmax is roughly uniform, so the analyst-relevant rate — fire on whichever step wins, which is what the real run actually did — is on the order of three times the reported number.

The suite gets this right and the real run does not. Suite:

```python
pe = point_estimates(Xr)
k = int(np.argmax(pe["step"]))          # whichever step wins
if contrast_fires(Xr, 1000, SEED + r, k):
```

Real-run power curve:

```python
if contrast_fires(Xs, B_POWER, SEED + r, 2):   # step 3 only
```

**Second-review test.** I nearly withdrew this as immaterial: the measured rate is 0.00/100, and tripling 0.00 is still 0.00 as a point estimate, so the outcome-C gate would almost certainly pass either way. That reasoning is right about the *outcome* and wrong about the *record*. The number is quoted in the manuscript as "the rule's false-positive rate," it gates admissibility of the paper's only correctly-targeted echelon statistic, and the two committed implementations of the same quantity disagree. A reader auditing the gate would be checking a quantity the label does not describe. CONFIRMED at MINOR.

**Severity:** MINOR (the gate's conclusion is very likely unaffected; the defect is in what the reported number measures).

**Proposed adjudication:** fix — either re-measure the null cell with `want_index` set to the per-replication argmax, matching the suite, or relabel the reported quantity as "false-positive rate for separating the ordering step specifically" and state that it is a lower bound on the rule's overall false-positive rate.

---

### F-09 — Two ledger values are labeled "bias" in the manuscript when they are mean estimates, making the sentence read against its own conclusion
**Pass:** 6 (interpretation overreach) / presentation
**Location:** `t1_theorem_checks.ols_vs_yw` → JSON keys `ols_mean` / `yw_mean`; manuscript §6.3, TBL-2 caption, Appendix B table

**Claim as written.** §6.3: *"The estimator choice is justified by the supplementary OLS-vs-YW comparison (OLS bias 0.8170991417292447 vs Yule-Walker bias 0.7817918714625745; OLS less biased: true)."* Repeated in the TBL-2 caption and the Appendix B verification table.

**What I found.** The underlying computation is correct. The values are **mean estimates** at true phi = 0.95, n = 40, 200 histories. Actual biases are |0.8171 − 0.95| = 0.1329 (OLS) and |0.7818 − 0.95| = 0.1682 (YW), so OLS is indeed the less biased of the two and `ols_less_biased: true` is right. But as printed — "OLS bias 0.817 vs Yule-Walker bias 0.782" — a reader computes that the larger number is OLS's and concludes the opposite of the stated verdict. The JSON keys are `ols_mean` and `yw_mean`; only the manuscript prose mislabels them.

**Second-review test.** Checked the token source: the word "bias" is in the hand-written prose surrounding the tokens, not in the ledger or renderer, so this is a one-word prose fix in three places and touches no number. CONFIRMED.

**Severity:** LOAD-BEARING by the stated criterion (the values are ledger rows, `LB-E1-ols-bias` family, and the sentence justifies a pre-registered estimator choice), but the defect is purely nominal — no computation, verdict, or downstream result moves.

**Proposed adjudication:** fix — replace "bias" with "mean estimate (true phi 0.95, n = 40)" in §6.3, the TBL-2 caption, and Appendix B. Consider renaming the ledger ids to match, since the current names invite the same error again.

---

### F-10 — "The primary specification" denotes different specifications in §6.3 and §7.1
**Pass:** 6 (interpretation overreach) / presentation
**Location:** manuscript §5.3, §5.4, §7.1

**What I found.** §5.4 makes SPEC-M the specification of the primary falsifier. §7.1 then writes: *"manufacturing-aggregate mean rho 1.0644 (SPEC-R) and 0.8034 (SPEC-M). Under the primary specification the boundary is not a line these sectors occasionally cross; it is a line they operate above."* The sentence is only true of SPEC-R, so "the primary specification" here means the E5 ranking primary, while thirty lines earlier the same phrase meant SPEC-M. A reader tracking which spec carries which claim — which this paper asks them to do repeatedly — is given a term that switches referent.

**Second-review test.** §5.3 names them "the monitoring specification" and "the ranking specification" and never designates either globally "primary," so neither reading is anchored. CONFIRMED as genuine ambiguity rather than a reader error.

**Severity:** MINOR.

**Proposed adjudication:** fix — say "SPEC-R" rather than "the primary specification" in §7.1, and reserve "primary" for the E1 falsifier throughout.

---

## WITHDRAWN

Recorded because the withdrawals are evidence the passes applied a test rather than accumulating volume.

- **W-01 — E1 drops missing observations without re-indexing, so `[:n_min]` may align sectors by position rather than by date.** `load_series` filters `if v != "."` and returns a bare array with no date index, and `run_panel` truncates every sector to a common `n_min` from the *start*. If any member series had an embedded gap or a later start date, index *i* would be a different month in different sectors, and the joint block bootstrap's "one index set applied to every oscillating sector" would preserve nothing. **Withdrawn:** I could not establish the premise. `pull.py` (which holds `SECTOR_MAP`) is not in the package, and E14's stricter reader — which hard-fails on a non-numeric observation and is applied to a partly overlapping FRED set — completes on the real store, indicating FRED gaps are not present in these files. Without the store or `pull.py` this is unverifiable from inside the package. Flagged here as the single highest-value thing for the author to confirm rather than asserted as a defect.
- **W-02 — E1's joint bootstrap p is invalid because the panel is selected on full-sample information.** Withdrawn on focused re-examination; selection is a function of `rho` only, the outcome is what the bootstrap scrambles, so the null is not contaminated. The residual disclosure issue is retained as F-06.
- **W-03 — E14's contrast is a winner's-curse statistic, since `kstar = argmax(pe["step"])` is chosen from the same sample used to build the resample distribution.** Withdrawn: the selection bias is measured empirically rather than assumed away — the false-positive characterization applies the identical select-then-contrast procedure to null chains, so the bias is inside the measured rate. The separate labeling defect in how that rate is measured is F-08.
- **W-04 — E2 leaks, because the crisis estimation window (2008–2009) sits inside the realized outcome window (2007–2010).** Withdrawn: disclosed verbatim in §6.1 — *"the crisis estimation window is contemporaneous with part of the realized window - and is never an out-of-sample prediction."* Correctly scoped by L-06.
- **W-05 — E6 mislabels its rolling `rho` by dating a trailing-60 window to a month it does not contain.** Withdrawn: `y[t - ROLL_WIN:t]` excludes index `t`, so the value dated to month `t` uses data through `t−1`. Conservative, not leaky. DESIGN 195 states the intent explicitly.
- **W-06 — E14's telescoping identity is reported as a passed consistency check.** Withdrawn: §7.1 and §5.6 both state at length that it is an algebraic identity that cannot fail and carries no information, and the code comment (DESIGN 20.4) says the same. This is handled better than the rule requires.
- **W-07 — E6's REFUTE verdict is suppressed in favor of a softer reading.** Withdrawn: §8.2 reports REFUTE explicitly and alongside, and the reclassification to non-severe is argued from the instrument's inability to fire in either direction rather than from the result's direction. This is correct v1.9.7 handling.
- **W-08 — Ledger rows without a `json_path` bypass the mechanical tie.** Withdrawn: all 21 are `derived`, and re-executing `build_claims.DERIVED` against the committed outputs reproduces every one exactly.
- **W-09 — OUTLINE's ARG-18/24/25 cite sections 6.4/8.1/8.2 that hold different content in the manuscript.** Withdrawn: these are stale cross-references inside the outline's own recharacterization notes; the outline's section column is correct throughout and no manuscript content is missing.

---

## Pass-by-pass summary

1. **Look-ahead** — one finding (F-06): per-observation construction is clean; sector selection is full-sample and the "out-of-sample" label at panel level is not earned. E6's dating convention checked and clean (W-05).
2. **Index/row alignment** — no confirmed finding. E14 intersects on levels before differencing and asserts the realized n; E6 aligns by an explicit month dictionary. One unresolvable premise recorded at W-01 as the top author-verification item.
3. **Statistical inference validity** — two findings (F-07, F-08). E14's own contrast-rule disclosure is complete and honest, and the cure is correctly targeted; the same error is uncured in E2's component bake-off.
4. **Does the spec test the thesis** — two findings (F-04, F-05). The falsifier tests the intensity ratio, not the compound bound, and its detector operates below the paper's declared data floor.
5. **Experiment classification** — **no findings.** This is the paper's strongest pass. Saturating metrics are flagged verdict-invalid (E5 share-above, E14 pre-registered rule), the unadjudicable capacity test is reported as inconclusive rather than negative, INCONCLUSIVEs carry measured detection probability (0.00 / 0.93 / 0.35 / 1.00), and the one uncharacterized cell — the durable-goods arm — says so rather than borrowing a neighbor's power figure.
6. **Interpretation overreach** — three findings (F-03, F-09, F-10). Elsewhere the Abstract and Conclusion track the body closely, including on the withdrawals and the reactive monitor.
7. **Is the gap claim real** — **no findings.** Section 2 survives contact with the literature as described. The i.i.d.-demand distinction is stated precisely and confined to the foundational analytical results rather than the tradition; Li-Dörfler and Leng et al. are differentiated on object rather than dismissed; explicit non-novelty is conceded for the adaptation-speed/transient-quality tradeoff and for persistence-driven amplification; the Warburton-Disney Lambert W overlap is characterized as shared apparatus rather than shared content; the Osadchiy rho-notation collision is pre-empted. Novelty is claimed for the combination and no broader.
8. **Completeness** — three findings (F-01 TBL-A component, F-02, F-03). Mechanically: 506/506 ledger rows tie to outputs, renderer reproduces byte-identically, 73/73 citations present and cited with zero orphans, all S-/L-/C-/TBL-/EQ-/THM- nodes present.
9. **Proof rigor** — **no findings.** Appendix G is the most careful part of the package. G.0's Remark states plainly that the sketch's per-step inequality is false for general matrices and scopes it to A4; G.1 supplies the matrix-general bound with the correct constant; G.2 explicitly retracts the v0.1 global gain-monotonicity step as FALSE and rebuilds on G.1b, which is itself honestly labeled NUMERICALLY VERIFIED rather than proved and flagged for this pass; G.3 supplies the interiority condition (C) the source lacked and derives the Lambert W form with the parameter bundle made explicit; G.4 corrects the source's sign and states the total derivative including the indirect channel; G.6 is a Proposition with all three approximations labeled and the `2pW` inflation named as a retained modeling constant rather than a derived quantity. I found no step that silently assumes what a scope condition excludes. G.1b's open analytic proof is disclosed, not concealed, and the theorem's scope is correctly stated as the verified surface.
10. **Methods-code fidelity** — one finding (F-01), **pass incomplete.** E1/E2/E3/E4/E6/E14 prose matches the committed operators on windows, transforms, samples, bootstrap constructions, and seeds. E5-monitor, E7, E9, E10, E11, E12 and `analysis/suites/` were not reached; §5.7's paired-design and seed-recording claims are verified for E4 and E14 only, and F-01 shows that one of the four Appendix F studies does not match that prose.

---

## Overall assessment

This is an unusually well-instrumented package, and the mechanical layer holds up under independent re-execution: the ledger ties to the committed outputs on all 506 rows, the renderer reproduces byte-identically, and the citation and node ties are complete. The passes that most often produce findings in empirical work — experiment classification, prior-art positioning, and proof rigor — came back clean, and not vacuously: the paper flags its own saturating metrics as verdict-invalid, reports measured detection probability for its inconclusive results, retracts a false proof step in G.2 rather than papering over it, and discloses two of its own process failures in the AI-assistance section. The confirmed findings cluster in a different and more specific place: **the manuscript's description of its own experiments is less accurate than the experiments themselves.** E8 is an analysis of the source's committed records described in Methods as a run (F-01) and its inputs are absent from TBL-A; a DESIGN-mandated robustness leg for E6 was computed, committed, and then not reported, and it inverts the sign of the claim it bears on (F-03); the falsifier's detector operates below the paper's own declared data floor (F-04) and is rank-invariant to the exponent that is the paper's central theoretical claim (F-05); and one uncured instance of exactly the contrast error the paper discloses and cures elsewhere sits in E2's verdict rule (F-07). None of these overturn the theorem, and none show a number to be wrong — every figure I could recompute recomputed. What they show is that four load-bearing sentences describe operators that differ from the committed code, and that the paper's own stated commitments (report both specs; the registry governs TBL-A; S-4 is a scope condition not a preference) are the standard several of them fail against. Four of the ten findings are LOAD-BEARING by the prompt's criterion, so a second round is triggered; I expect most to resolve as disclosure fixes rather than re-runs, with F-04 the most likely to be a legitimate rebut-with-reason and W-01 the one item that needs author-side data I do not have.

**Caveat on coverage, stated so it cannot be mistaken for a clean pass:** Pass 10 did not reach E5-monitor, E7, E9, E10, E11, E12, or `analysis/suites/`. Those scripts are unreviewed for methods-code fidelity, and the "no findings" results above should not be read as covering them.


Continuing Pass 10 on the scripts I hadn't reached. Reading them now.Pass 10 is now complete. Eight further findings, all verified against the committed artifacts.

---

# Adversarial Review Findings — "The Escalation Cost" (Phase 5a) — ADDENDUM

**Continuation of the same review.** This addendum completes Pass 10 against the scripts I had not reached (`e5_instability_ranking.py`, `e5_monitor_tbl4.py`, `e7_chain_sweep.py`, `e9_hysteresis.py`, `e10_sovereign.py`, `e11_ui.py`, `e12_nonstationarity.py`) and revises the pass summary and overall assessment accordingly. Findings continue the F-nn sequence. Nothing in the first delivery is retracted.

---

## CONFIRMED FINDINGS (continued)

### F-11 — The replacement ranking key saturates at the floor under SPEC-M; the reported CHIPS rank of #10 is a sort artifact of the frozen member map
**Pass:** 5 (experiment classification), with a Pass 6 component
**Location:** `analysis/e5_instability_ranking.py` `sector_rho_stats` / `rank_under`; `DESIGN.md` amendment 2026-07-13 (lines 185–187); manuscript §5.5, §8.1, TBL-4 caption, C-05

**Claim as written.** The DESIGN amendment diagnoses the original key's failure precisely: under SPEC-R, *"% months rho > 1 SATURATES - the top six sectors… all read 100.0%, a six-way tie at the ceiling. A saturated key carries ZERO ordering information among the tied sectors, so the emitted ranks (#1-#6) were tiebreak/sort artifacts, not measurements."* The replacement, mean exceedance, was chosen *"SOLELY for having dynamic range (non-saturation)."* §5.5 tells the reader the fix worked: the old key *"was found to saturate at its ceiling and tie the leaders,"* and the new key *"was chosen for dynamic range."*

**What I found.** Mean exceedance is `mean(max(rho − 1, 0))`, which floors at exactly zero for any sector whose rolling rho never exceeds one. Under SPEC-M that is eight of seventeen sectors:

| SPEC-M rank | sector | mean exceedance |
|---|---|---|
| 9 | MRTSIR441USS | 1.9797904794413695e-05 |
| **10** | **A34SIS** | **0.0** |
| 11 | A35SIS | 0.0 |
| 12 | R4232IM163SCEN | 0.0 |
| 13 | R4233IM163SCEN | 0.0 |
| 14 | R4234IM163SCEN | 0.0 |
| 15 | R4236IM163SCEN | 0.0 |
| 16 | MRTSIR444USS | 0.0 |
| 17 | MRTSIR452USS | 0.0 |

`rank_under` sorts with `rows.sort(key=lambda r: r["mean_exceedance"], reverse=True)`. Python's sort is stable, so ties retain input order, and input order is `pull.SECTOR_MAP` member order. I verified the prediction: the eight zero-valued sectors appear at ranks 10–17 in exactly their member-map sequence (A34SIS 4th in the map, A35SIS 5th, R4232 9th, R4233 10th, R4234 11th, R4236 12th, MRTSIR444 16th, MRTSIR452 17th). **A34SIS's rank of #10 is determined by its position in the frozen member map and by nothing measured.**

The instrument fixed the ceiling tie and reproduced an identical tie at the floor. §5.5 and the TBL-4 caption disclose only the ceiling saturation ("Share is the fraction of months rho > 1 under SPEC-R - near one for most sectors, the saturation record"); the floor saturation is nowhere in the manuscript, and TBL-4 prints SPEC-R exceedance only, so a reader cannot see the eight-way zero tie.

The substantive consequence is for §8.1's verbal reading and C-05. Under SPEC-M, A34SIS's measured exceedance is not "low" — it is *zero*, tied with seven others, i.e. the sector never crosses the boundary at all. This is the same picture E1 gives (`frac_months_above_1 = 0.0`) and E6 gives (all SPEC-M bins 0.76–0.88, F-03). §8.1 nonetheless says the CHIPS sectors *"sit in the top-instability cluster,"* and C-05 says they are *"among the more structurally unstable."* Neither holds under the robustness specification, where one of the two sectors is in an eight-way tie at zero.

**Second-review test — one component withdrawn.** I initially wrote this as invalidating the DROPPED verdict, on the grounds that `both_topquartile_M` is decided against a rank produced by a tiebreak. That is wrong and I withdraw it: A34SIS's exceedance is exactly 0 and nine sectors are *strictly* above it, so its rank is ≥ 10 under any tiebreak whatever, and the top-quartile cut is 5. **The DROPPED verdict is robust.** What survives is that a ledgered number (`LB-E5-chips-rank-M-A34SIS = 10`) is reported as a measurement when it is a sort artifact of exactly the kind the amendment was written to eliminate, and that the verbal characterization built on it is unsupported under that spec. CONFIRMED at that scope.

**Severity:** LOAD-BEARING (ledger row; C-05; §8.1's reported ranks).

**Proposed adjudication:** fix — report A34SIS's SPEC-M position as "tied last, mean exceedance 0.0 (eight-way tie)" rather than "#10", disclose the floor saturation alongside the ceiling saturation in §5.5 and the TBL-4 caption, and condition C-05 and §8.1 on SPEC-R. The verdict itself needs no change and the honest headline survives intact.

---

### F-12 — Every ledgered monitoring number uses the unsustained crossing definition; Methods states the sustained one
**Pass:** 10 (methods-code fidelity)
**Location:** `analysis/e5_monitor_tbl4.py` `episode_analysis` / `run_monitoring`; manuscript §5.5, §7.4, TBL-4 episode columns

**Claim as written.** §5.5: *"The monitoring record (Section 7.4) applies the same rolling construction at both specifications across the full sample, **marks upward boundary crossings as a below-to-above transition sustained three months**, and reports status and first crossing within twenty-four months either side of each episode onset."*

**What I found.** The code computes both definitions and reports the unsustained one everywhere that matters:

```python
crossings = [m for m in range(w0, w1 + 1) if above[m] and (m > 0 and not above[m - 1])]
sustained = [m for m in crossings if m + SUSTAIN_MONTHS <= len(rr) and bool(above[m:m + SUSTAIN_MONTHS].all())]
...
status = "crossing" if crossings else (...)          # NOT sustained
first = crossings[0] if crossings else None          # NOT sustained
```

`summary` then derives `n_crossing`, `n_crossing_before_onset`, `mfg_status`, and `mfg_first_crossing` from `status` and `first`. The `sustained_crossing` field is computed, carried in the JSON, and consumed by **no ledger row and no sentence in the paper** — I checked all ten `LB-E5-monitor-*` rows.

The two definitions diverge materially. Under SPEC-M:

| quantity | as reported (unsustained) | under the definition §5.5 states |
|---|---|---|
| GFC crossings in window | 6 | 5 (R4238's 2009-02 does not sustain) |
| COVID crossings in window | 8 | 2 (six are one-to-two-month blips) |
| COVID crossings preceding onset | 2 | **0** |
| mfg aggregate, COVID first crossing | 2020-02-01 | 2020-04-01 |

**§7.4's dated claim is the one that moves.** As written: *"Around the 2020-03 onset, 8 sectors crossed, of which 2 nominally preceded the onset by one to two months."* Those two are AMTMIS (first 2020-02) and AMDMIS (first 2020-01). Under the sustained definition both become 2020-04 — *after* the onset. So under the rule §5.5 announces, there are zero pre-onset crossings at COVID as well as at the GFC.

**Second-review test.** I checked DESIGN 195, which defines `SUSTAINED CROSSING` and the four-valued `STATUS` as *separate* fields and does not require status to be sustained. **The code matches DESIGN.** The defect is confined to the manuscript prose, which describes an operator the code does not run. I also note the direction: the sustained definition *strengthens* the paper's own conclusion that the monitor is purely reactive, so this error runs against the author's interest — which is worth recording but does not make the prose accurate. CONFIRMED.

**Severity:** LOAD-BEARING (four ledger rows; a dated claim in §7.4; TBL-4's COVID first-crossing dates for six sectors).

**Proposed adjudication:** fix — either correct §5.5 to describe the unsustained definition actually used and note that `sustained_crossing` is carried in the artifact, or promote the sustained figures to the reported ones. The second is the stronger paper: it retires the "2 nominally preceded" hedge entirely and lets §7.4 say zero pre-onset crossings at both onsets.

---

### F-13 — §5.7 states the chain-length grid ran at fifty seeds; it ran at 250
**Pass:** 10 (methods-code fidelity)
**Location:** `analysis/e7_chain_sweep.py` `N_SEEDS = 250`; `e7_chain_sweep.json` `spec.n_seeds = 250`; manuscript §5.7 vs §7.5 vs TBL-7 Panel B

**What I found.** §5.7: *"The chain-length study reports its full grid - three chain lengths by three capacity levels by four demand environments, **at fifty seeds** - as the experiment rather than as a search."* The committed spec is `n_seeds: 250`, `seed_start: 3000`; fifty is the *source's* count (`SOURCE_N_SEEDS = 50`, seeds 3000–3049). The same manuscript contradicts §5.7 twice: §7.5 says *"re-run at five times the seed count,"* and Panel B is headed *"Ours (250 seeds) | Source (50 seeds)."*

**Second-review test.** I checked whether "at fifty seeds" could be read as describing the source's grid — the sentence's subject is "The chain-length study," which throughout §5.7 and Appendix F denotes this paper's E7. It cannot be read the other way without contradicting §7.5. CONFIRMED.

**Severity:** MINOR (a single wrong number in Methods prose; every reported cell is correct and the seed count is stated correctly in two other places).

**Proposed adjudication:** fix — "at 250 seeds, five times the source's fifty."

---

### F-14 — Panel B's "source inside our CI" compares nested samples: the source's 50 seeds are a subset of our 250
**Pass:** 3 (statistical inference validity)
**Location:** `e7_chain_sweep.py` `SEED_START = 3000`, `SOURCE_SEED_START, SOURCE_N_SEEDS = 3000, 50`; manuscript TBL-7 Panel B

**Claim as written.** Panel B: *"resolution vs the source's 50-seed record (ar1_high x 2.4x; a regression check, not a calibration),"* with a `Source inside our CI` column reading `false` for all three cells.

**What I found.** Our seeds run 3000–3249; the source's run 3000–3049. The engine is vendored byte-identical and MD5-asserted, so seeds 3000–3049 in our run reproduce the source's trials — `SOURCES.md` line 98 confirms this directly (*"recomputing… from these raw records returns v16's +0.44/+0.14/-0.14 to three decimals"*). **The source's sample is a 20% nested subsample of ours, not an independent one.** A `false` in that column therefore does not mean two independent estimates disagree; it means the 200 seeds we added moved the mean away from the first 50, which is arithmetic rather than evidence. The two estimates are positively correlated by construction and a marginal-interval containment test is not the right comparison for them.

**Second-review test.** I weighed withdrawing this as harmless, since Panel B is explicitly labelled a check rather than a calibration and §7.5 draws only the defensible inference (that more than half the source's grid was unresolved at its seed count). That labelling does limit the damage. But the boolean is printed in a table a reader will read as "our result disagrees with theirs," and the nesting is not disclosed anywhere. CONFIRMED at MINOR.

**Severity:** MINOR.

**Proposed adjudication:** fix — one line in the Panel B caption stating that the source's fifty seeds are the first fifty of ours, so the comparison measures the contribution of the additional 200 seeds rather than agreement between independent runs.

---

### F-15 — E12's Leg A decision rule commits the contrast error the paper diagnoses and cures elsewhere
**Pass:** 3 (statistical inference validity — contrast rule)
**Location:** `analysis/e12_nonstationarity.py` `ci_disjoint_below` and `execute_decision_rule` condition (ii); manuscript §7.5, Appendix F Panel E

**What I found.** Condition (ii) of E12's frozen rule decides whether fixed-alpha damping beats the oracle and the OLS estimator at the claim locus by asking whether their **marginal 95% confidence intervals are disjoint**:

```python
def ci_disjoint_below(a_ci, b_ci):
    """True iff interval a sits entirely below interval b (conservative
    ordering: a < b resolved without paired SEs)."""
    return a_ci[1] < b_ci[0]
...
cond = (fx["sign"] == "benefit"
        and ci_disjoint_below(fx["ci"], orc["ci"])
        and ci_disjoint_below(fx["ci"], ols["ci"]))
```

The three variants are evaluated on the **same seed set** in the same paired design (`seed_start` shared across variants), so these are exactly the "quantities estimated from a COMMON resample… decided by whether their MARGINAL intervals overlap" the v1.9.11 rule names. The docstring identifies the discarded pairing itself — *"resolved without paired SEs"* — and rationalizes it as conservative.

The package contains the correct statistic for the identical comparison. Leg B's `paired_contrast` computes `fixed_minus_oracle` and `fixed_minus_ols` per seed with `resolved = abs(mean) > Z95 * se`. So both the wrong and the right statistic for the same question are committed, and Panel E prints both sets of numbers adjacently without distinguishing their construction: *"fixed-alpha at the long-chain locus -0.6928… / -1.1212…"* (Leg A, marginal intervals) then *"Paired 50-seed contrasts (leg B): fixed-vs-oracle -1.0688 / -1.5125; fixed-vs-OLS -0.8708 / -1.1970."*

**Second-review test — severity reduced, finding retained.** Two mitigations are real and I want them on the record. (i) The direction is conservative: disjoint marginal intervals is *harder* to satisfy than a paired test, so this construction cannot manufacture a false positive, unlike E14's pre-registered rule which could not fire at all. (ii) §7.5's headline sentence — the one that carries L-04 and S-8 — quotes the **Leg B paired numbers**, not the Leg A gate. So the paper's load-bearing claim rests on the correct statistic. What remains is that a conjunct of a reported verdict (`EXPECTED-CONFIRMED-RECIPE-LEVEL`) is decided by the prohibited construction, in a paper that devotes §5.6 and a full subsection of §7.1 to explaining why that construction is wrong. The prompt is explicit that this is a finding and not a style note. CONFIRMED.

**Severity:** LOAD-BEARING by the stated criterion (conjunct of a reported verdict), materially mitigated by (i) and (ii).

**Proposed adjudication:** rebut-with-reason or fix. The cheap fix is to replace condition (ii)'s `ci_disjoint_below` with the Leg B paired contrast, which already exists and already resolves in the same direction. If the author prefers to keep the frozen rule, the honest disclosure is a sentence in §5.7 or Appendix F noting that Leg A's ordering conjunct uses disjoint marginal intervals on a paired design, that this is conservative, and that the properly paired contrast is Leg B and is the one quoted in §7.5.

---

### F-16 — E10 computes a raw-levels persistence leg for every country and reports none of it, against an explicit Methods commitment
**Pass:** 8 (completeness) / 10
**Location:** `analysis/e10_sovereign.py`; `e10_sovereign.json` field `phi_raw_levels`; manuscript §5.2, §9.1, TBL-5

**Claim as written.** §5.2, in the passage that justifies estimating persistence in levels: *"Where unit-root concerns apply, results are reported on **both the level series and a stationary transformation**, and the boundary is visible in the results rather than hidden - the three sovereign countries whose detrended estimates come back above one (Section 9.1) are that boundary showing itself, not an anomaly."*

**What I found.** `phi_raw_levels` is computed and committed for all eighteen countries. TBL-5 and §9.1 report `phi (detrended)` only. Sovereign debt-to-GDP is the paper's own named example of where unit-root concerns apply — it is the case the §5.2 commitment was written for — and it is the one place the commitment is not honored.

The unreported leg is not neutral. On raw levels **four** countries come back explosive rather than three:

| country | phi (detrended, reported) | phi (raw levels, unreported) |
|---|---|---|
| Germany | 1.1313 | 1.1172 |
| Japan | 1.0348 | 1.0375 |
| Portugal | 1.0105 | 1.0146 |
| **USA** | 0.9794 | **1.0128** |

So §9.1's characterization — *"15 of 18 countries in a tight near-unit band"* and *"explosive {Germany, Japan, Portugal}"* — becomes 14 of 18 with the USA added, on the leg the paper promised to report.

**Second-review test.** The reading is WITHDRAWN either way, so no verdict moves and L-05 caps the section at suggestive. I nonetheless retain the finding at full weight, because the commitment in §5.2 is not decorative: it is the paper's answer to the most obvious methodological objection to its whole estimation strategy, and it is unmet in precisely the case that objection targets. Reporting the less favorable leg is what makes the answer credible. CONFIRMED.

**Severity:** LOAD-BEARING (an explicit stated Methods commitment, unmet; the unreported leg changes a reported count).

**Proposed adjudication:** fix — add the `phi_raw_levels` column to TBL-5 with the corresponding ledger rows, and state the 14-of-18 levels count alongside the 15-of-18 detrended count in §9.1.

---

### F-17 — "Statistically indistinguishable" in §9.2 has no statistic behind it anywhere in the package
**Pass:** 3 (statistical inference validity)
**Location:** `analysis/e11_ui.py` `pooled_ar1`; `e11_ui.json`; manuscript §9.2

**Claim as written.** §9.2: *"pooled GFC phi 0.7075797321455143 (n 371) sits far below the boundary corner 0.997992 and **is statistically indistinguishable from normal**."*

**What I found.** `pooled_ar1` returns `{"phi", "n_pairs"}` and nothing else — no standard error, no test statistic. I enumerated every key in `e11_ui.json`: `classification, date, decision, design_pin, experiment, i_normal_stable, ii_gfc_crosses_corner, jurisdictions_normal, n_pairs, phi, phi_normal, phi_star_corner, pooled_gfc, pooled_normal, pooled_normal_rho, reading, st`. No dispersion measure exists. None of the eleven `LB-E11-*` ledger rows carries an SE, a p-value, or a test outcome. The inferential claim is asserted, not computed.

This breaches a rule the project invokes by name elsewhere. COVERAGE.md line 99, withdrawing the chiplet compound-rho metric, reasons: *"Importing an uncomputed stability metric would contradict the v1.9.11 severity rule (severity is quantified, never asserted)."* The same rule applies to an uncomputed indistinguishability claim.

A related construction is worth flagging in the same breath: `normal = dq[(q < 2008Q1) | (q > 2009Q4)]` excludes only the GFC, so the "normal" baseline **includes the 2020 COVID unemployment-insurance shock** — the largest disturbance in the series. This does not affect the WITHDRAWN decision, which turns on the absolute threshold `pg["phi"] >= 0.997992`, but it is the comparator the unbacked "indistinguishable from normal" phrase points at.

**Second-review test.** The section is suggestive-only, WITHDRAWN, and bounded by L-05 and S-7, so nothing downstream depends on it. But the sentence makes a specific inferential assertion in a paper whose entire method is that such assertions are ledgered, and the phrase is doing rhetorical work — it is what converts "the number is low" into "the mechanism is absent." CONFIRMED at MINOR.

**Severity:** MINOR (not an Abstract/Conclusion claim and, precisely because it is unbacked, not a ledger row).

**Proposed adjudication:** fix — either compute and ledger a difference test, or replace the phrase with the descriptive statement the artifact supports: "sits at 0.708 against a normal-period 0.731, both far below the 0.998 boundary corner," and note the COVID-in-baseline construction.

---

### F-18 — "Sigma" denotes two different quantities in two committed scripts and is printed under one label in adjacent panels of the same table
**Pass:** 10 (methods-code fidelity) / presentation
**Location:** `e8_pricing.py` line 143 vs `e9_hysteresis.py` line 379; manuscript TBL-7 Panels C and D

**What I found.** Two definitions, same name:

```python
# e8_pricing.py
sigma = (abs(mean) / se if se else None)     # unsigned t-statistic
# e9_hysteresis.py
"sigma": float(d.mean() / se) if se > 0 else None    # signed t-statistic
```

Neither is a standard deviation. The manuscript prints both under the bare label "sigma" in adjacent panels of TBL-7: Panel C gives *"Cut side (mean, sigma): low-phi -581.3646581811907 (17.145693608921093),"* where a negative mean carries a positive "sigma"; Panel D's column header is *"Sticky environment (benefit, sigma)"* with entries such as *"-540.5837281160061 (-2.4340964614005594)"*, where the sign now tracks the mean. A reader encountering `8401.301149517853 (10.32833831781141)` under a header reading "(benefit, sigma)" will most naturally read the parenthetical as a dispersion, which it is not; and the sign convention flips between the two panels without notice.

**Second-review test.** Both computations are correct for what they are, and Panel C's `16.093436134350174 sigma` is used in a context ("verdict ASSERTED") where a t-statistic reading is the intended one. The defect is purely nominal — but it is the same class as F-09, where "bias" was printed for a mean estimate, and the two together suggest the label layer between the artifacts and the prose was not audited. CONFIRMED at MINOR.

**Severity:** MINOR.

**Proposed adjudication:** fix — label both as "t" or "effect / SE", state the sign convention once, and reconcile the signed/unsigned difference between the two scripts or note it.

---

## WITHDRAWN (continued)

- **W-10 — E5's DROPPED CHIPS verdict is decided by a tie-break artifact.** Withdrawn: A34SIS's SPEC-M exceedance is exactly 0 with nine sectors strictly above, so its rank is ≥10 under any tiebreak and the top-quartile cut is 5. The verdict is robust; only the reported rank number is an artifact (retained as F-11).
- **W-11 — E11's WITHDRAWN reading is unsafe because the "normal" baseline contains COVID.** Withdrawn: the gate is the absolute condition `pg["phi"] >= 0.997992`, not a comparison to normal, so the withdrawal stands regardless of the baseline's composition. The baseline issue survives only as it bears on the unbacked comparison phrase, folded into F-17.
- **W-12 — E10's single global linear detrend across 1870–2020 manufactures the three explosive estimates.** Withdrawn: the paper does not rely on those estimates; it reports the precondition failing, withdraws the reading, and names the failure as the boundary showing itself. The dual-implementation guard (`max_dual_impl_diff = 0.0`), the JST MD5 pin, and the consecutive-pairs-only AR(1) — which correctly handles the war-year gaps — are all sound. The unreported *levels* leg is a separate matter and is F-16.
- **W-13 — E12's `paradox_count` (oracle worse than OLS in 7 of 9 drift cells) rests on the marginal-interval construction of F-15.** Withdrawn: `e12_paradox_count` is computed from Leg B's `drift_paired_contrasts` with `resolved` from a paired SE, not from `ci_disjoint_below`. The paradox claim uses the correct statistic.
- **W-14 — E7 is presented as this paper's experiment when its engine is the source's vendored code.** Withdrawn: unlike E8 (F-01), this is disclosed. TBL-A carries the row (*"Source simulation sweep (9,000 trials; fixed in-house artifact)… E7 regression record; E12 leg B"*), and the script states the limit explicitly: *"It may NOT claim independent re-implementation."* §7.5's language ("re-run at five times the seed count") is consistent with a re-run of vendored code.

**Open item for the author, not raised as a finding.** E9 reports fidelity `TIER-EXACT, max relative diff 0.0` against the source's committed hysteresis artifact, and `SOURCES.md` line 97 describes E9 as re-implemented *"from specification."* A from-specification re-implementation reproducing four cells at exactly zero relative difference implies the re-implementation consumes the random stream in the same order as the source's code, which is a stronger correspondence than "from specification" usually delivers. I did not read `e9_hysteresis.py` closely enough to determine whether this is expected (shared seeds 2000–2019 plus a deliberately mirrored draw order) or whether it indicates closer derivation than the description implies. Worth one sentence of confirmation in the adjudication.

---

## Revised pass-by-pass summary

1. **Look-ahead** — one finding (F-06). Per-observation constructions clean across E1, E5-monitor, E6; sector selection is full-sample and the panel-level "out-of-sample" label is not earned.
2. **Index/row alignment** — no confirmed finding. E14 intersects on levels before differencing; E6 and E5-monitor align by explicit month dictionaries; E10 restricts to consecutive-year pairs, correctly handling the JST gaps; E11 uses consecutive-quarter pairs with within-jurisdiction demeaning. W-01 remains the one unresolvable premise.
3. **Statistical inference validity** — five findings (F-07, F-08, F-14, F-15, F-17). E14's own disclosure and cure are exemplary; the same error recurs uncured in E2's verdict conjunct and E12's Leg A gate, and two further comparisons (E7 Panel B nesting, E11 indistinguishability) are made without an adequate statistic.
4. **Does the spec test the thesis** — two findings (F-04, F-05).
5. **Experiment classification** — one finding (F-11), downgraded from my initial "no findings." The paper's handling of saturation, severity, and verdict-invalidity is genuinely strong — but the *replacement* instrument chosen to cure a ceiling saturation reproduces the identical defect at the floor under the robustness spec, undisclosed.
6. **Interpretation overreach** — three findings (F-03, F-09, F-10), with F-11 and F-16 contributing.
7. **Is the gap claim real** — **no findings.** Unchanged.
8. **Completeness** — five findings (F-01, F-02, F-03, F-16, and F-11's disclosure component). Mechanical ties all reproduce: 506/506 ledger rows, byte-identical render, 73/73 citations, all S-/L-/C-/TBL-/EQ-/THM- nodes.
9. **Proof rigor** — **no findings.** Unchanged; Appendix G remains the strongest part of the package.
10. **Methods-code fidelity** — **now complete.** Six findings (F-01, F-12, F-13, F-16, F-17, F-18). E1/E2/E3/E4/E6/E7/E10/E12/E14 operators match their prose on windows, transforms, samples, and seeds; the failures are concentrated in E5-monitor's crossing definition, E7's seed count, E8's provenance, E10's unreported leg, and the label layer between artifacts and prose.

---

## Revised overall assessment

Completing Pass 10 sharpens rather than changes the shape of the first assessment, and it strengthens the diagnosis. The mechanical layer holds: I re-derived all 506 ledger rows from the committed outputs, reproduced the rendered manuscript byte-for-byte, and found the citation and node ties complete — and across eighteen findings I did not find a single computed number that was wrong. Appendix G survives a close read with no logical gap, and its willingness to retract its own v0.1 step as FALSE and to carry Lemma G.1b as explicitly *numerically verified rather than proved* is the behaviour the archetype is supposed to produce. Section 2 survives contact with the literature it cites. What the completed pass confirms is that the package's weakness is consistently **descriptive rather than computational**: the manuscript's account of its own experiments drifts from the committed code at eight distinct points, and in every case the code is the more careful artifact. E8 is a re-analysis described as a run; E5's monitor reports unsustained crossings under a Methods sentence promising sustained ones, which is the difference between "two sectors nominally preceded the onset" and "none did"; E7's seed count is stated as fifty in one section and 250 in two others; E6's and E10's committed robustness legs exist, are mandated by DESIGN or by §5.2, and are absent from the tables; and the replacement ranking key that §5.5 presents as the cure for saturation saturates at the floor under the very spec it was supposed to be checked against. Alongside these sits a second pattern the review prompt asked me to hunt specifically: the contrast error the paper diagnoses at length for E14 and cures correctly there is left uncured in two other places (E2's verdict conjunct, E12's Leg A gate), in both cases where the paired machinery to fix it already exists in the same script. Seven of eighteen findings are LOAD-BEARING by the stated criterion, so a second round is triggered. My expectation is that most resolve as disclosure and prose fixes rather than re-runs — F-04 and F-15 are the two most likely to be legitimate rebut-with-reason, and F-12 and F-16 are the two most likely to change a reported number.

**Coverage now stated in full:** all ten passes ran to completion. The single item I could not resolve from inside the package is W-01 (whether any member series carries an embedded gap or a non-1992 start, which would make E1's positional `[:n_min]` truncation and its joint bootstrap misalign sectors by date); `pull.py` and the raw store are withheld by rule, so that one needs author-side confirmation. The E9 exact-reproduction question above is an open item, not a finding.
