# Forward Predictions -- The Escalation Cost

**The Escalation Cost: Intensity, Duration, and the Growing Damage of Regime Change** (see the paper, Section 11, "Forward Prediction: Self-Service Diagnostic"). This file is the dated public registration of the paper's two standing forward predictions. The git commit that adds this file is the immutable public registration timestamp; the public release accompanies the coordinated launch. Live tracking is maintained at www.LaggingTruth.com.

- **Registered:** 2026-07-24 (registration date carried in the paper's committed ledger; this file's repo commit is the public timestamp).
- **Trigger:** event-triggered -- the next NBER-dated US recession onset after registration. Not deadline-bound.
- **Data:** public series only -- the monthly US inventory-to-sales series used throughout the paper (the seventeen-sector panel documented in Appendix A, retrieved from FRED) for Prediction B; NBER business-cycle dates (nber.org) for the trigger and windows; for Prediction A, whatever demand series the firm applying the diagnostic already holds.
- **Lock / resolution:** each prediction resolves once, on the first finalized data release covering its window, so later revisions cannot change the verdict. Every protocol constant below is a ledger row emitted by the committed registration generator and byte-verified against it on every verification run -- a registration whose terms can be quietly edited afterwards is not a registration.
- **Horizon:** if no qualifying trigger occurs before **2031-07-31**, the predictions are untestable and carry forward, re-registered and dated.
- **Status:** OPEN at registration.

## Why these are registered

Every other check in this paper -- the machine-checked claim ledger, the computation-integrity review, the verified proofs, the capped adversarial read -- is a check the author commissioned and could in principle have shaped. A dated claim about events that have not yet happened is the one validator that routes around both the author and the reviewer, because the world scores it and neither party gets a say. That is why the constants below are ledgered rather than typed.

## PREDICTION A -- The Self-Service Diagnostic

Carried from the pinned source, locked April 2026; restated and re-registered at this rebuild's commit.

**Claim.** Any firm can compute the closed-loop spectral radius rho from three quantities it already holds -- its estimated demand persistence phi (estimator `ols_ar1_intercept`, the paper's pre-registered choice, Section 6.3), its measurement window W, and its feedback gain -- via the companion-matrix construction of EQ-1. Above the threshold **1.0**, the firm's response to its next demand shock AMPLIFIES (bullwhip); below it, the response DECAYS.

- **Calculator.** A public implementation is at LaggingTruth.com/diagnostic.
- **FALSIFIED** by systematic decay in above-threshold systems, or systematic amplification in below-threshold systems, under the stated computation.
- **Weight.** Prediction A is the standing engineering claim: it is what makes the theorem usable by someone who never reads the proof.

## PREDICTION B -- The Sector-Level Two-Class Bet

New at this rebuild; registered at publication.

**Claim.** At the trigger event, the flagged ("oscillating") class shows amplifying inventory/sales responses **exceeding** the never-crossing class, under the registered metric and test below.

The paper's committed rolling construction (Section 6.3) partitions the seventeen-sector panel into **9 boundary-crossing** and **8 never-crossing** sectors. The class lists are extracted mechanically from the committed output and registered verbatim, exactly as the ledger emits them:

```
flagged:        A31SIS,A36SIS,AMDMIS,AMNMIS,AMTMIS,MRTSIR441USS,R4231IM163SCEN,R4238IM163SCEN,R423IRM163SCEN
never-crossing: A34SIS,A35SIS,MRTSIR444USS,MRTSIR452USS,R4232IM163SCEN,R4233IM163SCEN,R4234IM163SCEN,R4236IM163SCEN
```

Membership is also public in the paper's Table TBL-2, so both classes can be read off before any trigger occurs rather than assembled afterwards. The classification was fixed by an earlier experiment and is reproduced from that experiment's committed output, not re-derived for this registration.

**Honesty note, registered as part of the claim.** Under this committed construction the CHIPS-dependent computers/electronics sector sits in the NEVER-CROSSING class while wholesale machinery sits in the flagged class. An earlier informal sketch that named both CHIPS sectors as flagged is superseded by the committed classification, and the specification-sensitivity of such flags is itself one of this paper's findings (Section 8.1). The exposure is genuinely two-sided: the never-crossing class is non-empty and includes a CHIPS-dependent sector.

### Protocol (every degree of freedom fixed in advance)

- **Trigger:** next NBER-dated US recession onset after registration.
- **Metric:** peak absolute deviation of log inventory/sales from its pre-onset baseline mean, within 24 months of onset, normalized by the pre-onset 60-month baseline standard deviation, per sector, from the same public monthly series the paper uses (Appendix A).
- **Test:** one-sided Mann-Whitney, oscillating > never-crossing, at alpha 0.05.

Three choices with their reasons on the record. The metric is normalized by each sector's own pre-onset variability rather than compared in raw units, because sectors differ by an order of magnitude in how much their inventory ratios ordinarily move and an unnormalized comparison would rank them by volatility rather than by the effect the prediction is about. The test is rank-based rather than parametric, because at class sizes in single digits no distributional assumption is credible and a rank test needs none. The onset date is taken from an external authority rather than chosen by inspection, which removes the degree of freedom most easily abused after the fact.

### Resolution

- **CONFIRMED** if the one-sided Mann-Whitney test rejects at alpha 0.05 in the predicted direction.
- **FALSIFIED** if, at the trigger event, the flagged class does NOT exceed the never-crossing class under the registered metric and test.
- **UNTESTABLE** (carries forward, re-registered and dated) if no qualifying trigger occurs before **2031-07-31**.

**Two outcomes are explicitly NOT falsifications**, stated now so the boundary cannot be redrawn later: a trigger event in which both classes deviate substantially is not a falsification provided the ordering holds, and a trigger event whose data are not yet finalized at the scoring window does not resolve the prediction -- it waits for the first finalized release covering the window. See the paper, Section 11.4, for the full statement.

## Step-by-step replication protocol (reader-runnable)

Anyone can reproduce the verdict from public data.

1. **Identify the trigger.** Take the next NBER-dated US recession onset after 2026-07-24 (nber.org).
2. **Pull the series.** Retrieve the seventeen monthly inventory-to-sales series listed in the paper's Appendix A from FRED, through 24 months past the onset, on the first finalized release covering that window.
3. **Compute the metric.** For each sector: take log inventory/sales; compute the pre-onset 60-month baseline mean and standard deviation ending at onset; find the peak absolute deviation from that baseline mean within 24 months of onset; divide by the baseline standard deviation.
4. **Split by the registered classes.** Use the two lists above verbatim -- 9 flagged, 8 never-crossing.
5. **Test.** One-sided Mann-Whitney, flagged > never-crossing, alpha 0.05.
6. **Record.** Enter the dated verdict below.

## Scored verdicts

*None to date. No qualifying trigger has occurred since registration.*
