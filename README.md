# Solving-Navier-Stokes

**Status (5 November 2026): the Navier–Stokes Millennium Prize Problem is not solved in the sense most people mean, and this
repository does not solve it.**

| Clay statement | content | status |
|---|---|---|
| (A) | unforced global regularity on $\mathbb R^3$ | **open** |
| (B) | unforced global regularity on $\mathbb R^3/\mathbb Z^3$ | **open** |
| (C) | breakdown on $\mathbb R^3$ for some smooth data **and smooth force** | claimed by OpenAI (8 Sep 2026) with a Lean 4 proof of an independently written statement; audited here, and the proof rebuilt from source and kernel-checked here (12–13 Nov 2026); not refereed, not accepted by Clay |
| (D) | breakdown on $\mathbb R^3/\mathbb Z^3$ | same |
| unforced blowup | the question everyone means | **open** |

On 14 November 2026, Clay's Millennium Problems page listed Navier–Stokes alone under "Active problems", apart from
its five "Unsolved problems" and the solved Poincaré conjecture, without saying what "Active" means. No prize has been
awarded (`docs/02-status-november-2026.md`).

What this repository is: an honest, checkable account of where the problem stands, with every claim either proved
in full, verified by machine, or marked as someone else's claim with its evidence.

## Contents

| path | what it is |
|---|---|
| `docs/01-official-problem.md` | Fefferman's four statements, side conditions (1)–(11), the erratum, the prize rules, and the logic between the statements |
| `docs/02-status-november-2026.md` | timeline of the 2026 claims and disputes; what is and is not established; sources |
| `docs/03-audit-openai-lean-formalization.md` | **line-by-line audit** of OpenAI's Lean statement against the official (C)/(D); diff against DeepMind's reference; static scan; proof architecture; the kernel check and what it leaves open |
| `docs/04-rigorously-proven-results.md` | complete proofs of the classical estimates (energy identity, scaling, 2D regularity, Leray's local bound, small data, Serrin-type criteria, Lions' hyperviscosity) and precise statements of the deep theorems |
| `docs/05-why-A-and-B-are-open.md` | the supercriticality obstruction, Tao's averaged-equation barrier, non-uniqueness, why forced ≠ unforced |
| `docs/06-failed-claims-and-audit-checklist.md` | documented failed claims and a 15-point checklist for the next one |
| `audit/` | frozen, hashed copies of the audited Lean files; scripts to re-fetch, diff and scan; the kernel check; their outputs, including the kernel check's results |
| `verify/identities.py` | exact symbolic verification (sympy) of every identity used in `docs/04`, including an exact non-zero value of the 3D vortex-stretching integral |
| `numerics/spectral.py` | tested pseudo-spectral 2D/3D solvers used to cross-check the identities numerically |
| `tests/` | `pytest` suite (symbolic checks must pass; solvers must satisfy the energy identity, 2D monotonicity, the exact Taylor–Green solution, and agree with the exact stretching integral) |

## Run the checks

```bash
pip install -r requirements.txt
python verify/identities.py
python -m pytest -q
```

```bash
# re-fetch the audited Lean sources, verify hashes, diff against DeepMind's reference, re-run the static scan
audit/fetch_and_diff.sh /tmp/ns-audit
```

Rebuilding the Lean proof itself needs the Lean toolchain and Mathlib; the exact commands are in
`docs/03-audit-openai-lean-formalization.md`, Section 7. `audit/kernel-check/` automates the rebuild, with Mathlib
built from source, and the kernel checks of (C)/(D). It runs as SLURM jobs on Harvard's FASRC cluster or,
experimentally, as chained jobs on GitHub's free runners; see its README. The GitHub route ran on 12–13 November 2026
and every check passed, with Lean's kernel only; the results are in `audit/results/kernel-check-2026-11-13/`.

## The short version of the argument

1. The official problem asks for a proof of **any one** of four statements. Two are regularity (force zero), two are
   breakdown (force allowed). A forced blowup proves a breakdown statement and says nothing about regularity
   for the unforced equation: (A) and (C) can both be true.
2. OpenAI's September 2026 Lean development proves exactly DeepMind's encoding of (C) and (D). I checked that encoding
   against Fefferman's conditions field by field, diffed it against the upstream reference, and scanned the
   640 000-line proof for every known escape hatch. The statement is faithful and the proof is axiom-clean. On
   12–13 November 2026 a rebuild from source on GitHub's runners passed Comparator, `#print axioms` and `leanchecker`
   (Lean's kernel only; caveats in `docs/03`, Section 7).
3. The unforced problem is open because every unconditional estimate is supercritical by half a derivative
   (proved in `docs/04`), and Tao's averaged equation shows no "soft" argument can close that gap.

Nothing here should be read as a solution. If someone tells you Navier–Stokes is solved, ask which of (A)–(D).
