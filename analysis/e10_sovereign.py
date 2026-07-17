"""e10_sovereign.py - E10: sovereign ratings extension (SUGGESTIVE tier).
DESIGN Section 13 E10 operator + amendment 2026-07-17b. Characterization:
country phi/rho map + crossing counts; reduced rule per the gate's severity
analysis; ground-up dual-implementation rho (the v14 mandate).
Writes analysis/outputs/e10_sovereign.json.
"""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib
from typing import Any, Dict
import numpy as np
import pandas as pd
import theory_lib as tl

_HERE = pathlib.Path(__file__).resolve().parent
DESIGN_PIN = "74c73ea165a7363c6714fe803fbe76b1"
JST_MD5 = "5614589349612f4c79f5b73e11b3732d"
STORE = pathlib.Path(os.environ.get(
    "EC_STORE", r"C:\Users\jaek9\Documents\LaggingTruth\The-Escalation-Cost"))
DEFAULT_JST = STORE / "raw" / "JSTdatasetR6.dta"
OUT = _HERE / "outputs" / "e10_sovereign.json"
W = 5
BG_GRID = [0.05, 0.10, 0.25, 0.50, 1.00, 1.50]
CALM_BG = 0.05
PHI_STAR_15 = 0.691462  # gate probe: only live content of condition (2)


def rho_independent(phi: float, w: int, bg: float) -> float:
    """From-scratch companion-matrix spectral radius - written independently
    of theory_lib.companion_np (the mandated second implementation).
    Dynamics: x_t = phi*x_{t-1} - bg*(1/w)*sum_{j=1..w} x_{t-j}."""
    k = bg / w
    top = [phi - k] + [-k] * (w - 1)
    m = np.zeros((w, w))
    m[0, :] = top
    for i in range(1, w):
        m[i, i - 1] = 1.0
    return float(np.max(np.abs(np.linalg.eigvals(m))))


def ar1_pairs(years: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
    """With-intercept OLS AR(1) on CONSECUTIVE-year pairs only."""
    idx = {int(t): float(v) for t, v in zip(years, y)}
    x0, x1 = [], []
    for t in sorted(idx):
        if t - 1 in idx:
            x0.append(idx[t - 1]); x1.append(idx[t])
    x0, x1 = np.asarray(x0), np.asarray(x1)
    n = len(x0)
    if n < 10:
        return {"phi": None, "n_pairs": n}
    xm, ym = x0.mean(), x1.mean()
    phi = float(((x0 - xm) * (x1 - ym)).sum() / ((x0 - xm) ** 2).sum())
    return {"phi": phi, "n_pairs": n}


def detrend(years: np.ndarray, y: np.ndarray) -> np.ndarray:
    a = np.polyfit(years.astype(float), y, 1)
    return y - np.polyval(a, years.astype(float))


def run_e10(jst_path: str | None = None) -> Dict[str, Any]:
    p = pathlib.Path(jst_path) if jst_path else pathlib.Path(
        os.environ.get("E10_JST_TARGET", str(DEFAULT_JST)))
    raw = p.read_bytes()
    md5 = hashlib.md5(raw).hexdigest()
    if md5 != JST_MD5:
        raise RuntimeError(f"JST MD5 mismatch: {md5}")
    d = pd.read_stata(p)[["country", "year", "debtgdp"]].dropna()

    countries = []
    guard_max_dual_diff = 0.0
    for c in sorted(d["country"].unique()):
        sub = d[d["country"] == c].sort_values("year")
        yrs = sub["year"].to_numpy()
        y = sub["debtgdp"].to_numpy(dtype=float)
        det = ar1_pairs(yrs, detrend(yrs, y))
        rawv = ar1_pairs(yrs, y)
        row = {"country": str(c), "n_obs": int(len(y)),
               "year_min": int(yrs.min()), "year_max": int(yrs.max()),
               "phi_detrended": det["phi"], "n_pairs": det["n_pairs"],
               "phi_raw_levels": rawv["phi"]}
        if det["phi"] is not None and abs(det["phi"]) < 1.0:
            rhos = {}
            for bg in BG_GRID:
                r1 = tl.rho(det["phi"], W, bg)
                r2 = rho_independent(det["phi"], W, bg)
                diff = abs(r1 - r2)
                guard_max_dual_diff = max(guard_max_dual_diff, diff)
                if not np.isfinite(r1) or r1 <= 0 or diff > 1e-12:
                    raise RuntimeError(f"v14 guard tripped: {c} bg={bg} "
                                       f"r1={r1} r2={r2}")
                rhos[str(bg)] = r1
            inv = tl.rho(det["phi"], W, 0.0)
            if abs(inv - abs(det["phi"])) > 1e-9:
                raise RuntimeError(f"invariant failed for {c}")
            row["rho_by_bg"] = rhos
            row["rho_calm"] = rhos[str(CALM_BG)]
        else:
            row["rho_by_bg"] = None
            row["rho_calm"] = None
        countries.append(row)

    phis = [r["phi_detrended"] for r in countries]
    all_stationary = all(ph is not None and abs(ph) < 1.0 for ph in phis)
    counts = {}
    if all_stationary:
        for bg in BG_GRID:
            counts[str(bg)] = sum(
                1 for r in countries if r["rho_by_bg"][str(bg)] > 1.0)
        vals = [counts[str(bg)] for bg in BG_GRID]
        weakly = all(b >= a for a, b in zip(vals, vals[1:]))
        strictly = any(b > a for a, b in zip(vals, vals[1:]))
    else:
        weakly = strictly = False

    offered = bool(all_stationary and weakly and strictly)
    return {
        "experiment": "E10", "date": "2026-07-17",
        "design_pin": DESIGN_PIN, "jst_md5": md5,
        "classification": "characterization - suggestive tier; reduced rule "
                          "per amendment 2026-07-17b",
        "spec": {"W": W, "bg_grid": BG_GRID, "calm_bg": CALM_BG,
                 "phi_star_bg15": PHI_STAR_15,
                 "primary": "linearly detrended AR(1), consecutive pairs"},
        "countries": countries,
        "crossing_counts": counts,
        "decision": {
            "i_all_stationary": bool(all_stationary),
            "ii_weakly_monotone": bool(weakly),
            "ii_strictly_somewhere": bool(strictly),
            "iii_by_construction": "Spearman(rho_calm, phi) = 1 mathematically"
                                   " - reported, zero evidential weight",
            "reading": "OFFERED" if offered else "WITHDRAWN",
        },
        "guards": {"max_dual_impl_diff": guard_max_dual_diff,
                   "invariant_checked": True},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jst", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    res = run_e10(a.jst)
    out = pathlib.Path(a.out) if a.out else OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2))
    print(f"E10: reading={res['decision']['reading']} | "
          f"all_stationary={res['decision']['i_all_stationary']} | "
          f"counts={res['crossing_counts']} | "
          f"max_dual_diff={res['guards']['max_dual_impl_diff']:.2e}")
    for r in res["countries"]:
        ph = r["phi_detrended"]
        rc = r["rho_calm"]
        print(f"  {r['country']:<12} phi={ph:+.4f} (n={r['n_pairs']}) "
              f"rho_calm={rc if rc is None else round(rc,4)} "
              f"raw={r['phi_raw_levels']:+.4f}")


if __name__ == "__main__":
    main()
