"""e3_covid_episode.py - E3: COVID episode test (pre-registered expected null).
DESIGN.md Section 6 (pin 74c73ea165a7363c6714fe803fbe76b1).

Purpose: probe the theorem's stated DOMAIN BOUNDARY. The Measurement Damage
mechanism models persistence INCREASES (Minsky tightening), not compound
shocks where persistence DROPS. COVID is the canonical compound shock, so the
pre-registered expectation is a NULL correlation - a null here CONFIRMS the
boundary, it does not weaken the thesis. Verdict polarity is therefore
inverted relative to E1/E2.

Operator (frozen): identical to E2 with phi_1 from 2017-2019, phi_2 from
2020-2021, realized deviation over 2020-2022; ADDITIONALLY the per-sector
direction of the persistence change (phi_2 - phi_1) is computed.

Decision rule (pre-registered, three-way):
  CONSISTENT-WITH-BOUNDARY (the expected, thesis-consistent outcome):
      |Spearman(D, realized)| non-significant (p > 0.10) AND persistence
      DROPPED in a majority of sectors (> 8 of 17).
  ANOMALY-REQUIRING-EXPLANATION: EITHER a strongly positive SIGNIFICANT
      correlation (p < 0.10, S > 0 - flatters the metric but contradicts the
      stated mechanism; reported as a problem, not a win), OR persistence
      ROSE in a majority AND the correlation is null (which would convert
      COVID from boundary case to genuine counter-evidence; reported as such).
  (A negative or mixed non-significant result with persistence dropping still
  reads CONSISTENT-WITH-BOUNDARY - the boundary claim is about the ABSENCE of
  the E1 mechanism, plus the falsifiable persistence-direction prediction.)

Reuses the E2 pipeline verbatim (windows are the only parameter change);
writes analysis/outputs/e3_covid_episode.json.
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
from e1_rolling_validation import BG_SPEC, KAPPA, TAU, W_SPEC, ols_phi  # noqa: E402
from e2_gfc_episode import boot_p, load_series_dated, spearman, window  # noqa: E402

OUT = _HERE / "outputs" / "e3_covid_episode.json"

PRE = ("2017-01", "2019-12")
CRISIS = ("2020-01", "2021-12")
PEAK = ("2020-01", "2022-12")
ALPHA = 0.10
B_BOOT = 2000
SEED = 20260713


def sector_row(sid: str) -> tuple[float, float, float]:
    """Return (D, realized_excess_deviation, delta_phi) for the COVID windows."""
    dates, y = load_series_dated(sid)
    pre = window(dates, y, PRE[0], PRE[1])
    cri = window(dates, y, CRISIS[0], CRISIS[1])
    peak = window(dates, y, PEAK[0], PEAK[1])
    phi1 = ols_phi(pre)
    phi2 = ols_phi(cri)
    r1 = rho(phi1, W_SPEC, BG_SPEC)
    r2 = rho(phi2, W_SPEC, BG_SPEC)
    d = (r2 / r1) ** TAU if r1 > 0 else np.nan
    mu_pre = pre.mean()
    realized = np.abs(peak - mu_pre).mean() - np.abs(pre - mu_pre).mean()
    return d, realized, phi2 - phi1


def run_panel(rows: list[tuple[str, float, float, float]],
              seed: int = SEED) -> dict:
    """rows: (name, D, realized, delta_phi) x 17. Verdict under the frozen
    three-way E3 rule. Used verbatim by the synthetic suite and the real run."""
    rng = np.random.default_rng(seed)
    D = np.array([r[1] for r in rows])
    realized = np.array([r[2] for r in rows])
    dphi = np.array([r[3] for r in rows])
    ok = np.isfinite(D) & np.isfinite(realized)
    D, realized, dphi = D[ok], realized[ok], dphi[ok]
    n = int(ok.sum())

    s_d, p_d = boot_p(D, realized, rng)
    n_dropped = int((dphi < 0).sum())
    majority_dropped = n_dropped > n / 2
    significant = p_d < ALPHA

    if significant and s_d > 0:
        verdict = "ANOMALY-REQUIRING-EXPLANATION"
        anomaly_kind = "positive-significant-contradicts-mechanism"
    elif (not significant) and (not majority_dropped):
        verdict = "ANOMALY-REQUIRING-EXPLANATION"
        anomaly_kind = "persistence-rose-majority-null-correlation"
    else:
        verdict = "CONSISTENT-WITH-BOUNDARY"
        anomaly_kind = None

    return dict(n=n, spearman_D=s_d, p_one_sided=p_d, significant=significant,
                n_dropped=n_dropped, majority_dropped=majority_dropped,
                verdict=verdict, anomaly_kind=anomaly_kind,
                sectors=[r[0] for r in rows])


def main() -> None:
    members = [(sid, title) for sid, role, title in pull.SECTOR_MAP
               if role.startswith("member")]
    assert len(members) == 17
    rows = []
    for sid, title in members:
        d, rz, dp = sector_row(sid)
        rows.append((f"{sid} ({title})", d, rz, dp))
    res = run_panel(rows)
    out = dict(experiment="E3", date="2026-07-13",
               design_pin="74c73ea165a7363c6714fe803fbe76b1",
               spec=dict(W=W_SPEC, bg=BG_SPEC, kappa=KAPPA, tau=TAU,
                         pre=PRE, crisis=CRISIS, peak=PEAK, alpha=ALPHA,
                         B=B_BOOT, seed=SEED),
               **res)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print(f"E3 {res['verdict']}"
          + (f" ({res['anomaly_kind']})" if res['anomaly_kind'] else "")
          + f": Spearman(D, realized) = {res['spearman_D']:+.4f} "
          f"p = {res['p_one_sided']:.4f} (n = {res['n']}); "
          f"persistence dropped in {res['n_dropped']}/{res['n']} sectors "
          f"(majority-dropped: {res['majority_dropped']})")


if __name__ == "__main__":
    main()
