"""e6_capacity_threshold.py - E6: capacity-utilization stability threshold
(semiconductors). DESIGN.md Section 9 (pin 74c73ea165a7363c6714fe803fbe76b1).

Tests the empirical link between semiconductor capacity utilization and the
spectral radius rho, and locates the rho = 1 crossing relative to the Factory
Physics 85-90% utilization knee (Hopp-Spearman VUT nonlinearity).

Operator (frozen):
  - Fed G.17 semiconductor capacity utilization CAPUTLG3344S (monthly, %);
  - NAICS 334 (computers/electronics, A34SIS) rho series from E5's pipeline
    (rolling 60-month persistence -> rho), SPEC-R primary + SPEC-M robustness;
  - align rho_t to utilization_t by month; bin months by utilization into
    < 75, 75-85, 85-90, >= 90; mean rho per bin; check monotonicity across
    bins and identify the crossing bin (first bin whose mean rho >= 1);
  - report the current (latest) utilization reading.

Decision rule (frozen): SUPPORT iff mean rho increases MONOTONICALLY across the
bins (in utilization order) AND the rho = 1.0 crossing lies in the 85-90 or
>= 90 bin (consistent with the Factory Physics knee). REFUTE (claim dropped)
if no monotone relationship, or the crossing is below 80% / absent - the
monitoring-benchmark section is cut or reframed. Bins with < 6 months are
reported but excluded from the monotonicity test (thin-bin guard).

Writes analysis/outputs/e6_capacity_threshold.json.
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
from e1_rolling_validation import ols_phi  # noqa: E402
from e2_gfc_episode import load_series_dated  # noqa: E402

OUT = _HERE / "outputs" / "e6_capacity_threshold.json"

CHIPS_MFG = "A34SIS"          # NAICS 334 computers/electronics I/S
UTIL_SERIES = "CAPUTLG3344S"  # Fed G.17 semiconductor capacity utilization
ROLL_WIN = 60
SPEC_R = dict(name="SPEC-R", W=12, bg=3.0)
SPEC_M = dict(name="SPEC-M", W=8, bg=0.05)
BIN_EDGES = [(-np.inf, 75.0), (75.0, 85.0), (85.0, 90.0), (90.0, np.inf)]
BIN_LABELS = ["<75", "75-85", "85-90", ">=90"]
THIN_BIN = 6


def rho_series_dated(sid: str, W: int, bg: float) -> tuple[list[str], np.ndarray]:
    """Rolling 60-month rho for a sector, returned with the month labels at
    which each rho is computed (label = the month at the END of the window)."""
    dates, y = load_series_dated(sid)
    out_dates, rhos = [], []
    for t in range(ROLL_WIN, len(y)):
        phi = ols_phi(y[t - ROLL_WIN:t])
        rhos.append(rho(phi, W, bg))
        out_dates.append(dates[t])   # rho at month t uses the trailing window
    return out_dates, np.asarray(rhos)


def bin_and_analyze(rho_dates: list[str], rho_vals: np.ndarray,
                    util_dates: list[str], util_vals: np.ndarray) -> dict:
    """Align rho to utilization by month, bin, compute per-bin mean rho, test
    monotonicity, and locate the crossing bin."""
    util_by_month = {d: v for d, v in zip(util_dates, util_vals)}
    paired_u, paired_r = [], []
    for d, r in zip(rho_dates, rho_vals):
        if d in util_by_month:
            paired_u.append(util_by_month[d])
            paired_r.append(r)
    paired_u = np.asarray(paired_u)
    paired_r = np.asarray(paired_r)

    bins = []
    for (lo, hi), label in zip(BIN_EDGES, BIN_LABELS):
        mask = (paired_u >= lo) & (paired_u < hi)
        n = int(mask.sum())
        mean_rho = float(paired_r[mask].mean()) if n > 0 else None
        bins.append(dict(label=label, lo=(None if lo == -np.inf else lo),
                         hi=(None if hi == np.inf else hi), n=n,
                         mean_rho=mean_rho))

    # monotonicity across bins with adequate n (in utilization order)
    thick = [b for b in bins if b["n"] >= THIN_BIN and b["mean_rho"] is not None]
    monotone = all(thick[i]["mean_rho"] <= thick[i + 1]["mean_rho"] + 1e-12
                   for i in range(len(thick) - 1)) if len(thick) >= 2 else False

    # crossing bin = first bin (utilization order) whose mean rho >= 1
    crossing_label = None
    for b in bins:
        if b["mean_rho"] is not None and b["n"] >= THIN_BIN and b["mean_rho"] >= 1.0:
            crossing_label = b["label"]
            break
    crossing_at_knee = crossing_label in ("85-90", ">=90")

    return dict(n_paired=int(len(paired_r)), bins=bins,
                monotone=bool(monotone), crossing_bin=crossing_label,
                crossing_at_knee=bool(crossing_at_knee))


def run_analysis(spec: dict) -> dict:
    rd, rv = rho_series_dated(CHIPS_MFG, spec["W"], spec["bg"])
    ud, uv = load_series_dated(UTIL_SERIES)
    res = bin_and_analyze(rd, rv, ud, uv)
    res["spec"] = spec
    res["current_utilization"] = float(uv[-1])
    res["current_utilization_month"] = ud[-1]
    return res


def run_experiment() -> dict:
    """Full E6: primary SPEC-R verdict + SPEC-M robustness. Used verbatim by
    the synthetic suite and the real run."""
    primary = run_analysis(SPEC_R)
    robust = run_analysis(SPEC_M)
    verdict = ("SUPPORT" if primary["monotone"] and primary["crossing_at_knee"]
               else "REFUTE")
    return dict(primary_spec_R=primary, robustness_spec_M=robust,
                verdict=verdict)


def main() -> None:
    res = run_experiment()
    out = dict(experiment="E6", date="2026-07-13",
               design_pin="74c73ea165a7363c6714fe803fbe76b1", **res)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    p = res["primary_spec_R"]
    print(f"E6 {res['verdict']}: SPEC-R monotone={p['monotone']}, "
          f"crossing bin={p['crossing_bin']} (at knee: {p['crossing_at_knee']}); "
          f"current utilization {p['current_utilization']:.1f}% "
          f"({p['current_utilization_month']})")
    print("SPEC-R mean rho by utilization bin:")
    for b in p["bins"]:
        mr = f"{b['mean_rho']:.3f}" if b["mean_rho"] is not None else "n/a"
        print(f"  {b['label']:6s} n={b['n']:4d}  mean rho {mr}")


if __name__ == "__main__":
    main()
