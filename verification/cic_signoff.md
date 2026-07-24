# 7-Point CIC Signoff - The Escalation Cost (Phase 3)

Review of every generating script named in analysis/claims.lock against the
seven claim-integrity classes (Standard v1.9.3; Phase-3 checklist box 3).
Every script was read IN FULL, line by line, from the committed source on
2026-07-24 (session record: ClickUp task 86bawqj0e, comments 90140231335986
and the box-3 evidence comment; DECISIONS.md 2026-07-24 entries).

Reviewer: Claude (container-side QA role). Author of record: Jae Kim.
Anchors below are referenced by claims.lock rows' cic_ref fields.

The seven classes:
1. re-executes to the claim;
2. index/row alignment after diff / dropna / concat / resample;
3. NaN and gap handling explicit;
4. no look-ahead;
5. overlap vs non-overlapping subsample consistency;
6. no computation across record/station boundaries;
7. input integrity (obs count, coverage, gaps match Methods).

Verdict key: PASS = clears the class; N/A = class structurally inapplicable
(stated why); every entry ends SIGNED with date.

---

## e1_rolling_validation

1. PASS - main -> run_panel -> verdict/pooled/p_panel -> committed JSON; ledger reads that JSON.
2. PASS - pure positional numpy; (D, outcome) pairs constructed in the same loop iteration; joint isfinite pair-filter; n_min truncation uniform (341-obs gap-free inputs, class 7).
3. PASS - FRED "." tokens skipped at load; D set NaN when rho_baseline <= 0 and jointly filtered with its outcome.
4. PASS - predictor D_t strictly trailing (60m/12m windows ending at t); the 12m forward window is the OUTCOME by design. Note: sector CLASSIFICATION (chronic/oscillating/never-crossing) uses the full sample - a pre-registered sample partitioning with frozen precedence, not a per-t signal.
5. PASS - overlapping 12m outcomes handled by the pre-registered 24-month circular block bootstrap (joint index set across sectors for the panel p); block size justified in-source (trailing-12 anchor keeps dependence inside the block) and verified by the suite's measured false-positive rate.
6. PASS - each sector's series processed independently; pooling is of per-sector statistics, never of series.
7. PASS - hashed store via frozen pull.SECTOR_MAP; assert 17 members; per-sector n_obs recorded (341 uniform, matches the freeze manifest and Methods).

SIGNED 2026-07-24.

## e2_gfc_episode

1. PASS - sector_d_and_realized + run_panel -> spearman_D/p/components/verdict -> committed JSON.
2. PASS - DATE-KEYED window selection (YYYY-MM inclusive comparisons) - immune to positional shifts; the four per-sector values built jointly; one joint finiteness mask applied to all arrays.
3. PASS - "." skipped at load; D NaN-guarded on rho_pre <= 0 and mask-filtered.
4. PASS with note - frozen episode windows; the crisis window (2008-2009) is contemporaneous with part of the realized window (2007-2010) BY DESIGN: E2 is a corroborating episode ASSOCIATION, not out-of-sample prediction (E1 owns prediction). PHASE-4 FRAMING NOTE: the manuscript must not phrase E2 predictively.
5. PASS - cross-sectional n = 17; permutation of realized against fixed D is the exact small-n null (no serial structure across sectors); the constant-tau bake-off leg correctly reported n/a (a constant cannot rank).
6. PASS - all windows within each sector's own series.
7. PASS - 17-member assert; date-windowed selection; hashed store; n recorded in output.

SIGNED 2026-07-24.

## e3_covid_episode

1. PASS - sector_row + run_panel -> three-way verdict + direction counts -> committed JSON.
2. PASS - reuses E2's date-keyed pipeline verbatim (imports, not reimplementation); joint mask on (D, realized, delta_phi).
3. PASS - as E2.
4. PASS - as E2 (episode association; boundary probe with inverted polarity, pre-registered).
5. PASS - as E2.
6. PASS - as E2.
7. PASS - as E2.
Rule fidelity: the three-way branch logic matches the frozen docstring exactly (positive-significant -> anomaly; null + persistence-rose-majority -> anomaly; else consistent-with-boundary).

SIGNED 2026-07-24.

## e4_beer_game

1. PASS - run_montecarlo -> mean costs / paired p / rr CI / verdict -> committed JSON (naive present in output; EXCLUDED from the ledger by decision - DROPPED not-a-measurement).
2. PASS - paired BY CONSTRUCTION: identical demand array per run across all four ordering brains; costs indexed by run.
3. PASS - no NaN paths (deterministic arithmetic; rolling_phi clip + den>0 fallback).
4. PASS - order decision at t uses demand realized at t (standard periodic review: order placed after observing demand) and trailing history only; forecast exponential-smoothed on observed data.
5. PASS - runs are independent (fresh rng base_seed+i); paired sign-flip permutation test and bootstrap CI operate on run-level iid replicates.
6. PASS - pairing within run only; echelon interactions are the modeled system, not a boundary violation.
7. PASS - fully synthetic with committed seeds and the full frozen calibration recorded in spec; phi_engagement DERIVED by bisection, not assumed.

SIGNED 2026-07-24.

## e5_instability_ranking

1. PASS - run_ranking -> both-spec rankings + graded CHIPS verdict -> committed JSON.
2. PASS - per-sector independent rolling stats; no cross-series pairing exists to misalign.
3. PASS - "." skipped at load; gap-free inputs per freeze (class 7); no NaN-producing operations.
4. N/A - declared descriptive diagnostic (not a forecast); full-sample ranking is the object itself. The ranking-key saturation history (binary share saturated -> INCONCLUSIVE, not a result; key re-registered blind) is disclosed in-source - exemplary v1.9.7 hygiene.
5. N/A - no significance claims made; overlapping rolling windows feed descriptive means only.
6. PASS - per-sector only.
7. PASS - 17-member assert; hashed store; n_months recorded per sector.

SIGNED 2026-07-24.

## e6_capacity_threshold

1. PASS - run_experiment -> bins/monotone/crossing + current reading -> committed JSON.
2. PASS - MONTH-KEYED dict join of rho to utilization (pairs only where both months exist) - the class-2 correct pattern.
3. PASS - "." skipped; unmatched months skipped explicitly; thin bins (n < 6) reported but excluded from the monotonicity test; empty bins carry mean_rho = None.
4. PASS - rho at month t from the trailing window ending t, paired with same-month utilization; contemporaneous characterization by design.
5. PASS with note - overlapping rolling rho observations feed binned MEANS only; no CI or test is claimed on them. The pre-registered rule's REFUTE is ledgered as reported-alongside (severity-failed rule per DESIGN S9 amendment; v1.9.7), never as the finding.
6. PASS - one sector + one utilization series; no cross-series computation beyond the keyed pairing.
7. PASS - hashed store; n_paired recorded; current utilization value + month recorded.

SIGNED 2026-07-24.

## e7_chain_sweep

Scope: this entry covers the E7 DRIVER (ours). The vendored engine it drives
was CIC-cleared on all seven classes at the battery (DISC-05; DESIGN 14d/14e)
and is MD5-asserted by the suite - that clearance is referenced, not repeated.
beer_engine.py (the E4-parameterized engine used by the suite's fidelity legs)
rides with this entry: it is a mechanical parameterization of e4_beer_game's
simulate() under a bitwise fidelity contract enforced by e7_suite LEG 1.

1. PASS - run_sweep -> cells/crossover/stability/headline_vs_source -> committed JSON.
2. PASS - pairing keyed by trial_seed with success-filter on BOTH sides before set intersection.
3. PASS - failed trials filtered and counted (n_failed recorded); n_paired < 2 -> explicit unresolved cell with None fields; crossover logic skips None means.
4. N/A for the driver (simulation; the oracle variant is deliberately informed and labeled as diagnostic).
5. PASS - independent seeds; within-seed paired differences with ddof=1 SEs; each cell carries its OWN achieved MDD, never inherited (pre-registered); unresolved boundaries never reported as crossings.
6. PASS - pairing within seed only.
7. PASS - vendored source MD5-asserted by the suite; seed range recorded with the source-subset property documented; n_trials/n_failed per cell.

SIGNED 2026-07-24.

## e8_pricing

1. PASS - claim_a/claim_b/robustness computed from the asserted artifacts -> committed JSON; the two-claim separation makes DISC-03's substitution structurally impossible.
2. PASS - trial_seed-keyed dict pairing + set intersection, success-filtered.
3. PASS - success filter; n < 2 -> explicit None dict; robustness artifact-unavailable path explicit and recorded.
4. N/A - analysis of a committed artifact (no execution); the source code's own CIC (all seven, DESIGN 16c) covers generation.
5. PASS - independent seeds; paired SEs; sigma reported per cell; Claim A deliberately reported as a BOUND (powering to a verdict would be circular - documented in-source).
6. PASS - pairing within (env, seed) within artifact.
7. PASS - EXEMPLARY: every artifact's registered SHA256 asserted as a hard stop BEFORE any number is computed; inputs registered in data/SOURCES.md.

SIGNED 2026-07-24.

## e9_hysteresis

Scope: covers the E9 driver + analysis AND e9_hysteresis_demand.py (OUR
spec-derived hysteresis layer; authorship provenance and the two pre-registered
faithfulness proofs - h=0 bit-equivalence and the TIER-EXACT fidelity
comparison - are documented in that module's header and DESIGN Sec 12).

1. PASS - run_e9 -> cells/decision/crossover/fidelity -> committed JSON.
2. PASS - exact 4-tuple pairing (env, scenario, h, seed) via full-key match; fails loud (StopIteration) rather than mispairing; fidelity index keyed on the same tuple.
3. PASS - per-trial success flag with failure records (traceback preserved, first 5 in output); se = 0 -> degenerate status; fidelity missing-trial -> FAIL tier.
4. PASS - the demand walk updates the pool from the CURRENT price before demand realizes, and the policy decides the NEXT price from history 0..t only at review boundaries (mirrors the vendored call-site discipline that cleared CIC-4); strict input validation raises on invalid parameters.
5. PASS - independent seeds; paired diffs with ddof=1; pre-registered resolution language including the indeterminate band (within 1 SE of zero).
6. PASS - pairing within exact (env, h, seed); inventory sim uses a constant rand_seed common across arms (deliberate common-random-numbers pairing of the inventory layer while demand varies by trial seed).
7. PASS - fidelity target SHA256-gated (mismatch -> FAIL tier, never silent); frozen configuration block recorded; the run executes at the source's own seeds so one run is both the fidelity check and the result. Smoke mode modifies COPIES of the envs and writes to a separate smoke file; the real construction is untouched.

SIGNED 2026-07-24.

## e10_sovereign

1. PASS - run_e10 -> countries/decision/guards -> committed JSON.
2. PASS - YEAR-KEYED consecutive-pair construction (pairs only where t-1 exists) - never pairs across the JST gaps; pandas dropna + per-country sort.
3. PASS - dropna explicit; n_pairs < 10 -> phi None, handled by every downstream consumer.
4. N/A for claim (full-sample characterization); the full-sample linear detrend is a disclosed frozen-spec limitation, on record.
5. N/A - no inferential claims on the per-country estimates; consecutive-pair AR(1) only.
6. PASS - EXEMPLARY: pairing strictly within country and across consecutive years only.
7. PASS - EXEMPLARY: runtime MD5 gate on the JST input RAISES on mismatch; dual-implementation rho guard raises above 1e-12; rho invariant check (bg=0 -> |phi|) raises; n_obs/n_pairs/year ranges recorded per country.

SIGNED 2026-07-24.

## e11_ui

1. PASS - run_e11 -> pooled/jurisdictions/decision -> committed JSON.
2. PASS - PeriodIndex consecutive-quarter pairing within jurisdiction (t-1 membership test); groupby(st, q) aggregation; quarterly smoothing is a disclosed frozen-spec choice.
3. PASS - to_numeric(errors=coerce) + dropna explicit; n_pairs < 30 -> phi None.
4. N/A - characterization; GFC/normal split by calendar quarters.
5. PASS - consecutive-quarter pairs pooled after within-jurisdiction demeaning; n_pairs recorded (8,068 normal / 371 GFC).
6. PASS - pairing never crosses jurisdictions (per-state index membership); demeaning per state.
7. PASS - EXEMPLARY: runtime MD5 gate on ETA539 raises on mismatch; usecols explicit; dual-impl rho guard shared from e10.

SIGNED 2026-07-24.

## e12_nonstationarity

1. PASS - run_e12 -> LEG A map + LEG B contrasts + mechanical decision -> committed JSON; classification firewall in the output ("CANNOT support the thesis").
2. PASS - LEG B 5-tuple keyed index (env, L, cap, variant, seed), success-filtered at load; contrasts require ALL THREE keys (variant, comparator, baseline) present per seed - proper triple pairing; LEG A keyed by (env, L, cap).
3. PASS - n < 2 -> explicit None dict; missing keys skipped per seed, never imputed.
4. N/A - analysis of two committed artifacts; the oracle variant is deliberately informed and labeled.
5. PASS - EXEMPLARY: where paired SEs are not recoverable (LEG A aggregates), ordering uses CI DISJOINTNESS, explicitly conservative and documented; LEG B uses proper per-seed paired SEs (ddof=1).
6. PASS - pairing per exact (env, L, cap, seed).
7. PASS - BOTH legs hash-gated at load (LEG A MD5, LEG B SHA256; raise on mismatch); the sr_numerical pre-correction variant firewalled as context-only, never claim-carrying; scope note frozen to the tested trajectory shape.

SIGNED 2026-07-24.

## t1_theorem_checks

1. PASS - symbolic_checks + numeric_grid + ols_vs_yw -> committed JSON; ledger reads the leg fields directly.
2-6. N/A - closed-form symbolic verification (sympy S1-S8) and deterministic numeric grids on synthetic cells; no data series, no pairing, no temporal structure, no records.
7. PASS - grid pins and seed recorded in the output; the 2026-07-24 amendment (dedicated THM-3 dual-path identity assertion, 105 checks) proven verification-only by deep diff (every pre-existing field bit-identical).

SIGNED 2026-07-24.

## t2_wstar

1. PASS - brute-force argmin vs closed-form W* over the 105-cell interior grid -> committed JSON.
2-6. N/A - deterministic numeric grid; no data series.
7. PASS - grid bounds and unimodality check recorded; numeric-only by design (THM-2's symbolic legs live in t1, source-verified).

SIGNED 2026-07-24.

## t3_kstar

1. PASS - k* grid -> mfg argmin / in-band / all-below-1 / verdict -> committed JSON (honest MIXED with the k=1.0 corner boundary reported).
2-6. N/A - deterministic numeric grid; no data series.
7. PASS - grid pins recorded; numeric-only by design and LABELED proposition-numeric-only in the ledger (the written proof with labeled approximations is the Phase-4 three-way obligation, per author ruling 2026-07-24).

SIGNED 2026-07-24.

## fp_registration

1. PASS - main() -> literal registered constants + mechanical class extraction from the committed e1 output -> committed JSON; ledger reads that JSON by path.
2. N/A - no series operations; the only data touch is a key/value read of e1's sector list.
3. N/A - no numeric series; the classification field is categorical and complete (asserted to partition all 17 sectors).
4. PASS - no look-ahead by construction: bet (b)'s class lists come from the committed, pre-registration E1 output (full-sample pre-registered partition, as disclosed in e1's own class-4 note); all other fields are registration literals fixed before any resolving data exists.
5. N/A - no subsampling.
6. PASS - class lists extracted per-sector with no cross-sector computation; the sector-id split takes the token before the first space (ids contain no spaces; titles follow in parentheses).
7. PASS - input integrity: the e1 artifact's MD5 is computed from the exact bytes read and embedded in the output; the builder carries it as a hashed input and verify.py re-hashes the same committed path on every run.

SIGNED 2026-07-24.
