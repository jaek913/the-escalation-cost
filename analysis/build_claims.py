#!/usr/bin/env python3
"""build_claims.py - THE ESCALATION COST - sole writer of analysis/claims.lock.

Phase-3 builder (Standard v1.9.3 discipline; see ClickUp 86bawqj0e and
DECISIONS.md 2026-07-24). claims.lock is GENERATED - never hand-edited.

Every row wires one load-bearing value to:
  script          the committed generating script (analysis/...)
  output          the committed result artifact the value is read from
  json_path       dot/bracket path inside that artifact ("" for derived rows)
  derived         named mechanical extractor over the committed artifact
                  (selection/min/max/count only - the builder computes NO science)
  expected        the value at build time (scalar: float/int/str/bool)
  tol_rel         relative tolerance for numeric comparison (exact-match rows: 0)
  inputs          [{id, sha256|md5}] - hashed inputs per data/SOURCES.md
                  plus artifact hashes embedded in the output itself
  cic_ref         anchor into verification/cic_signoff.md (signed at CIC step)
  verify_mode     "rerun" (verify.py re-executes the script and compares) or
                  "artifact" (long simulation: verify.py re-hashes the committed
                  output + inputs and re-extracts; --full forces re-execution)
  leg             for theorem rows: "symbolic" | "numeric" (v1.9.3 two-row rule)
  label           optional: "not-a-theorem" for supplementary checks; notes

Load-bearing = anything the Abstract/Conclusion states or depends on
(OUTLINE v1.8 LB families; family prefix ties ledger rows to OUTLINE rows).
Excluded by decision: LB-E4-naive (DROPPED not-a-measurement, OUTLINE v1.4);
LB-E7-crossover (renamed LB-E7-gradient, OUTLINE v1.0); LB-E13-firm-bookend
(conditional on the deferred EDGAR entry). LB-FP-diagnostic landed 2026-07-24
(Phase-4 registration constants via analysis/fp_registration.py; public
registration at 5c).
"""
from __future__ import annotations
import datetime as _dt
import json
import pathlib
import re
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "analysis" / "outputs"
LOCK = ROOT / "analysis" / "claims.lock"
SOURCES = ROOT / "data" / "SOURCES.md"


# ------------------------------------------------------------------ loading --
def load(fname: str) -> dict:
    with open(OUT / fname, "r", encoding="utf-8") as fh:
        return json.load(fh)


def parse_sources() -> dict:
    """Parse the 'Pulled files' table -> {exp_tag: [{'id':..., 'sha256':...}]}."""
    by_exp: dict[str, list] = {}
    in_table = False
    for line in SOURCES.read_text(encoding="utf-8").splitlines():
        if line.startswith("## Pulled files"):
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if not in_table or not line.startswith("|") or line.startswith("|--"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 9 or cells[0] == "id":
            continue
        sid, used_by, sha = cells[0], cells[4], cells[7].strip("`")
        for tag in re.findall(r"E\d+|T\d+", used_by):
            by_exp.setdefault(tag, []).append({"id": sid, "sha256": sha})
    return by_exp


def path_get(obj, path: str):
    """Resolve 'a.b[2].c' / dict-key-with-dots via bracket ['k'] syntax."""
    cur = obj
    for tok in re.findall(r"\[\'[^\']+\'\]|\[\d+\]|[^.\[\]]+", path):
        if tok.startswith("['"):
            cur = cur[tok[2:-2]]
        elif tok.startswith("["):
            cur = cur[int(tok[1:-1])]
        else:
            cur = cur[tok]
    return cur


# --------------------------------------------- mechanical derived extractors --
def _e1_osc(d):
    return [s for s in d["sectors"] if s.get("klass") == "oscillating"]

DERIVED = {
    "e1_osc_spearman_min": lambda d: min(s["spearman"] for s in _e1_osc(d)),
    "e1_osc_spearman_max": lambda d: max(s["spearman"] for s in _e1_osc(d)),
    "e10_n_stationary":    lambda d: sum(1 for c in d["countries"]
                                         if c["phi_detrended"] < 1.0),
    "e10_explosive":       lambda d: {c["country"]: round(c["phi_detrended"], 6)
                                      for c in d["countries"]
                                      if c["phi_detrended"] >= 1.0},
    "e10_stat_phi_min":    lambda d: min(c["phi_detrended"] for c in d["countries"]
                                         if c["phi_detrended"] < 1.0),
    "e10_stat_phi_max":    lambda d: max(c["phi_detrended"] for c in d["countries"]
                                         if c["phi_detrended"] < 1.0),
    "e10_calm_rho_min":    lambda d: min(c["rho_by_bg"]["0.05"] for c in d["countries"]
                                         if c["phi_detrended"] < 1.0),
    "e10_calm_rho_max":    lambda d: max(c["rho_by_bg"]["0.05"] for c in d["countries"]
                                         if c["phi_detrended"] < 1.0),
    "e11_rho_min":         lambda d: min(d["pooled_normal_rho"].values()),
    "e11_rho_max":         lambda d: max(d["pooled_normal_rho"].values()),
    "e11_jur_phi_min":     lambda d: min(j["phi_normal"] for j in d["jurisdictions_normal"]),
    "e11_jur_phi_max":     lambda d: max(j["phi_normal"] for j in d["jurisdictions_normal"]),
    "e11_jur_phi_median":  lambda d: statistics.median(j["phi_normal"]
                                                       for j in d["jurisdictions_normal"]),
    "t1_counterexample_n": lambda d: len(d["numeric"]["counterexamples"]),
    "t1_thm1_symbolic":    lambda d: bool(d["symbolic"]["S2_dsma_convex"]
                                          and d["symbolic"]["S3_thm1_induction_tau4"]),
    "t1_thm2_symbolic":    lambda d: bool(d["symbolic"]["S4_loss_convex"]
                                          and d["symbolic"]["S5_interiority_condition"]
                                          and d["symbolic"]["S6_lambertw_solves_foc"]),
    "t1_statics_symbolic": lambda d: bool(d["symbolic"]["S7a_g_phi_positive"]
                                          and d["symbolic"]["S7b_g_a_positive"]
                                          and d["symbolic"]["S7c_g_ce_negative"]),
    "t3_mfg_argmin":       lambda d: (d["mfg_argmins"][0]
                                      if len(set(d["mfg_argmins"])) == 1
                                      else sorted(set(d["mfg_argmins"]))),
    "e5_mfg_meanrho_R":    lambda d: next(x["mean_rho"] for x in d["ranking_R"]
                                          if x["sector"] == "AMTMIS"),
    "e5_mfg_meanrho_M":    lambda d: next(x["mean_rho"] for x in d["ranking_M"]
                                          if x["sector"] == "AMTMIS"),
    "e12_paradox_count":   lambda d: sum(
        1 for k, cell in d["leg_b"]["drift_paired_contrasts"].items()
        if k.endswith("_oracle_minus_ols") and cell["resolved"]
        and cell["mean"] > 0),
}


# ----------------------------------------------------------------- row spec --
# (id, output_file, path_or_derived, verify_mode, leg/label/note kwargs)
def rows_spec():
    R = []

    def row(lb, out, path, mode="rerun", derived=None, tol=1e-9, **kw):
        R.append(dict(id=lb, output=out, json_path=("" if derived else path),
                      derived=(path if derived else ""), verify_mode=mode,
                      tol_rel=tol, **kw))

    # ---- THEOREM ROWS (v1.9.3: two separate rows per theorem-bearing claim;
    #      each leg confirmed present by reading the check's source 2026-07-24).
    t1 = "t1_theorem_checks.json"
    row("LB-T1-bound-symbolic", t1, "t1_thm1_symbolic", derived=True, leg="symbolic",
        note="sympy S2 (D_SMA strictly convex) + S3 (induction identity tau=4); "
             "legs read and confirmed in t1_theorem_checks.py symbolic_checks()")
    row("LB-T1-bound-numeric-allpass", t1, "numeric.all_pass", leg="numeric",
        note="numeric_grid(): dominant-mode THM-1a check + damage-bound stress, "
             "440 cells / 35 in-domain")
    row("LB-T1-bound-numeric-indomain", t1, "numeric.n_indomain", leg="numeric")
    row("LB-T1-bound-numeric-counterexamples", t1, "t1_counterexample_n",
        derived=True, leg="numeric")
    row("LB-T2-wstar-symbolic", t1, "t1_thm2_symbolic", derived=True, leg="symbolic",
        note="sympy S4 (loss convex) + S5 (interiority condition C) + "
             "S6 (Lambert-W solves FOC); in t1_theorem_checks.py")
    t2 = "t2_wstar.json"
    row("LB-T2-wstar-numeric-match", t2, "interior_match", leg="numeric",
        note="t2_wstar.py: closed-form W* vs brute-force argmin, 105 interior cells")
    row("LB-T2-wstar-numeric-matchrate", t2, "match_rate", leg="numeric")
    row("LB-T2-wstar-numeric-unimodal-failures", t2, "unimodal_failures", leg="numeric")
    row("LB-T2-statics-symbolic", t1, "t1_statics_symbolic", derived=True,
        leg="symbolic", note="corrected G.4 statics signs S7a/S7b/S7c (sympy)")
    row("LB-T2-statics-numeric-monophi-fail", t1, "numeric.mono_phi_fail",
        leg="numeric", note="A3 monotonicity failures across ALL 440 cells")
    row("LB-T2-statics-numeric-monobg-fail", t1, "numeric.mono_bg_fail",
        leg="numeric", note="gain-envelope lemma G.1b failures (in-domain)")
    row("LB-THM3-symbolic", t1, "symbolic.S8_thm3_log_identity", leg="symbolic",
        note="THM-3 exact identity log D = tau(ln r2 - ln r1) (sympy)")
    row("LB-THM3-numeric", t1, "numeric.thm3_identity_fail", leg="numeric",
        note="dedicated dual-path identity assertion added to numeric_grid() "
             "2026-07-24 per author ruling (hybrid option): log D via the power "
             "path vs tau (ln r2 - ln r1) via the log path, rel 1e-12, own "
             "counters - 0 failures expected. E10/E11 dual-impl guards exercise "
             "the identity again on real-data paths.")
    row("LB-THM3-numeric-checked", t1, "numeric.thm3_identity_checked",
        leg="numeric",
        note="identity assertions performed (in-domain cells x kappa grid)")
    t3 = "t3_kstar.json"
    row("LB-T3-kstar-mfg-argmin", t3, "t3_mfg_argmin", derived=True, leg="numeric",
        label="proposition-numeric-only",
        note="k* Proposition: t3_kstar.py is numeric-only (source read 2026-07-24 "
             "- no sympy leg exists); the written proof with labeled approximation "
             "steps is the Phase-4 obligation (three-way record). FLAGGED for "
             "author ruling: accept as proposition-with-Phase-4-proof or add a "
             "symbolic leg.")
    row("LB-T3-kstar-inband", t3, "mfg_in_band_080_098", leg="numeric",
        label="proposition-numeric-only")
    row("LB-T3-kstar-allbelow1", t3, "all_argmins_below_1", leg="numeric",
        label="proposition-numeric-only",
        note="False - the honest MIXED scope boundary (author disposition A: "
             "mild-scenario corners at k=1.0 are the claim's boundary)")
    row("LB-T3-kstar-verdict", t3, "verdict", leg="numeric",
        label="proposition-numeric-only")
    row("LB-T1-estimator-ols", t1, "estimator_comparison.ols_mean",
        label="not-a-theorem", note="supplementary OLS-vs-YW bias comparison")
    row("LB-T1-estimator-yw", t1, "estimator_comparison.yw_mean",
        label="not-a-theorem")
    row("LB-T1-estimator-ols-less-biased", t1,
        "estimator_comparison.ols_less_biased", label="not-a-theorem")

    # ---- E1 primary falsifier
    e1 = "e1_rolling_validation.json"
    row("LB-E1-panel-spearman", e1, "pooled_mean_spearman")
    row("LB-E1-panel-p", e1, "p_panel")
    row("LB-E1-panel-n-oscillating", e1, "n_oscillating")
    row("LB-E1-panel-n-chronic", e1, "n_chronic")
    row("LB-E1-panel-verdict", e1, "verdict")
    row("LB-E1-range-min", e1, "e1_osc_spearman_min", derived=True)
    row("LB-E1-range-max", e1, "e1_osc_spearman_max", derived=True)

    # ---- E2 GFC episode
    e2 = "e2_gfc_episode.json"
    row("LB-E2-gfc-spearman", e2, "spearman_D")
    row("LB-E2-gfc-p", e2, "p_one_sided")
    row("LB-E2-gfc-n", e2, "n")
    row("LB-E2-components-rho-crisis", e2, "components.rho_crisis")
    row("LB-E2-components-absdphi", e2, "components.abs_delta_phi")
    row("LB-E2-components-combined-ge", e2, "combined_ge_components")
    row("LB-E2-gfc-verdict", e2, "verdict")

    # ---- E3 COVID boundary
    e3 = "e3_covid_episode.json"
    row("LB-E3-covid-spearman", e3, "spearman_D")
    row("LB-E3-covid-p", e3, "p_one_sided")
    row("LB-E3-covid-n", e3, "n")
    row("LB-E3-persistence-direction-count", e3, "n_dropped")
    row("LB-E3-persistence-direction-majority", e3, "majority_dropped")
    row("LB-E3-covid-verdict", e3, "verdict")

    # ---- E4 Beer Game (model-bound; naive EXCLUDED - DROPPED not-a-measurement)
    e4 = "e4_beer_game.json"
    row("LB-E4-erp", e4, "mean_cost.basestock", mode="artifact",
        note="id retained for continuity; misnomer disclosed in OUTLINE - E4 "
             "built the full-gap self-calibrating base-stock, no ERP")
    row("LB-E4-tool", e4, "mean_cost.spectral", mode="artifact")
    row("LB-E4-tool-p", e4, "p_spectral_vs_basestock", mode="artifact")
    row("LB-E4-tool-relreduction", e4, "rel_reduction_mean", mode="artifact")
    row("LB-E4-full", e4, "mean_cost.full", mode="artifact")
    row("LB-E4-winrate", e4, "win_rate_full_vs_spectral", mode="artifact")
    row("LB-E4-tool-phi-engagement", e4, "phi_engagement", mode="artifact")
    row("LB-E4-tool-verdict", e4, "verdict", mode="artifact",
        note="model-bound per OUTLINE v1.4 / DESIGN amendment 2026-07-16")

    # ---- E5 instability ranking (valid redesigned run; SPEC-R primary)
    e5 = "e5_instability_ranking.json"
    for i in range(17):
        row(f"LB-E5-ranking-r{i+1:02d}-sector", e5, f"ranking_R[{i}].sector")
        row(f"LB-E5-ranking-r{i+1:02d}-meanexc", e5,
            f"ranking_R[{i}].mean_exceedance")
    row("LB-E5-chips-rank-R-A34SIS", e5, "chips_ranks_R['A34SIS']")
    row("LB-E5-chips-rank-R-R4238", e5, "chips_ranks_R['R4238IM163SCEN']")
    row("LB-E5-chips-rank-M-A34SIS", e5, "chips_ranks_M['A34SIS']")
    row("LB-E5-chips-rank-M-R4238", e5, "chips_ranks_M['R4238IM163SCEN']")
    row("LB-E5-chips-verdict", e5, "chips_verdict")
    row("LB-E5-persistence-mfg-meanrho-R", e5, "e5_mfg_meanrho_R", derived=True,
        note="mfg aggregate (AMTMIS) mean rho, SPEC-R primary - the "
             "LB-E5-persistence family's committed value")
    row("LB-E5-persistence-mfg-meanrho-M", e5, "e5_mfg_meanrho_M", derived=True,
        note="mfg aggregate (AMTMIS) mean rho, SPEC-M detrended variant")

    # ---- E6 capacity threshold (CHARACTERIZATION + ESTIMATE; no verdict promoted)
    e6 = "e6_capacity_threshold.json"
    for i, lab in enumerate(("lt75", "75-85", "85-90", "ge90")):
        row(f"LB-E6-threshold-bin{i+1}-{lab}-mean", e6,
            f"primary_spec_R.bins[{i}].mean_rho")
        row(f"LB-E6-threshold-bin{i+1}-{lab}-n", e6,
            f"primary_spec_R.bins[{i}].n")
    row("LB-E6-current-utilization", e6, "primary_spec_R.current_utilization")
    row("LB-E6-current-month", e6, "primary_spec_R.current_utilization_month")
    row("LB-E6-threshold-rule-outcome", e6, "verdict",
        note="the pre-registered rule's REFUTE - reported ALONGSIDE per DESIGN "
             "S9 amendment; NOT the finding (severity failed; v1.9.7)")

    # ---- E7 chain sweep (CHARACTERIZATION; rebuild)
    e7 = "e7_chain_sweep.json"
    for k, cnt in (("n-resolved", "n_resolved"), ("n-unresolved", "n_unresolved"),
                   ("n-harm", "n_harm"), ("n-benefit", "n_benefit")):
        row(f"LB-E7-gradient-{k}", e7, f"stability_statement.{cnt}",
            mode="artifact")
    for L in ("4", "6", "8"):
        row(f"LB-E7-gradient-cap24-ar1high-L{L}", e7,
            f"crossover['cap2.4_ar1_high'].by_length['{L}']", mode="artifact")
        row(f"LB-E7-gradient-cap24-ar1high-L{L}-resolved", e7,
            f"crossover['cap2.4_ar1_high'].resolved['{L}']", mode="artifact")
        row(f"LB-E7-gradient-cap13-ar1high-L{L}", e7,
            f"crossover['cap1.3_ar1_high'].by_length['{L}']", mode="artifact")
    for i, L in enumerate(("4", "6", "8")):
        row(f"LB-E7-calibration-L{L}-source", e7,
            f"headline_vs_source.rows[{i}].source_mean", mode="artifact")
        row(f"LB-E7-calibration-L{L}-ours", e7,
            f"headline_vs_source.rows[{i}].ours_mean", mode="artifact")
        row(f"LB-E7-calibration-L{L}-source-in-ci", e7,
            f"headline_vs_source.rows[{i}].source_in_our_ci", mode="artifact")

    # ---- E8 pricing (VERDICT Claim B + ESTIMATE-WITH-BOUNDS Claim A)
    e8 = "e8_pricing.json"
    row("LB-E8-up-claimb-mean", e8,
        "claim_b.cells.level_shift_up_persistent.mean", mode="rerun")
    row("LB-E8-up-claimb-sigma", e8,
        "claim_b.cells.level_shift_up_persistent.sigma", mode="rerun")
    for env in ("level_shift_down_persistent", "low_phi_shift_down",
                "mid_phi_shift_down"):
        row(f"LB-E8-down-{env}-mean", e8, f"claim_b.cells.{env}.mean")
        row(f"LB-E8-down-{env}-sigma", e8, f"claim_b.cells.{env}.sigma")
    row("LB-E8-up-claimb-verdict", e8, "claim_b.verdict")
    row("LB-E8-up-claima-mean", e8,
        "claim_a.by_arm.phi_gated_asymmetric.level_shift_up_persistent.mean",
        note="the formula's own contribution - a BOUND, not a verdict")
    row("LB-E8-up-claima-cipct-lo", e8, "claim_a.by_arm.phi_gated_asymmetric."
        "level_shift_up_persistent.ci_pct_of_claim_b[0]")
    row("LB-E8-up-claima-cipct-hi", e8, "claim_a.by_arm.phi_gated_asymmetric."
        "level_shift_up_persistent.ci_pct_of_claim_b[1]")
    for cap in ("1.8x", "2.4x", "3.0x"):
        row(f"LB-E8-up-cap{cap.replace('.','')}-mean", e8,
            f"robustness['capacity {cap}'].level_shift_up_persistent.mean")

    # ---- E9 hysteresis (qualification of E8 Claim B; TIER-EXACT fidelity)
    # Cell ids encode OUTLINE family + intensity: strained sticky env
    # (level_shift_up_persistent) = LB-E9-robust; noisy env (low_phi_shift_up)
    # = LB-E9-fragile; h tag = intensity x100 (family-prefix tie, DECISIONS 44).
    e9 = "e9_hysteresis.json"
    _e9cells = load(e9)["cells"]
    _e9fam = {"level_shift_up_persistent": "robust", "low_phi_shift_up": "fragile"}
    for i, cell in enumerate(_e9cells):
        fam = _e9fam[cell["env"]]
        htag = f"h{int(round(cell['h'] * 100)):03d}"
        row(f"LB-E9-{fam}-{htag}-benefit", e9, f"cells[{i}].benefit_mean",
            mode="artifact")
        row(f"LB-E9-{fam}-{htag}-sigma", e9, f"cells[{i}].sigma",
            mode="artifact")
    row("LB-E9-verdict", e9, "decision.verdict", mode="artifact")
    row("LB-E9-fidelity-tier", e9, "fidelity.tier", mode="artifact")
    row("LB-E9-fidelity-maxreldiff", e9, "fidelity.max_rel_diff",
        mode="artifact", tol=0.0,
        note="TIER-EXACT: bit-for-bit, 320 trials - exact zero")

    # ---- E10 sovereign (WITHDRAWN per rule; characterization)
    e10 = "e10_sovereign.json"
    row("LB-E10-calm-n-stationary", e10, "e10_n_stationary", derived=True)
    row("LB-E10-calm-explosive", e10, "e10_explosive", derived=True, tol=0.0,
        note="dict {country: phi} - exact-match row")
    row("LB-E10-calm-phi-min", e10, "e10_stat_phi_min", derived=True)
    row("LB-E10-calm-phi-max", e10, "e10_stat_phi_max", derived=True)
    row("LB-E10-calm-rho-min", e10, "e10_calm_rho_min", derived=True)
    row("LB-E10-calm-rho-max", e10, "e10_calm_rho_max", derived=True)
    row("LB-E10-crisis-reading", e10, "decision.reading",
        note="WITHDRAWN - conjunctive rule stops at stationarity failure; "
             "crossing sweep never reached (LB-E10-crisis per OUTLINE)")
    row("LB-E10-calm-guard-dualimpl", e10, "guards.max_dual_impl_diff", tol=0.0,
        note="v14-site guard: bit-exact dual implementation, exact zero")

    # ---- E11 UI (WITHDRAWN per rule; characterization)
    e11 = "e11_ui.json"
    row("LB-E11-normal-phi", e11, "pooled_normal.phi")
    row("LB-E11-normal-n", e11, "pooled_normal.n_pairs")
    row("LB-E11-normal-rho-min", e11, "e11_rho_min", derived=True)
    row("LB-E11-normal-rho-max", e11, "e11_rho_max", derived=True)
    row("LB-E11-normal-jur-phi-min", e11, "e11_jur_phi_min", derived=True)
    row("LB-E11-normal-jur-phi-max", e11, "e11_jur_phi_max", derived=True)
    row("LB-E11-normal-jur-phi-median", e11, "e11_jur_phi_median", derived=True)
    row("LB-E11-gfc-phi", e11, "pooled_gfc.phi")
    row("LB-E11-gfc-n", e11, "pooled_gfc.n_pairs")
    row("LB-E11-gfc-corner", e11, "phi_star_corner")
    row("LB-E11-gfc-reading", e11, "decision.reading")

    # ---- E12 non-stationarity (EXPECTED-CONFIRMED-RECIPE-LEVEL)
    e12 = "e12_nonstationarity.json"
    row("LB-E12-oracle-verdict", e12, "decision.verdict")
    row("LB-E12-oracle-harm-all-drift", e12, "decision.i_oracle_harm_all_drift")
    for cell in ("L4x1.3", "L8x2.4"):
        row(f"LB-E12-oracle-{cell.replace('.','')}-mean", e12,
            f"decision.i_oracle_cells['{cell}'].mean")
    for loc in ("L8x1.8", "L8x2.4"):
        k = loc.replace(".", "")
        row(f"LB-E12-oracle-fixed-{k}-mean", e12,
            f"decision.ii_claim_locus['{loc}'].fixed.mean")
        row(f"LB-E12-oracle-legb-{k}-fixedvsoracle", e12,
            f"decision.iii_leg_b_paired['{loc}'].fixed_minus_oracle.mean")
        row(f"LB-E12-oracle-legb-{k}-fixedvsols", e12,
            f"decision.iii_leg_b_paired['{loc}'].fixed_minus_ols.mean")
    row("LB-E12-oracle-paradox-count", e12, "e12_paradox_count", derived=True,
        note="drift cells where oracle paired-resolved WORSE than OLS - the "
             "perfect-information paradox (mechanical count over leg_b)")
    row("LB-E12-oracle-winscheck", e12, "decision.oracle_wins_check")

    # ---- FORWARD-PREDICTION REGISTRATION (Phase 4; OUTLINE ARG-27) --------
    # Registered protocol constants, emitted by the committed deterministic
    # generator analysis/fp_registration.py (bet (b) class lists extracted
    # mechanically from the committed E1 output, whose md5 is embedded).
    fp = "fp_registration.json"
    row("LB-FP-diagnostic-registered", fp, "registered", tol=0)
    row("LB-FP-diagnostic-horizon", fp, "horizon", tol=0)
    row("LB-FP-diagnostic-threshold", fp, "threshold_rho")
    row("LB-FP-diagnostic-estimator", fp, "estimator", tol=0)
    row("LB-FP-diagnostic-calculator-url", fp, "calculator_url", tol=0)
    row("LB-FP-diagnostic-trigger", fp, "bet_b.trigger", tol=0)
    row("LB-FP-diagnostic-metric-window-months", fp, "bet_b.metric_window_months")
    row("LB-FP-diagnostic-baseline-months", fp, "bet_b.baseline_months")
    row("LB-FP-diagnostic-alpha", fp, "bet_b.alpha")
    row("LB-FP-diagnostic-test", fp, "bet_b.test", tol=0)
    row("LB-FP-diagnostic-n-flagged", fp, "bet_b.n_flagged")
    row("LB-FP-diagnostic-n-decay", fp, "bet_b.n_decay")
    row("LB-FP-diagnostic-flagged-sectors", fp, "bet_b.flagged_sectors", tol=0)
    row("LB-FP-diagnostic-decay-sectors", fp, "bet_b.decay_sectors", tol=0)

    return R


# --------------------------------------------------------------------- main --
def main() -> None:
    by_exp = parse_sources()
    cache: dict[str, dict] = {}
    rows_out = []
    design_pins = set()
    for spec in rows_spec():
        fname = spec["output"]
        if fname not in cache:
            cache[fname] = load(fname)
        data = cache[fname]
        design_pins.add(data.get("design_pin", ""))
        if spec["derived"]:
            expected = DERIVED[spec["derived"]](data)
        else:
            expected = path_get(data, spec["json_path"])
        if isinstance(expected, float):
            expected = float(expected)
        exp_tag = data.get("experiment", "")
        inputs = list(by_exp.get(exp_tag, []))
        # artifact hashes embedded in the output itself
        for key, algo in (("jst_md5", "md5"), ("eta_md5", "md5"),
                          ("e1_md5", "md5")):
            if key in data:
                inputs.append({"id": key, algo: data[key]})
        if exp_tag == "E12":
            inputs.append({"id": "leg_a_e7_rebuild", "md5": data["leg_a"]["md5"]})
            inputs.append({"id": "leg_b_source_sweep",
                           "sha256": data["leg_b"]["sha256"]})
        script = {"T1": "analysis/t1_theorem_checks.py",
                  "T2": "analysis/t2_wstar.py",
                  "T3": "analysis/t3_kstar.py"}.get(
            exp_tag, f"analysis/{fname.replace('.json', '.py')}")
        rec = dict(id=spec["id"], script=script,
                   output=f"analysis/outputs/{fname}",
                   json_path=spec["json_path"], derived=spec["derived"],
                   expected=expected, tol_rel=spec["tol_rel"],
                   inputs=inputs,
                   cic_ref=f"verification/cic_signoff.md#{pathlib.Path(script).stem}",
                   verify_mode=spec["verify_mode"])
        for opt in ("leg", "label", "note"):
            if opt in spec:
                rec[opt] = spec[opt]
        rows_out.append(rec)
    ids = [r["id"] for r in rows_out]
    assert len(ids) == len(set(ids)), "duplicate LB-ids"
    design_pins.discard("")
    assert len(design_pins) == 1, f"mixed design pins: {design_pins}"
    lock = {"paper": "The Escalation Cost",
            "generated_by": "analysis/build_claims.py",
            "generated_at": _dt.date.today().isoformat(),
            "design_pin_md5": design_pins.pop(),
            "never_hand_edit": True,
            "n_rows": len(rows_out),
            "rows": sorted(rows_out, key=lambda r: r["id"])}
    with open(LOCK, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(lock, indent=1, sort_keys=False) + "\n")
    n_thm = sum(1 for r in rows_out if r.get("leg"))
    print(f"claims.lock written: {len(rows_out)} rows "
          f"({n_thm} theorem-leg rows) -> {LOCK}")


if __name__ == "__main__":
    main()
