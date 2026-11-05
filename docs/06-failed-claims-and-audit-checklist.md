# Claimed solutions that failed, and a checklist for auditing the next one

Claimed proofs of Navier–Stokes regularity (or blowup) appear every year. The failures have recognisable
shapes. This document records the well-documented cases and turns them into a checklist that was applied,
in `03-audit-openai-lean-formalization.md`, to the 2026 claim.

## 1. Documented failed claims

**Penny Smith, 2006.** "Immortal smooth solution of the three space dimensional Navier–Stokes system"
(arXiv, October 2006) claimed global regularity. The author withdrew it within days after a gap was found
in a key lemma. Lesson: an argument that is correct "except for one lemma" is not a proof; the hard lemma
*is* the problem.

**Mukhtarbay Otelbaev, 2013–14.** A 100-page paper in Russian claimed global existence for the periodic
problem (statement (B)) via an abstract inequality for a class of nonlinear operators. The inequality
(numbered (6.34), derived from (6.33) on p. 56) was false: counterexamples were given publicly by Stephen
Montgomery-Smith and, in simplified form, by Terence Tao, and the author acknowledged in February 2014
that Proposition 6.3 was not proved. Lesson: an abstract inequality that would prove regularity for *every*
operator sharing the formal properties of the Navier–Stokes nonlinearity is exactly what Tao's 2016 averaged
counterexample says cannot exist. Check every abstract lemma on the simplest concrete operator.

**Unrefereed and lightly refereed "proofs", 2008–2025.** Dozens of preprints and a few journal papers
(in venues outside the mainstream analysis literature) claim (A) or (B). Recurring errors, each of which
contradicts a theorem in `04-rigorously-proven-results.md`:

* using a maximum principle for the vorticity in 3D (false: the stretching term $(\omega\cdot\nabla)u$ has no sign; Theorem 3);
* using conservation of $\|\omega\|_{L^p}$ (true only in 2D; Theorem 4);
* closing an $H^1$ estimate with the energy bound alone (impossible: Theorem 5 and Theorem 5′);
* treating the pressure as an independent given function rather than the nonlocal functional
  $p = -\Delta^{-1}\partial_i\partial_j(u_iu_j)$ determined by $u$;
* proving uniqueness in a class in which uniqueness is false (Buckmaster–Vicol 2019);
* "regularity for small data" presented as regularity for all data (Theorem 6 is classical);
* a numerical computation presented as a proof.

**2026 (status, not failure).** The OpenAI forced-blowup claim (statements (C), (D)) has a machine-checked
formalization and a natural-language manuscript. The formal statement is faithful (Section 3 of the audit).
The manuscript's correspondence to the formal proof has been publicly disputed (Bastounis–Circelli–Hansen,
arXiv:2610.08144), and experts quoted in the press say the argument does not follow the program OpenAI
originally cited. None of that is a refutation; it means human understanding of the proof lags the
machine certificate. It also has nothing to do with (A)/(B).

## 2. The checklist

Apply every item to any claimed resolution. A single "no" on items 1–6 is fatal.

### Statement
1. **Which Clay alternative, exactly?** (A)/(B) are unforced regularity for all data; (C)/(D) are forced breakdown for some data. Does the claim's theorem statement match one of them *verbatim*, including: $\nu>0$ arbitrary, $n=3$, smoothness of $u^0$ and $f$, the decay conditions (4)/(5) or periodicity (8)/(9), smooth $p$ and $u$ on $\mathbb R^3\times[0,\infty)$, bounded energy (7) on $\mathbb R^3$, periodic $p$ on the torus?
2. **Is the solution class the official one?** Weak solutions, mild solutions, solutions in a space-time Sobolev class, solutions "with $p \in L^{3/2}$": each is a different problem. A regularity theorem in a smaller class or a nonexistence theorem in a larger class is not the Clay statement.

### Regularity proofs (A)/(B)
3. **Tao's test.** Would the argument apply unchanged to the averaged equation of Tao (2016)? If yes, it is wrong.
4. **Scaling test.** Identify the quantity the proof claims to bound for all time. Compute its scaling exponent under $u_\lambda = \lambda u(\lambda x,\lambda^2t)$. If the exponent is negative, the bound cannot control small scales and some step is false. If the only inputs are the energy identity and Sobolev/interpolation inequalities, the exponent is $-\tfrac12$ (Theorem 5′).
5. **Dimension test.** Does the argument work equally in dimension $n\ge4$, or for the hypodissipative equation $(-\Delta)^\alpha$ with $\alpha<5/4$? Any such "proof" proves too much.
6. **Concrete check of every abstract inequality** (the Otelbaev test) on the simplest nontrivial operator.

### Blowup proofs (C)/(D) or unforced
7. **Is the constructed object an exact solution** for the stated $f$ in the stated class, with $f$ *verified* smooth and decaying (the hard part of forced constructions), or merely an approximate one?
8. **Does the nonexistence conclusion use a valid uniqueness theorem** in the official class — on $\mathbb R^3$ with no decay assumption on $p$ and no $L^2$ bound on $\nabla u$ (only (7))?
9. **Does blowup happen on a compact set** (so that smoothness of a global competitor on $\mathbb R^3\times[0,\infty)$ gives a contradiction), or only at infinity?
10. **Is it unforced?** If $f\neq0$, the result is (C)/(D) and leaves (A)/(B) untouched. Say so.

### Formal proofs
11. **Faithfulness of the formal statement.** Was the statement written independently of the prover (e.g. the Google DeepMind Formal Conjectures encoding), and compared mechanically (Comparator / `lake check`)? Read every definition in the challenge file; junk values of partial operations (`fderiv`, `derivWithin`, Bochner integrals) must be closed off by explicit hypotheses.
12. **Axioms and escape hatches.** Only `propext`, `Quot.sound`, `Classical.choice`; no `sorry`, `axiom`, `native_decide`, `implemented_by`, `unsafe`, `opaque`/`partial` in the proof closure; no `set_option` tricks; a second kernel (nanoda) agrees.
13. **Trusted base.** Pinned toolchain and Mathlib commit, untampered cache, sandboxed build, independent rebuild on a second machine.
14. **Prose vs. formal.** A mismatch between the natural-language proof and the Lean proof does not invalidate the formal theorem; it does mean the manuscript is not itself a verified proof and must be read as an informal commentary on the formal development.

### Social
15. **Peer review and the prize rules.** The Clay rules (revised 2018) require publication in a qualifying refereed outlet, a two-year waiting period, and general acceptance by the community. A press release, a blog post, a preprint and a compiled repository satisfy none of these yet.

## 3. How this repository should be updated

* If (C)/(D) are accepted (refereed publication plus Clay statement): update `02-status-november-2026.md` and the status table in `05-why-A-and-B-are-open.md`; (A)/(B) remain open.
* If an error is found in the OpenAI formalization (e.g. a definition in the challenge file that does not mean what it says): record the exact declaration and why, in `03-audit-openai-lean-formalization.md`.
* If an unforced result appears: it is a new theorem, not covered by any document here; audit it with the checklist above before writing anything.
