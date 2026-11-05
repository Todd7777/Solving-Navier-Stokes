# Why Clay statements (A) and (B) are still open (November 2026)

Short version: a forced blowup — which is what has been claimed and formalized in 2026 — does not
touch the unforced global-regularity question, and every known unconditional estimate for the unforced
equation is supercritical by half a derivative. Nobody has a candidate proof of (A) or (B), and nobody has
a candidate unforced singularity. This document explains each of those sentences precisely.

## 1. The logic: (C) does not contradict (A)

In Fefferman's formulation (see `01-official-problem.md`):

* (A) **for every** smooth, rapidly decaying, divergence-free $u^0$, **with $f \equiv 0$**, there is a global smooth solution with bounded energy;
* (C) **there exist** a smooth decaying $u^0$ **and a smooth decaying force $f$** for which no such solution exists.

The quantifier structures are different and the force is different. (C) is proved by exhibiting one
pair $(u^0, f)$; the 2026 constructions take $u^0 = 0$ and $f \ne 0$. For $u^0 = 0$ and $f \equiv 0$ the
unique smooth bounded-energy solution is $u \equiv 0$, which is global. So (C), even if established beyond
doubt, says nothing about (A). Likewise (D) says nothing about (B). The four statements are not two
complementary pairs; they are four independent claims, and the Clay problem asks for any one of them.

The unforced question "do smooth, finite-energy solutions of $\partial_t u + (u\cdot\nabla)u = \nu\Delta u - \nabla p$
ever blow up?" is what most analysts mean by "the Navier–Stokes problem". It is open in both directions.

## 2. The analytic obstruction: supercriticality

`04-rigorously-proven-results.md`, Theorems 1, 2 and 5′, give the precise statement:

* the only quantities controlled for all time by the data are $\|u\|_{L^\infty_t L^2_x}$ and $\|\nabla u\|_{L^2_t L^2_x}$ (the energy identity);
* under the scaling symmetry $u_\lambda(x,t) = \lambda u(\lambda x,\lambda^2 t)$ both scale like $\lambda^{-1/2}$;
* a quantity must scale like $\lambda^{0}$ or better to control the solution at small scales
  (Theorem 7 shows exactly how a critical bound closes the argument);
* so the known control is short by exactly one half derivative, in every known estimate.

Physically: a hypothetical singularity concentrates vorticity at ever smaller scales; the energy of
such a concentrated structure *tends to zero* under zoom-in, so the energy budget does not forbid it,
and the dissipation $\nu\|\nabla u\|^2$ — the only thing fighting it — is itself supercritical. In two
dimensions the energy is critical (Theorem 2) and the vorticity has no stretching term (Theorem 3),
which is why 2D was settled in 1959 and 3D was not.

## 3. Barriers that rule out whole classes of proofs

**Tao's averaged equation (2016).** Replace the bilinear term $B(u,u) = \mathbb P\nabla\cdot(u\otimes u)$ by an
averaged operator $\tilde B$ that still satisfies the energy identity $\langle\tilde B(u,u),u\rangle = 0$, the same
scaling, and the same harmonic-analysis estimates (Littlewood–Paley, Bernstein, Sobolev, paraproduct bounds).
Tao proved that this averaged system has smooth Schwartz data that blow up in finite time. Consequence: *any*
proof of (A) must use a property of the genuine nonlinearity that the averaged one lacks. Energy methods,
Fourier-cutoff methods, and abstract functional-analytic arguments that are insensitive to the fine structure
of $B$ are all excluded. This is the single most useful test to apply to a claimed proof of (A): if the argument
would go through verbatim for $\tilde B$, it is wrong.

**Non-uniqueness of weak solutions.** Buckmaster–Vicol (2019) showed that finite-energy distributional
solutions are wildly non-unique (any energy profile can be prescribed); Albritton–Brué–Colombo (2022) showed
that even Leray–Hopf solutions are non-unique once a body force is allowed. So "construct a weak solution and
show it is unique, hence regular" cannot work in the distributional class, and in the Leray–Hopf class
it would require new ideas that survive the forced counterexample.

**No self-similar blowup.** The natural first guess for an unforced singularity is Leray's self-similar
ansatz $u(x,t) = (T-t)^{-1/2}U\big(x/\sqrt{T-t}\big)$. Nečas–Růžička–Šverák (1996) showed $U\in L^3$ forces
$U\equiv0$, and Tsai (1998) excluded profiles satisfying the local energy inequality. Any unforced blowup
must therefore be non-self-similar, and by Beale–Kato–Majda it must have $\int_0^T\|\omega\|_{L^\infty}dt = \infty$,
and by Caffarelli–Kohn–Nirenberg its singular set must have one-dimensional parabolic measure zero.

## 4. Why "forced blowup" is genuinely easier than "unforced blowup"

With a force the energy balance reads
$\|u(t)\|^2 + 2\nu\int_0^t\|\nabla u\|^2 = \|u_0\|^2 + 2\int_0^t\langle f,u\rangle$:
the force can inject energy at the scales and times where the construction needs it. All 2026
constructions (Córdoba–Martínez-Zoroa, Alpöge–Buckmaster, OpenAI; see `02-status-november-2026.md`)
are of this type: an approximate singular flow is written down, and the force is *defined* to be whatever
residual the approximate flow leaves in the equation, after which the real work is to show that this
residual can be made smooth and decaying. The public expositions of the OpenAI construction describe the
force as "amplified oscillatory pulses" supplying an "annular stress", corrected through an "infinite-order
correction cycle". In the unforced problem the residual must be absorbed by the dynamics itself: the
approximate solution has to be corrected to an exact solution of the homogeneous equation, with all errors
controlled under the fixed energy budget $\|u_0\|^2$ and against viscous damping at every scale. That is a
different and much harder problem (compare the "positive defect" formulation of the unforced search in the
September 2026 literature).

Two further differences matter for the Clay statements:

* **Stability is not required.** A forced singular solution need not be stable under perturbation of the
  data; (C) asks only for existence of one bad $(u^0,f)$. The unforced problem (A) is about *all* data, so a
  counterexample must be an actual solution of the homogeneous equation, and a regularity proof must handle
  all data at once.
* **Pressure and solution class.** On $\mathbb R^3$ the Clay solution class (7) bounds only the velocity's
  energy; the pressure is unconstrained at infinity. A nonexistence proof must therefore show that *every*
  smooth finite-energy competitor, whatever its pressure does at infinity, coincides with the singular flow
  before the singular time. (The OpenAI Lean development spends a large part of its whole-space proof on
  exactly this "pressure recovery"; see `03-audit-openai-lean-formalization.md`.)

## 5. What numerics can and cannot say

Numerical evidence for 3D singularities exists (Hou and collaborators, 2014–2023, for axisymmetric Euler and
Navier–Stokes near a boundary; the 2025 DeepMind–Gómez-Serrano "unstable singularities" for IPM, Boussinesq
and Euler), and computer-assisted proofs have settled the Euler problem with boundary (Chen–Hou). But no finite
computation can prove (A): regularity is a statement about all data and all times, and a computation that
shows a norm "appears to blow up" cannot distinguish a genuine singularity from a very large but finite
transient. Conversely a computation cannot disprove (A) either unless it is turned into a rigorous
computer-assisted proof with interval arithmetic and a stability analysis of the self-similar profile. The
`numerics/` directory in this repository is therefore deliberately modest: it checks identities and exhibits the
2D/3D dichotomy; it proves nothing about regularity.

## 6. What a resolution would have to contain

* **A proof of (A) or (B)** must produce a new quantity, bounded for all time in terms of the data, that is
  critical or subcritical under the scaling of Theorem 2, and the argument must fail for Tao's averaged
  equation. Nothing of this kind is known, even conditionally.
* **An unforced counterexample** must be an exact smooth solution of the homogeneous equation with finite
  energy that loses smoothness in finite time, non-self-similar by Section 3, with a rigorous (likely
  computer-assisted) stability analysis of the blowup mechanism. The 2025–26 program of searching for
  unstable self-similar profiles with machine-learning assistance is explicitly aimed at this, and has so far
  produced candidates only for equations without viscosity or with forcing.

## 7. Status table

| statement | content | status (5 Nov 2026) |
|---|---|---|
| (A) | unforced global regularity on $\mathbb R^3$ | **open** |
| (B) | unforced global regularity on $\mathbb T^3$ | **open** |
| (C) | forced breakdown on $\mathbb R^3$ | claimed by OpenAI (8 Sep 2026) with a Lean formalization against an independently written statement; not yet refereed or accepted by the Clay Institute |
| (D) | forced breakdown on $\mathbb T^3$ | same (follows from (C) by periodization in the OpenAI development) |
| unforced blowup (not a Clay alternative, but the question everyone means) | **open** |
