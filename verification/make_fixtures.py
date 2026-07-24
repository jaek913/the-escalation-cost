#!/usr/bin/env python3
"""make_fixtures.py - deterministic generator of verify.py's broken fixtures.

Run once from the repo root (or verification/): writes the nine fixture
directories under verification/fixtures/, each a deliberately broken input
set that verify.py --selftest must turn RED for its named class. Fixtures
are committed alongside this generator; regenerate only via this script
(generator-level discipline - never hand-edit a fixture).
"""
from __future__ import annotations
import json
import pathlib

F = pathlib.Path(__file__).resolve().parent / "fixtures"


def minilock(cic_ref="verification/cic_signoff.md#e1_rolling_validation",
             ids=("LB-X-a",), expected=1.0, tol=1e-9):
    rows = [dict(id=i, script="analysis/x.py",
                 output="analysis/outputs/x.json", json_path="v", derived="",
                 expected=expected, tol_rel=tol, inputs=[], cic_ref=cic_ref,
                 verify_mode="rerun") for i in ids]
    return dict(paper="fixture", n_rows=len(rows), design_pin_md5="0" * 32,
                rows=rows)


def w(d, name, content):
    p = F / d
    p.mkdir(parents=True, exist_ok=True)
    if isinstance(content, dict):
        content = json.dumps(content, indent=1)
    with open(p / name, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)


PAPER_OK = ("Body cites [@good] and places {{LB-X-a}}.\n"
            "<!-- anchor: FIG-100 -->\nAs FIG-100 shows... see FIG-100.\n"
            "S-100 appears. L-100 appears. verification/cic_signoff.md "
            "exists.\n"
            "[@good]: Good, A. (2020). A fine source.\n")
OUT_OK = ("| LB-X-a | fixture family | ARG-1 | DONE |\n"
          "Required anchors: S-100 and L-100.\n")


def paper_fix(name, frag, paper=PAPER_OK, outline=OUT_OK):
    w(name, "manifest.json", dict(kind="paper", expect_fragment=frag))
    w(name, "claims.lock", minilock())
    w(name, "paper.md", paper)
    w(name, "OUTLINE.md", outline)
    (F / name / "verification").mkdir(parents=True, exist_ok=True)
    w(name + "/verification", "cic_signoff.md", "present\n")


def main() -> None:
    w("value_drift", "manifest.json",
      dict(kind="value", expect_fragment="[value] LB-X-a: expected"))
    w("value_drift", "claims.lock", minilock())
    w("value_drift/outputs", "x.json", '{"v": 2.0}')

    w("unsigned_cic", "manifest.json",
      dict(kind="cic", expect_fragment="not SIGNED"))
    w("unsigned_cic", "claims.lock", minilock())
    w("unsigned_cic", "cic_signoff.md",
      "# fixture\n\n## e1_rolling_validation\n\n"
      "1. PASS - looks fine but nobody signed it.\n")

    paper_fix("missing_citation", "citation used but undefined",
              paper=PAPER_OK.replace("[@good] and", "[@good] and [@bad] and"))
    paper_fix("surviving_stub", "surviving stub",
              paper=PAPER_OK + "\nTODO finish this paragraph.\n")
    paper_fix("missing_section", "required section anchor missing: S-100",
              paper=PAPER_OK.replace("S-100 appears. ", ""))
    paper_fix("orphan_figure", "never referenced (orphan): FIG-100",
              paper=PAPER_OK.replace("As FIG-100 shows... see FIG-100.", ""))
    paper_fix("dangling_crossref", "dangling cross-reference: see S-999",
              paper=PAPER_OK + "For the derivation see S-999.\n")
    paper_fix("dropped_limit", "scope/limit-of-claim anchor missing: L-100",
              paper=PAPER_OK.replace("L-100 appears. ", ""))
    paper_fix("missing_artifact",
              "artifact missing on disk: verification/ghost.md",
              paper=PAPER_OK + "\nSee verification/ghost.md for the record.\n")
    print(f"fixtures written under {F}")


if __name__ == "__main__":
    main()
