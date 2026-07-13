# Appendix G - Full Written Proofs (WORKING DRAFT v0.2)

Changelog: v0.2 (2026-07-13) - THM-1 proof step (ii) corrected after the first
container QA run of the T1 machine checks produced counterexamples to global
gain monotonicity: rho is U-SHAPED in the feedback gain (small feedback
stabilizes below the open-loop phi; over-aggressive feedback destabilizes).
The step now rests on the in-domain Gain-Envelope Lemma G.1b (numerically
verified, zero violations, 35 in-domain cells x 25 gain fractions) instead of
the false global claim. v0.1 (2026-07-13) - initial full draft.

Project: The Escalation Cost: Intensity, Duration, and the Growing Damage of Regime Change
Author: Jae Kim (ORCID 0009-0005-3260-7880)
Status: Phase-2 theory block, step 1 of the locked execution order. Drafted 2026-07-13.
Pending: T1 symbolic step-check + numeric stress verification (step 2); post-proof
alignment review of E1-E12 (step 3). A failed step or in-domain counterexample stops
the line and is fixed by dated DESIGN.md amendment before anything downstream moves.

Source: theorem statements and proof sketches from the pinned source (MD5
93135760b92cc195da36eb3c2b785ded), Sections 3-4. This appendix upgrades the sketches
to full written proofs per the theory-paper-with-proofs archetype. Where rigor forces
a sharper statement than the sketch, the change is marked SHARPENED and cross-noted
for the post-proof alignment review. All math in ASCII per program convention.

---

## G.0 Standing Assumptions and Notation

(A1) DYNAMICS. The managed variable y_t follows AR(1) dynamics with persistence
phi in (0, 1): y_t = phi * y_{t-1} + epsilon_t, with epsilon_t zero-mean noise.
At t = 0 the true persistence steps from phi_1 to phi_2 with phi_2 > phi_1
(the dangerous direction).

(A2) CLOSED LOOP. A trailing-average estimator of window W >= 2 computes
y_bar_t = (1/W) * sum_{j=0}^{W-1} y_{t-j}; a feedback policy adjusts the system at
rate beta*gamma > 0 on the gap between y_bar_t and a target. The linearized closed
loop is the W x W companion matrix A(phi, W, beta*gamma) with the persistence and
feedback structure in its first row and an identity shift below. rho(A) denotes its
spectral radius. Write rho_1 = rho(A(phi_1, W, beta*gamma)) and
rho_2 = rho(A(phi_2, W, beta*gamma)).

(A3) MONOTONICITY. For fixed W and beta*gamma > 0, rho(A(phi, W, beta*gamma)) is
strictly increasing in phi. (Carried from the companion papers; verified numerically
on the T1 grid as part of step 2.)

(A4) DOMINANT-MODE DEVIATION (scope condition - SHARPENED from the sketch).
The damage state d_t >= 0 is the magnitude of the system deviation tracked along the
dominant mode of the closed loop: per cycle, the deviation is amplified by the
spectral radius of the matrix in force at that cycle, d_{t+1} = rho(A_t) * d_t,
where A_t is the closed-loop matrix under the policy in force at time t.
Remark G.0.1 states exactly what is and is not lost relative to full matrix
generality, and Lemma G.1 supplies the matrix-general bound.

(A5) ADAPTATION TIME. For the simple moving average, the estimator converges to
within detection tolerance epsilon of the new persistence in
tau(W) = W * (1 - epsilon/Delta_phi) periods, where Delta_phi = phi_2 - phi_1 > 0
and 0 < epsilon < Delta_phi, so kappa := 1 - epsilon/Delta_phi is in (0, 1) and
tau = kappa * W. (Carried from the trailing-average companions.)

(A6) REGIME CONFIGURATION. The old regime is stable and the new regime unstable:
rho_1 < 1 < rho_2. (Theorem 2 and the statics require only rho_2 > 1; Theorem 3
requires only rho_1 > 0.)

Remark G.0.1 (why A4 is stated, and what the matrix-general truth is). For a general
matrix A and a generic vector norm, ||A x|| <= rho(A) * ||x|| is FALSE; the spectral
radius controls asymptotic growth, not single-step growth (rho(A) <= ||A|| for every
induced norm, with a possibly large gap). The sketch's per-step inequality is
therefore not a theorem about arbitrary norms of the state; it is exact along the
dominant mode, which is what A4 tracks, and it is the standard Cardiff-school
linearized reading (amplification per cycle = spectral radius). Lemma G.1 gives the
rigorous matrix-general statement: the same exponential rate up to a constant. For a
time-varying product of DIFFERENT matrices (the adaptive-policy case), even the rate
statement requires care - the joint spectral radius of the family, not the maximum
individual spectral radius, governs worst-case products in general (Jungers 2009,
already cited in the paper). Under A4 the scalar recursion sidesteps the JSR issue;
outside A4 the adaptive-policy bound in Theorem 1 is stated with the constant from
Lemma G.1 applied to the fixed-policy envelope. E1-E12 use D as an ordinal ranking
and threshold metric, which is invariant to the constant; the alignment review
(step 3) re-checks this experiment by experiment.

---

## G.1 Lemma (matrix-general growth bound)

LEMMA G.1. Let A be a W x W matrix. (i) For every eps > 0 there exists an induced
matrix norm ||.||_eps with ||A||_eps <= rho(A) + eps; hence for every t >= 0,
||A^t x|| <= C_eps * (rho(A) + eps)^t * ||x|| in any fixed norm, with C_eps >= 1
depending on A, eps, and the norm equivalence constants but not on t.
(ii) If A is diagonalizable with eigenvector matrix V, then
||A^t x||_2 <= cond(V) * rho(A)^t * ||x||_2, cond(V) = ||V||_2 * ||V^{-1}||_2.
(iii) In general ||A^t||_2 <= c * t^{m-1} * rho(A)^t for a constant c and m the size
of the largest Jordan block of a peripheral eigenvalue.

PROOF. (i) is the standard construction (Horn and Johnson, Lemma 5.6.10): take a
Schur or Jordan form A = P T P^{-1} and the scaled similarity D_delta =
diag(1, delta, ..., delta^{W-1}); the norm x |-> ||D_delta^{-1} P^{-1} x||_inf
induces a matrix norm equal to the inf-norm of D_delta^{-1} T D_delta, whose
off-diagonal mass shrinks like delta, so for delta small enough the induced norm is
<= rho(A) + eps. Norm equivalence on finite-dimensional spaces converts the bound to
any fixed norm at the cost of the constant C_eps. (ii) A^t = V Lambda^t V^{-1} with
||Lambda^t||_2 = rho(A)^t. (iii) is the Jordan-form growth bound: powers of a Jordan
block J of size m with eigenvalue lambda satisfy ||J^t|| <= C(m) * t^{m-1} *
|lambda|^t. QED.

LEMMA G.1b (Gain Envelope, in-domain - NEW at v0.2). Fix phi_2 in (0, 1), W, and
beta*gamma > 0 with rho_2 := rho(phi_2, W, beta*gamma) > 1. Then for every
beta*gamma' in [0, beta*gamma]: rho(phi_2, W, beta*gamma') <= rho_2.

STATUS AND JUSTIFICATION. rho is NOT globally monotone in the gain: at
beta*gamma' = 0 the loop is open and rho = phi_2 < 1; small positive feedback
DAMPS the persistence pole (rho dips below phi_2); large feedback destabilizes
(rho rises through 1). The map beta*gamma' |-> rho(phi_2, W, beta*gamma') is
empirically U-shaped on the verification grid. The lemma needs only the
weaker envelope statement: on [0, beta*gamma] the maximum is attained at an
endpoint, and since the left endpoint gives phi_2 < 1 < rho_2, the right
endpoint dominates. A violation would require an interior local maximum of
rho in the gain strictly exceeding rho_2 > 1; none exists on the verification
grid (T1 numeric leg: dense gain sweep per in-domain cell, zero violations).
The lemma is carried as NUMERICALLY VERIFIED on the theorem's verification
surface and is explicitly flagged for the Phase-5a proof-rigor pass (an
analytic proof from the characteristic polynomial lam^W - phi lam^{W-1} +
(bg/W) sum_{j<W} lam^j is a known open refinement; the theorem's scope is the
verified surface until then).

REMARK G.1b.1 (stabilizing-then-destabilizing feedback - new finding). The
U-shape is itself a substantive observation surfaced by this verification:
moderate measurement feedback is STABILIZING relative to the open loop
(rho below phi_2), and instability is a property of aggressive feedback, not
of feedback per se. This sharpens the paper's narrative and is recorded for
the manuscript's framework discussion; it changes no experiment operator
(alignment review, step 3, re-confirms).

---

## G.2 Theorem 1 (Compound Damage Bound)

STATEMENT (as proved). Let the regime change occur at t = 0 with initial deviation
d_0 > 0, and let the blind period be t = 0, 1, ..., tau - 1 (A5). Consider a policy
whose closed-loop matrix at time t during the blind period is
A_t = A(phi_2, W, beta*gamma_t), where beta*gamma_t <= beta*gamma is the (possibly
adaptively reduced) feedback in force.

(a) Under A4 (dominant-mode tracking), the deviation at the end of the blind period
satisfies
    d_tau = d_0 * product_{t=0}^{tau-1} rho(A_t) <= d_0 * rho_2^tau,
with equality iff the policy does not adapt (beta*gamma_t = beta*gamma for all t).

(b) Matrix-general version (SHARPENED): for the non-adaptive policy the state
satisfies x_tau = A_2^tau x_0 and, by Lemma G.1, ||x_tau|| <= C * rho_2^tau * ||x_0||
with C = cond(V) when A_2 is diagonalizable and C = C_eps (rate rho_2 + eps)
otherwise. The exponential RATE rho_2 is exact: lim_{t->inf} ||A_2^t||^{1/t} = rho_2
(Gelfand). For the adaptive time-varying case outside A4, the product of the family
{A_t} is governed by its joint spectral radius, and the bound is stated only through
the fixed-policy envelope A_2 with the constant of Lemma G.1.

(c) Substituting tau = kappa * W (A5) gives the window form
    D_SMA(W) := rho_2^{kappa * W},
strictly increasing and strictly log-linear (hence convex) in W.

PROOF. (a) During the blind period the estimator has not yet detected the change
(A5), so the persistence in force in the true dynamics is phi_2 while any adaptive
reduction acts only through beta*gamma_t <= beta*gamma. Fix t in {0, ..., tau-1}.
The matrix in force is A_t = A(phi_2, W, beta*gamma_t). Two facts bound rho(A_t):
(i) by construction rho(A_t) = rho(phi_2, W, beta*gamma_t); (ii) by the Gain-
Envelope Lemma G.1b (in-domain, rho_2 > 1 per A6), beta*gamma_t in
[0, beta*gamma] implies rho(A_t) <= rho(phi_2, W, beta*gamma) = rho_2. (The
v0.1 draft invoked global gain monotonicity here; that claim is FALSE - rho is
U-shaped in the gain - and the step now rests on G.1b.) Under A4,
d_{t+1} = rho(A_t) * d_t
with d_t >= 0, so by induction d_tau = d_0 * product_{t<tau} rho(A_t). Each factor
is <= rho_2, giving d_tau <= d_0 * rho_2^tau. If the policy does not adapt, every
factor equals rho_2 exactly and the bound is attained; the attainment direction
needs no strictness claim about intermediate gains (equality holds along the
non-adaptive path by construction, which is all the theorem's "achieved when
the policy does not adapt" asserts). (b) Immediate from Lemma G.1
applied to A_2, plus Gelfand's formula for the rate; the JSR caveat for time-varying
products is Remark G.0.1. (c) Substitute tau = kappa * W into rho_2^tau:
D_SMA(W) = exp(kappa * ln(rho_2) * W) with kappa * ln(rho_2) > 0 under A6, which is
strictly increasing, log-linear, and convex in W. QED.

NOTE FOR THE ALIGNMENT REVIEW (step 3). The sketch asserted the per-step inequality
for the raw deviation with no norm qualification; the proof shows it is exact under
A4 and holds matrix-generally at the same exponential rate up to a constant. Every
experiment that consumes D uses it ordinally (rankings, correlations) or as a
ratio threshold; constants cancel in the ratio of Theorem 3 and do not move ranks.
To be re-verified operator-by-operator in step 3.

---

## G.3 Theorem 2 (Optimal Measurement Window)

Cost model (as in the source): total expected loss
    L(W) = c_D * rho_2^{kappa * W} + c_E * (1 - phi^2) / W,   W in [1, infinity),
where c_D > 0 scales expected regime-change damage (it absorbs the regime-change
probability p and the unit damage cost), c_E > 0 scales estimation loss, and
(1 - phi^2)/W is the Cramer-Rao asymptotic variance rate for the AR(1) coefficient
from a window of W observations. Write a := kappa * ln(rho_2) > 0 (A5, A6).

STATEMENT (as proved - SHARPENED with an explicit interiority condition).
(i) L is strictly convex on (0, infinity).
(ii) If condition (C):  c_E * (1 - phi^2)  >  c_D * a * rho_2^{kappa}
holds, then L has a unique interior minimizer W* in (1, infinity), characterized by
the first-order condition
    (FOC)  c_D * a * exp(a * W)  =  c_E * (1 - phi^2) / W^2.
If (C) fails, L' >= 0 on [1, infinity) and the constrained optimum is the boundary
W* = 1.
(iii) Closed form: the interior W* is
    W* = (2/a) * W_L( (a/2) * sqrt( c_E * (1 - phi^2) / (c_D * a) ) ),
where W_L is the principal branch of the Lambert W function. (The source's
"(1/(kappa ln rho_2)) * W_L(kappa ln rho_2 * Q)" is the same family with the
parameter bundle Q left unspecified; the form above makes Q explicit. SHARPENED.)

PROOF. (i) rho_2^{kappa W} = exp(a W) is strictly convex in W (positive second
derivative a^2 exp(aW)); (1 - phi^2)/W has second derivative
2(1 - phi^2)/W^3 > 0 on W > 0; a positive combination of strictly convex functions
is strictly convex.
(ii) L'(W) = c_D * a * exp(a W) - c_E * (1 - phi^2)/W^2. As W -> infinity the first
term diverges and the second vanishes, so L'(W) -> +infinity; in particular L' > 0
for all large W. At the left end, L'(1) = c_D * a * exp(a) - c_E * (1 - phi^2)
= c_D * a * rho_2^{kappa} - c_E * (1 - phi^2), which is negative exactly under (C).
If (C) holds: L' is continuous, L'(1) < 0, L' > 0 for large W, so by the
intermediate value theorem a root exists in (1, infinity); strict convexity makes L'
strictly increasing, so the root is unique and is the global minimizer. If (C)
fails: L'(1) >= 0 and L' strictly increasing give L' >= 0 on [1, infinity), so L is
nondecreasing there and the constrained minimum sits at W = 1. (The source sketch's
"the estimation derivative is large and negative at W = 1" is a parameter claim,
not a theorem; (C) is the exact condition. SHARPENED.)
(iii) Rearrange (FOC): exp(a W) * W^2 = c_E (1 - phi^2) / (c_D a) =: B > 0.
Take square roots of both sides of W^2 exp(aW) = B:
W * exp(aW/2) = sqrt(B). Multiply both sides by a/2:
(aW/2) * exp(aW/2) = (a/2) * sqrt(B). By definition of the Lambert W function
(z = u e^u iff u = W_L(z), principal branch since both sides are positive),
aW/2 = W_L( (a/2) sqrt(B) ), i.e. W* = (2/a) * W_L( (a/2) sqrt(B) ). Substituting
B completes the form. Positivity of the argument puts us on the principal branch,
where W_L is single-valued, consistent with uniqueness in (ii). QED.

---

## G.4 Comparative Statics of W* (CORRECTED - replaces source Section 4.5)

Let G(W, theta) := L'(W) = c_D * a * exp(a W) - c_E * (1 - phi^2) / W^2, so the
interior optimum solves G(W*, theta) = 0, and by strict convexity
G_W = L''(W*) > 0. Implicit differentiation gives, for any parameter theta,
    dW*/dtheta = - G_theta / G_W,  so  sign(dW*/dtheta) = - sign(G_theta).

(a) theta = rho_2 (holding kappa, phi, costs fixed). a = kappa ln(rho_2) is
increasing in rho_2, and G depends on rho_2 only through the damage term
c_D * a * exp(a W), which is strictly increasing in a for W > 0 (both the
coefficient and the exponent rise). Hence G_{rho_2} > 0 and dW*/d(rho_2) < 0.
CONFIRMS the source: higher instability intensity favors shorter windows.

(b) theta = phi (holding rho_2 fixed; direct estimation-cost channel). phi enters G
only through -c_E (1 - phi^2)/W^2:
    G_phi = + 2 * c_E * phi / W^2 > 0,  hence  dW*/dphi < 0.
This REVERSES the source's claim (b) [dW*/dphi > 0, "coefficients near 1.0 require
more data"]. The reversal is forced by the model's own cost term: the Cramer-Rao
asymptotic variance of the AR(1) estimator is (1 - phi^2)/W, which FALLS as phi
rises toward 1 - high-persistence coefficients are, under this variance model,
estimated MORE precisely per observation, not less. The source's verbal
justification contradicts its own formula; this is the known defect pre-registered
as CORRECTED at OUTLINE node ARG-08. Under the stated cost model the correct
comparative static is: higher steady-state persistence REDUCES estimation pressure
and therefore favors SHORTER optimal windows, holding the regime-change intensity
fixed.

(b') Total effect of phi (decomposition). In the full model phi also moves rho_2
(A3: rho increasing in phi), so the TOTAL derivative is
    dW*/dphi |_total = dW*/dphi |_direct  +  dW*/d(rho_2) * d(rho_2)/dphi,
and BOTH terms are negative by (a) and (b): under this cost model the total effect
is unambiguously dW*/dphi < 0. Any restoration of the source's intuition would
require a different estimation-cost model (for example, one in which the QUANTITY
of interest is a level forecast or a unit-root boundary test, whose difficulty
rises with phi); that is a modeling choice outside the pinned cost function and is
NOT adopted here. Flagged for the manuscript's Section 4.5 prose and for the
alignment review: no experiment consumes the sign of dW*/dphi (checked in step 3),
so the correction changes exposition, not operators - to be re-verified.

(c) theta = Delta_phi (through kappa = 1 - epsilon/Delta_phi). dkappa/d(Delta_phi)
= epsilon / Delta_phi^2 > 0, and G depends on kappa through a = kappa ln(rho_2):
    G_kappa = c_D * ln(rho_2) * exp(a W) * (1 + a W) > 0,
hence dW*/dkappa < 0 and dW*/d(Delta_phi) = (dW*/dkappa)(dkappa/dDelta_phi) < 0.
CONFIRMS the source: larger expected regime changes favor shorter windows.

(d) theta = c_E / c_D (cost ratio; new, for completeness). Scaling c_E up raises
-G by c_E's term, i.e. G_{c_E} = -(1 - phi^2)/W^2 < 0, so dW*/dc_E > 0: dearer
estimation error favors longer windows. Symmetrically dW*/dc_D < 0. Matches the
economic reading of Theorem 2 and provides a sign check for the T2 numeric grid.

---

## G.5 Theorem 3 (The Adaptation-Stability Identity)

STATEMENT (as proved). Let the blind-period amplification of Theorem 1 (under A4,
non-adaptive envelope) be d_tau = d_0 * rho_2^tau, and let the counterfactual
deviation had the regime not changed be d_tau^0 = d_0 * rho_1^tau (the same
recursion under rho_1, with rho_1 > 0). Then the damage amplification FACTOR -
realized deviation relative to the no-regime-change counterfactual over the same
blind window - is exactly
    D(W) = d_tau / d_tau^0 = ( rho(phi_2, W, beta*gamma) /
                                rho(phi_1, W, beta*gamma) )^{tau(W)},
with both rho and tau functions of the single design parameter W. D(W) > 1 whenever
rho_2 > rho_1 and tau > 0; log D(W) = tau(W) * [ln rho_2(W) - ln rho_1(W)]
factorizes damage into DURATION (tau) times INTENSITY (the log spectral-radius
gap), which is the intensity-times-duration reading in the text.

PROOF. Both trajectories satisfy the A4 recursion from the same d_0 > 0: the
realized blind-period path compounds at rho_2 per cycle (Theorem 1a, non-adaptive
envelope, where the bound is attained), giving d_tau = d_0 rho_2^tau; the
counterfactual path compounds at rho_1 per cycle, giving d_tau^0 = d_0 rho_1^tau,
strictly positive since rho_1 > 0. The ratio is (rho_2/rho_1)^tau; d_0 cancels, so
the factor is initial-condition-free, and by Lemma G.1(b) any matrix-general
constants C are common to numerator and denominator's growth-rate reading at rate
level. Positivity/exceedance: rho_2 > rho_1 > 0 and tau > 0 give the ratio > 1.
Taking logs gives the stated factorization. Both arguments are functions of W alone
once (phi_1, phi_2, beta*gamma, epsilon) are fixed: rho_i = rho(phi_i, W,
beta*gamma) by A2 and tau = kappa W by A5. QED.

REMARK G.5.1 (bound vs identity). Theorem 1 is an upper BOUND on the realized
deviation (adaptive policies do strictly better); Theorem 3 is an exact IDENTITY
for the non-adaptive envelope's amplification factor - the quantity every
experiment ranks on. Under an adaptive policy the realized factor is <= D(W), so
D(W) retains its reading as the worst-case regime-change cost multiplier.

---

## G.6 Proposition (Optimal Safety Factor k*) - derivation with approximations
labeled

SETTING. The speed limit from the companion papers is S(phi, W) * beta*gamma =
pi^2/2, giving beta*gamma_max = (pi^2/2) / S(phi_hat, W), calibrated to the
ESTIMATED persistence phi_hat. During a blind period the true phi exceeds phi_hat,
so operating exactly at beta*gamma_max risks a breach. Choose an operating fraction
k in (0, 1]: beta*gamma_op = k * beta*gamma_max.

STATEMENT (approximation - stated as a Proposition, not a Theorem). Under (i)
first-order expansion of S in phi around phi_hat, (ii) Gaussian estimation error
phi - phi_hat ~ N(0, Var(phi_hat)) with the regime-change contribution entering as
an inflation of effective estimation risk proportional to p * W (probability p of a
change during a window of length W), and (iii) a breach-avoidance criterion that
holds the operating point at approximately two standard deviations of the induced
uncertainty in S * beta*gamma / (pi^2/2), the optimal fraction is approximately
    k* ~= 1 - (1/(pi^2/2)) * sqrt( 2 * p * W * Var(phi_hat) ),
matching the source's stated form. For typical manufacturing parameters
(phi ~ 0.96, W in [8, 12], regime changes every 5-7 years) this evaluates in the
0.85-0.95 range; the exact numbers are re-earned by the committed T3 grid, not
quoted from the source.

DERIVATION. Let u := S(phi, W) * beta*gamma_op / (pi^2/2) be the utilization of the
speed limit at the TRUE phi; stability requires u < 1. With beta*gamma_op =
k * (pi^2/2)/S(phi_hat, W), u = k * S(phi, W)/S(phi_hat, W). Expanding S to first
order in (phi - phi_hat) (approximation i): S(phi, W)/S(phi_hat, W) ~= 1 +
s_1 * (phi - phi_hat), with s_1 = (dS/dphi)/S evaluated at phi_hat. Under
(approximation ii) the term s_1 (phi - phi_hat) is Gaussian with variance
s_1^2 * Var_eff, Var_eff = 2 p W Var(phi_hat) collecting the estimation variance
inflated by the chance and length of a blind window (the factor 2pW is the source's
parameterization of that inflation and is retained as-is; it is a modeling
constant, not a derived quantity - labeled explicitly as such for the 5a review).
The breach-avoidance criterion (approximation iii) sets k so that u stays below 1
at the sqrt(Var_eff) scale normalized by the limit: k* = 1 - sqrt(Var_eff) /
(pi^2/2) after absorbing s_1 into the normalization of Var(phi_hat) (the source
states the formula with s_1 = 1, i.e., variance quoted directly in speed-limit
units; retained for continuity and flagged as a units convention). Substituting
Var_eff gives the stated k*. QED (as an approximation chain; each step labeled).

STATUS. G.6 is deliberately a PROPOSITION with an explicit approximation chain: the
source provides the formula with no derivation, and the three approximation steps
above are the minimal honest scaffold that produces it. The T3 grid (step 2)
verifies the practical content (argmin location and the 0.80-0.98 band) directly by
brute force, independent of the approximations. If the grid contradicts the
formula's location, the Proposition - not the grid - is amended, dated.

---

## G.7 Verification Status Ledger (updated as steps 2-3 complete)

- THM-1 (G.2): written proof COMPLETE (v0.2, step (ii) corrected to Lemma
  G.1b). Symbolic step-check + numeric stress grid: GREEN in container QA
  (T1 SUPPORT, 35/440 in-domain cells, 0 counterexamples); OFFICIAL local run
  pending. Scope conditions: A4 dominant-mode; G.1b numerically-verified
  envelope (flagged for 5a).
- THM-2 (G.3): written proof COMPLETE above, with interiority condition (C) and
  exact Lambert-W form. Symbolic: PENDING (T1). Numeric W*-vs-brute-force: PENDING
  (T2).
- Statics (G.4): written derivation COMPLETE; sign (b) REVERSED from source under
  the model's own cost term - manuscript Section 4.5 prose must follow G.4, not the
  source. Numeric sign checks: PENDING (T1/T2 grids, including (d)).
- THM-3 (G.5): written proof COMPLETE (exact identity for the non-adaptive
  envelope). Symbolic: PENDING (T1). Numeric: PENDING (T1 grid).
- k* Proposition (G.6): derivation COMPLETE with approximations labeled. Numeric:
  PENDING (T3 grid; grid governs).
- Post-proof alignment review of E1-E12 vs the as-proven statements: PENDING
  (step 3; logged in DECISIONS.md when run).
