"""e5_monitor_tbl4.py - E5 monitoring extension: TBL-4 crossing-date
characterization (DESIGN.md Section 8, AMENDMENT 2026-07-24; OUTLINE ARG-18,
LB-E5-monitor family).

CHARACTERIZATION (v1.9.7): descriptive, no verdict. Per sector x spec x
episode (GFC onset 2008-09, COVID onset 2020-03; window onset +/- 24 months):
status in {above-throughout, never-above, crossing}, first/sustained upward
crossing dates, lead months vs onset. Backward-looking narrative, registered
as WEAKER than the Section 5.3 falsifier.

The rolling construction is E5's VERBATIM (trailing 60-month OLS AR(1);
rho under SPEC-R and SPEC-M) and the script HARD-TIES itself to the frozen
instrument: full-sample stats recomputed here must equal E5's committed output
rows exactly, and that artifact's MD5 is embedded as a hashed input.

Suite (synthetic, store-free): python analysis/e5_monitor_tbl4.py --suite
Real run (store-dependent):   python analysis/e5_monitor_tbl4.py

Writes analysis/outputs/e5_monitor_tbl4.json.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "data"))
from theory_lib import rho  # noqa: E402

OUT = _HERE / "outputs" / "e5_monitor_tbl4.json"
E5_OUT = _HERE / "outputs" / "e5_instability_ranking.json"

ROLL_WIN = 60
SPEC_R = dict(name="SPEC-R", W=12, bg=3.0)   # primary (saturation expected)
SPEC_M = dict(name="SPEC-M", W=8, bg=0.05)   # informative crossing story
ONSETS = {"gfc": "2008-09", "covid": "2020-03"}
WINDOW_MONTHS = 24   # onset +/- 24 (fixed pre-run; DESIGN amendment)
SUSTAIN_MONTHS = 3   # one quarter (fixed pre-run)
MFG_AGG = "AMTMIS"


# ------------------------------------------------------------------ loading --
def load_series_dated(sid: str):
    """Dated twin of e1's load_series: identical '.'-token filtering so the
    value array is index-aligned with the frozen loaders; returns (dates,
    values). Integrity: main() asserts values == e1.load_series(sid)."""
    import pull  # noqa: E402  (store-backed; imported only on real runs)
    path = pull.RAW / f"fred_{sid}.csv"
    dates, vals = [], []
    with open(path) as f:
        next(f)
        for line in f:
            d, v = line.strip().split(",")
            if v != ".":
                dates.append(d)
                vals.append(float(v))
    return dates, np.asarray(vals)


# ----------------------------------------------------------------- operator --
def rolling_rho_dated(dates: list[str], y: np.ndarray, W: int, bg: float):
    """E5's rolling construction, dated: rho at month t uses y[t-60:t]
    (strictly trailing). Returns (rho_dates, rho_array)."""
    from e1_rolling_validation import ols_phi  # noqa: E402
    n = len(y)
    rr, rd = [], []
    for t in range(ROLL_WIN, n):
        phi = ols_phi(y[t - ROLL_WIN:t])
        rr.append(rho(phi, W, bg))
        rd.append(dates[t])
    return rd, np.asarray(rr)


def full_sample_stats(rr: np.ndarray) -> dict:
    """E5's per-sector stats (verbatim definitions) for the integrity tie."""
    exceedance = np.maximum(rr - 1.0, 0.0)
    return dict(mean_exceedance=float(exceedance.mean()),
                peak_rho=float(rr.max()), mean_rho=float(rr.mean()),
                pct_months_above_1=float((rr > 1.0).mean()),
                n_months=int(len(rr)))


def episode_analysis(rho_dates: list[str], rr: np.ndarray,
                     onset_prefix: str) -> dict:
    """Mechanical crossing analysis over the onset +/- WINDOW_MONTHS window.
    UPWARD CROSSING at m iff rr[m] > 1 and rr[m-1] <= 1 (prior month from the
    FULL series, so a window opening above-boundary is not a crossing).
    SUSTAINED = first upward crossing with SUSTAIN_MONTHS consecutive months
    above (within data bounds). Lead months positive = crossing before onset.
    """
    onset_idx = None
    for i, d in enumerate(rho_dates):
        if d.startswith(onset_prefix):
            onset_idx = i
            break
    assert onset_idx is not None, f"onset {onset_prefix} not in rho dates"
    w0 = max(0, onset_idx - WINDOW_MONTHS)
    w1 = min(len(rr) - 1, onset_idx + WINDOW_MONTHS)
    above = rr > 1.0
    win = above[w0:w1 + 1]

    crossings = [m for m in range(w0, w1 + 1)
                 if above[m] and (m > 0 and not above[m - 1])]
    sustained = [m for m in crossings
                 if m + SUSTAIN_MONTHS <= len(rr)
                 and bool(above[m:m + SUSTAIN_MONTHS].all())]

    if win.all():
        status = "above-throughout"
    elif not win.any():
        status = "never-above"
    else:
        status = "crossing" if crossings else (
            "above-throughout" if win.all() else "mixed-no-upward-crossing")

    def _date(m):
        return rho_dates[m] if m is not None else "none"

    first = crossings[0] if crossings else None
    first_sus = sustained[0] if sustained else None
    return dict(
        status=status,
        above_at_window_start=bool(above[w0]),
        n_window_months=int(w1 - w0 + 1),
        share_above_in_window=float(win.mean()),
        first_crossing=_date(first),
        sustained_crossing=_date(first_sus),
        lead_months_vs_onset=(int(onset_idx - first)
                              if first is not None else None),
        onset_month=rho_dates[onset_idx])


# --------------------------------------------------------------------- main --
def run_monitoring(members, series_by_sid, e5_rows_by_spec) -> dict:
    """Full monitoring characterization. Used verbatim by the real run;
    the suite exercises episode_analysis and the operator on synthetics."""
    per_spec = {}
    for spec in (SPEC_R, SPEC_M):
        rows, key = [], spec["name"]
        for sid, title in members:
            dates, y = series_by_sid[sid]
            rd, rr = rolling_rho_dated(dates, y, spec["W"], spec["bg"])
            st = full_sample_stats(rr)
            # INTEGRITY TIE: must equal E5's committed row exactly.
            e5r = e5_rows_by_spec[key][sid]
            for f in ("mean_exceedance", "peak_rho", "mean_rho",
                      "pct_months_above_1", "n_months"):
                assert abs(st[f] - e5r[f]) < 1e-12, \
                    f"stats-tie broken: {key}/{sid}/{f}"
            episodes = {ep: episode_analysis(rd, rr, pre)
                        for ep, pre in ONSETS.items()}
            rows.append(dict(sector=sid, title=title, **st,
                             episodes=episodes))
        summary = {}
        for ep in ONSETS:
            eps = [r["episodes"][ep] for r in rows]
            mfg = next(r for r in rows if r["sector"] == MFG_AGG)
            m_ep = mfg["episodes"][ep]
            summary[ep] = dict(
                n_above_throughout=sum(e["status"] == "above-throughout"
                                       for e in eps),
                n_never_above=sum(e["status"] == "never-above" for e in eps),
                n_crossing=sum(e["status"] == "crossing" for e in eps),
                n_crossing_before_onset=sum(
                    e["status"] == "crossing"
                    and e["lead_months_vs_onset"] is not None
                    and e["lead_months_vs_onset"] > 0 for e in eps),
                mfg_status=m_ep["status"],
                mfg_first_crossing=m_ep["first_crossing"],
                mfg_sustained_crossing=m_ep["sustained_crossing"])
        per_spec[key] = dict(sectors=rows, summary=summary)
    return per_spec


def main() -> None:
    import pull  # noqa: E402
    from e1_rolling_validation import load_series  # noqa: E402
    members = [(sid, title) for sid, role, title in pull.SECTOR_MAP
               if role.startswith("member")]
    assert len(members) == 17
    e5_raw = E5_OUT.read_bytes()
    e5_md5 = hashlib.md5(e5_raw).hexdigest()
    e5 = json.loads(e5_raw.decode("utf-8"))
    e5_rows_by_spec = {
        "SPEC-R": {r["sector"]: r for r in e5["ranking_R"]},
        "SPEC-M": {r["sector"]: r for r in e5["ranking_M"]},
    }
    series_by_sid = {}
    for sid, _ in members:
        dates, y = load_series_dated(sid)
        assert np.array_equal(y, load_series(sid)), f"loader drift: {sid}"
        series_by_sid[sid] = (dates, y)

    per_spec = run_monitoring(members, series_by_sid, e5_rows_by_spec)
    out = dict(experiment="E5", date="2026-07-24",
               design_pin="74c73ea165a7363c6714fe803fbe76b1",
               e5_md5=e5_md5, roll_win=ROLL_WIN,
               spec_R=SPEC_R, spec_M=SPEC_M,
               window_months=WINDOW_MONTHS, sustain_months=SUSTAIN_MONTHS,
               onsets=ONSETS, per_spec=per_spec)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    for key in ("SPEC-R", "SPEC-M"):
        s = per_spec[key]["summary"]
        print(f"{key}: gfc above-throughout {s['gfc']['n_above_throughout']}"
              f"/17, crossing {s['gfc']['n_crossing']} "
              f"({s['gfc']['n_crossing_before_onset']} before onset); "
              f"covid above-throughout {s['covid']['n_above_throughout']}/17,"
              f" crossing {s['covid']['n_crossing']} "
              f"({s['covid']['n_crossing_before_onset']} before onset); "
              f"mfg gfc {s['gfc']['mfg_status']}"
              f" first {s['gfc']['mfg_first_crossing']}")
    print("E5-MONITOR written:", OUT.name)


# -------------------------------------------------------------------- suite --
def _mk_dates(n, y0=2000, m0=1):
    ds, y, m = [], y0, m0
    for _ in range(n):
        ds.append(f"{y:04d}-{m:02d}-01")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return ds


def suite() -> None:
    legs = []

    # Leg 1: above-throughout planted array
    n = 120
    ds = _mk_dates(n)
    rr = np.full(n, 1.2)
    ep = episode_analysis(ds, rr, "2002-01")
    legs.append(("above-throughout", ep["status"] == "above-throughout"
                 and ep["first_crossing"] == "none"))

    # Leg 2: never-above
    rr = np.full(n, 0.8)
    ep = episode_analysis(ds, rr, "2002-01")
    legs.append(("never-above", ep["status"] == "never-above"))

    # Leg 3: single planted upward crossing at exact month (index 30)
    rr = np.full(n, 0.9)
    rr[30:] = 1.1
    ep = episode_analysis(ds, rr, "2002-01")   # onset index 24; window 0..48
    legs.append(("planted-crossing-exact",
                 ep["status"] == "crossing"
                 and ep["first_crossing"] == ds[30]
                 and ep["sustained_crossing"] == ds[30]
                 and ep["lead_months_vs_onset"] == 24 - 30))

    # Leg 4: 2-month spike must NOT read sustained (SUSTAIN_MONTHS=3)
    rr = np.full(n, 0.9)
    rr[30:32] = 1.1
    ep = episode_analysis(ds, rr, "2002-01")
    legs.append(("spike-not-sustained",
                 ep["status"] == "crossing"
                 and ep["first_crossing"] == ds[30]
                 and ep["sustained_crossing"] == "none"))

    # Leg 5: window opens above-boundary -> NOT a crossing (prior month above;
    # the above-run ends INSIDE the window so the window is not all-above)
    rr = np.full(n, 0.9)
    rr[10:60] = 1.1                      # above long before the window
    ep = episode_analysis(ds, rr, "2004-01")   # onset 48; window 24..72
    legs.append(("no-false-crossing-at-entry",
                 ep["above_at_window_start"]
                 and ep["first_crossing"] == "none"
                 and ep["status"] == "mixed-no-upward-crossing"))

    # Leg 6: end-to-end operator - a regime change moves the trailing-60
    # estimate across the boundary. SPEC-M's boundary corner sits near
    # phi = 0.998, which stationary small-sample OLS cannot reach (downward
    # bias ~ (1+3*phi)/60), so the planted post-jump regime is a near-
    # deterministic linear ramp (unit-root drift): OLS AR(1) with intercept
    # reads phi ~ 1 there. Pre-jump: seeded white noise (phi ~ 0, far below).
    rng = np.random.default_rng(20260724)
    n2 = 200
    y = np.empty(n2)
    y[:130] = rng.normal(0, 1.0, 130)          # pre-jump: no persistence
    ramp = np.arange(n2 - 130, dtype=float)
    y[130:] = y[129] + ramp + rng.normal(0, 1e-6, n2 - 130)
    ds2 = _mk_dates(n2)
    rd, rr2 = rolling_rho_dated(ds2, y, SPEC_M["W"], SPEC_M["bg"])
    above = rr2 > 1.0
    jump_pos = 130 - ROLL_WIN            # rho index of the first post-jump month
    legs.append(("e2e-jump-crossing",
                 (not above[:jump_pos].any()) and above[jump_pos:].any()))

    # Leg 7: dated loader keeps dates aligned through "." filtering
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "fred_TEST.csv"
        p.write_text("DATE,TEST\n2000-01-01,1.0\n2000-02-01,.\n"
                     "2000-03-01,3.0\n")
        class _P:  # minimal pull stand-in
            RAW = pathlib.Path(td)
        sys.modules["pull"] = _P
        try:
            dts, vals = load_series_dated("TEST")
        finally:
            del sys.modules["pull"]
        legs.append(("dated-loader-filtering",
                     dts == ["2000-01-01", "2000-03-01"]
                     and np.array_equal(vals, np.array([1.0, 3.0]))))

    bad = [name for name, ok in legs if not ok]
    for name, ok in legs:
        print(f"  {name:28s} {'PASS' if ok else 'FAIL'}")
    if bad:
        print(f"SUITE RED: {bad}")
        sys.exit(2)
    print(f"SUITE GREEN: all {len(legs)} legs pass")


if __name__ == "__main__":
    if "--suite" in sys.argv:
        suite()
    else:
        main()
