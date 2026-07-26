"""render_paper.py - substitute {{LB-id}} tokens with ledger values.

The committed renderer required by the Standard's Phase-4 rule that no figure
is ever retyped by hand: every load-bearing number in the manuscript appears as
a {{LB-id}} token in the SOURCE (paper/the-escalation-cost.md, the authoritative
file that verify.py polices) and is substituted here, mechanically, from
analysis/claims.lock (itself produced only by the committed builder).

Rendering rules (deterministic. Without a format suffix there is NO rounding -
the ledger's stored precision is the paper's precision):
  str   -> as-is
  bool  -> "true" / "false"
  int   -> decimal string
  float -> repr(value) (shortest round-trip representation)
  dict  -> compact JSON, sorted keys (used by interval-style rows)
  null  -> "n/a" (a committed artifact's honest not-computed marker - e.g.
           calm rho for the explosive sovereign countries, where the
           diagnostic's own precondition fails; the ledger stores the null)

FORMAT SUFFIX (v1.9.11 era): a token may be written {{LB-id:SPEC}} where SPEC
is a Python format spec, e.g. {{LB-E14-chain-full-s3-ratio:.4f}} -> 2.3667.
This is PRESENTATION ONLY and changes nothing in the ledger: the stored value
is still the full-precision number the script produced, verify.py still ties
the manuscript to it, and the suffix cannot alter which value is quoted. It
exists because a table of sixteen-significant-figure floats is unreadable, and
the alternative - rounding in the builder - would destroy precision in the
LEDGER, which is the one place it must never be lost.

A suffix is accepted ONLY on int and float values. A suffix on a string, bool,
dict or null is a hard error rather than a silent pass-through, because those
types format without raising and would quietly produce something the author did
not intend.

Fails loud (exit 2) if the manuscript contains a token with no ledger row, a
format suffix that does not apply to its value, or any {{...}} that is not a
ledger token. The reverse direction (every ledger id placed in the paper) is
verify.py's job; the renderer re-asserts it anyway - and a ledger id placed
ONLY as {{LB-id:SPEC}} counts as placed, in both this script and verify.py.

Output: paper/the-escalation-cost.rendered.md (never hand-edited; regenerated
on every change to the source or the ledger).
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "paper" / "the-escalation-cost.md"
LOCK = ROOT / "analysis" / "claims.lock"
OUT = ROOT / "paper" / "the-escalation-cost.rendered.md"


def split_token(tok: str) -> tuple:
    """'LB-x' -> ('LB-x', None); 'LB-x:.4f' -> ('LB-x', '.4f').

    LB ids contain hyphens but never colons, so the first colon separates the
    id from an optional format spec.
    """
    if ":" in tok:
        lb, spec = tok.split(":", 1)
        return lb.strip(), spec.strip()
    return tok.strip(), None


def fmt(v, spec: str | None = None) -> str:
    if spec is None:
        if v is None:
            return "n/a"
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, str):
            return v
        if isinstance(v, int):
            return str(v)
        if isinstance(v, float):
            return repr(v)
        if isinstance(v, dict):
            return json.dumps(v, sort_keys=True, separators=(", ", ": "))
        raise TypeError(f"unrenderable ledger value type: {type(v).__name__}")
    # A format suffix is presentation only, and only numbers may carry one.
    # bool is a subclass of int and is excluded deliberately: format(True, '.2f')
    # returns '1.00', which is never what an author meant to write.
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise TypeError(
            f"format suffix ':{spec}' applied to a "
            f"{'bool' if isinstance(v, bool) else type(v).__name__} value; "
            "suffixes are valid only on int and float")
    return format(v, spec)


def main() -> int:
    rows = json.loads(LOCK.read_text(encoding="utf-8"))["rows"]
    values = {r["id"]: r["expected"] for r in rows}
    text = SRC.read_text(encoding="utf-8")

    problems = []
    tokens = re.findall(r"\{\{([^{}]+)\}\}", text)
    placed = set()
    for t in sorted(set(tokens)):
        lb, spec = split_token(t)
        placed.add(lb)
        if lb not in values:
            problems.append(f"token has no ledger row: {{{{{t}}}}}")
            continue
        if spec is not None:
            try:
                fmt(values[lb], spec)
            except (TypeError, ValueError) as e:
                problems.append(f"bad format suffix {{{{{t}}}}}: {e}")
    for i in sorted(values):
        if i not in placed:
            problems.append(f"ledger id never placed in source: {i}")
    if problems:
        for p in problems:
            print(f"RENDER RED: {p}")
        return 2

    def sub(m: re.Match) -> str:
        lb, spec = split_token(m.group(1))
        return fmt(values[lb], spec)

    rendered = re.sub(r"\{\{([^{}]+)\}\}", sub, text)
    header = ("<!-- RENDERED FILE - generated by analysis/render_paper.py from "
              "the token source and analysis/claims.lock; NEVER hand-edited. -->\n")
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(header + rendered)
    n = len(tokens)
    print(f"RENDER GREEN: {n} token occurrences ({len(set(tokens))} distinct ids) "
          f"substituted; output {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
