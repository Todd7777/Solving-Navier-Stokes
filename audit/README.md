# audit/

Inputs and tooling for `docs/03-audit-openai-lean-formalization.md`.

* `reference/` — byte-exact copies of the audited files, with `SHA256SUMS`:
  * `openai_f9e8bc5_*` from `https://github.com/openai/NavierStokesAndEuler` at commit `f9e8bc5b38b6e212696e8a30e3e91517af887bbd` (Apache-2.0; copyright OpenAI / The Formal Conjectures Authors, headers preserved);
  * `formal-conjectures_8bf45ed_*` and `formal-conjectures_main_2026-11-05_*` from `https://github.com/google-deepmind/formal-conjectures` (Apache-2.0; copyright The Formal Conjectures Authors).
* `scan_lean_repo.sh <repo>` — static scan for `sorry`, axioms, escape hatches, `set_option`, foreign imports; prints sizes and pinned dependencies.
* `fetch_and_diff.sh [workdir]` — clones the audited commit, fetches the DeepMind reference, checks hashes, diffs the challenge against the reference and against the solution-side copy, runs the scan. It also re-downloads Clay's official statement and prize rules and says whether they still match the versions read on 14 November 2026 (docs/01), printing the statement's errata.
* `kernel-check/` — rebuilds the Lean project from source, Mathlib included, and runs Comparator, `#print axioms` and `leanchecker` (see its README).
* `results/` — outputs of the above: the scan and diff of 5 November 2026, and `kernel-check-2026-11-13/`, the results of the kernel check of 12–13 November 2026 with their provenance and caveats. Each published kernel-check directory has a `SHA256SUMS` that the tests verify.

Neither script above builds the Lean project; `kernel-check/` does. See `docs/03`, Section 7.
