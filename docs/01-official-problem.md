# The official problem: four statements, not one

The Clay Mathematics Institute's Navier–Stokes Millennium Prize Problem is defined by Charles Fefferman's
official description, *Existence and smoothness of the Navier–Stokes equation*; the PDF that Clay hosts ends with
two errata. This document reproduces its structure precisely, because almost every public dispute about
"whether Navier–Stokes has been solved" is a dispute about *which of the four statements* is meant.

> **Source (Cited, read 14 November 2026).** The official PDF,
> `https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf`: 6 pages, 203,736 bytes, SHA-256
> `c1b5f27b1a64705cfaf1afceea513db5deedca8a18ca56ab32e7f86445a06d0c`; its metadata gives 4 August 2006 as the
> creation date and 5 February 2013 as the last modification. Equations (1)–(11), statements (A)–(D) and the errata
> below agree with it. Earlier versions of this file were a paraphrase from memory, written where that host was not
> reachable; the check against the PDF found no difference of substance. The PDF itself is not copied here.

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

**Errata (Cited).** The PDF ends with two. The first reads, verbatim: "The further condition
$p(x + e_j, t) = p(x, t)$ should be made explicit in Eqn (8)." Equation (8) is where periodicity is imposed, on the
data. But in (B) and (D) the pressure is never data: it belongs to the solution $(p,u)$. So the condition can only
mean that the solution's pressure is periodic, as (10) requires of its velocity, and that is how the Formal
Conjectures encoding states it. Without it, $p$ could contain a term $c(t)\cdot x$ (a spatially uniform
acceleration); see Section 3 and `03-audit-openai-lean-formalization.md`, Section 3.4.

The second erratum corrects the signs in the weak formulation that the PDF numbers (12) and the erratum calls
"Eqn (10)". Corrected, it reads
$-\iint u\cdot\partial_t\theta - \sum_{ij}\iint u_iu_j\,\partial_j\theta_i = \nu\iint u\cdot\Delta\theta
+ \iint f\cdot\theta + \iint p\,\operatorname{div}\theta$ over $\mathbb R^3\times\mathbb R$. This is what
integration by parts gives for a smooth solution of (1), (2) and a test field $\theta$ compactly supported in
$\mathbb R^3\times(0,\infty)$ (**Machine-checked**: `verify/identities.py`, Section D). As printed, (12) has the
opposite signs on the $\partial_t\theta$ and pressure terms, and it fails for smooth solutions (**Theorem**). Take
$\theta=(\theta_1,0,0)$ with $\theta_1\ge0$ not identically zero. For $u\equiv0$, $p=x_1$, $f=e_1$, the printed left
side is $0$ and its right side is $\iint\theta_1-\iint x_1\partial_1\theta_1 = 2\iint\theta_1 > 0$. For $u=t\,e_1$,
$p=0$, $f=e_1$, its left side is $\iint t\,\partial_t\theta_1-\iint t^2\,\partial_1\theta_1=-\iint\theta_1$ and its
right side is $\iint\theta_1$ (the integrals of $\partial_1\theta_1$ and $\Delta\theta_1$ over $x$ vanish).
(Both are exact solutions of (1), (2), checked in the same section.) The weak formulation is commentary: it is not
part of (A)–(D).

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

**Cited** (the rules, `https://www.claymath.org/wp-content/uploads/2022/03/millennium_prize_rules_0.pdf`, 4 pages,
SHA-256 `9b5003745c0ae7268dc7769f83e1c61eaca674f28631f1df2cd8400976640b2a`, read 14 November 2026). The rules are
dated 26 September 2018 and supersede all earlier statements. Under rule 4, CMI may award a prize only if the
proposed solution:

* has been published in a "Qualifying Outlet" (a refereed mathematics publication of worldwide repute, or one meeting
  relaxed conditions approved by its board);
* was published at least two years earlier;
* has achieved general acceptance in the global mathematics community, as determined in the sole discretion of CMI;
* and answers the questions raised by the official description.

Evaluation is sequential (rule 7). General acceptance comes first. Then, if CMI decides that the solution merits
detailed consideration, it convenes a special advisory committee of at least three members, at least two of them
experts in the area. For Navier–Stokes, "a resolution in either direction" goes through this standard procedure (rule
5(b)). That covers a breakdown result such as (C) or (D) as well as (A) or (B).

A press announcement, a preprint, or a compiled formal proof satisfies none of these steps by itself. OpenAI's
announcement says that it does not intend to claim the prize. That announcement could not be read from here, so this
point is reported from the sources in `02-status-november-2026.md`.
