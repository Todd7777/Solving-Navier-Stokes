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
python -m pytest -q   # 2026-11-13: 25 pass
```

In the cloud environment `pytest` on PATH can be a uv tool without numpy or sympy, which fails at collection;
`python -m pytest` runs in the interpreter the requirements went into.

## State on 2026-11-13

- `audit/kernel-check/kernel_check.sh` rebuilds OpenAI's proof and runs the kernel checks. It is Linux-only and
  compiles Mathlib from source by default, which takes hours. A cloud session is the wrong place for it. It runs as
  three chained SLURM jobs on FASRC Cannon (`audit/kernel-check/submit_fasrc.sh`) or as up to 20 chained jobs on
  GitHub's free runners (`.github/workflows/kernel-check.yml`, experimental); see `audit/kernel-check/README.md`.
- **The kernel check has run.** GitHub run 43243527940 (2026-11-12/13, three jobs, 11 h 55 min) built Mathlib from
  source and passed every check: Comparator for (C)/(D) and for Euler, `#print axioms`, `leanchecker` per module
  and `--fresh`. The results, with provenance, are in `audit/results/kernel-check-2026-11-13/` (a `SHA256SUMS` the
  tests verify). `docs/03`, Sections 0, 7 and 9, records it as Machine-checked, with caveats: Lean's kernel only
  (nanoda off), a sandbox short of two of Comparator's assumptions (Linux 7.0 without the `systemd-run` guard; the
  runner account has passwordless `sudo`), and GitHub's runners and cache in the trusted base. It says nothing
  about (A) or (B), nor about whether the Lean statements are (C) and (D) (`docs/03`, Section 3).
- The first GitHub run (2026-11-12) stopped at once because `github_slot.sh` lacked its executable bit (fixed in
  `15cbf09`). Comparator fit in 16 GB. Runners had a 145 GB disk with 118 GB free after cleanup.
- FASRC: the fetch stage passed in a cloud session on 2026-11-09; build and check have not run on Cannon. The
  README's Fairshare note says how to keep the cost down, and the GitHub timings are a basis for sizing.

## Where the next steps are

`docs/05-why-A-and-B-are-open.md` and the audit checklist in `docs/06-failed-claims-and-audit-checklist.md`.
For the kernel check: a second run off GitHub with the nanoda kernel, for example on FASRC (`docs/03`, Section 9).
