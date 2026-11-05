# Status of the problem as of 5 November 2026

## 1. One-paragraph summary

On 8 September 2026 OpenAI announced an AI-generated proof of finite-time blowup for the three-dimensional
incompressible Navier–Stokes equations *with a smooth external force*, on $\mathbb R^3$ and on the torus, i.e. Clay
alternatives (C) and (D), together with a Lean 4 formalization checked against an independently written statement.
The Clay Mathematics Institute said on 11 September that the problem had "apparently been settled" and that its
evaluation would be "deliberately unhurried"; it still lists the problem as open. The unforced statements (A) and
(B) — global regularity for all smooth data with $f\equiv0$ — are untouched and open. A priority dispute with
Tristan Buckmaster and Levent Alpöge, whose forced-blowup results for Euler, Boussinesq and the porous-medium
equation were released the same week, and a published critique arguing that the Lean proof does not faithfully
mirror the English manuscript, are the two live controversies. Neither affects the logical status of (A)/(B).

## 2. Timeline

Dates are from the sources listed in Section 5. Items marked † rest on secondary reporting only.

| date | event |
|---|---|
| 2014 | Otelbaev's claimed proof of (B) withdrawn after a counterexample to its key inequality (Montgomery-Smith; Tao). |
| 2016 | Tao: finite-time blowup for an averaged Navier–Stokes equation (JAMS). |
| 2019 | Buckmaster–Vicol: non-uniqueness of weak solutions (Annals). |
| 2022 | Albritton–Brué–Colombo: non-uniqueness of forced Leray solutions (Annals 196). Chen–Hou: computer-assisted Euler/Boussinesq blowup with boundary. |
| 2023–25 | Córdoba–Martínez-Zoroa: forced blowup for 3D Euler and related models. |
| 18 Sep 2025 | Google DeepMind with Gómez-Serrano, Buckmaster et al.: families of *unstable* self-similar singularities for Euler (with boundary), IPM and Boussinesq, found with physics-informed neural networks. Not Navier–Stokes. |
| Aug–Sep 2026 | Alpöge–Buckmaster (and Coiculescu for IPM): finite-time blowup with smooth forcing for IPM, 2D Boussinesq and 3D Euler, with Lean formalizations; a hypodissipative Navier–Stokes result announced but withheld pending completion of its formal check. Tao (Mathstodon, 8 Sep†): "a remarkable achievement", no obvious obstruction in principle to reaching Navier–Stokes. |
| 3–6 Sep 2026† | Buckmaster's public account: word of the unpublished work reaches OpenAI; two calls with Sébastien Bubeck on 6 Sep. OpenAI disputes the account; Bubeck calls the allegations false. |
| 8 Sep 2026 | OpenAI publishes a 166-page manuscript *Finite time blowup for Navier–Stokes*, a 57-page *Finite time blowup for the Euler equation*, a blog post, and the repository `openai/NavierStokesAndEuler`; says it will not claim the prize. Quanta Magazine covers it the same day. |
| 10 Sep 2026 | Repository commit `f9e8bc5b…` (the snapshot audited here). |
| 11 Sep 2026 | Clay Mathematics Institute statement: problem "apparently been settled", review "deliberately unhurried" and "absolutely rigorous" (Martin Bridson). |
| late Sep 2026 | Preprints on the *unforced* search (e.g. arXiv:2609.23868, "The Positive Defect Problem") and expository companions to the OpenAI construction (arXiv:2609.35406). |
| 6 Oct 2026 | Bastounis, Circelli, Hansen, arXiv:2610.08144, *Navier–Stokes lost in translation*: argue that bound (10.19) and the argument of Lemma 8.6 in the manuscript are not faithfully represented in the Lean development (file `NavierStokes/R3/PressureFlux.lean`), and that Lean-checking an autoformalization does not certify the natural-language proof. They explicitly do not claim the theorem is false. |
| Oct 2026† | Scientific American: experts working through the manuscript say it does *not* follow the Córdoba–Martínez-Zoroa program OpenAI first cited (Cao-Labora: "a fundamentally different method"); De Lellis: resolution of the provenance question is unlikely because the model's reasoning is opaque. |
| 5 Nov 2026 | No refereed publication; Clay lists the problem as open; (A)/(B) open; no public unforced result. |

## 3. What is and is not established

| claim | evidence | status |
|---|---|---|
| (C), (D) as formal theorems in Lean 4 + Mathlib, against DeepMind's independent statement | `openai/NavierStokesAndEuler`, sorry-free, standard axioms only, Comparator + nanoda enabled (per the repository) | **claimed and machine-checked by the authors**; independently reproducible by anyone with the toolchain (see audit §7); not yet refereed |
| the formal statement is Fefferman's (C)/(D) | line-by-line audit in `03-…` | **confirmed here**, with one documented caveat on the periodic pressure erratum |
| the English manuscript is a correct human-readable proof | disputed (arXiv:2610.08144; expert comments in the press) | **not established**; the certificate is the Lean development, not the PDF |
| unforced Euler blowup on $\mathbb R^3$ from smooth compactly supported data | same repository, separate statement | claimed and machine-checked by the authors; a major result on its own if it holds |
| (A), (B) | nothing new | **open** |
| unforced Navier–Stokes blowup | nothing new (Alpöge–Buckmaster's withheld result is hypodissipative and forced) | **open** |
| Clay prize | rules require publication, two years, general acceptance | **not awarded; not claimed** |

## 4. What this repository contributes

* a precise statement of the four alternatives and the logic between them (`01-…`);
* an independent audit of the formal statement and the structure of the formal proof, with the inputs frozen and hashed (`03-…`, `audit/`);
* complete proofs of the classical estimates and a precise account of the obstruction (`04-…`, `05-…`);
* a checklist for the next claim (`06-…`);
* exact symbolic verification of every identity used, and tested numerical instruments (`verify/`, `numerics/`, `tests/`).

It does **not** contain a proof of (A) or (B), or of unforced blowup. Anyone claiming otherwise, in this repository or
elsewhere, should be measured against `06-failed-claims-and-audit-checklist.md`.

## 5. Sources

Primary (read directly in this session):
* `https://github.com/openai/NavierStokesAndEuler` — the formalization (commit `f9e8bc5b38b6e212696e8a30e3e91517af887bbd`).
* `https://github.com/google-deepmind/formal-conjectures` — `FormalConjectures/Millenium/NavierStokes.lean` at commit `8bf45ed7…` and at `main` (now `Millennium/`).
* `https://github.com/leanprover/comparator` — what the Comparator check guarantees (now `lake check` in Lean ≥ 4.35).

Primary (not reachable from the sandbox; cited by URL):
* OpenAI announcement: `https://openai.com/index/navier-stokes-solution/`; manuscripts `https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf` and `https://cdn.openai.com/pdf/315b36cd-ec98-4023-8342-93345194ece1/euler.pdf`.
* Clay Mathematics Institute: problem page `https://www.claymath.org/millennium/navier-stokes-equation/`; official statement `https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf`; rules `https://www.claymath.org/millennium-problems/rules`.
* Bastounis, Circelli, Hansen, arXiv:2610.08144 (`https://arxiv.org/abs/2610.08144`).
* Albritton, Brué, Colombo, Ann. of Math. 196 (2022) 415–455 (`https://annals.math.princeton.edu/2022/196-1/p03`).
* Google DeepMind blog, 18 Sep 2025 (`https://deepmind.google/blog/discovering-new-solutions-to-century-old-problems-in-fluid-dynamics/`).
* Otelbaev counterexample: `https://warwick.ac.uk/fac/sci/maths/people/staff/james_robinson/lf/otelbaev/`; `https://aperiodical.com/2014/06/so-what-happened-to-the-abc-conjecture-and-navier-stokes/`.

Secondary (press; used only for dates and quotations, marked † above):
Quanta Magazine (8 Sep 2026), Scientific American (Sep–Oct 2026, three articles), Science (`science.org`, "How an AI math breakthrough ignited a controversy"), Axios (8 Sep 2026), The Tufts Daily (Sep 2026), the-decoder.com, and the statement by Tristan Buckmaster hosted at `cims.nyu.edu/~tristanb/statement.pdf`.
