# A1 — Frequency invariance of the E1 rolling validation

**Status: PRE-REGISTRATION. Written before the analysis script exists and
before any quarterly result has been computed. Committing this file IS the
pre-registration.**

Robustness appendix to *The Escalation Cost*. Not a new paper: same theory,
same data, same estimator, one additional axis (sampling frequency). No new
claim about the world is made here — the only question is whether E1's
reading survives coarser sampling of the same series.

---

## 1. Why this exists

Every experiment in *The Escalation Cost* is monthly. The frequency is not
cosmetic: W is a look-back in **months**, bg is the share of the gap closed
**per month**, and rho is the spectral radius of a companion matrix whose
period is the sampling interval. A quarterly run of the same code is
therefore a different model, not the same model on less data.

This matters beyond tidiness. Public company filings report sales and
inventory **quarterly**. If — and only if — the reading survives quarterly
sampling, a firm-level study on SEC filings becomes possible: ~80-100
observations per firm, hundreds of firms, all public and independently
checkable. If the reading does not survive, that path closes and this
appendix says so.

**This appendix does not attempt the firm-level study.** It asks one
question of data already in the ESC store.

## 2. The question, stated as a falsifiable claim

Aggregate the 17-sector monthly inventory-to-sales panel to quarterly, run
E1's frozen pipeline on it, and compare against the published monthly result
(pooled mean Spearman +0.1505, p_panel 0.0090, 9 oscillating sectors,
verdict SUPPORT).

**H1 (attenuation-with-preservation).** The quarterly run preserves the sign
and the cross-sector ordering of the monthly run, at reduced magnitude.

Temporal aggregation of a flow variable is well studied: summing months into
quarters raises measured persistence toward 1 and induces a moving-average
component the AR(1) estimator does not model. The honest prior is therefore
**attenuated but rank-correlated**, not identical. A quarterly result that
matched the monthly one exactly would be more suspicious than one that
weakened.

## 3. Decision rule — FIXED BEFORE THE RUN

Let S_m be the per-sector Spearman coefficients from the published monthly
E1 (17 sectors), S_q the same from the quarterly run.

**PASS (frequency-robust)** iff ALL THREE hold:

1. **Sign.** Pooled mean Spearman across the quarterly oscillating set is
   **> 0**.
2. **Ordering.** Spearman rank correlation between S_m and S_q across all 17
   sectors is **>= +0.50**.
3. **Verdict.** The quarterly run returns **SUPPORT** under E1's own
   unmodified RULE B (>= 2 oscillating sectors, pooled mean > 0,
   one-sided joint block-bootstrap p < 0.01).

**PARTIAL** iff (1) and (2) hold but (3) does not — the ordering survives,
the significance does not. This is the outcome the aggregation literature
makes most likely, and it is reported as such, not upgraded.

**FAIL** iff (1) or (2) fails.

Interpretation, fixed in advance:
- PASS -> a quarterly firm-level study is scoped as its own pre-registered
  work. This appendix does not authorise any claim about firms.
- PARTIAL -> quarterly sampling preserves ordering but not detection power;
  any firm-level work must be framed as ranking, never as a per-firm verdict.
- FAIL -> the quarterly path is closed. Recorded and published as such.

## 4. Method — FROZEN

**Input.** The same hashed FRED store used by E1
(`data/pull.py` SECTOR_MAP, 17 `role="member"` series). No new download. The
store hash is recorded in the output JSON.

**Aggregation.** Inventory-to-sales is a **ratio**, not a flow, so it is not
summed. The quarterly value is the **calendar-quarter mean of its three
monthly values** (Jan-Mar, Apr-Jun, Jul-Sep, Oct-Dec). Quarters with fewer
than 3 available months are dropped from the head/tail only. This choice is
made now, before seeing any result; the alternative (end-of-quarter sampling)
is NOT run, to avoid a two-specification search.

**Constants.** Every month-denominated constant in `e1_rolling_validation.py`
is divided by 3 and rounded to the nearest integer, preserving the same real
time spans:

| constant | monthly | quarterly | real span |
|---|---|---|---|
| BASE_WIN | 60 | 20 | 5 years |
| RECENT_WIN | 12 | 4 | 1 year |
| FWD_WIN | 12 | 4 | 1 year |
| BLOCK | 24 | 8 | 2 years |
| W_SPEC | 8 | 3 | ~2 quarters vs 8 months (see note) |

**Note on W, stated plainly because it is the weakest link.** SPEC-M's W=8
months has no exact quarterly equivalent; 8/3 = 2.67 rounds to 3. The run is
therefore executed at **W=3 as primary**, with **W=2 and W=4 reported as a
sensitivity strip in the same output**. The decision rule is evaluated on
W=3 only. The strip exists so a reader can see whether the verdict hinges on
the rounding; it is not a search for a favourable W.

bg = 0.05, kappa = 0.75, B = 2000, seed = 20260713 are unchanged.

**Estimator.** `run_panel()` from `e1_rolling_validation.py` is imported and
called **verbatim** — not copied, not reimplemented — with the module-level
constants monkeypatched to the quarterly values before the call. This
guarantees the two runs differ only in input and constants.

**Comparison.** Per-sector S_q is joined to the published monthly S_m by
sector id from `analysis/outputs/e1_rolling_validation.json`.

## 5. Known confounds and limits, recorded before the run

1. **Aggregation bias is expected, not a defect.** Averaging three months
   raises measured AR(1) persistence. A higher quarterly phi is a property
   of the transform, not evidence of anything about the world.
2. **n falls by ~3x.** 341 monthly observations become ~113 quarterly; after
   a 20-quarter base window and 4-quarter forward window, usable pairs per
   sector fall to roughly 90. The bootstrap has correspondingly less power.
   A PARTIAL outcome driven purely by lost power is the most likely single
   result and must not be reported as evidence against the theory.
3. **Classification may move.** Sectors sit near the rho=1 boundary; the
   oscillating / never-crossing / chronic split is computed fresh on the
   quarterly series and may not match the monthly split. Both classifications
   are reported side by side. The monthly classification is NOT imposed on
   the quarterly run.
4. **This tests the transform, not a new population.** All 17 series are the
   same national aggregates. Nothing here says anything about a single firm
   or a single business — that is the pilot's question and the (possible)
   firm-level study's question.

## 6. Outputs

`analysis/outputs/a1_frequency_invariance.json` containing: per-sector S_m,
S_q, both classifications, pooled means, p_panel, the three decision-rule
components with PASS/PARTIAL/FAIL, the W sensitivity strip, n_obs at both
frequencies, the store hash, and the seed.

A short results note is appended to this file after the run — **appended,
never rewritten**. If the result is FAIL, it is recorded here and in
DECISIONS.md with the same prominence as a pass.

## 7. What this appendix will never claim

That the method works on quarterly firm data; that a public company can be
graded from filings; that the pilot is unnecessary. It answers one question:
does E1's reading survive when the same series is sampled three times more
coarsely.
