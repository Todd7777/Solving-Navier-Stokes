# Independent kernel check of the 2026 Lean proof of Clay (C)/(D)

This directory contains a self-contained job that rebuilds OpenAI's Lean development
(`github.com/openai/NavierStokesAndEuler` at the audited commit `f9e8bc5`) **from source**,
including Mathlib, and checks it three independent ways. It is the one step of the audit in
`docs/03-audit-openai-lean-formalization.md` that could not be run inside the cloud session that
wrote it (see "Why this was not run here" below). It has since run in full on GitHub's runners, on
12–13 November 2026, and every check passed: see `audit/results/kernel-check-2026-11-13/`.

| file | purpose |
|---|---|
| `kernel_check.sh` | portable driver: `fetch`, `build`, `check`, or `all` |
| `fasrc.sbatch` | runs one stage as a SLURM job on Harvard FASRC (Cannon) |
| `submit_fasrc.sh` | submits fetch, build and check as three chained SLURM jobs |
| `github_slot.sh` | one job of the GitHub Actions run (`.github/workflows/kernel-check.yml`) |
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
  Landlock was active. Comparator's README further asks for a `systemd-run` guard against a landrun vulnerability
  that Linux 7.1 fixes, and for an unprivileged user; this script provides neither. The static scan shows the
  solution defines no metaprograms (no `elab`, `macro_rules`, `initialize`, `#eval`, `run_cmd`), so compiling it runs
  only Mathlib's and Lean's own tactics.

Mathlib is compiled from source by default, which removes the "trust the binary cache" assumption that the
Comparator README mentions. With this Lake (4.34) `lake build --no-cache` is not enough on its own: it stops
downloads, but Lake also restores modules from a local artifact cache by default (`~/.cache/lake` or an elan
toolchain cache), which on a machine that has used Lean before may hold artifacts built elsewhere. The script
therefore sets `LAKE_NO_CACHE=1`, `LAKE_ARTIFACT_CACHE=false` and a `LAKE_CACHE_DIR` inside the work directory,
and clears variables that could point Lake at another toolchain, compiler or search path (`LEAN_PATH`, `LEAN_CC`,
`ELAN_TOOLCHAIN`, …). Set `USE_MATHLIB_CACHE=1` to trade that away for speed.

## Running it

On any Linux machine with `git`, `curl`, `python3` (3.6+), about 40 GB of free disk and as many cores as
possible:

```bash
git clone https://github.com/Todd7777/Solving-Navier-Stokes.git
cd Solving-Navier-Stokes
WORK=$PWD/../ns-kernel-check audit/kernel-check/kernel_check.sh all
```

Optional tools: Go ≥ 1.24 for the real `landrun` sandbox, and Rust (`cargo`) for the nanoda second kernel.
Without them the job still runs, and `SUMMARY.txt` records which checks were skipped.

### On Harvard FASRC (Cannon): three SLURM jobs

The stages need very different resources, so each runs as its own job: `fasrc.sbatch` runs one stage, and
`submit_fasrc.sh` submits all three, each starting only if the one before succeeded. On a login node:

```bash
git clone https://github.com/Todd7777/Solving-Navier-Stokes.git
cd Solving-Navier-Stokes
export WORK=$SCRATCH/<lab>/Lab/$USER/ns-kernel-check   # shared storage; FASRC's example lab is jharvard_lab
audit/kernel-check/submit_fasrc.sh --dry-run           # prints the three sbatch commands
audit/kernel-check/submit_fasrc.sh                     # submits them
```

| stage | partition | CPUs | memory | time limit | basis |
|---|---|---|---|---|---|
| fetch | `test` | 2 | 2 GB | 30 min | measured in a cloud session: 66 s, largest process 100 MB, 4.2 GB written; needs GitHub |
| build | `sapphire` | 64 | 256 GB | 8 h | Mathlib from source: 2.30 million lines in 8,370 files at the pinned commit |
| check | `sapphire` | 16 | 256 GB | 2 days | builds the solution (0.64 million lines, 2,655 files), then long single-threaded kernel replays |

Only the fetch figures are measured, in a cloud session; nothing has been built on Cannon yet. For scale, on GitHub's
runners (4 CPUs, 16 GB) the Mathlib build took 2 h 51 min and the check steps 8 h 19 min, replaying one module at a
time, and nothing ran out of memory (`audit/results/kernel-check-2026-11-13/`). Lean sizes its thread pools by the CPUs of
the node, not of the job, so the job sets `LEAN_NUM_THREADS` to its CPU count. `leanchecker NavierStokes Euler` replays
modules in parallel, and each replay reads its own copy of the `.olean` files it imports (Lean maps a file at a fixed
address only once per process), so the job runs one replay per 12 GB of memory (`LEANCHECKER_THREADS`).

* **Resuming.** Everything lives in `WORK`. If a job runs out of time, submit again from that stage
  (`submit_fasrc.sh build` submits build and check, `submit_fasrc.sh check` only check). Lake keeps every module already
  built, and a re-run stage replaces its own lines in `SUMMARY.txt`. A check can also keep the steps that already
  passed and redo only the rest: `RESUME_CHECK=1 audit/kernel-check/submit_fasrc.sh check`. To change a request, e.g.
  `KC_SBATCH_CHECK="--time=2-12:00"`; for every job, e.g. `KC_SBATCH_ALL="--account=<lab> --mail-type=END,FAIL"`.
* **Fairshare.** Every job is CPU-only. FASRC charges the cores and memory a job was given for as long as it runs,
  failed and killed jobs included. `sapphire` costs 0.6 per core-hour and, by FASRC's formula, about 0.07 per GB-hour
  (exact weights: `scontrol show partition sapphire`), less than `shared` (1.0 per core-hour) or the requeue
  partitions (0.125 per GB-hour); `test` is exempt but meant for development and testing. At these sizes a 2-hour
  build would cost about 110 TRES-hours and a 12-hour check about 320. The check asks for only 16 cores because most
  of it is single-threaded. To spend less: try the build on `test` for an hour first
  (`KC_SBATCH_BUILD="--partition=test --time=0-01:00" audit/kernel-check/submit_fasrc.sh`; the check job is then
  cancelled, and a later `submit_fasrc.sh build` continues where the test stopped), resume instead of restarting, and
  size later runs with `seff <job>`.
* **Killed is not rejected.** A step that fails with `rc=137` was killed, usually for exceeding its memory, and says
  nothing about the proof. See `sacct -j <job> -o JobID,State,MaxRSS,ReqMem` and resubmit with more memory or a smaller
  `LEANCHECKER_THREADS`, with `RESUME_CHECK=1` so that only the killed step runs again.
* **Network.** Only the fetch job needs it, plus the build job if `cargo` or Go is on your `PATH` (to clone nanoda or
  landrun). If compute nodes cannot reach GitHub, run `audit/kernel-check/kernel_check.sh fetch` on a login node with
  `WORK` set (about 20 s of CPU) and then `submit_fasrc.sh build`.
* **Sandbox.** landrun needs Landlock (Linux 5.13 or later). FASRC's compute nodes run Rocky Linux 8.10 with kernel 4.18
  (FASRC, June 2025), so expect Comparator's unsandboxed shim; `SUMMARY.txt` and `machine-check.txt` record what the
  check node had. See "Trust that remains after a PASS".
* **Optional tools** come from the `PATH` you submit with: install Rust (rustup) first if you want the nanoda kernel.
* **Scratch is purged.** FASRC deletes netscratch files older than 90 days (60 from December 2026). Copy `results/`
  out when the check finishes.

### On GitHub Actions (free, experimental)

`.github/workflows/kernel-check.yml` runs the same stages on GitHub's free runners, which give a public repository
4 CPUs, 16 GB of memory and at most 6 hours per job. The work goes through up to 20 chained jobs ("slots"). Each slot
works for about 5 hours from wherever the previous one stopped, then saves the work directory in the repository's
Actions cache for the next. Only `workflow_dispatch` starts it, and GitHub offers that only once the workflow file is
on the default branch. Then use Actions > kernel-check > Run workflow, or:

```bash
gh workflow run kernel-check.yml
```

Each slot's `results/` is an artifact (`results-slot-NN-attempt-M`). The final `report` job shows the latest
`SUMMARY.txt` and fails unless the check finished with `OVERALL` PASS.

The check replays one module at a time and splits `leanchecker NavierStokes Euler` into parts of about 300 modules, so
that each part fits in a slot (`LEANCHECKER_PART`). A step cut off by a slot's time limit starts again in the next slot,
at most three times, and is then recorded as `FAIL not finished`. A step killed for memory (`rc=137`) is recorded and not
retried. On a 16 GB runner either outcome is a limit of the runner, not a finding about the proof. The nanoda kernel is
off by default for the same reason.

The first full run (run 43243527940, 12–13 November 2026) took three slots and 11 h 55 min. Slot 01 fetched, built
Mathlib in 2 h 51 min, and ran both Comparator checks (38 min and 1 h 12 min). Slot 02 ran `#print axioms` and seven
`leanchecker` parts of about 38 minutes each. Slot 03 reran the part that slot 02's time limit had cut off, then ran the
last part and the two `--fresh` replays (38 and 41 min). Nothing ran out of memory, Comparator included, and every
check passed. The results are in `audit/results/kernel-check-2026-11-13/`.

Trust: the build is still from source, but GitHub's runners and its cache, which carries the build from slot to slot,
join the trusted base. A runner's kernel may offer Landlock, in which case Comparator runs inside real landrun;
`SUMMARY.txt` records which sandbox ran. On 12–13 November the runners had Linux 7.0 with Landlock, and the runner
account could use `sudo` without a password (see "Trust that remains after a PASS"). "Re-run failed jobs" on a failed
slot resumes from what that slot saved. A run fills most of the repository's 10 GB Actions cache; the last entry
expires after 7 days unused, or can be deleted under Actions > Caches.

## Results

Everything lands in `$WORK/results/`. `SUMMARY.txt` has one PASS/FAIL line per check and an `OVERALL` line.
Logs for each step sit next to it, `machine-<stage>.txt` describes the machine each stage ran on, and under SLURM or
GitHub Actions `jobs.log` lists the jobs and the commit of this repository they ran. The SLURM check job ends as FAILED unless
`OVERALL` is PASS. To publish a run, from the repository checkout:

```bash
d=audit/results/kernel-check-$(date -u +%F)
mkdir -p "$d" && cp -r "$WORK/results/." "$d/"
git switch -c "kernel-check-$(date -u +%F)"
git add "$d" && git commit -m "Kernel-check results from FASRC Cannon"
git push -u origin HEAD
```

and open a pull request. This repository is public, and the logs contain cluster paths and your username. Any FAIL
line in Comparator, `#print axioms` or `leanchecker` would be a finding of the first order and should be reported with
its log, once a killed process (`rc=137`) has been ruled out.

## Why this was not run here

The cloud session that wrote this audit could download the pinned Lean release, the OpenAI repository and every
dependency, and it verified all hashes (the `fetch` phase passed end to end on 7 November 2026). Compiling them was
refused by that session's permission policy, which does not allow executing externally obtained code (about 2.9
million lines of Lean). The machine also had only 4 cores, against roughly 30–60 CPU-hours of work. The job is
written to be run where that is allowed and fast.

On 9 November 2026 a later cloud session ran the fetch stage again, through `fasrc.sbatch` and into an empty
directory: every hash and revision matched, and the network policy blocked no host. That session did not build or
check either; the SLURM jobs above exist for that.

On 12–13 November 2026 the GitHub Actions route ran all three stages, and every check passed. See "On GitHub Actions"
above and `audit/results/kernel-check-2026-11-13/`.
