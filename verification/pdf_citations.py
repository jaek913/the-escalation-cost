#!/usr/bin/env python3
"""PDF-only citation transform (Phase 5c).

WHY THIS EXISTS
---------------
The manuscript carries pandoc-style citation keys - [@Lee-1997a] in the body and
[@Lee-1997a]: Lee, H., ... definitions in the reference list. Those keys are NOT
decoration: verify.py's paper check ties them both ways, failing on any key used
but undefined and on any key defined but never used. That tie is what proves the
reference list carries no orphans and the body no dangling citations, and the
Phase-5a reviewer verified it at 73/73 in both rounds. The sibling papers in the
series have no equivalent check.

But the build has no --citeproc step, so those keys reached the PDF verbatim: the
body printed "[@Lee-1997a]" and the reference list printed as one run-on block
with "[@Key]:" prefixes. The rest of the series prints plain author-year text and
separate reference paragraphs.

Deleting the keys from the source would match the series and destroy the check.
So the keys stay in the committed artifacts and this transform rewrites them for
the PDF only - the same pattern build_pdf.ps1 already uses for the copyright
glyph and for line-break hints. Committed artifacts are untouched.

WHAT IT DOES
------------
1. Parses every "[@key]: entry" definition into surnames + year + entry text.
2. Rewrites in-body [@key] and [@k1; @k2; ...] as (Surname Year) /
   (S1 and S2 Year) / (S1 et al. Year), semicolon-separated for groups - the
   series convention, e.g. "(Girouard and Andre 2005)".
3. Replaces the reference-definition block with the entry texts as separate
   paragraphs, sorted by first surname then year, with the "[@key]:" prefixes
   removed.

FAIL-CLOSED
-----------
Every failure mode aborts the build rather than degrading the PDF silently:
an unparseable definition, a body key with no definition, or two distinct keys
that would render as the same author-year string (which would leave a reader
unable to tell which source is meant). Silence is the one thing a citation
transform must never do.

USAGE
    python verification/pdf_citations.py <input.md> <output.md>
"""
from __future__ import annotations

import pathlib
import re
import sys

DEF_RE = re.compile(r'^\[@([^\]]+)\]:[ \t]*(.+)$', re.M)
CITE_RE = re.compile(r'\[((?:[^\[\]]*@[^\[\]]*))\]')
KEY_RE = re.compile(r'@([A-Za-z0-9\-\._]+)')
# Surname, allowing the usual particles, immediately before a comma.
SUR_RE = re.compile(r"((?:[Vv]an\s+(?:de[nr]?\s+)?|[Dd]e\s+|[Dd]i\s+|[Oo]')?"
                    r"[A-Z][A-Za-z\u2019'\-]+),")


def die(msg: str) -> None:
    print(f"CITATION TRANSFORM FAILED: {msg}", file=sys.stderr)
    raise SystemExit(1)


def parse_def(key: str, entry: str) -> tuple:
    m = re.match(r'(.+?)\((\d{4}[a-z]?)\)', entry)
    if not m:
        die(f"reference [@{key}] has no parseable '(year)': {entry[:80]}")
    surnames = SUR_RE.findall(m.group(1))
    if not surnames:
        die(f"reference [@{key}] yields no surname: {m.group(1)[:80]}")
    return surnames, m.group(2)


def author_year(surnames: list, year: str) -> str:
    if len(surnames) == 1:
        return f"{surnames[0]} {year}"
    if len(surnames) == 2:
        return f"{surnames[0]} and {surnames[1]} {year}"
    return f"{surnames[0]} et al. {year}"


def sort_key(surnames: list, year: str) -> tuple:
    return (surnames[0].lower(), year)


def main() -> int:
    if len(sys.argv) != 3:
        die("usage: pdf_citations.py <input.md> <output.md>")
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    text = src.read_text(encoding="utf-8")

    defs = DEF_RE.findall(text)
    if not defs:
        die("no [@key]: reference definitions found")
    meta, seen_ay = {}, {}
    for key, entry in defs:
        if key in meta:
            die(f"reference [@{key}] defined more than once")
        surnames, year = parse_def(key, entry)
        ay = author_year(surnames, year)
        if ay in seen_ay:
            die(f"ambiguous citation: [@{key}] and [@{seen_ay[ay]}] both render "
                f"as '({ay})'. Disambiguate with a year suffix (1997a / 1997b) "
                f"in the reference entries.")
        seen_ay[ay] = key
        meta[key] = (surnames, year, entry.rstrip(), ay)

    # --- 1. locate the reference-definition block -------------------------
    # Everything OUTSIDE this block is prose that may cite, and all of it must
    # be rewritten - including the appendices, which in this manuscript come
    # AFTER the reference list. An earlier version rewrote only the text before
    # the References heading and left a citation key printing verbatim inside
    # Appendix G, which is the same mistake as the truncation below, one step
    # smaller: assuming the document ends where the references begin.
    dmatches = list(DEF_RE.finditer(text))
    span_start = dmatches[0].start()
    span_end = dmatches[-1].end()
    between = text[span_start:span_end]
    stray = [ln for ln in between.split("\n")
             if ln.strip() and not ln.lstrip().startswith("[@")]
    if stray:
        die(f"the reference-definition block is not contiguous; {len(stray)} "
            f"non-definition line(s) sit inside it, first: {stray[0][:70]!r}. "
            f"Refusing to rewrite a span whose contents are not understood.")

    missing, n_cites = [], 0

    def sub_cite(m: re.Match) -> str:
        nonlocal n_cites
        keys = KEY_RE.findall(m.group(1))
        if not keys:
            return m.group(0)
        out = []
        for k in keys:
            if k not in meta:
                missing.append(k)
                return m.group(0)
            out.append(meta[k][3])
        n_cites += 1
        return "(" + "; ".join(out) + ")"

    head = CITE_RE.sub(sub_cite, text[:span_start])
    tail = CITE_RE.sub(sub_cite, text[span_end:])
    if missing:
        die(f"document cites undefined key(s): {sorted(set(missing))}")

    # --- 2. rebuild the reference list in place ---------------------------
    # CRITICAL: replace ONLY the definition block. This manuscript places
    # Appendices A-G and the closing copyright/licence paragraph AFTER the
    # reference list, and an earlier version of this script replaced everything
    # from the References heading to end of file - silently dropping three
    # appendices, the proofs and the licence from a PDF that still built and
    # still reported SUCCESS. Caught by a post-build content probe, not by the
    # build itself.
    ordered = sorted(meta.values(), key=lambda t: sort_key(t[0], t[1]))
    rebuilt = "\n\n".join(t[2] for t in ordered)

    out_text = head + rebuilt + tail
    print(f"[ OK ] reference block replaced in place "
          f"({len(between)} chars -> {len(rebuilt)} chars); "
          f"{len(tail)} chars after it preserved and citation-rewritten")

    leftover = out_text.count("[@")
    if leftover:
        die(f"{leftover} citation key(s) still present after the transform; "
            f"the PDF would print them verbatim.")

    dst.write_text(out_text, encoding="utf-8", newline="\n")
    print(f"[ OK ] citations: {n_cites} in-text citation groups rewritten, "
          f"{len(ordered)} reference entries reformatted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
