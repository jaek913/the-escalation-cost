# The Escalation Cost

**Intensity, Duration, and the Growing Damage of Regime Change**

Author: Jae Kim (jae@laggingtruth.com, ORCID 0009-0005-3260-7880)

A work-in-progress research paper produced under the Lagging Truth Research-to-Publication
Standard. Posted as a pre-print: comments welcome, refutable by anyone. The data dictionary,
code, claims ledger, and adversarial-review transcript are public so that every quantitative
claim can be independently reproduced.

## What this paper argues

When a backward-looking trailing average of window W drives a feedback policy on a persistent
variable, and that variable's persistence steps up in a regime change, the estimator lags reality
for an adaptation time tau. During this blind period the closed-loop spectral radius rho can cross
the stability boundary undetected and deviations compound. The paper develops the Measurement
Damage Theorem: the damage accumulated during the blind period is bounded by D = (rho_2/rho_1)^tau
- an intensity factor (the spectral-radius ratio, how fast errors amplify) raised to a duration
(the adaptation time, how long the system measures blind), both functions of the same design
parameter W. A unique optimal window W* minimizes expected total cost by trading estimation
accuracy against adaptation speed, computable in closed form via the Lambert W function. The
single-loop stability criterion S(phi, W) * beta*gamma < pi^2/2 (proved in the companion "The
Measurement Trap") is the speed limit; the theorem quantifies the cost of operating near or above
it during transitions and yields an optimal safety factor k* below the limit.

The theorem is tested on 34 years of monthly U.S. Census Bureau data across 17 sectors, and its
diagnostic is applied to supply-chain ordering, the sectors the CHIPS Act depends on, sovereign
credit ratings, and unemployment-insurance tax formulas.

The single result that would falsify the thesis is stated in `THESIS.md`.

## Reproducibility contract

A number appears in the paper only if a committed script, run on hashed input data, regenerates
it on demand. Done = `verify.py` exits green AND the outline reconciliation gate is green.

## Repository layout

- `THESIS.md` - the claim, why it matters, the gap, the falsifier, the prior-art scan, the archetype.
- `DESIGN.md`, `OUTLINE.md`, `COVERAGE.md` - Phase 1 (design, argument roadmap, source disposition).
- `data/SOURCES.md`, `data/pull.py` - data dictionary + pull/verify (documentation-only; raw data not committed).
- `analysis/`, `analysis/outputs/` - analysis scripts and their JSON outputs.
- `claims.lock`, `verify.py` - the load-bearing-number ledger and the mechanical checker.
- `paper/` - the manuscript, its rendered form, and the renderer's inputs.
- `verification/` - the adversarial-review transcript and the three-way proof record.
- `DECISIONS.md` (append-only), `CORRECTIONS.md` (public, from 5c), `requirements.txt`.

Two self-contained folders per project: this git repo (all committable work) and a git-ignored
project-local data store for restricted/large data (location and per-file SHA256 recorded in
`data/SOURCES.md`).

## Licensing

- Code (analysis, verification, builders, renderers): MIT (see `LICENSE`).
- Paper: CC BY-NC-ND 4.0. Plain-English companion: CC BY-NC 4.0 (canonical home: LaggingTruth.com).

## Status

Phase 5 (Launch) - published as a pre-print with the full verification apparatus. See `DECISIONS.md` for the phase log.
