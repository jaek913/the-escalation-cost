"""recover_pricing_source.py - Literal-SQL recovery from the MemPalace ChromaDB store.

Discrepancy-Resolution Methods playbook, Method 1 (Source Recovery), literal-SQL
sub-technique. Run when semantic search plateaus on a code block: it keeps
returning the prose and docstrings AROUND the code, never the code body.

Target: the Phase 2.7 pricing simulation (E8 / DISC-01, DISC-02). The semantic
pass recovered the function NAMES below but not their BODIES - the documented
plateau signature.

Procedure (playbook):
  Step 1 - snapshot the BACKUP db locally (inert; no locks, no WAL issues).
  Step 2 - open read-only (mode=ro), search embedding_fulltext_search.string_value
           for a RARE fingerprint. Rare wins: a unique function name pinned the
           Paper 2 target in 2 hits; a common word returned 626 and was useless.
  Step 3 - dump the matching rowid plus a NEIGHBOURHOOD (rowid-4 .. rowid+6),
           because chunks are stored in DOCUMENT ORDER and a script body plus its
           surrounding explanation span several consecutive rows. A chunk far
           larger than the uniform ~800 chars is often a whole script in one block.

CAUTION (playbook): chunks from different papers/sessions look alike - the series
shares machinery and vocabulary. Read the full neighbourhood and confirm the
surrounding context belongs to Phase 2.7 pricing before drawing any conclusion.
"The literal search gives you ground truth, but only if you verify which ground
you are standing on."

Paths are taken as ARGV, never interpolated into a string literal: a Windows path
containing \\Users triggers a unicode-escape error on the \\U.

Usage:
  python recover_pricing_source.py <path-to-chroma.sqlite3> <out.txt>
"""

import sqlite3
import sys

# Rarest first. These came from the semantic pass; they are distinctive enough
# that a hit should pin the target immediately.
FINGERPRINTS = [
    "apply_pricing_to_retailer_streams",
    "PricingScenarioConfig",
    "get_transition_period_for_environment",
    "assign_realized_streams_to_retailer",
    "sku_baseline_streams",
    "level_shift_up_persistent",
    "low_phi_shift_up",
    "mid_phi_shift_down",
]

NEIGHBOURHOOD_BACK = 4
NEIGHBOURHOOD_FWD = 6


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    db_path, out_path = sys.argv[1], sys.argv[2]

    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cur = con.cursor()
    out = []

    def w(s=""):
        out.append(s)
        print(s)

    w("LITERAL-SQL RECOVERY - Phase 2.7 pricing source")
    w("=" * 70)

    # 1) Count hits per fingerprint, rarest-usable first.
    w("")
    w("--- fingerprint hit counts (rare = good; 1-5 hits pins it) ---")
    counts = {}
    for fp in FINGERPRINTS:
        cur.execute(
            "SELECT COUNT(*) FROM embedding_fulltext_search WHERE string_value LIKE ?",
            ("%" + fp + "%",),
        )
        n = cur.fetchone()[0]
        counts[fp] = n
        w("  %6d  %s" % (n, fp))

    # 2) For each usable fingerprint, dump rowids + chunk sizes.
    usable = [fp for fp in FINGERPRINTS if 0 < counts[fp] <= 40]
    if not usable:
        w("")
        w("No usable fingerprint (all zero, or all too common). Widen or re-fingerprint.")
        con.close()
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(out))
        return

    w("")
    w("--- rowids + chunk sizes (an outsized chunk is often a whole script) ---")
    targets = []
    for fp in usable:
        cur.execute(
            "SELECT rowid, LENGTH(string_value) FROM embedding_fulltext_search "
            "WHERE string_value LIKE ? ORDER BY rowid",
            ("%" + fp + "%",),
        )
        rows = cur.fetchall()
        w("")
        w("  [%s]  %d hit(s)" % (fp, len(rows)))
        for rid, ln in rows:
            flag = "  <-- OUTSIZED, likely a full script block" if ln > 3000 else ""
            w("    rowid %8d   %6d chars%s" % (rid, ln, flag))
            targets.append(rid)

    # 3) Dump each hit's neighbourhood in document order.
    w("")
    w("=" * 70)
    w("--- NEIGHBOURHOOD DUMPS (document order; confirm the context is Phase 2.7) ---")
    seen = set()
    for rid in sorted(set(targets)):
        lo, hi = rid - NEIGHBOURHOOD_BACK, rid + NEIGHBOURHOOD_FWD
        if any(r in seen for r in range(lo, hi + 1)):
            continue
        w("")
        w("=" * 70)
        w("=== neighbourhood of rowid %d  (rows %d..%d) ===" % (rid, lo, hi))
        cur.execute(
            "SELECT rowid, string_value FROM embedding_fulltext_search "
            "WHERE rowid BETWEEN ? AND ? ORDER BY rowid",
            (lo, hi),
        )
        for r, txt in cur.fetchall():
            seen.add(r)
            marker = "  <<<<< HIT" if r == rid else ""
            w("")
            w("----- rowid %d (%d chars)%s -----" % (r, len(txt), marker))
            w(txt)

    con.close()
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("")
    print("Wrote %s" % out_path)


if __name__ == "__main__":
    main()
