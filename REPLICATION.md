# REPLICATION.md - The Escalation Cost
Version 1.0 - 2026-07-17. ASCII-only. This document makes the paper
rebuildable from text: it consolidates, for every check and experiment, the
frozen specification's location, the committed script, the hashed inputs, the
exact run command, and the committed output artifact. The frozen operators and
decision rules themselves live in DESIGN.md (append-only, dated amendments) -
this document POINTS to them and never restates them, so it cannot drift from
the record. It exists because the one failure mode that caused every problem
in this project's history was a specification living only in code (see
DECISIONS entries on E4/Section 5.4): nothing in this paper depends on any
unwritten construction.

## 0. Environment

- OS: Windows 11 (author machine); analyses are pure Python and run on any OS.
- Python 3.12; numpy, pandas, scipy (standard versions; no pinned exotica).
- Repo: github.com/jaek913/the-escalation-cost (private until launch).
- Data store: git-ignored, env var EC_STORE, default
  C:\Users\jaek9\Documents\LaggingTruth\The-Escalation-Cost. All inputs are
  pulled, hashed, and registered by data/pull.py; the generated data/SOURCES.md
  is the authoritative input registry (44 registered entries: 43 verified
  OK + 1 conditional-deferred EDGAR).
  Verify at any time: `python data\pull.py --verify`.
- Every analysis writes JSON to analysis/outputs/ (committed). Every
  experiment has a validation suite in analysis/suites/ run BEFORE the
  analysis (two-stage protocol; see DECISIONS).
- Determinism: all synthetic experiments seed explicitly; theory computations
  are closed-form/eigenvalue; reruns reproduce committed outputs bit-for-bit
  up to platform float printing.

## 1. Theory checks (proofs in paper/proofs_appendix_g.md)

| Check | Spec | Script | Output |
|---|---|---|---|
| T1 theorem checks (symbolic + numeric grid) | DESIGN Sec 4; proofs App G | analysis/t1_theorem_checks.py | analysis/outputs/t1_theorem_checks.json |
| T2 W* (period/optimum) | DESIGN Sec 4 | analysis/t2_wstar.py | analysis/outputs/t2_wstar.json |
| T3 k* operating point | DESIGN Sec 4 | analysis/t3_kstar.py | analysis/outputs/t3_kstar.json |

Shared theory library: analysis/theory_lib.py (rho, companion matrix,
bg_star, damage, estimators). T1-verified; E10/E11 additionally cross-check
rho against an independent from-scratch eigenvalue implementation
(analysis/e10_sovereign.py::rho_independent) to <= 1e-12.

## 2. Empirical core (real data)

| Exp | Spec | Script | Inputs (SOURCES.md ids) | Output |
|---|---|---|---|---|
| E1 rolling 34y validation (primary falsifier; Rule B) | DESIGN Sec 5 + amendments | analysis/e1_rolling_validation.py | fred_* sector I/S panel (17 sectors) | analysis/outputs/e1_rolling_validation.json |
| E2 GFC episode | DESIGN Sec 5 | analysis/e2_gfc_episode.py | same panel | analysis/outputs/e2_gfc_episode.json |
| E3 COVID episode (pre-registered expected-weak) | DESIGN Sec 5 | analysis/e3_covid_episode.py | same panel | analysis/outputs/e3_covid_episode.json |
| E5 instability ranking (redesigned) | DESIGN Sec 10 + amendment | analysis/e5_instability_ranking.py | sector panel | analysis/outputs/e5_instability_ranking.json |
| E6 capacity threshold (recharacterized) | DESIGN Sec 11 + amendment | analysis/e6_capacity_threshold.py | fred_CAPUTLG3344S, fred_IPG3344S + panel | analysis/outputs/e6_capacity_threshold.json |
| E10 sovereign (suggestive; WITHDRAWN) | DESIGN Sec 13 + amendment 2026-07-17b | analysis/e10_sovereign.py | e10_jst_r6 (JSTdatasetR6.dta, MD5 5614589349612f4c79f5b73e11b3732d) | analysis/outputs/e10_sovereign.json |
| E11 UI (suggestive; WITHDRAWN) | DESIGN Sec 13 + amendment 2026-07-17c | analysis/e11_ui.py | e11_eta539 (MD5 8f5cd02610f88a147d20c8173429d787) | analysis/outputs/e11_ui.json |

## 3. Simulation battery (Beer Game family; vendored engine)

Vendored source modules: analysis/vendor/ (CIC-cleared at E7; see DECISIONS
DISC-05). Engine deterministic; seeds recorded in each output's spec block.

| Exp | Spec | Script | Inputs | Output |
|---|---|---|---|---|
| E4 Beer Game MC (model-bound verdict) | DESIGN Sec 7 + audit amendment 2026-07-16 | analysis/e4_beer_game.py | none external | analysis/outputs/e4_beer_game.json |
| E7 chain-length sweep (rebuild, 45,000 trials, all 5 variants) | DESIGN Sec 8 + amendments | analysis/e7_chain_sweep.py | none external; source artifact phase26_chain_sweep_50seed as regression target | analysis/outputs/e7_chain_sweep.json (MD5 fdb79fd32566d4129226eea422c356cb) |
| E8 pricing (analysis of source artifact) | DESIGN Sec 9 (E8 gate) | analysis/e8_pricing.py | phase27_validation_50seed + capsweep + elasticity artifacts | analysis/outputs/e8_pricing.json |
| E9 hysteresis (spec-derived re-impl; TIER-EXACT) | DESIGN Sec 12 amendment 2026-07-16 | analysis/e9_hysteresis.py + e9_hysteresis_demand.py | phase27_hysteresis_20seed (cross-check target) | analysis/outputs/e9_hysteresis.json |
| E12 non-stationarity (analysis; recipe-level) | DESIGN Sec 13 amendment 2026-07-17 | analysis/e12_nonstationarity.py | our e7_chain_sweep.json + phase26_chain_sweep_50seed | analysis/outputs/e12_nonstationarity.json |

## 4. Run commands (author-machine form; container form uses env overrides)

```
python data\pull.py            # pull + hash inputs -> SOURCES.md
python data\pull.py --verify   # re-hash against disk
python analysis\suites\eN_suite.py   # per experiment, BEFORE the analysis
python analysis\eN_<name>.py         # the analysis; writes outputs JSON
```
Suite-before-analysis is mandatory (two-stage protocol). Env overrides used
by suites/analyses for non-default input paths: E10_JST_TARGET,
E11_ETA_TARGET, E12_SWEEP_TARGET, EC_STORE.

## 5. Where every number in the manuscript comes from

OUTLINE.md (v1.8) maps every argument (ARG-*), ledgered value (LB-*), and
table (TBL-*) to its experiment and section; no manuscript value is
hard-coded - each cites an LB id whose value appears in a committed
analysis/outputs JSON. DECISIONS.md (39 entries) records every choice,
surprise, correction, and process defect, dated and append-only. The
discrepancy register (in DECISIONS) closed with 7/7 dossiers RESOLVED and
zero open.

## 6. Verification levels available to a replicator

1. Hash check: `python data\pull.py --verify` (inputs) + git log (code).
2. Re-run any analysis; compare against the committed outputs JSON.
3. Re-run any suite; ALL PASS expected (planted effects, planted nulls,
   dual-implementation agreements, regression targets).
4. Ground-up: reimplement from the frozen DESIGN operators alone. Precedent
   that this suffices: E9's spec-derived re-implementation reproduced the
   source artifact bit-for-bit (max_rel_diff = 0.0, 320 trials).
