#!/usr/bin/env python3
"""verify.py - THE ESCALATION COST - the paper's verification gate.

Phase-3 deliverable (ClickUp 86bawqj0e box 6; Standard v1.9.3; author rulings
DECISIONS 42/44). Exit 0 = GREEN (all checks pass), exit 1 = RED.

CHECKS
  1. LEDGER-VALUE:  re-read every committed output named by claims.lock and
     re-extract every row's value (json_path or the builder's mechanical
     extractor), comparing to `expected` within `tol_rel` (0 = exact).
     Catches output drift, hand-edits, and ledger/output divergence.
  2. INPUT-HASH:    re-hash every hashed input a row names (sha256/md5)
     against data/SOURCES.md's registered store paths + the known artifact
     map. A missing store file is RED (run data/pull.py --verify).
  3. RERUN:         re-execute every script whose rows carry
     verify_mode="rerun", byte-comparing the regenerated output against the
     committed bytes (deterministic scripts: any diff is RED; the committed
     file is restored either way). verify_mode="artifact" scripts (E4, E7,
     E9 - long simulations) are NOT re-executed by default (author ruling:
     their check is 1+2); --full re-executes them too. One --full run is
     MANDATORY before the Phase-5 freeze, output ledgered.  --no-rerun
     skips all re-execution (extraction+hash only; container QA mode).
  4. CIC:           every row's cic_ref anchor exists in
     verification/cic_signoff.md and that entry is SIGNED.
  5. OUTLINE-TIE:   the family-prefix convention, bidirectional (OUTLINE
     v1.9 changelog; DECISIONS 44): every non-exempt OUTLINE LB family has
     >= 1 ledger row; every ledger id extends some OUTLINE family.
     Exempt-deferred: LB-E4-naive, LB-E13-firm-bookend, LB-FP-diagnostic,
     LB-E5-monitor.
  6. PAPER (arms at Phase 4 when paper/the-escalation-cost.md exists):
     every ledger id present at its {{LB-id}} token; no placeholders
     (TODO/TBD/XXX/STUB); every [@citekey] defined in the references
     section; every FIG-/TBL-/EQ-/THM-/P-THM- anchor referenced and every
     reference anchored; S- section and C-/L- scope/limit anchors from
     OUTLINE present; internal cross-references resolve; every
     verification/ path the manuscript names exists on disk.
     Absent a manuscript these report SKIPPED (not green, not red).

SELF-TEST (--selftest): runs the checker classes against the deliberately
broken fixtures in verification/fixtures/ and is GREEN only if EVERY fixture
turns RED for its named class:
  value_drift, unsigned_cic, missing_citation, surviving_stub,
  missing_section, orphan_figure, dangling_crossref, dropped_limit,
  missing_artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import statistics
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
ANALYSIS = ROOT / "analysis"
OUTPUTS = ANALYSIS / "outputs"
LOCK = ANALYSIS / "claims.lock"
SOURCES = ROOT / "data" / "SOURCES.md"
CIC = ROOT / "verification" / "cic_signoff.md"
OUTLINE = ROOT / "OUTLINE.md"
PAPER = ROOT / "paper" / "the-escalation-cost.md"
FIXTURES = ROOT / "verification" / "fixtures"
STORE = pathlib.Path(os.environ.get(
    "EC_STORE", r"C:\Users\jaek9\Documents\LaggingTruth\The-Escalation-Cost"))

TIE_EXEMPT = {"LB-E4-naive", "LB-E13-firm-bookend", "LB-FP-diagnostic",
              "LB-E5-monitor"}

# Embedded-input ids -> on-disk locations (everything else resolves via the
# SOURCES.md "Pulled files" table's store-path column).
EMBEDDED_INPUTS = {
    "jst_md5": STORE / "raw" / "JSTdatasetR6.dta",
    "eta_md5": STORE / "raw" / "eta539_ar539.csv",
    "leg_a_e7_rebuild": OUTPUTS / "e7_chain_sweep.json",
    "leg_b_source_sweep": STORE / "raw" / "phase26"
                          / "aggregated_chain_length_sweep.json",
}

RED, GREEN, SKIP = "RED", "green", "SKIPPED"


# --------------------------------------------------------------- utilities --
def path_get(obj, path: str):
    cur = obj
    for tok in re.findall(r"\[\'[^\']+\'\]|\[\d+\]|[^.\[\]]+", path):
        if tok.startswith("['"):
            cur = cur[tok[2:-2]]
        elif tok.startswith("["):
            cur = cur[int(tok[1:-1])]
        else:
            cur = cur[tok]
    return cur


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


def values_equal(expected, actual, tol_rel: float) -> bool:
    if isinstance(expected, bool) or isinstance(actual, bool):
        return expected == actual
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        if tol_rel == 0:
            return expected == actual
        scale = max(abs(expected), abs(actual), 1e-300)
        return abs(expected - actual) <= tol_rel * scale
    return expected == actual


def parse_sources_paths(sources_path: pathlib.Path) -> dict:
    """id -> (store_path, sha256) from the 'Pulled files' table."""
    out = {}
    in_table = False
    for line in sources_path.read_text(encoding="utf-8").splitlines():
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
        sid, sha, spath = cells[0], cells[7].strip("`"), cells[8].strip("`")
        out[sid] = (spath, sha)
    return out


def file_hash(p: pathlib.Path, algo: str) -> str:
    h = hashlib.new(algo)
    h.update(p.read_bytes())
    return h.hexdigest()


# ----------------------------------------------------------------- checks --
def check_ledger_values(lock: dict, outputs_dir: pathlib.Path) -> list:
    problems, cache = [], {}
    for r in lock["rows"]:
        fname = pathlib.Path(r["output"]).name
        if fname not in cache:
            fp = outputs_dir / fname
            if not fp.exists():
                problems.append(f"[value] {r['id']}: output missing: {fp}")
                cache[fname] = None
                continue
            cache[fname] = json.loads(fp.read_text(encoding="utf-8"))
        data = cache[fname]
        if data is None:
            continue
        try:
            actual = (DERIVED[r["derived"]](data) if r["derived"]
                      else path_get(data, r["json_path"]))
        except Exception as e:
            problems.append(f"[value] {r['id']}: extraction failed: {e}")
            continue
        if not values_equal(r["expected"], actual, r["tol_rel"]):
            problems.append(f"[value] {r['id']}: expected {r['expected']!r} "
                            f"got {actual!r} (tol_rel {r['tol_rel']})")
    return problems


def check_input_hashes(lock: dict, sources_path: pathlib.Path) -> list:
    problems = []
    id_map = parse_sources_paths(sources_path)
    seen = set()
    for r in lock["rows"]:
        for inp in r["inputs"]:
            iid = inp["id"]
            if iid in seen:
                continue
            seen.add(iid)
            if "sha256" in inp and iid in id_map:
                spath, _ = id_map[iid]
                p = pathlib.Path(spath)
                if not p.is_absolute():
                    p = STORE / spath
                algo, want = "sha256", inp["sha256"]
            elif iid in EMBEDDED_INPUTS:
                p = EMBEDDED_INPUTS[iid]
                algo = "md5" if "md5" in inp else "sha256"
                want = inp.get("md5") or inp.get("sha256")
            else:
                problems.append(f"[input] {iid}: no path resolution "
                                f"(not in SOURCES table or embedded map)")
                continue
            if not p.exists():
                problems.append(f"[input] {iid}: store file missing: {p}")
                continue
            got = file_hash(p, algo)
            if got != want:
                problems.append(f"[input] {iid}: {algo} mismatch: "
                                f"registered {want} on-disk {got}")
    return problems


def check_rerun(lock: dict, full: bool) -> list:
    problems = []
    scripts = {}
    for r in lock["rows"]:
        scripts.setdefault(r["script"], set()).add(r["verify_mode"])
    for script, modes in sorted(scripts.items()):
        if "rerun" not in modes and not full:
            continue
        sp = ROOT / script
        outs = sorted({ROOT / r["output"] for r in lock["rows"]
                       if r["script"] == script})
        before = {o: o.read_bytes() for o in outs if o.exists()}
        try:
            res = subprocess.run([sys.executable, str(sp)], cwd=str(ROOT),
                                 capture_output=True, text=True, timeout=86400)
        except Exception as e:
            problems.append(f"[rerun] {script}: execution failed: {e}")
            continue
        if res.returncode != 0:
            problems.append(f"[rerun] {script}: exit {res.returncode}: "
                            f"{res.stderr.strip()[-300:]}")
        for o, prev in before.items():
            now = o.read_bytes() if o.exists() else b""
            if now != prev:
                problems.append(f"[rerun] {script}: regenerated {o.name} "
                                f"differs from the committed bytes")
                o.write_bytes(prev)   # restore the committed state
    return problems


def check_cic(lock: dict, cic_path: pathlib.Path) -> list:
    problems = []
    if not cic_path.exists():
        return [f"[cic] signoff file missing: {cic_path}"]
    text = cic_path.read_text(encoding="utf-8")
    entries = {}
    for m in re.finditer(r"^## (\S+)\n(.*?)(?=^## |\Z)", text,
                         re.M | re.S):
        entries[m.group(1)] = m.group(2)
    for ref in sorted({r["cic_ref"] for r in lock["rows"]}):
        anchor = ref.split("#", 1)[1]
        if anchor not in entries:
            problems.append(f"[cic] anchor missing: {ref}")
        elif "SIGNED" not in entries[anchor]:
            problems.append(f"[cic] entry not SIGNED: {anchor}")
    return problems


def check_tie(lock: dict, outline_path: pathlib.Path) -> list:
    problems = []
    fams = []
    for line in outline_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*(LB-[A-Za-z0-9-]+)\s*\|", line)
        if m and m.group(1) != "LB-id":
            fams.append(m.group(1))
    ids = [r["id"] for r in lock["rows"]]

    def tied(i, f):
        return i == f or i.startswith(f + "-")
    for f in fams:
        if f in TIE_EXEMPT:
            continue
        if not any(tied(i, f) for i in ids):
            problems.append(f"[tie] OUTLINE family has no ledger row: {f}")
    for i in ids:
        if not any(tied(i, f) for f in fams):
            problems.append(f"[tie] ledger id outside every OUTLINE family: {i}")
    return problems


def check_paper(lock: dict, paper_path: pathlib.Path,
                outline_path: pathlib.Path, root: pathlib.Path) -> list:
    """Phase-4 reconciliation. Returns problems; caller handles arming."""
    problems = []
    text = paper_path.read_text(encoding="utf-8")

    # every ledger id present at its {{LB-id}} token
    for r in lock["rows"]:
        if "{{%s}}" % r["id"] not in text:
            problems.append(f"[paper] ledger id never placed: {{{{{r['id']}}}}}")

    # surviving stubs / placeholders
    for pat in (r"\bTODO\b", r"\bTBD\b", r"\bXXX\b", r"\{\{STUB[^}]*\}\}"):
        for m in re.finditer(pat, text):
            problems.append(f"[paper] surviving stub/placeholder: {m.group(0)}")

    # citations: every [@key] used must be defined once in a references
    # section as a line starting "[@key]:"
    used = set(re.findall(r"\[@([A-Za-z0-9_:-]+)\](?!:)", text))
    defined = set(re.findall(r"^\[@([A-Za-z0-9_:-]+)\]:", text, re.M))
    for k in sorted(used - defined):
        problems.append(f"[paper] citation used but undefined: [@{k}]")
    for k in sorted(defined - used):
        problems.append(f"[paper] citation defined but never used: [@{k}]")

    # anchors: FIG-/TBL-/EQ-/THM-/P-THM- must be anchored (a line
    # "<!-- anchor: ID -->" or a heading containing the ID) AND referenced
    # in the text at least once elsewhere.
    anchor_pat = r"<!--\s*anchor:\s*([A-Z-]+[A-Za-z0-9-]*)\s*-->"
    anchor_ids = set(re.findall(anchor_pat, text))
    text_wo_anchors = re.sub(anchor_pat, "", text)
    ref_ids = set(re.findall(r"\b((?:FIG|TBL|EQ|THM|P-THM)-[A-Za-z0-9-]+)\b",
                             text_wo_anchors))
    for i in sorted(ref_ids - anchor_ids):
        problems.append(f"[paper] referenced id has no anchor: {i}")
    for i in sorted(anchor_ids - ref_ids):
        problems.append(f"[paper] anchored id never referenced (orphan): {i}")

    # sections + scope/limit anchors required by OUTLINE (S- and C-/L- ids
    # listed in OUTLINE must appear in the paper)
    otext = outline_path.read_text(encoding="utf-8")
    required = set(re.findall(r"\b((?:S|C|L)-[0-9]+[A-Za-z0-9-]*)\b", otext))
    for i in sorted(required):
        if i not in text:
            kind = ("section" if i.startswith("S-")
                    else "scope/limit-of-claim")
            problems.append(f"[paper] required {kind} anchor missing: {i}")

    # internal cross-references: "see <ID>" resolves iff the id is anchored
    # or appears elsewhere in the body beyond the "see" mention itself
    for m in re.finditer(r"see\s+((?:FIG|TBL|EQ|THM|P-THM|S|C|L)-[A-Za-z0-9-]+)",
                         text_wo_anchors):
        i = m.group(1)
        if i not in anchor_ids and text_wo_anchors.count(i) < 2:
            problems.append(f"[paper] dangling cross-reference: {m.group(0)}")

    # named verification/ artifacts must exist on disk
    for m in re.finditer(r"\b(verification/[A-Za-z0-9_./-]+)", text):
        if not (root / m.group(1)).exists():
            problems.append(f"[paper] named artifact missing on disk: "
                            f"{m.group(1)}")
    return problems


# ---------------------------------------------------------------- selftest --
FIXTURE_CLASSES = ["value_drift", "unsigned_cic", "missing_citation",
                   "surviving_stub", "missing_section", "orphan_figure",
                   "dangling_crossref", "dropped_limit", "missing_artifact"]


def run_selftest() -> int:
    print("SELF-TEST: every fixture must turn RED for its class")
    failures = 0
    for cls in FIXTURE_CLASSES:
        fdir = FIXTURES / cls
        manifest = json.loads((fdir / "manifest.json").read_text())
        expect_frag = manifest["expect_fragment"]
        kind = manifest["kind"]
        if kind == "value":
            lock = json.loads((fdir / "claims.lock").read_text())
            problems = check_ledger_values(lock, fdir / "outputs")
        elif kind == "cic":
            lock = json.loads((fdir / "claims.lock").read_text())
            problems = check_cic(lock, fdir / "cic_signoff.md")
        elif kind == "paper":
            lock = json.loads((fdir / "claims.lock").read_text())
            problems = check_paper(lock, fdir / "paper.md",
                                   fdir / "OUTLINE.md", fdir)
        else:
            print(f"  {cls:<20} BAD MANIFEST kind={kind}")
            failures += 1
            continue
        hit = any(expect_frag in p for p in problems)
        status = "RED as required" if hit else "FAILED TO RED"
        if not hit:
            failures += 1
        print(f"  {cls:<20} {status}"
              + ("" if hit else f"  (problems: {problems})"))
    if failures:
        print(f"SELF-TEST RED: {failures} fixture(s) did not trip")
        return 1
    print("SELF-TEST GREEN: all 9 fixtures trip their checks")
    return 0


# -------------------------------------------------------------------- main --
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true",
                    help="also re-execute artifact-mode scripts (E4/E7/E9); "
                         "MANDATORY once before the Phase-5 freeze")
    ap.add_argument("--no-rerun", action="store_true",
                    help="skip all script re-execution (extraction+hash only; "
                         "container QA mode)")
    ap.add_argument("--selftest", action="store_true",
                    help="run the broken-fixture self-test and exit")
    a = ap.parse_args()

    if a.selftest:
        return run_selftest()

    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    print(f"verify.py - {lock['paper']} - {lock['n_rows']} ledger rows "
          f"(design pin {lock['design_pin_md5']})")
    report = {}
    report["ledger-values"] = check_ledger_values(lock, OUTPUTS)
    report["input-hashes"] = check_input_hashes(lock, SOURCES)
    report["rerun"] = (None if a.no_rerun else check_rerun(lock, a.full))
    report["cic-signoff"] = check_cic(lock, CIC)
    report["outline-tie"] = check_tie(lock, OUTLINE)
    if PAPER.exists():
        report["paper"] = check_paper(lock, PAPER, OUTLINE, ROOT)
    else:
        print("  paper            : SKIPPED (no manuscript yet - arms at Phase 4)")

    red = False
    for name, problems in report.items():
        if problems is None:
            print(f"  {name:<17}: {SKIP} (--no-rerun)")
            continue
        status = GREEN if not problems else RED
        if problems:
            red = True
        print(f"  {name:<17}: {status}"
              + (f" ({len(problems)} problem(s))" if problems else ""))
        for p in problems:
            print(f"      {p}")
    print("VERIFY " + ("RED" if red else "GREEN"))
    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main())
