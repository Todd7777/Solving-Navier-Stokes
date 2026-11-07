# Independent kernel check of the 2026 Lean proof of Clay (C)/(D)

This directory contains a self-contained job that rebuilds OpenAI's Lean development
(`github.com/openai/NavierStokesAndEuler` at the audited commit `f9e8bc5`) **from source**,
including Mathlib, and checks it three independent ways. It is the one step of the audit in
`docs/03-audit-openai-lean-formalization.md` that could not be run inside the cloud session that
wrote it (see "Why this was not run here" below).

| file | purpose |
|---|---|
| `kernel_check.sh` | portable driver: `fetch`, `build`, `check`, or `all` |
| `fasrc.sbatch` | SLURM wrapper for Harvard FASRC (Cannon) |
| `PrintAxiomsNavierStokes.lean`, `PrintAxiomsEuler.lean` | `#print axioms` for the four main theorems |

## What the job checks

1. **Inputs are the audited ones.** The Lean release zip, the OpenAI commit, eight pinned files of the
   OpenAI repository, the eleven Lake dependencies and the Google DeepMind reference statement are all
   checked against the hashes and revisions frozen in `audit/reference/`. Any mismatch aborts the run.
2. **Comparator** (the Lean FRO's checker, the version pinned by OpenAI) for both the Navier–Stokes and
   the Euler challenge. It builds the challenge and the solution itself, exports both environments with
   `lean4export`, checks that each main theorem has *exactly* the challenge's statement (down to every
   definition it mentions), that it uses only `propext`, `Quot.sound` and `Classical.choice`, and replays the
   exported proof closure through the Lean kernel and, if Rust is available, through the independent
   `nanoda` kernel.
3. **`#print axioms`** for the four main theorems; the script fails unless each depends on exactly
   `{propext, Classical.choice, Quot.sound}`.
4. **`leanchecker`** (shipped with Lean): replays every declaration of every `NavierStokes.*` and `Euler.*`
   module through the kernel, then replays the *entire* environment of each solution module, Mathlib
   included, into a fresh environment (`--fresh`), which detects environment tampering.
5. A static scan of the solution sources for escape hatches (`sorry`, `axiom`, `unsafe`, `native_decide`,
   `implemented_by`, `set_option`, metaprograms).

The order respects Comparator's assumption that the solution is never compiled outside its sandbox before
Comparator runs. Only Mathlib and the checking tools are built first.

## Trust that remains after a PASS

* The Lean kernel, or nanoda if it ran.
* The Lean release binary. Its SHA-256 is pinned to what was downloaded on 7 November 2026; it is the
  official GitHub release asset of `leanprover/lean4` v4.34.0-rc2, commit `6a10ac8c`.
* The faithfulness of the challenge statement to Fefferman's (C)/(D). That is a human judgement, made line by
  line in `docs/03`, Section 3, with one caveat about the periodic-pressure erratum.
* The sandbox, only if the solution could attack the build. Comparator calls `landrun --best-effort`, which
  silently runs **without** isolation on kernels lacking Landlock (Linux < 5.13). The job records whether
  Landlock was active. The static scan shows the solution defines no metaprograms (no `elab`, `macro_rules`,
  `initialize`, `#eval`, `run_cmd`), so compiling it runs only Mathlib's and Lean's own tactics.

Mathlib is compiled from source by default, which removes the "trust the binary cache" assumption that the
Comparator README mentions. Set `USE_MATHLIB_CACHE=1` to trade that away for speed.

## Running it

On any Linux machine with `git`, `curl`, `python3` (3.6+), about 40 GB of free disk and as many cores as
possible:

```bash
git clone -b claude/gallant-pasteur-52wnri https://github.com/Todd7777/Solving-Navier-Stokes.git
cd Solving-Navier-Stokes
WORK=$PWD/../ns-kernel-check audit/kernel-check/kernel_check.sh all
```

On FASRC, see the header of `fasrc.sbatch`, then:

```bash
sbatch audit/kernel-check/fasrc.sbatch
```

Optional tools: Go ≥ 1.24 for the real `landrun` sandbox, and Rust (`cargo`) for the nanoda second kernel.
Without them the job still runs, and `SUMMARY.txt` records which checks were skipped.

## Results

Everything lands in `$WORK/results/`. `SUMMARY.txt` has one PASS/FAIL line per check and an `OVERALL` line.
Logs for each step sit next to it. To publish a run, copy `results/` into `audit/results/kernel-check-<date>/` in this repository
and commit it. Any FAIL line in Comparator, `#print axioms` or `leanchecker` would be a finding of the first order and
should be reported with its log.

## Why this was not run here

The cloud session that wrote this audit could download the pinned Lean release, the OpenAI repository and every
dependency, and it verified all hashes (the `fetch` phase passed end to end on 7 November 2026). Compiling them was
refused by that session's permission policy, which does not allow executing externally obtained code (about 2.9
million lines of Lean). The machine also had only 4 cores, against roughly 30–60 CPU-hours of work. The job is
written to be run where that is allowed and fast.
