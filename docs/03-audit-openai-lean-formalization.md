# Audit of the OpenAI Lean formalization of Clay statements (C) and (D)

Audited: `https://github.com/openai/NavierStokesAndEuler`, commit `f9e8bc5b38b6e212696e8a30e3e91517af887bbd`
(author recorded in git as Boris Alexeev, 2026-09-10 07:51:24 -0400). Audit date: 5 November 2026.
Inputs are frozen with SHA-256 hashes in `audit/reference/`; the scripts that produced every number below are in
`audit/`, and their output from today is in `audit/results/`.

## 0. Verdict in five lines

1. The Lean statements `NavierStokes.Comparator.navier_stokes_breakdown_R3` / `…_periodic` are a faithful encoding of
   Fefferman's (C) and (D), with the erratum requiring periodic pressure in (D) (Section 3, one caveat in 3.4).
2. The statement file is Google DeepMind's independent encoding, unchanged in every definition and in both theorem
   statements (Section 4: the only differences are imports, namespace, attributes and docstrings).
3. The 641 k-line proof development declares no axioms and contains no `sorry` outside the four intentional challenge
   placeholders; no `native_decide`, `implemented_by`, `unsafe`, `opaque`, `partial`, or `set_option` anywhere (Section 5).
4. I could **not** rebuild it here: the Lean release and Mathlib cache servers are outside this sandbox's network policy.
   The kernel check therefore rests on OpenAI's own report and on whoever has run `lake build`/Comparator since. Exact
   reproduction commands are in Section 7.
5. None of this bears on (A)/(B), which remain open. The published critique of the manuscript (Section 8) does not
   challenge the formal theorem; it challenges the manuscript as a human-readable proof.

## 1. What was audited

| item | value |
|---|---|
| toolchain | `leanprover/lean4:v4.34.0-rc2` |
| Mathlib | `85e3a25e006c35636f0e53b0e9296caca2685bc0` (tag `v4.34.0-rc2`) |
| Comparator | `19e111e2141cf333c7daff0f64c5f24acc91dd2e` (tag `v4.34.0-rc2`), nanoda second kernel enabled |
| `NavierStokes/` | 816 files, 429 279 lines, 26 200 `theorem`/`lemma`, 7 497 `def`, 524 `structure` |
| `Euler/` | 1 839 files, 211 578 lines, 10 632 `theorem`/`lemma`, 3 287 `def` |
| challenge statements | `ComparatorChallenges/NavierStokes.lean` (sha256 `0cd193b8…`), `ComparatorChallenges/Euler.lean` (`b11e9baf…`) |
| permitted axioms (Comparator config) | `propext`, `Quot.sound`, `Classical.choice` |
| top-level theorems | `NavierStokes.Comparator.navier_stokes_breakdown_R3`, `NavierStokes.Comparator.navier_stokes_breakdown_periodic`, `Euler.euler_breakdown_R3`, `Euler.exists_compact_smooth_euler_singularity` |

## 2. What the Comparator check means

Comparator (Lean FRO; merged into Lean core as `lake check` from v4.35) builds the *challenge* module and the
*solution* module in a sandbox, exports both environments with `lean4export`, and then verifies three things:
(i) each listed theorem in the solution has exactly the same statement as in the challenge, down to every
declaration the statement depends on (including `Init`); (ii) the proof uses no axioms beyond the permitted list;
(iii) the solution environment replays through the Lean kernel and, optionally, through an independent kernel
(nanoda, written in Rust). The challenge file is *trusted*: Comparator does not judge whether the definitions in it
mean what the docstrings say. That is precisely the part a human must audit, and it is Section 3 below.

Residual trusted base after a successful Comparator run: the Lean kernel (or nanoda), the pinned Mathlib build
(cache untampered), the sandbox, and the faithfulness of the challenge file.

## 3. Faithfulness of the challenge statements to Fefferman's (C) and (D)

The challenge file is reproduced in `audit/reference/openai_f9e8bc5_ComparatorChallenges_NavierStokes.lean`.
Notation: `ℝ³ = EuclideanSpace ℝ (Fin 3)`; `v : ℝ³ → ℝ → ℝ³` is the solution velocity, `v x t` position-first;
`↿f` is the uncurried function on `ℝ³ × ℝ`.

### 3.1 Statement (C)

```lean
theorem navier_stokes_breakdown_R3 (nu : ℝ) (hnu : nu > 0) :
    ∃ (u₀ : ℝ³ → ℝ³) (f : ℝ³ → ℝ → ℝ³),
    InitialVelocityConditionDecay u₀ ∧ ForceConditionDecay f ∧
    ¬ (∃ v p, NavierStokesExistenceAndSmoothnessRn nu u₀ f v p)
```

| Fefferman | Lean field | assessment |
|---|---|---|
| "Take $\nu>0$ and $n=3$" | hypotheses `(nu : ℝ) (hnu : nu > 0)`; `ℝ³` | ✓ universally quantified over all $\nu>0$ |
| $u^0$ smooth, divergence-free | `InitialVelocityCondition.smooth : ContDiff ℝ ∞ u₀`; `div_free : ∀ x, ∇⬝ u₀ x = 0` | ✓ (`∇⬝` is the trace of `fderiv`; genuine because `u₀` is smooth) |
| (4) $\lvert\partial^\alpha u^0\rvert\le C_{\alpha K}(1+\lvert x\rvert)^{-K}$ | `decay : ∀ m : ℕ, ∀ K : ℝ, ∃ C, ∀ x, ‖iteratedFDeriv ℝ m u₀ x‖ ≤ C / (1 + ‖x‖) ^ K` | ✓ the $m$-th Fréchet derivative bounds all multi-indices of order $m$; $K$ real ⊇ $K$ natural |
| $f$ smooth on $\mathbb R^3\times[0,\infty)$ | `ForceCondition.smooth : ContDiffOn ℝ ∞ (↿f) (univ ×ˢ Ici 0)` | ✓ smooth up to $t=0$ in Mathlib's within-sense |
| (5) $\lvert\partial_x^\alpha\partial_t^m f\rvert\le C(1+\lvert x\rvert+t)^{-K}$ | `decay : ∀ m K, ∃ C, ∀ x, ∀ t ≥ 0, ‖iteratedFDerivWithin ℝ m (↿f) (univ ×ˢ Ici 0) (x,t)‖ ≤ C / (1 + ‖x‖ + t) ^ K` | ✓ joint space-time derivatives of all orders |
| (1) $\partial_tu+(u\cdot\nabla)u=\nu\Delta u-\nabla p+f$ | `navier_stokes : ∀ x, ∀ t ≥ 0, derivWithin (v x ·) (Ici 0) t + fderiv ℝ (v · t) x (v x t) = nu • Δ (v · t) x - gradient (p · t) x + f x t` | ✓ `fderiv … x (v x t)` is the Jacobian applied to $v$, i.e. $(v\cdot\nabla)v$; `Δ` is Mathlib's Laplacian (trace of the second derivative); signs match |
| (2) $\nabla\cdot u=0$ | `div_free : ∀ x, ∀ t ≥ 0, ∇⬝ (v · t) x = 0` | ✓ |
| (3) $u(x,0)=u^0(x)$ | `initial_condition : ∀ x, v x 0 = u₀ x` | ✓ |
| (6) $p,u\in C^\infty(\mathbb R^3\times[0,\infty))$ | `velocity_smooth`, `pressure_smooth : ContDiffOn ℝ ∞ (↿·) (univ ×ˢ Ici 0)` | ✓ |
| (7) $\int\lvert u\rvert^2dx<C$ for all $t$ | `integrable : ∀ t ≥ 0, MemLp (‖v · t‖) 2` and `globally_bounded_energy : ∃ E, ∀ t ≥ 0, (∫ x, ‖v x t‖ ^ 2) < E` | ✓ see 3.3(b) |
| "there exist no solutions $(p,u)$" | `¬ (∃ v p, NavierStokesExistenceAndSmoothnessRn nu u₀ f v p)` | ✓ |

### 3.2 Statement (D)

Same equation, initial condition and smoothness; data conditions `InitialVelocityConditionPeriodic` (smooth,
divergence-free, `IsOnePeriodic u₀`, i.e. (8) for $u^0$) and `ForceConditionPeriodic` (smooth on the half-space,
`∀ t ≥ 0, IsOnePeriodic (f · t)` = (8) for $f$, and decay `≤ C / (1 + t) ^ K` of all space-time derivatives = (9));
solution class `NavierStokesExistenceAndSmoothnessPeriodic` with `isOnePeriodic_velocity` = (10), smoothness = (11),
and `isOnePeriodic_pressure` (erratum). No energy condition, matching (D). `IsOnePeriodic g := ∀ x i, g (x + single i 1) = g x`
is periodicity with period 1 in each coordinate, i.e. $\mathbb R^3/\mathbb Z^3$. ✓

### 3.3 Points a sceptical reader should check, and what I found

(a) **Partial operations and junk values.** Mathlib's `fderiv`, `derivWithin`, `Δ`, `gradient` return $0$ where the
function is not differentiable. Could a "solution" exploit that? No: `velocity_smooth` and `pressure_smooth` give joint
$C^\infty$ smoothness on $\mathbb R^3\times[0,\infty)$, so every spatial derivative is genuine, and the time derivative
within `Ici 0` is the genuine one-sided derivative at $t=0$ and the ordinary derivative for $t>0$. On the data side,
`smooth` makes the divergence of `u₀` genuine.

(b) **The Bochner integral.** `∫ x, ‖v x t‖ ^ 2` is $0$ if the integrand is not integrable, which would make
`globally_bounded_energy` vacuous for a non-$L^2$ competitor. The separate field `integrable` (= $v(\cdot,t)\in L^2$)
closes that hole. With it, the two fields together are exactly (7). Lebesgue measure on `EuclideanSpace ℝ (Fin 3)` is
Mathlib's `volume`, normalised so that the unit cube has measure 1.

(c) **Smoothness on a closed half-space.** `ContDiffOn ℝ ∞ F (univ ×ˢ Ici 0)` means: at every point of the closed
half-space $F$ has a Taylor expansion of every order within the set, with continuous within-derivatives. For the
closed half-space this is the usual notion of "smooth up to the boundary" and (by Seeley extension) equivalent to
being the restriction of a smooth function on $\mathbb R^3\times\mathbb R$. Either reading gives the same class.

(d) **Real exponents.** `(1 + ‖x‖) ^ K` with `K : ℝ` is `Real.rpow`; requiring the bound for all real $K$ is
equivalent to requiring it for all natural $K$.

(e) **Nothing is assumed about the pressure at infinity or about $\nabla u$** in the whole-space solution class. That is
the official (7). It makes the theorem *stronger* (nonexistence over a larger class), and it is why the development
contains a long "pressure recovery / weak–strong comparison" argument (Section 6).

### 3.4 The one caveat: periodic pressure in (D)

The Lean (D) requires the competitor's pressure to be 1-periodic in $x$ (`isOnePeriodic_pressure`). The Formal
Conjectures docstring says this follows "the errata appended to the Clay problem statement". I could not read the
Clay PDF from this sandbox to confirm the wording of that erratum. The point matters because requiring more of the
competitor makes a nonexistence theorem *weaker*: with $u$ and $f$ periodic, taking the divergence of (1) shows that
any smooth pressure is $p = p_{\mathrm{per}} + c(t)\cdot x + d(t)$ with $p_{\mathrm{per}}$ periodic and $c(t)$ a free
spatially-uniform acceleration (the gradient of a harmonic function with periodic gradient is constant by Liouville's
theorem). The literal original wording of (D) would therefore admit competitors driven by $f - c(t)$ for an arbitrary
smooth $c$, which are not covered by the formal theorem. Under the erratum they are excluded, and the formal
statement is exactly the corrected (D). Readers who care about (D) specifically should confirm the erratum against the
official PDF; (C) is unaffected, since on $\mathbb R^3$ the finite-energy condition on $u$ pins the pressure down
(and the development proves this).

## 4. The challenge file versus DeepMind's reference

`audit/results/diff_2026-11-05.txt` is a whitespace-insensitive diff of
`formal-conjectures @ 8bf45ed70d48b2b2a501de9c00b26bfa38c573ee : FormalConjectures/Millenium/NavierStokes.lean`
against `ComparatorChallenges/NavierStokes.lean`. The complete list of differences:

* `import FormalConjecturesUtil` → `import Mathlib`; the `ℝ^n`/`ℝ³` notations are inlined as `local notation`;
* `namespace NavierStokes` → `namespace NavierStokes.Comparator`; `notation "∇⬝"` becomes `local notation`;
* the Formal Conjectures metadata attributes (`@[category API, AMS 35]`, `@[category research open, AMS 35]`) are removed;
* the two statements (A) and (B) (`navier_stokes_existence_and_smoothness_R3` / `_periodic`, with `f := 0`) are removed;
* docstring text about the file's origin is changed.

Every definition (`divergence`, `IsOnePeriodic`, the five condition structures, the three solution structures) and both
theorem statements (C), (D) are **identical**. The solution-side copy `NavierStokes/ComparatorDefinitions.lean`, which
the proof actually imports, is also identical to the challenge except for the two theorem statements it omits; in any
case Comparator compares the two environments mechanically.

The current `main` of Formal Conjectures (file now under `Millennium/`) is also frozen in `audit/reference/`; it differs
from the `8bf45ed` revision only in metadata and attributes.

## 5. Static scan of the proof development

From `audit/results/scan_2026-11-05.txt` (`audit/scan_lean_repo.sh`):

| pattern | hits | meaning |
|---|---|---|
| `sorry` | 5 | 4 are the intentional challenge placeholders in `ComparatorChallenges/*.lean` (never imported by the proof), 1 is the word in a docstring |
| `axiom` declarations | 0 | none |
| `unsafe`, `native_decide`, `implemented_by`, `@[extern`, `opaque`, `partial`, `ofReduceBool`, `admit`, `run_cmd`, `run_tac`, `#eval`, `macro_rules`, `elab` | 0 each | no escape hatches, no meta-programming |
| `set_option` | 0 | no heartbeat or recursion-depth overrides at all |
| `initialize` | 3 | all inside comments |
| `Classical.choice` (as a term) | 156 | ordinary use of the axiom of choice, which is permitted |
| `local instance` | 1 542 | norm/inner-product structures on function spaces defined locally; standard |
| imports outside `Mathlib`/`NavierStokes`/`Euler` | none | |

`ComparatorSolution.lean` ends with `#print axioms` for both theorems; `formalization.yaml` records the output as
`propext`, `Classical.choice`, `Quot.sound` and `sorry_count: 0`. I could not run `#print axioms` myself (Section 7).

## 6. How the proof is organised (what the certificate actually certifies)

Reading the bridge files (`NavierStokes/ComparatorR3Theorem.lean`, `ComparatorTheorem.lean`, `R3/Theorem.lean`,
`R3/ProblemStatement.lean`, `R3/CandidateBreakdown.lean`, `R3/H3WeakStrong.lean`, `R3/PressureRecovery.lean`,
`PeriodicPaperTheorem.lean`):

1. **Candidate.** For viscosity $\nu=1$ a velocity/pressure/force triple is constructed with: $u(\cdot,0)=0$; $f$ smooth,
   compactly supported in space and in strictly positive time; $u,p$ smooth on $\mathbb R^3\times[0,1)$, supported in a fixed
   compact $K$; the equation holds for $0<t<1$; kinetic energy bounded uniformly for $t<1$; and `SpeedUnboundedAtOne`:
   $\sup_x|u(x,t)|\to\infty$ as $t\uparrow1$. (`R3/ProblemStatement.lean`, `R3/Theorem.lean`.)
2. **All viscosities.** Parabolic rescaling by $\sqrt\nu$ in space gives the candidate at every $\nu>0$ with the same
   singular time 1 (`theorem_1_1_with_initial_rest`).
3. **Comparison.** Any global smooth finite-energy competitor $(v,q)$ with the same $f$ and zero data agrees with the
   candidate for $t<1$. This is a weak–strong uniqueness argument in an $H^3$-type class
   (`strong_unique_of_pressure_pairing`), whose only delicate input is that the competitor's pressure — about which
   (7) says nothing — pairs correctly against test functions; `PressureRecovery.lean` recovers the canonical pressure
   gradient of any smooth finite-energy competitor by time-averaging and a vanishing theorem for harmonic
   functionals.
4. **Contradiction.** A global smooth $v$ is bounded on the compact set $K\times[0,1]$, but equals the candidate there,
   whose speed is unbounded as $t\uparrow1$ (`CandidateBreakdown.lean`). Hence no competitor exists: (C).
5. **Torus.** The compact candidate is compressed into the central quarter-cube and periodized; uniqueness of smooth
   periodic solutions with periodic pressure gives (D) (`PeriodicPaperTheorem.lean`, `ComparatorTheorem.lean`).

This is the standard logical shape "one singular solution + uniqueness in the official class ⇒ nonexistence of a global
solution". The mathematically hard content — the construction in step 1 — occupies essentially all of the 429 k lines
and I did not read it; its correctness is exactly what the kernel check certifies.

## 7. What I could not do, and how to do it

The sandbox's network policy blocks `release.lean-lang.org` (Lean toolchains), the Mathlib cache hosts, and
`claymath.org`, `arxiv.org`, `openai.com`. GitHub itself is reachable, so the repository and the DeepMind reference
were fetched and hashed, but no Lean binary or Mathlib `.olean` cache could be obtained, and compiling Mathlib from
source on four cores is not feasible in a session. To reproduce the kernel check on an ordinary machine (expect
several hours and ~10 GB):

```bash
git clone https://github.com/openai/NavierStokesAndEuler.git
cd NavierStokesAndEuler
git checkout f9e8bc5b38b6e212696e8a30e3e91517af887bbd
sha256sum ComparatorChallenges/NavierStokes.lean   # expect 0cd193b8d5cbd0266e6e2f72e68dd5abcdcf2430ebd435dd9289737e9aa7da61
lake exe cache get
lake build
```

```bash
# independent statement/axiom/kernel check (needs landrun, lean4export, nanoda_bin on PATH; see ComparatorChallenges/README.md)
lake exe comparator ComparatorChallenges/NavierStokes.json
lake exe comparator ComparatorChallenges/Euler.json
```

```bash
# the scripts in this repository
audit/fetch_and_diff.sh /tmp/ns-audit
```

A successful run of the second block is the strongest available evidence for (C)/(D) short of a human-readable proof.
Anyone who runs it should also diff `ComparatorChallenges/NavierStokes.lean` against the frozen copy here before
trusting it: the challenge file is the trusted base.

*Update, 9 November 2026.* `audit/kernel-check/` now automates all of the above from pinned inputs, with Mathlib built
from source, and adds `#print axioms` and `leanchecker`. Its README explains how to run it as three SLURM jobs on
Harvard's FASRC Cannon cluster. The pinned Lean release is also published on GitHub, which cloud sessions can reach:
the job's fetch stage, which downloads every input and checks it against the hashes frozen here, passed on 7 November
(as recorded in that README) and again on 9 November 2026. On 9 November the challenge statement and the DeepMind
reference it fetched were byte-identical to the frozen copies, and their diff matched the one behind Section 4. The
build and check stages have not been run for this audit yet, so the verdict above is unchanged: the kernel check
still rests on OpenAI's own report and on whoever has run it since.

## 8. The "lost in translation" critique, read carefully

Bastounis, Circelli and Hansen (arXiv:2610.08144, 6 Oct 2026) compare the manuscript with the Lean development and
report that the pressure-flux bound (10.19) and the argument of Lemma 8.6 are not what the Lean files
(e.g. `NavierStokes/R3/PressureFlux.lean`) prove; they conclude that "the formalised Lean proof does not correspond to
the NL proof", and state explicitly that they are not claiming the natural-language proof is wrong. Three
consequences, which the press coverage has tended to blur:

* **The formal theorem is unaffected.** If the challenge statement is faithful (Section 3) and the build is sound, (C)
  and (D) are theorems whatever the PDF says. The Lean development is the proof; the PDF is a commentary on it.
* **The manuscript is not, by itself, a verified proof.** Its 166 pages have not been refereed, and the one published
  close reading found places where it and the certificate diverge. Human understanding of *why* the construction works
  is therefore incomplete, which is a legitimate concern for the Clay process (general acceptance) even if the
  formal certificate is impeccable.
* **The provenance question is separate again.** Whether the construction follows Córdoba–Martínez-Zoroa, or
  Alpöge–Buckmaster, or neither, and who deserves credit, does not change what is proved.

## 9. Residual risks and open items

| risk | status |
|---|---|
| challenge file does not mean what it says | audited in Section 3; one documented caveat (3.4) |
| hidden axioms / escape hatches | none found by static scan; must be confirmed by `#print axioms` and Comparator on a rebuild |
| tampered Mathlib cache or toolchain | mitigated only by rebuilding from pinned commits on an independent machine |
| Lean kernel bug | mitigated by the second kernel (nanoda) when Comparator is run with `enable_nanoda` |
| statement faithful but trivially satisfiable | not possible here: (C)/(D) have no definition holes; all definitions are fixed by the challenge |
| human-readable proof incorrect or non-matching | open (Section 8); irrelevant to the formal theorem, relevant to acceptance |
| (A)/(B) | untouched and open |

## 10. Bottom line

As a formal claim, (C) and (D) are in the best evidential position any Millennium-problem claim has ever been in:
a mechanically checked proof of an independently written statement that I have verified, line by line, is the
official one (modulo the periodic-pressure erratum). As a piece of human mathematics, the result is not yet
understood, not yet refereed, and not accepted by the Clay Institute. And as an answer to the question most people
mean — do smooth, unforced, finite-energy Navier–Stokes flows ever blow up? — it says nothing at all.
