"""e11_ui.py - E11: UI extension (SUGGESTIVE tier). DESIGN Sec 13 E11 operator
+ amendment 2026-07-17c. Pooled within-jurisdiction-demeaned AR(1); reduced
rule; dual-implementation rho guards (from e10_sovereign).
Writes analysis/outputs/e11_ui.json.
"""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib
import numpy as np
import pandas as pd
import theory_lib as tl
from e10_sovereign import rho_independent

_HERE = pathlib.Path(__file__).resolve().parent
DESIGN_PIN = "74c73ea165a7363c6714fe803fbe76b1"
ETA_MD5 = "8f5cd02610f88a147d20c8173429d787"
STORE = pathlib.Path(os.environ.get(
    "EC_STORE", r"C:\Users\jaek9\Documents\LaggingTruth\The-Escalation-Cost"))
DEFAULT_ETA = STORE / "raw" / "eta539_ar539.csv"
OUT = _HERE / "outputs" / "e11_ui.json"
W_SET = [12, 16, 20]
W_PRIMARY = 16
BG_GRID = [0.05, 0.10, 0.25]
PHI_STAR_CORNER = 0.997992  # W=20 x bg=0.25 (gate probe)
GFC = ("2008Q1", "2009Q4")


def pooled_ar1(df: pd.DataFrame) -> dict:
    """Pooled within-jurisdiction-demeaned AR(1) on consecutive-quarter
    pairs. df columns: st, q (PeriodIndex), iur."""
    x0, x1 = [], []
    for st, g in df.groupby("st"):
        s = g.set_index("q")["iur"].sort_index()
        s = s - s.mean()
        for t in s.index:
            if t - 1 in s.index:
                x0.append(s[t - 1]); x1.append(s[t])
    x0, x1 = np.asarray(x0), np.asarray(x1)
    if len(x0) < 30:
        return {"phi": None, "n_pairs": int(len(x0))}
    phi = float((x0 * x1).sum() / (x0 * x0).sum())
    return {"phi": phi, "n_pairs": int(len(x0))}


def _rho_guarded(phi: float, w: int, bg: float) -> float:
    r1, r2 = tl.rho(phi, w, bg), rho_independent(phi, w, bg)
    if abs(r1 - r2) > 1e-12 or not np.isfinite(r1) or r1 <= 0:
        raise RuntimeError(f"guard tripped: {phi} {w} {bg}")
    return r1


def run_e11(path: str | None = None) -> dict:
    p = pathlib.Path(path) if path else pathlib.Path(
        os.environ.get("E11_ETA_TARGET", str(DEFAULT_ETA)))
    raw = p.read_bytes()
    md5 = hashlib.md5(raw).hexdigest()
    if md5 != ETA_MD5:
        raise RuntimeError(f"ETA539 MD5 mismatch: {md5}")
    d = pd.read_csv(p, usecols=["st", "rptdate", "c19"], low_memory=False)
    d["c19"] = pd.to_numeric(d["c19"], errors="coerce")
    d = d.dropna()
    d["q"] = pd.PeriodIndex(pd.to_datetime(d["rptdate"]), freq="Q")
    dq = (d.groupby(["st", "q"])["c19"].mean().rename("iur").reset_index())

    g0, g1 = pd.Period(GFC[0], "Q"), pd.Period(GFC[1], "Q")
    gfc = dq[(dq["q"] >= g0) & (dq["q"] <= g1)]
    normal = dq[(dq["q"] < g0) | (dq["q"] > g1)]

    pn, pg = pooled_ar1(normal), pooled_ar1(gfc)

    rho_map = {}
    cond1 = pn["phi"] is not None and abs(pn["phi"]) < 1.0
    if cond1:
        for w in W_SET:
            for bg in BG_GRID:
                r = _rho_guarded(pn["phi"], w, bg)
                rho_map[f"W{w}_bg{bg}"] = r
                if r >= 1.0:
                    cond1 = False
    cond2 = (pg["phi"] is not None and pg["phi"] >= PHI_STAR_CORNER)
    offered = bool(cond1 and cond2)

    juris = []
    for st, g in normal.groupby("st"):
        r = pooled_ar1(g.assign(st=st))
        row = {"st": str(st), "phi_normal": r["phi"],
               "n_pairs": r["n_pairs"]}
        if r["phi"] is not None and abs(r["phi"]) < 1.0:
            row["rho_W16_bg010"] = _rho_guarded(r["phi"], W_PRIMARY, 0.10)
        else:
            row["rho_W16_bg010"] = None
        juris.append(row)

    return {
        "experiment": "E11", "date": "2026-07-17",
        "design_pin": DESIGN_PIN, "eta_md5": md5,
        "classification": "characterization - suggestive tier; reduced rule "
                          "per amendment 2026-07-17c",
        "pooled_normal": pn, "pooled_gfc": pg,
        "pooled_normal_rho": rho_map,
        "phi_star_corner": PHI_STAR_CORNER,
        "jurisdictions_normal": juris,
        "decision": {"i_normal_stable": bool(cond1),
                     "ii_gfc_crosses_corner": bool(cond2),
                     "reading": "OFFERED" if offered else "WITHDRAWN"},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--eta", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    res = run_e11(a.eta)
    out = pathlib.Path(a.out) if a.out else OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2))
    pn, pg = res["pooled_normal"], res["pooled_gfc"]
    print(f"E11: reading={res['decision']['reading']} | "
          f"normal phi={pn['phi']:.4f} (n={pn['n_pairs']}) | "
          f"gfc phi={pg['phi']:.4f} (n={pg['n_pairs']}) | "
          f"corner phi*={res['phi_star_corner']}")
    print("  normal rho:", {k: round(v, 4)
                            for k, v in res["pooled_normal_rho"].items()})
    js = [r["phi_normal"] for r in res["jurisdictions_normal"]
          if r["phi_normal"] is not None]
    print(f"  per-jurisdiction normal phi: n={len(js)} "
          f"min={min(js):.3f} median={float(np.median(js)):.3f} "
          f"max={max(js):.3f}")


if __name__ == "__main__":
    main()
