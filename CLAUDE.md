# CLAUDE.md

Guidance for Claude Code sessions in this repository, local or cloud.

## What this is

An audited account of the Navier–Stokes Millennium problem: Fefferman's four statements, the status of the
2026 claims, a line-by-line audit of OpenAI's Lean formalization of the forced-breakdown statements (C) and (D),
complete proofs of the classical estimates, sympy-verified identities, and tested spectral solvers.
Unforced global regularity, statements (A) and (B), is open, and this repository does not settle it.

## Ground rules

- Do not claim or imply that the problem is solved, and always say which of (A)–(D) a statement concerns.
  Label every new claim as **Theorem** (complete proof here), **Machine-checked**, **Cited** (only after reading
  the source), **Numerical**, or **Conjecture/Heuristic**.
- A numerical pattern is evidence, not proof. Try to construct a counterexample before building on it.
- Run the checks before and after every change. A new failure is a regression until shown otherwise.
- Commit verified work in small steps and push before the session ends. Work left only inside a cloud
  session can be lost with it.

## Setup and checks

```bash
pip install -r requirements.txt
python verify/identities.py
pytest -q          # 2026-11-08: 7 pass
```

## State on 2026-11-08

- `audit/kernel-check/kernel_check.sh` rebuilds OpenAI's proof and runs the kernel checks. It is Linux-only and
  compiles Mathlib from source by default, which takes hours. A cloud session (about 4 CPUs and 16 GB of RAM)
  is the wrong place for it. Run it on a cluster.
- The audit itself could not rebuild the proof. `docs/03-audit-openai-lean-formalization.md`, Section 7, says
  what was and was not checked and gives the exact rebuild commands.

## Where the next steps are

`docs/05-why-A-and-B-are-open.md` and the audit checklist in `docs/06-failed-claims-and-audit-checklist.md`.
