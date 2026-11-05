# The official problem: four statements, not one

The Clay Mathematics Institute's Navier–Stokes Millennium Prize Problem is defined by Charles Fefferman's
official description, *Existence and smoothness of the Navier–Stokes equation* (2000; the current PDF carries
later errata). This document reproduces its structure precisely, because almost every public dispute about
"whether Navier–Stokes has been solved" is a dispute about *which of the four statements* is meant.

> **Source caveat.** The official PDF is hosted at
> `https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf`. That host was not reachable from the
> sandbox in which this repository was written, so the text below is a careful paraphrase from memory of the
> official statement, cross-checked against the machine-readable encoding written independently by Google
> DeepMind's *Formal Conjectures* project (reproduced verbatim in `audit/reference/`, with docstrings that
> cite Fefferman's equation numbers). Before quoting it as official, check it against the PDF.

## 1. The equations and the side conditions

Unknowns: velocity $u(x,t)\in\mathbb R^3$ and pressure $p(x,t)\in\mathbb R$, for $x\in\mathbb R^3$, $t\ge0$. Given:
viscosity $\nu>0$, initial velocity $u^0(x)$, external force $f(x,t)$.

$$\text{(1)}\quad \partial_t u_i + \sum_{j} u_j\,\partial_j u_i = \nu\Delta u_i - \partial_i p + f_i(x,t), \qquad
\text{(2)}\quad \nabla\cdot u = 0, \qquad
\text{(3)}\quad u(x,0) = u^0(x).$$

Whole-space side conditions (all derivatives of all orders, all decay rates $K$):

$$\text{(4)}\quad |\partial_x^\alpha u^0(x)| \le C_{\alpha K}(1+|x|)^{-K}, \qquad
\text{(5)}\quad |\partial_x^\alpha\partial_t^m f(x,t)| \le C_{\alpha m K}(1+|x|+t)^{-K} \ \text{ on } \mathbb R^3\times[0,\infty),$$
$$\text{(6)}\quad p,u\in C^\infty(\mathbb R^3\times[0,\infty)), \qquad
\text{(7)}\quad \int_{\mathbb R^3}|u(x,t)|^2\,dx < C \ \text{ for all } t\ge0 \ \text{(bounded energy)}.$$

Periodic side conditions ($e_j$ the unit vectors):

$$\text{(8)}\quad u^0(x+e_j) = u^0(x),\ \ f(x+e_j,t)=f(x,t), \qquad
\text{(9)}\quad |\partial_x^\alpha\partial_t^m f(x,t)| \le C_{\alpha m K}(1+|t|)^{-K},$$
$$\text{(10)}\quad u(x+e_j,t) = u(x,t), \qquad \text{(11)}\quad p,u\in C^\infty(\mathbb R^3\times[0,\infty)).$$

Erratum (as recorded by the Formal Conjectures encoding): in the periodic case the pressure $p$ is also required
to be periodic in $x$. Without it, $p$ could contain a term $c(t)\cdot x$ (a spatially uniform acceleration), which
is physically meaningless and makes the periodic problem ill-posed; see Section 3 and the audit.

## 2. The four statements

The problem asks for a proof of **any one** of the following.

* **(A) Existence and smoothness on $\mathbb R^3$.** Take $\nu>0$, $n=3$. Let $u^0$ be any smooth divergence-free field
  satisfying (4), and take $f\equiv0$. Then there exist smooth $(p,u)$ on $\mathbb R^3\times[0,\infty)$ satisfying (1),(2),(3),(6),(7).
* **(B) Existence and smoothness on $\mathbb R^3/\mathbb Z^3$.** Same with (4) replaced by (8) for $u^0$, $f\equiv0$, and
  (6),(7) replaced by (10),(11).
* **(C) Breakdown on $\mathbb R^3$.** Take $\nu>0$, $n=3$. There exist a smooth divergence-free $u^0$ and a smooth $f$ on
  $\mathbb R^3\times[0,\infty)$ satisfying (4),(5), for which there exist **no** $(p,u)$ satisfying (1),(2),(3),(6),(7).
* **(D) Breakdown on $\mathbb R^3/\mathbb Z^3$.** Same with (8),(9) for the data and (10),(11) for the solution.

Three remarks that matter in 2026:

1. **In (A) and (B) the force is zero. In (C) and (D) it is allowed to be non-zero.** A forced blowup proves (C)/(D)
   and leaves (A)/(B) untouched: both (A) and (C) can be true at once. See `05-why-A-and-B-are-open.md`, Section 1.
2. **(A) and (B) are different problems**, as are (C) and (D). Periodization turns a compactly supported whole-space
   blowup into a periodic one (this is how (D) is derived from (C) in the 2026 formalization), but no implication
   is known in the other direction, nor between the (A)/(B) pair.
3. **The solution class is deliberately minimal.** On $\mathbb R^3$ only $u$ is assumed to have finite energy; nothing is
   assumed about $p$ or $\nabla u$ at spatial infinity. A nonexistence proof for (C) must handle *every* smooth competitor
   in that class, including ones whose pressure behaves badly at infinity.

## 3. The machine-readable form

The Formal Conjectures project (Google DeepMind) encoded the four statements in Lean 4 / Mathlib; OpenAI used the
(C)/(D) half of that encoding, unchanged except for namespace and imports, as the *challenge* against which their proof
is checked. The encoding, with every field annotated by Fefferman's equation number, is in
`audit/reference/formal-conjectures_8bf45ed_Millenium_NavierStokes.lean`. For example, (7) becomes

```lean
integrable : ∀ t ≥ 0, MemLp (‖v · t‖) 2
globally_bounded_energy : ∃ E, ∀ t ≥ 0, (∫ x : ℝ^n, ‖v x t‖ ^ 2) < E
```

and (C) becomes

```lean
theorem navier_stokes_breakdown_R3 (nu : ℝ) (hnu : nu > 0) :
    ∃ (u₀ : ℝ³ → ℝ³) (f : ℝ³ → ℝ → ℝ³),
    InitialVelocityConditionDecay u₀ ∧ ForceConditionDecay f ∧
    ¬ (∃ v p, NavierStokesExistenceAndSmoothnessRn nu u₀ f v p)
```

A line-by-line comparison of this encoding with (1)–(11) is in `03-audit-openai-lean-formalization.md`, Section 3.

## 4. What "solved" means to the Clay Institute

Under the Institute's rules (revised 26 September 2018), a prize requires, in order: publication of the solution in a
qualifying refereed outlet; a waiting period of at least two years after publication; and general acceptance by the
mathematics community, as determined by the Institute in its sole discretion, after which an advisory committee
examines the work. A press announcement, a preprint, or a compiled formal proof satisfies none of these steps by itself.
OpenAI has stated that it does not intend to claim the prize for its 2026 result.
