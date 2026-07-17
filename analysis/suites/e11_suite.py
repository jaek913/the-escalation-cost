"""e11_suite.py - E11 validation suite. DESIGN amendment 2026-07-17c.
LEG 1 input hash; LEG 2 dual-impl + phi* corner regressions; LEG 3 planted
pooled AR(1) recovery (multi-jurisdiction, demeaning, gaps); LEG 4 planted
decision-rule logic; LEG 5 full run + roundtrip.
"""
from __future__ import annotations
import hashlib, json, os, pathlib, sys
import numpy as np
import pandas as pd

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
import theory_lib as tl  # noqa: E402
import e11_ui as e11  # noqa: E402


def _eta():
    return pathlib.Path(os.environ.get(
        "E11_ETA_TARGET", str(e11.DEFAULT_ETA)))


def leg1():
    ok = _eta().exists() and hashlib.md5(
        _eta().read_bytes()).hexdigest() == e11.ETA_MD5
    print(f"LEG 1 input hash: {'PASS' if ok else 'FAIL'}")
    return ok


def leg2():
    ok = True
    rng = np.random.default_rng(3)
    for phi in rng.uniform(0.05, 0.999, 30):
        for w in e11.W_SET:
            for bg in e11.BG_GRID + [0.0]:
                from e10_sovereign import rho_independent
                if abs(tl.rho(phi, w, bg) - rho_independent(phi, w, bg)) > 1e-12:
                    ok = False
    ok &= tl.rho(0.99790, 20, 0.25) < 1.0 < tl.rho(0.99810, 20, 0.25)
    ok &= all(tl.rho(0.999999, w, bg) < 1.0
              for w in e11.W_SET for bg in e11.BG_GRID
              if not (w == 20 and bg == 0.25))
    print(f"LEG 2 dual-impl + phi* corner: {'PASS' if ok else 'FAIL'}")
    return ok


def leg3():
    rng = np.random.default_rng(5)
    phi = 0.8
    rows = []
    for st in ["AA", "BB", "CC"]:
        level = rng.uniform(-5, 5)
        x = 0.0
        qs = pd.period_range("1990Q1", periods=400, freq="Q")
        for q in qs:
            x = phi * x + rng.normal()
            rows.append({"st": st, "q": q, "iur": level + x})
    df = pd.DataFrame(rows)
    r = e11.pooled_ar1(df)
    ok = abs(r["phi"] - phi) < 0.03 and r["n_pairs"] == 3 * 399
    # gap: drop a block from one jurisdiction; spanning pairs must vanish
    df2 = df[~((df.st == "AA") & (df.q >= pd.Period("2000Q1", "Q"))
               & (df.q <= pd.Period("2005Q4", "Q")))]
    r2 = e11.pooled_ar1(df2)
    ok &= r2["n_pairs"] == r["n_pairs"] - 24 - 1 and abs(r2["phi"] - phi) < 0.04
    ok &= e11.pooled_ar1(df.head(5))["phi"] is None
    print(f"LEG 3 planted pooled AR(1): {'PASS' if ok else 'FAIL'}")
    return ok


def leg4():
    def decide(pn, pg):
        c1 = abs(pn) < 1 and all(
            tl.rho(pn, w, bg) < 1 for w in e11.W_SET for bg in e11.BG_GRID)
        c2 = pg >= e11.PHI_STAR_CORNER
        return "OFFERED" if (c1 and c2) else "WITHDRAWN"
    ok = decide(0.85, 0.9985) == "OFFERED"
    ok &= decide(0.85, 0.95) == "WITHDRAWN"     # gfc below corner
    ok &= decide(1.02, 0.9985) == "WITHDRAWN"   # normal explosive
    ok &= decide(0.85, 1.05) == "OFFERED"       # gfc explosive: a fortiori
    print(f"LEG 4 planted decision-rule logic: {'PASS' if ok else 'FAIL'}")
    return ok


def leg5():
    res = e11.run_e11(str(_eta()))
    out = _HERE.parent / "outputs" / "e11_suite_check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2))
    back = json.loads(out.read_text())
    ok = back["experiment"] == "E11"
    ok &= back["decision"]["reading"] in ("OFFERED", "WITHDRAWN")
    ok &= back["pooled_normal"]["n_pairs"] > 5000
    ok &= len(back["jurisdictions_normal"]) >= 50
    print(f"LEG 5 full run + roundtrip: {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    legs = [leg1(), leg2(), leg3(), leg4(), leg5()]
    print(f"E11 SUITE ALL PASS: {all(legs)}")
    if not all(legs):
        sys.exit(1)


if __name__ == "__main__":
    main()
