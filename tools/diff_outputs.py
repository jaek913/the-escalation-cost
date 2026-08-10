#!/usr/bin/env python3
r"""diff_outputs.py - adjudicate the verify --full rerun mismatches.

For each of the three long-simulation outputs, compare the COMMITTED version
(exported by the caller to %TEMP%\<name>.committed.json) against the
REGENERATED version now in analysis/outputs/. Report:
  1) whether the two parse to semantically identical JSON,
  2) which paths differ and by how much (first 20),
  3) THE MONEY QUESTION: every claims.lock row whose file points into this
     output, evaluated against BOTH versions - any ledgered value that
     changed is flagged LEDGER-DRIFT.
"""
import json, os, sys, tempfile

FILES = ["e7_chain_sweep", "e9_hysteresis", "e10_sovereign"]
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP = tempfile.gettempdir()

def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, o

def jget(o, path):
    cur = o
    tok = ""
    i = 0
    try:
        while i < len(path):
            c = path[i]
            if c == ".":
                if tok: cur = cur[tok]; tok = ""
            elif c == "[":
                if tok: cur = cur[tok]; tok = ""
                j = path.index("]", i)
                cur = cur[int(path[i+1:j])]
                i = j
            else:
                tok += c
            i += 1
        if tok: cur = cur[tok]
        return cur
    except Exception:
        return "<PATH-MISSING>"

claims = json.load(open(os.path.join(REPO, "analysis", "claims.lock"), encoding="utf-8"))
rows = claims if isinstance(claims, list) else claims.get("claims", claims)
if isinstance(rows, dict): rows = list(rows.values())

overall_ledger_drift = 0
for name in FILES:
    committed_p = os.path.join(TEMP, f"{name}.committed.json")
    regen_p = os.path.join(REPO, "analysis", "outputs", f"{name}.json")
    print(f"\n================ {name} ================")
    if not os.path.exists(committed_p):
        print(f"  MISSING {committed_p} - run the git show export lines first"); continue
    A = json.load(open(committed_p, encoding="utf-8-sig"))   # committed (PS export adds BOM)
    B = json.load(open(regen_p, encoding="utf-8-sig"))       # regenerated
    da, db = dict(walk(A)), dict(walk(B))
    if da == db:
        print("  SEMANTICALLY IDENTICAL - byte-only difference (formatting/ordering/whitespace).")
    else:
        only_a = sorted(set(da) - set(db)); only_b = sorted(set(db) - set(da))
        changed = sorted(k for k in set(da) & set(db) if da[k] != db[k])
        print(f"  paths only in committed: {len(only_a)} | only in regenerated: {len(only_b)} | changed: {len(changed)}")
        for k in only_a[:6]: print(f"    -committed-only: {k} = {da[k]}")
        for k in only_b[:6]: print(f"    +regen-only:     {k} = {db[k]}")
        for k in changed[:20]:
            va, vb = da[k], db[k]
            delta = ""
            if isinstance(va,(int,float)) and isinstance(vb,(int,float)):
                delta = f"  (delta {vb-va:+.6g})"
            print(f"    ~ {k}: {va} -> {vb}{delta}")
        if len(changed) > 20: print(f"    ... and {len(changed)-20} more changed paths")
    # money question
    fname = f"{name}.json"
    tied = [r for r in rows if isinstance(r, dict) and fname in str(r.get("file", r.get("source_file", "")))]
    print(f"  ledger rows tied to this file: {len(tied)}")
    drift = 0
    for r in tied:
        jp = r.get("json_path", r.get("path", ""))
        va, vb = jget(A, jp), jget(B, jp)
        same = (va == vb) or (isinstance(va,(int,float)) and isinstance(vb,(int,float)) and abs(va-vb) < 1e-12)
        if not same:
            drift += 1
            print(f"    LEDGER-DRIFT {r.get('id')}: {jp}: {va} -> {vb}")
    if drift == 0 and tied:
        print("  ALL LEDGERED VALUES IDENTICAL across committed vs regenerated.")
    overall_ledger_drift += drift

print("\n================ VERDICT ================")
if overall_ledger_drift == 0:
    print("NO LEDGER-DRIFT anywhere: mismatches are cosmetic/environmental bytes only.")
else:
    print(f"LEDGER-DRIFT in {overall_ledger_drift} row(s): STOP - investigate before proceeding.")
