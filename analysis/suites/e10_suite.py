"""e10_suite.py - E10 validation suite. DESIGN amendment 2026-07-17b.
LEG 1 input hash; LEG 2 dual-implementation agreement + invariants + phi*
regression (the v14 guards); LEG 3 planted AR(1) recovery incl. gap handling;
LEG 4 planted detrend recovery; LEG 5 planted decision-rule logic;
LEG 6 full run + roundtrip.
"""
from __future__ import annotations
import hashlib, json, os, pathlib, sys
import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
import theory_lib as tl  # noqa: E402
import e10_sovereign as e10  # noqa: E402


def _jst():
    return pathlib.Path(os.environ.get(
        "E10_JST_TARGET", str(e10.DEFAULT_JST)))


def leg1():
    ok = _jst().exists() and hashlib.md5(
        _jst().read_bytes()).hexdigest() == e10.JST_MD5
    print(f"LEG 1 input hash: {'PASS' if ok else 'FAIL'}")
    return ok


def leg2():
    ok = True
    rng = np.random.default_rng(7)
    for phi in list(rng.uniform(0.05, 0.999, 40)) + [0.3, 0.9, 0.967084]:
        for bg in e10.BG_GRID + [0.0]:
            r1, r2 = tl.rho(phi, e10.W, bg), e10.rho_independent(
                phi, e10.W, bg)
            if abs(r1 - r2) > 1e-12 or not np.isfinite(r1) or r1 <= 0:
                ok = False
        if abs(tl.rho(phi, e10.W, 0.0) - abs(phi)) > 1e-9:
            ok = False
    # phi* regression: boundary values from the gate probes
    ok &= tl.rho(0.69140, e10.W, 1.5) < 1.0 < tl.rho(0.69150, e10.W, 1.5)
    ok &= tl.rho(0.96700, e10.W, 1.0) < 1.0 < tl.rho(0.96720, e10.W, 1.0)
    # no stationary crossing at bg <= 0.5
    ok &= all(tl.rho(0.999999, e10.W, b) < 1.0 for b in [0.05, 0.1, 0.25, 0.5])
    print(f"LEG 2 dual-impl + invariants + phi*: {'PASS' if ok else 'FAIL'}")
    return ok


def leg3():
    rng = np.random.default_rng(11)
    phi = 0.85
    y = [0.0]
    for _ in range(3000):
        y.append(phi * y[-1] + rng.normal())
    y = np.array(y[1:])
    yrs = np.arange(1000, 1000 + len(y))
    r = e10.ar1_pairs(yrs, y)
    ok = abs(r["phi"] - phi) < 0.03
    # gap handling: remove a block; pairs spanning the gap must be dropped
    keep = (yrs < 1500) | (yrs > 1600)
    r2 = e10.ar1_pairs(yrs[keep], y[keep])
    ok &= r2["n_pairs"] == keep.sum() - 2 and abs(r2["phi"] - phi) < 0.04
    # short series safety
    ok &= e10.ar1_pairs(yrs[:5], y[:5])["phi"] is None
    print(f"LEG 3 planted AR(1) + gaps: {'PASS' if ok else 'FAIL'}")
    return ok


def leg4():
    rng = np.random.default_rng(13)
    yrs = np.arange(1900, 2020)
    phi = 0.6
    e = [0.0]
    for _ in range(len(yrs)):
        e.append(phi * e[-1] + rng.normal())
    y = 5.0 + 0.3 * (yrs - 1900) + np.array(e[1:])
    r = e10.ar1_pairs(yrs, e10.detrend(yrs, y))
    ok = abs(r["phi"] - phi) < 0.12
    # raw levels on trended series must be near-unit-root (sanity contrast)
    ok &= e10.ar1_pairs(yrs, y)["phi"] > 0.9
    print(f"LEG 4 planted detrend recovery: {'PASS' if ok else 'FAIL'}")
    return ok


def leg5():
    # planted phi sets drive the reduced rule
    def decide(phis):
        allst = all(abs(p) < 1 for p in phis)
        if not allst:
            return "WITHDRAWN"
        vals = [sum(1 for p in phis if tl.rho(p, e10.W, b) > 1)
                for b in e10.BG_GRID]
        weakly = all(b >= a for a, b in zip(vals, vals[1:]))
        strictly = any(b > a for a, b in zip(vals, vals[1:]))
        return "OFFERED" if weakly and strictly else "WITHDRAWN"
    ok = decide([0.3, 0.8, 0.95]) == "OFFERED"        # 0.8,0.95 cross at 1.5
    ok &= decide([0.3, 0.4, 0.5]) == "WITHDRAWN"      # flat zero counts
    ok &= decide([0.3, 1.01, 0.5]) == "WITHDRAWN"     # explosive estimate
    print(f"LEG 5 planted decision-rule logic: {'PASS' if ok else 'FAIL'}")
    return ok


def leg6():
    res = e10.run_e10(str(_jst()))
    out = _HERE.parent / "outputs" / "e10_suite_check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2))
    back = json.loads(out.read_text())
    ok = back["experiment"] == "E10" and len(back["countries"]) == 18
    ok &= back["decision"]["reading"] in ("OFFERED", "WITHDRAWN")
    ok &= back["guards"]["max_dual_impl_diff"] <= 1e-12
    print(f"LEG 6 full run + roundtrip: {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    legs = [leg1(), leg2(), leg3(), leg4(), leg5(), leg6()]
    print(f"E10 SUITE ALL PASS: {all(legs)}")
    if not all(legs):
        sys.exit(1)


if __name__ == "__main__":
    main()
