# Corrections Log -- The Escalation Cost

Public, post-publication corrections log per the Research-to-Publication Standard (Phase 5c). Any error found in the published paper -- by the author, a reader, or a replicator -- is recorded here and handled in the open. Replications, counterexamples, and corrections are welcome: open an issue on this repository or email jae@laggingtruth.com.

Format per entry: **Date** | **Nature of the error** | **Who identified it** | **Change made** (and, where applicable, the affected `claims.lock` entries and the `verify.py` result after the change).

The paper's two registered forward predictions are scored in `PREDICTIONS.md`; if either resolves against the paper, the resolution is recorded there and mirrored here.

---

*No corrections to date. (Initialized 2026-07-30 in Phase-5c certification; public at the coordinated launch. Pre-publication defects -- including those found and fixed during the Phase-4 write-and-review cycle and the capped Phase-5a adversarial review, which the reviewer certified after a second delta-verification round -- are documented in `DECISIONS.md` and the `verification/` trail, not here; this log covers the published record from v1.0 onward.)*

---

## Known items carried forward to v1.1

Recorded here at initialization because they are known now, are disclosed in the published paper, and will be handled in the open rather than discovered later. Neither is an error in a reported number; both are code-level improvements deliberately declined for v1.0 because executing them would have changed certified statistics after certification.

- **SF-01 -- E1 evaluation-guard boundary.** The rolling evaluation's final point computes its forward mean over the eleven months remaining in the series rather than the documented twelve. The joint panel alignment removes that point for fourteen of seventeen sectors; it survives only as the last of 341 points in the three shortest series, one of which is regime-oscillating, contributing roughly one three-thousandth of the pooled falsifier evidence with no signed direction. Self-found during the Phase-5a review round and disclosed in the paper (Section 5.4) and in `REPLICATION.md`. The one-line guard correction (`t + 1 + FWD_WIN <= n`) is queued for v1.1, where the committed statistics are the reproduction target.
- **Date-keyed E1 panel join.** The panel alignment truncates every sector positionally to the shortest evaluation span. This is sound on the pinned store, where all seventeen series share a start month and carry no internal gaps, but it is sound because the data happens to be uniform rather than because the code enforces it. A date-keyed join -- the construction the paper's own echelon experiment already uses -- would make the property structural. Raised as a forward note by the Phase-5a reviewer and accepted as a v1.1 candidate.
