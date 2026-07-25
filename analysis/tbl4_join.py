#!/usr/bin/env python3
"""tbl4_join.py - THE ESCALATION COST - TBL-4 presentation join (Phase 4).

Purely mechanical, deterministic join of two committed artifacts into the
rank-ordered row set TBL-4 prints, so every table cell can be a ledger row
with a simple positional json_path (no cross-artifact joins in the builder):

  e5_instability_ranking.json  -> rank order, mean exceedance, share of
                                  months above 1 (SPEC-R primary)
  e5_monitor_tbl4.json         -> per-episode SPEC-M status + first upward
                                  crossing date (GFC, COVID)

No science is computed here: selection and join only, with hard asserts
(all 17 sectors matched; ranks contiguous 1..17). Both parents' MD5s are
embedded for input-integrity verification.

Output: analysis/outputs/tbl4_join.json
"""
from __future__ import annotations

import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
E5 = HERE / "outputs" / "e5_instability_ranking.json"
MON = HERE / "outputs" / "e5_monitor_tbl4.json"
OUT = HERE / "outputs" / "tbl4_join.json"


def _load(p):
    raw = p.read_bytes()
    return hashlib.md5(raw).hexdigest(), json.loads(raw.decode("utf-8"))


def main() -> None:
    e5_md5, e5 = _load(E5)
    mon_md5, mon = _load(MON)
    mon_by_sid = {r["sector"]: r
                  for r in mon["per_spec"]["SPEC-M"]["sectors"]}
    rows = []
    for r in e5["ranking_R"]:
        sid = r["sector"]
        m = mon_by_sid[sid]                      # KeyError = broken join
        rows.append(dict(
            rank=r["rank"], sector=sid, title=r["title"],
            mean_exceedance=r["mean_exceedance"],
            pct_months_above_1=r["pct_months_above_1"],
            gfc_status=m["episodes"]["gfc"]["status"],
            gfc_first=m["episodes"]["gfc"]["first_crossing"],
            covid_status=m["episodes"]["covid"]["status"],
            covid_first=m["episodes"]["covid"]["first_crossing"]))
    assert [x["rank"] for x in rows] == list(range(1, 18))
    assert len({x["sector"] for x in rows}) == 17
    out = dict(experiment="E5", date="2026-07-24",
               design_pin=e5["design_pin"],
               e5_md5=e5_md5, monitor_md5=mon_md5, rows=rows)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(out, indent=2))
    print(f"TBL-4 join written: 17 rank-ordered rows; e5_md5 {e5_md5}; "
          f"monitor_md5 {mon_md5}")


if __name__ == "__main__":
    main()
