#!/usr/bin/env python3
"""build_review_package.py - assemble the Phase 5a curated review package.

Standard v1.9.11, venue rule v1.9.1: the adversarial review receives ONE curated zip
assembled by script from the repo. This script IS that assembly: an explicit
include-list (never a repo glob), loud failure on any missing file, a manifest with
SHA256 per file written into the package as README_REVIEW.md, and a final zip hash.

EXCLUDED BY RULE (enforced by the include-list construction): DECISIONS.md, all
verification/ contents except cic_signoff.md, proof_threeway.md, and review_prompt.md,
the raw data store, data/pull.py, and every __pycache__.

Usage:  python verification/build_review_package.py
Output: review_package/ (staging) and the-escalation-cost_review_package.zip at repo
        root. Both are ephemeral build products - do not commit them.
"""
import hashlib
import shutil
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STAGE = REPO / "review_package"
ZIP = REPO / "the-escalation-cost_review_package.zip"

# ---- The curated include-list (v1.9.1). Directories are copied WITHOUT __pycache__.
FILES = [
    "paper/the-escalation-cost.md",
    "paper/the-escalation-cost.rendered.md",
    "analysis/claims.lock",
    "verification/cic_signoff.md",
    "verification/proof_threeway.md",
    "verification/review_prompt.md",
    "data/SOURCES.md",
    "OUTLINE.md",
    "COVERAGE.md",
    "DESIGN.md",
    "THESIS.md",
    "verify.py",
]
DIRS = [
    "analysis",           # ALL analysis scripts incl. renderer, builder, theory lib
    "analysis/outputs",   # every committed result JSON incl. fp_registration.json
    "analysis/suites",    # mechanism-validation suites
    "analysis/vendor",    # vendored code the scripts import
]
FORBIDDEN = ["DECISIONS.md"]  # sanity tripwire: must never appear in the stage
# Working-tree byproducts that are NOT committed outputs (git-ignored in the repo):
# the spec says "committed outputs", so these are skipped even if present locally.
SKIP_SUFFIXES = ("_suite_check.json", "_suite_smoke.json")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    missing = [f for f in FILES if not (REPO / f).is_file()]
    missing += [d for d in DIRS if not (REPO / d).is_dir()]
    if missing:
        print("FATAL - required package members missing:")
        for m in missing:
            print("   ", m)
        return 1

    if STAGE.exists():
        shutil.rmtree(STAGE)
    if ZIP.exists():
        ZIP.unlink()
    STAGE.mkdir()

    staged = []

    # Directories first (files list then overwrites nothing - analysis files are a
    # superset via the dir copy; explicit FILES entries under analysis/ simply assert
    # existence above).
    for d in DIRS:
        src = REPO / d
        for p in sorted(src.rglob("*")):
            if p.is_dir() or "__pycache__" in p.parts:
                continue
            if p.name.endswith(SKIP_SUFFIXES):
                continue
            rel = p.relative_to(REPO)
            dest = STAGE / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
            staged.append(rel)

    for f in FILES:
        src = REPO / f
        dest = STAGE / f
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        rel = Path(f)
        if rel not in staged:
            staged.append(rel)

    # Tripwire: the exclusion rule is structural, but verify it anyway.
    for bad in FORBIDDEN:
        if (STAGE / bad).exists():
            print(f"FATAL - forbidden file staged: {bad}")
            return 1
    for p in STAGE.rglob("*"):
        if p.name == "DECISIONS.md" or p.name == "Discrepancy_Register.md":
            print(f"FATAL - forbidden file staged at {p}")
            return 1

    staged = sorted(set(staged))
    lines = [
        "# Review Package Manifest - The Escalation Cost (Phase 5a)",
        "",
        "Curated per Standard v1.9.11 (venue rule v1.9.1). Assembled by",
        "verification/build_review_package.py. The reviewer's instructions are in",
        "verification/review_prompt.md - read that file first.",
        "",
        "DECISIONS.md and all other verification/ contents are withheld by rule.",
        "",
        f"Files: {len(staged)}",
        "",
        "| SHA256 (first 16) | Path |",
        "| --- | --- |",
    ]
    for rel in staged:
        lines.append(f"| {sha256(STAGE / rel)[:16]} | {rel.as_posix()} |")
    (STAGE / "README_REVIEW.md").write_text("\n".join(lines) + "\n", encoding="ascii")

    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(STAGE.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(STAGE))

    print(f"PACKAGE GREEN: {len(staged) + 1} files staged (incl. README_REVIEW.md)")
    print(f"  zip   : {ZIP.name}")
    print(f"  bytes : {ZIP.stat().st_size:,}")
    print(f"  sha256: {sha256(ZIP)}")
    print("Reminder: the zip and review_package/ are build products - do not commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
