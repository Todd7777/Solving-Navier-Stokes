# Kernel check of 12–13 November 2026

**Machine-checked.** On GitHub's runners, OpenAI's Lean development was rebuilt from source, Mathlib included: that
is `openai/NavierStokesAndEuler` at the audited commit `f9e8bc5`. Every check of `audit/kernel-check/kernel_check.sh`
passed (`SUMMARY.txt` ends with `OVERALL PASS`). The checked theorems are the Lean encodings of Clay statements (C) and
(D), `NavierStokes.Comparator.navier_stokes_breakdown_R3` and `…_periodic`, and OpenAI's two Euler theorems.

A kernel check cannot tell whether those Lean statements say what (C) and (D) say. That is the human audit in
`docs/03-audit-openai-lean-formalization.md`, Section 3, with its caveat on periodic pressure (3.4). Nothing here bears
on (A) or (B), which remain open.

The files are the run's `results/` directory, copied unchanged from the artifact of its last job. `SHA256SUMS` covers
every file except this README, and `tests/test_published_results.py` checks it.

## Provenance

| | |
|---|---|
| run | [kernel-check run 43243527940](https://github.com/Todd7777/Solving-Navier-Stokes/actions/runs/43243527940), attempt 1, started by `workflow_dispatch` with the default inputs (`nanoda` off, `sandbox` auto) |
| scripts | this repository at `15cbf0997130816c622c1b18d83ab87e1be7c120` |
| inputs | Lean 4.34.0-rc2 (commit `6a10ac8c`, release zip checked against its pinned SHA-256); the OpenAI repository at `f9e8bc5b38b6e212696e8a30e3e91517af887bbd`; its eleven Lake dependencies at their pinned revisions (`dependencies.txt`); landrun `ec104f6` |
| machines | three GitHub-hosted runners, each with 4 CPUs, 16 GB of memory and Linux 7.0.0-1017-azure with Landlock active (`jobs.log`, `machine-*.txt`); runner image `ubuntu24/20261111.370` for slot 01 and `ubuntu24/20261101.360` for slots 02 and 03 (job logs) |
| artifact | `results-slot-03-attempt-1` (id 14005563448). Its zip has SHA-256 `9fad26aa167320c61d2e18165e963bc7ecbf9fd0f09fffea5e8eed13326159bf`, the digest GitHub recorded; GitHub deletes it on 13 December 2026 |

## Timeline (UTC)

| job | worked | what it did |
|---|---|---|
| slot 01 | 12 Nov, 15:06–19:48 | started from an empty work directory (no cache entry); fetch, 1 min; Mathlib from source, 2 h 51 min; the checking tools, under a minute; Comparator for Navier–Stokes, 38 min, and for Euler, 1 h 12 min |
| slot 02 | 12 Nov 19:53 – 13 Nov 00:50 | `#print axioms`; `leanchecker` parts 1–7, about 38 min each; part 8 was cut off by the job's time limit |
| slot 03 | 13 Nov, 00:56–02:58 | part 8 again from the start, 37 min, and part 9, 5 min; `leanchecker --fresh` for the two solution modules, 38 and 41 min; static scan |

From start to final report the run took 11 h 55 min. The check steps add up to 8 h 19 min. Slots 02 and 03 report
the same host name, `runnervm7aw5e`, but ran on different runners (1000000365 and 1000000382, `jobs.log`).

## What each line of SUMMARY.txt means

| line | meaning |
|---|---|
| Lean release; audited files; DeepMind reference; lake dependencies | The inputs are those audited in `docs/03`: the release zip and its commit, the eight pinned files of the OpenAI repository (`hash-check.txt`) and the eleven dependencies. `diff-reference-vs-challenge.txt` is byte-identical to the diff of 9 November, which matched the one behind `docs/03`, Section 4. |
| Lake build caches: none; build Mathlib from source | No prebuilt file entered the build. Lake's downloads and its local artifact cache were off, and Mathlib and its dependencies were compiled in 8,761 build jobs (`build-mathlib.log`). |
| sandbox: landrun, Landlock active | Comparator compiled the solution inside a real landrun sandbox, not its unsandboxed shim. |
| Comparator: NavierStokes, Euler | Comparator's verdict, "Your solution is okay!" (`comparator-*.log`). It means that (i) each listed theorem has exactly the challenge's statement, down to every declaration the statement uses; (ii) its proof uses no axioms beyond `propext`, `Quot.sound` and `Classical.choice`; (iii) the exported proof replays through the Lean kernel. The four "declaration uses `sorry`" warnings in these logs come from the challenge files, whose theorems are `sorry` placeholders by design. |
| `#print axioms`; main theorems use only … | Lean reports exactly `[propext, Classical.choice, Quot.sound]` for all four main theorems, as OpenAI's `formalization.yaml` records. |
| `leanchecker`: replay modules, parts 1–9 | Each of the 2,438 compiled solution modules (609 under `NavierStokes/`, 1,829 under `Euler/`; `leanchecker-parts.txt`) had its own declarations replayed through the kernel on top of its imports. This is Lean's check against "environment hacking", meaning declarations that reached an `.olean` file without passing the kernel. Its logs are empty because `leanchecker` prints nothing unless it finds a problem. |
| `leanchecker --fresh` | Every declaration in the environment of each solution module, Lean core and Mathlib included, was replayed into an empty environment. |
| static scan | None of 17 patterns occurs in `NavierStokes/` or `Euler/`: `sorry`, `axiom`, `unsafe`, `native_decide`, `implemented_by`, `@[extern`, `opaque`, `partial`, `set_option`, `ofReduceBool`, `admit`, `run_cmd`, `run_tac`, `#eval`, `initialize`, `macro_rules`, `elab`. |

The 2,438 modules are the ones the two solution modules import, directly or indirectly. The other 207 files under
`NavierStokes/` and 10 under `Euler/` are not imported. They were not compiled, and they play no part in the checked
proof.

## Caveats

1. **One kernel.** Only Lean's own kernel checked the proof. Comparator's second kernel, nanoda, was not run, although
   OpenAI's configuration enables it. The workflow leaves it off by default because the runners have only 16 GB.
   `leanchecker` replays through the same kernel: it catches declarations that bypassed the kernel, not a bug in it.
2. **The sandbox fell short of two of Comparator's assumptions.** Comparator's README (at the pinned `19e111e`) asks
   for the check to run under `systemd-run --property=RestrictAddressFamilies=~AF_UNIX`. That guards against a landrun
   vulnerability that Linux 7.1 fixes. The runners had Linux 7.0, and the script does not add the guard. The README
   also assumes an unprivileged user, but GitHub's runner account can use `sudo` without a password; the workflow
   itself does so to free disk space. Both matter only if compiling the solution runs code that attacks the checker.
   The static scan finds no compile-time code in the solution (no `elab`, `macro_rules`, `initialize`, `#eval`,
   `run_cmd`, `run_tac`, `unsafe`, `implemented_by` or `@[extern`), so compiling it runs only Lean's and Mathlib's own
   elaborators and tactics.
3. **GitHub is in the trusted base.** Its runners are, and so is the Actions cache that carried the work directory from
   job to job. Comparator ran entirely in slot 01, from an empty work directory, so it does not depend on the cache.
   `#print axioms` and `leanchecker` ran in slots 02 and 03, on the toolchain and the compiled files restored from the
   cache. The job logs show the chain: slot 02 restored the entry slot 01 had saved (`kc-43243527940-slot-01-attempt-1`,
   4.4 GB), and slot 03 the one slot 02 had saved. Only workflow runs of this repository can write such entries.
4. **Order of the two Comparator checks.** Comparator also assumes that nothing adversarial has been compiled before
   the challenge. The Navier–Stokes check came first, when only Mathlib and the tools had been built. The Euler check
   ran in the same directory after the Navier–Stokes solution had been compiled; the argument in 2 covers it.
5. **One run.** A second run elsewhere would take GitHub out of the trusted base, and with nanoda it would add a second
   kernel. FASRC is one option (`audit/kernel-check/README.md`).
