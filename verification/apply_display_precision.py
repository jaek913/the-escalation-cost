#!/usr/bin/env python3
"""One-time display-precision migration (Phase 5c).

WHY THIS EXISTS
---------------
render_paper.fmt() renders a float with no format suffix as repr(v), which is
the shortest string that round-trips an IEEE-754 double - typically 16-19
digits. That is a DEFAULT, not a decision: the renderer was built with a
presentation-only format suffix ({{LB-id:.4f}}) for exactly this purpose, and
the manuscript simply never used it. The consequence in print was table columns
colliding under 17-digit cells whose trailing digits carry no information.

WHAT IT DOES
------------
Appends the display suffix ':.4f' to every {{LB-id}} token in the manuscript
whose ledger value is a float rendering seven or more decimal places, and only
to tokens that do not already carry a suffix.

WHAT IT DOES NOT DO
-------------------
It does not touch analysis/claims.lock. Display precision is presentation only;
the ledger keeps full precision, verify.py still recomputes and compares full
precision, and every certified value is unchanged. Integers, booleans, strings
and short floats are left alone.

WHY 4 DECIMALS IS SAFE HERE (verified before this script was written)
--------------------------------------------------------------------
Every long float in the manuscript was checked against the thresholds the paper
actually decides on - 1.0 for the spectral-radius boundary and 0.05 / 0.01 /
0.10 for the stated alphas. At four decimals NOT ONE value rounds onto a
threshold or across one. The contrast p-value that misses its frozen 0.05 bar
displays as 0.0515, which preserves both the verdict and the stated 0.0015
margin; the panel p displays as 0.0090, still inside 0.01; the explosive
sovereign estimates stay above 1.0. Five pairs of distinct values collapse to a
common four-decimal display (for example a country's detrended and raw-levels
estimates at 0.9871); that is an accurate statement that the two agree to four
decimals, and no reported count depends on the difference.

USAGE
-----
    python verification/apply_display_precision.py --dry-run
    python verification/apply_display_precision.py --apply

Run verify.py and the renderer afterwards; both must stay green.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOCK = ROOT / "analysis" / "claims.lock"
SRC = ROOT / "paper" / "the-escalation-cost.md"
SPEC = ".4f"
MIN_DECIMALS = 7


def long_float_ids() -> set:
    """Ledger ids whose value is a float printing >= MIN_DECIMALS decimals."""
    rows = json.loads(LOCK.read_text(encoding="utf-8"))["rows"]
    out = set()
    for r in rows:
        v = r["expected"]
        # bool is a subclass of int; both are excluded, as are strings/dicts.
        if isinstance(v, bool) or not isinstance(v, float):
            continue
        s = repr(v)
        if "." in s and "e" not in s.lower() and len(s.split(".")[1]) >= MIN_DECIMALS:
            out.add(r["id"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    targets = long_float_ids()
    text = SRC.read_text(encoding="utf-8")
    before = hashlib.md5(text.encode("utf-8")).hexdigest()

    touched, skipped_spec, instances = set(), set(), 0

    def sub(m: re.Match) -> str:
        nonlocal instances
        inner = m.group(1)
        if ":" in inner:                      # already carries a suffix
            lb = inner.split(":", 1)[0].strip()
            if lb in targets:
                skipped_spec.add(lb)
            return m.group(0)
        lb = inner.strip()
        if lb not in targets:
            return m.group(0)
        touched.add(lb)
        instances += 1
        return "{{" + lb + ":" + SPEC + "}}"

    new = re.sub(r"\{\{([^{}]+)\}\}", sub, text)
    after = hashlib.md5(new.encode("utf-8")).hexdigest()

    print(f"ledger ids with >= {MIN_DECIMALS} decimals : {len(targets)}")
    print(f"distinct ids given ':{SPEC}'              : {len(touched)}")
    print(f"token instances rewritten                 : {instances}")
    print(f"ids left alone (already had a suffix)     : {len(skipped_spec)}")
    print(f"manuscript md5 before                     : {before}")
    print(f"manuscript md5 after                      : {after}")

    unplaced = sorted(targets - touched - skipped_spec)
    if unplaced:
        print(f"note: {len(unplaced)} long-float ledger ids are not placed in "
              f"the manuscript (nothing to do for them)")

    if args.dry_run:
        print("\nDRY RUN - nothing written.")
        return 0

    SRC.write_text(new, encoding="utf-8", newline="\n")
    check = hashlib.md5(SRC.read_bytes()).hexdigest()
    print(f"\nwritten; read-back md5                    : {check}")
    if check != after:
        print("READ-BACK MISMATCH - investigate before proceeding.", file=sys.stderr)
        return 1
    print("read-back OK. Now run verify.py and analysis/render_paper.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
