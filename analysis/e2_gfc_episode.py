"""e2_gfc_episode.py - E2: GFC episode test (corroborating).
DESIGN.md Section 5 (pin 74c73ea165a7363c6714fe803fbe76b1).

Operator (frozen): for each of 17 sectors, phi_1 from 2003-2006 (pre-crisis),
phi_2 from 2008-2009 (crisis), D = (rho(phi_2)/rho(phi_1))^tau under SPEC-M
(W = 8, bg = 0.05, kappa = 0.75 -> tau = 6.0); realized outcome = excess
absolute I/S deviation during the 2007-2010 peak window (same deviation
definition as E1: fwd/base excess vs the pre-window mean). Spearman(D,
realized) across the 17 sectors, n = 17. Component bake-off, same episode and
same realized outcome: rho_crisis alone, |Delta phi| alone, tau alone - all
four rank correlations reported.

kappa note: tau = kappa*W is a single constant exponent applied to every
sector's rho-ratio; Spearman(D, realized) is rank-based and monotone in the
common exponent, so the E2 verdict is invariant to the kappa value (the pin
is for reproducibility). |Delta phi| and tau bake-off legs: tau is constant
across sectors here (W fixed), so its Spearman is degenerate (reported as
n/a - a constant cannot rank); the informative components are rho_crisis and
|Delta phi|.

Decision rule (frozen, corroborating): SUPPORT iff Spearman(D, realized) > 0
with one-sided p < 0.10 (n = 17, marginal + corroborating by construction)
AND combined-D point estimate >= each informative component's. WEAKENS
otherwise, reported honestly (E1 owns falsification; a negative E2 is reported
as evidence against, prominently).

AMENDMENT 2026-07-26 (DESIGN Section 5 amendment; Phase-5a finding F-07):
the ordering conjunct's READING is carried by the paired contrast, computed
within the same outcome-permutation machinery as the p-value - for each
permutation the same permuted outcome is ranked against D and both informative
components, so the contrast's null distribution preserves the covariance a
point comparison discards. Dedicated generator at SEED + 1; the original
three tests' draws are untouched and reproduce exactly. Committed reading:
RESOLVED-POSITIVE (c > 0, one-sided p < 0.05), RESOLVED-NEGATIVE (mirrored),
else UNRESOLVED. The verdict formula is unchanged; the report is amended.

Windows (frozen, inclusive, monthly): PRE 2003-01..2006-12; CRISIS
2008-01..2009-12; PEAK (realized) 2007-01..2010-12; the realized deviation's
baseline mean is the 2003-2006 pre-window level (the calm anchor the crisis
departs from).

Reads hashed data; writes analysis/outputs/e2_gfc_episode.json.
"""

from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "data"))
from theory_lib import rho  # noqa: E402
import pull  # noqa: E402

# E1 shares the canonical helpers; import them verbatim rather than reimplement.
from e1_rolling_validation import (BG_SPEC, KAPPA, TAU, W_SPEC,  # noqa: E402
                                   _rank, ols_phi, spearman)

OUT = _HERE / "outputs" / "e2_gfc_episode.json"

PRE = ("1992-01", "2003-01", "2006-12")     # (series_start_for_index, lo, hi)
CRISIS = ("2008-01", "2009-12")
PEAK = ("2007-01", "2010-12")
ALPHA = 0.10
B_BOOT = 2000
SEED = 20260713


def load_series_dated(sid: str) -> tuple[list[str], np.ndarray]:
    dates, vals = [], []
    with open(pull.RAW / f"fred_{sid}.csv") as f:
        next(f)
        for line in f:
            d, v = line.strip().split(",")
            if v != ".":
                dates.append(d[:7])  # YYYY-MM
                vals.append(float(v))
    return dates, np.asarray(vals)


def window(dates: list[str], y: np.ndarray, lo: str, hi: str) -> np.ndarray:
    idx = [i for i, d in enumerate(dates) if lo <= d <= hi]
    return y[idx]


def sector_d_and_realized(sid: str) -> tuple[float, float, float, float]:
    """Return (D, rho_crisis, abs_delta_phi, realized_excess_deviation)."""
    dates, y = load_series_dated(sid)
    pre = window(dates, y, PRE[1], PRE[2])
    cri = window(dates, y, CRISIS[0], CRISIS[1])
    peak = window(dates, y, PEAK[0], PEAK[1])
    phi1 = ols_phi(pre)
    phi2 = ols_phi(cri)
    r1 = rho(phi1, W_SPEC, BG_SPEC)
    r2 = rho(phi2, W_SPEC, BG_SPEC)
    d = (r2 / r1) ** TAU if r1 > 0 else np.nan
    mu_pre = pre.mean()
    realized = np.abs(peak - mu_pre).mean() - np.abs(pre - mu_pre).mean()
    return d, r2, abs(phi2 - phi1), realized


def boot_p(x: np.ndarray, realized: np.ndarray, rng: np.random.Generator,
           b: int = B_BOOT) -> tuple[float, float]:
    """One-sided positive-association p by permuting the 17 realized values
    against fixed x (cross-sectional n = 17; permutation is the exact small-n
    null - no serial structure across sectors to preserve)."""
    obs = spearman(x, realized)
    n = len(realized)
    rd = _rank(x); rd = rd - rd.mean()
    den0 = np.sqrt((rd ** 2).sum())
    count = 0
    for _ in range(b):
        perm = rng.permutation(n)
        ro = _rank(realized[perm]); ro = ro - ro.mean()
        den = den0 * np.sqrt((ro ** 2).sum())
        s = float((rd * ro).sum() / den) if den > 0 else 0.0
        if s >= obs:
            count += 1
    return obs, (count + 1) / (b + 1)


def paired_contrasts(D: np.ndarray, rho_c: np.ndarray, dphi: np.ndarray,
                     realized: np.ndarray, seed: int,
                     b: int = B_BOOT) -> dict:
    """AMENDMENT 2026-07-26 (F-07). Paired contrasts c = s_D - s_component,
    with a one-sided permutation p computed by ranking the SAME permuted
    outcome against all three predictors per draw (covariance preserved).
    Dedicated generator (seed = run seed + 1): the original tests' draw
    stream is untouched. Reading per the frozen DESIGN amendment."""
    rng = np.random.default_rng(seed)
    n = len(realized)
    obs = {"rho": spearman(D, realized) - spearman(rho_c, realized),
           "dphi": spearman(D, realized) - spearman(dphi, realized)}
    rD = _rank(D); rD = rD - rD.mean()
    rR = _rank(rho_c); rR = rR - rR.mean()
    rP = _rank(dphi); rP = rP - rP.mean()
    dD = np.sqrt((rD ** 2).sum())
    dR = np.sqrt((rR ** 2).sum())
    dP = np.sqrt((rP ** 2).sum())
    ge = {"rho": 0, "dphi": 0}
    le = {"rho": 0, "dphi": 0}
    for _ in range(b):
        ro = _rank(realized[rng.permutation(n)]); ro = ro - ro.mean()
        dn = np.sqrt((ro ** 2).sum())
        sD = float((rD * ro).sum() / (dD * dn)) if dD * dn > 0 else 0.0
        sR = float((rR * ro).sum() / (dR * dn)) if dR * dn > 0 else 0.0
        sP = float((rP * ro).sum() / (dP * dn)) if dP * dn > 0 else 0.0
        for key, c_pi in (("rho", sD - sR), ("dphi", sD - sP)):
            if c_pi >= obs[key]:
                ge[key] += 1
            if c_pi <= obs[key]:
                le[key] += 1

    def reading(key: str) -> tuple[float, float, str]:
        c = obs[key]
        p_up = (ge[key] + 1) / (b + 1)     # P(c_pi >= c_obs)
        p_dn = (le[key] + 1) / (b + 1)     # mirrored side
        if c > 0 and p_up < 0.05:
            lab = "resolved-positive"
        elif c < 0 and p_dn < 0.05:
            lab = "resolved-negative"
        else:
            lab = "unresolved"
        return c, p_up, lab

    c_r, p_r, l_r = reading("rho")
    c_p, p_p, l_p = reading("dphi")
    return dict(c_rho=c_r, c_rho_p=p_r, c_rho_reading=l_r,
                c_dphi=c_p, c_dphi_p=p_p, c_dphi_reading=l_p,
                B=b, seed=seed)


def run_panel(rows: list[tuple[str, float, float, float, float]],
              seed: int = SEED) -> dict:
    """rows: (name, D, rho_crisis, abs_dphi, realized) x 17. Verdict under the
    frozen E2 rule. Used verbatim by the synthetic suite and the real run."""
    rng = np.random.default_rng(seed)
    names = [r[0] for r in rows]
    D = np.array([r[1] for r in rows])
    rho_c = np.array([r[2] for r in rows])
    dphi = np.array([r[3] for r in rows])
    realized = np.array([r[4] for r in rows])
    ok = np.isfinite(D) & np.isfinite(realized)
    D, rho_c, dphi, realized = D[ok], rho_c[ok], dphi[ok], realized[ok]

    s_d, p_d = boot_p(D, realized, rng)
    s_rho, _ = boot_p(rho_c, realized, rng)
    s_dphi, _ = boot_p(dphi, realized, rng)
    components = {"rho_crisis": s_rho, "abs_delta_phi": s_dphi, "tau": None}
    informative = [v for k, v in components.items() if v is not None]
    combined_ge_components = all(s_d >= v - 1e-9 for v in informative)
    contrasts = paired_contrasts(D, rho_c, dphi, realized, seed + 1)

    verdict = ("SUPPORT" if s_d > 0 and p_d < ALPHA and combined_ge_components
               else "WEAKENS")
    return dict(n=int(ok.sum()), spearman_D=s_d, p_one_sided=p_d,
                components=components,
                combined_ge_components=combined_ge_components,
                contrasts=contrasts,
                verdict=verdict, sectors=names)


def main() -> None:
    members = [(sid, title) for sid, role, title in pull.SECTOR_MAP
               if role.startswith("member")]
    assert len(members) == 17
    rows = []
    for sid, title in members:
        d, rc, dp, rz = sector_d_and_realized(sid)
        rows.append((f"{sid} ({title})", d, rc, dp, rz))
    res = run_panel(rows)
    out = dict(experiment="E2", date="2026-07-13",
               design_pin="74c73ea165a7363c6714fe803fbe76b1",
               spec=dict(W=W_SPEC, bg=BG_SPEC, kappa=KAPPA, tau=TAU,
                         pre=PRE[1:], crisis=CRISIS, peak=PEAK,
                         alpha=ALPHA, B=B_BOOT, seed=SEED),
               **res)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    c = res["components"]
    k = res["contrasts"]
    print(f"E2 {res['verdict']}: Spearman(D, realized) = {res['spearman_D']:+.4f} "
          f"p = {res['p_one_sided']:.4f} (n = {res['n']}, corroborating); "
          f"components rho_crisis {c['rho_crisis']:+.3f} "
          f"|dphi| {c['abs_delta_phi']:+.3f} tau n/a; "
          f"combined >= components: {res['combined_ge_components']}")
    print(f"E2 paired contrasts (F-07 amendment, seed {k['seed']}, B {k['B']}): "
          f"c_rho {k['c_rho']:+.4f} p {k['c_rho_p']:.4f} [{k['c_rho_reading']}]; "
          f"c_dphi {k['c_dphi']:+.4f} p {k['c_dphi_p']:.4f} [{k['c_dphi_reading']}]")


if __name__ == "__main__":
    main()
