"""theory_lib.py - shared theory-block primitives for The Escalation Cost.

Canonical companion-matrix construction carried verbatim from the committed
Measurement Trap implementation (analysis/theory_checks.py in that repo):
  A[0,0] = phi - bg/W;  A[0,1:] = -bg/W;  identity shift on the subdiagonal.
Characteristic polynomial: lam^W - phi*lam^(W-1) + (bg/W) * sum_{j<W} lam^j.
Stability boundary closed form: bg* = (pi^2/2) * (1 - phi) / (1 - phi^W).

All quantities ASCII-named per program convention. No external data anywhere.
"""

from __future__ import annotations

import numpy as np
from scipy.special import lambertw


def companion_np(phi: float, w: int, bg: float) -> np.ndarray:
    a = np.zeros((w, w))
    a[0, 0] = phi - bg / w
    a[0, 1:] = -bg / w
    for i in range(1, w):
        a[i, i - 1] = 1.0
    return a


def rho(phi: float, w: int, bg: float) -> float:
    return float(np.max(np.abs(np.linalg.eigvals(companion_np(phi, w, bg)))))


def dominant_left_eigvec(a: np.ndarray) -> tuple[complex, np.ndarray]:
    """Return (lam1, w1) with |lam1| = rho(A) and w1^T A = lam1 w1^T."""
    vals, vecs = np.linalg.eig(a.T)
    k = int(np.argmax(np.abs(vals)))
    return vals[k], vecs[:, k]


def bg_star(phi: float, w: int, tol: float = 1e-10) -> float:
    """Stability boundary in bg by bisection (agrees with the closed form)."""
    lo, hi = 0.0, 10.0
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if rho(phi, w, mid) < 1.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def bg_star_closed(phi: float, w: int) -> float:
    return (np.pi ** 2 / 2.0) * (1.0 - phi) / (1.0 - phi ** w)


def tau_sma(w: int, kappa: float) -> float:
    """Adaptation time tau = kappa * W, kappa = 1 - epsilon/Delta_phi in (0,1)."""
    return kappa * w


def damage(phi1: float, phi2: float, w: int, bg: float, kappa: float) -> float:
    """Theorem 3 identity: D = (rho_2/rho_1)^tau."""
    r1 = rho(phi1, w, bg)
    r2 = rho(phi2, w, bg)
    return (r2 / r1) ** tau_sma(w, kappa)


def loss(w_val: float, a: float, est_num: float, c_d: float = 1.0,
         c_e: float = 1.0) -> float:
    """THM-2 cost model: L(W) = c_D exp(a W) + c_E est_num / W,
    a = kappa ln(rho_2) > 0, est_num = (1 - phi^2)."""
    return c_d * np.exp(a * w_val) + c_e * est_num / w_val


def wstar_closed(a: float, est_num: float, c_d: float = 1.0,
                 c_e: float = 1.0) -> float:
    """Exact Lambert-W optimum from Appendix G.3(iii):
    W* = (2/a) * W_L( (a/2) * sqrt( c_E est_num / (c_D a) ) )."""
    b = c_e * est_num / (c_d * a)
    z = (a / 2.0) * np.sqrt(b)
    return float(np.real((2.0 / a) * lambertw(z, 0)))


def interiority_c(a: float, est_num: float, c_d: float = 1.0,
                  c_e: float = 1.0) -> bool:
    """Condition (C) from G.3(ii) at the W = 1 left end:
    c_E (1 - phi^2) > c_D a exp(a)."""
    return c_e * est_num > c_d * a * np.exp(a)


def ols_phi(y: np.ndarray) -> float:
    """AR(1) coefficient by OLS with intercept (pre-registered estimator)."""
    x = y[:-1]
    z = y[1:]
    xm, zm = x.mean(), z.mean()
    return float(((x - xm) * (z - zm)).sum() / ((x - xm) ** 2).sum())


def yw_phi(y: np.ndarray) -> float:
    """Yule-Walker lag-1 estimate (diagnostic comparator)."""
    yc = y - y.mean()
    return float((yc[1:] * yc[:-1]).sum() / (yc ** 2).sum())


# Frozen T1 verification grid (DESIGN.md Section 1, verbatim)
GRID_PHI1 = (0.10, 0.30, 0.50, 0.70, 0.85)
GRID_PHI2 = (0.60, 0.75, 0.90, 0.95, 0.99)
GRID_W = (4, 8, 12, 24, 60)
GRID_BG = (0.02, 0.05, 0.20, 0.50)
GRID_KAPPA = (0.5, 0.75, 0.9)  # verification sweep over eps/Delta_phi in (0,1)
N_SEEDS = 100
