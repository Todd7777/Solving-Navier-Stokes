# audit/

Inputs and tooling for `docs/03-audit-openai-lean-formalization.md`.

* `reference/` — byte-exact copies of the audited files, with `SHA256SUMS`:
  * `openai_f9e8bc5_*` from `https://github.com/openai/NavierStokesAndEuler` at commit `f9e8bc5b38b6e212696e8a30e3e91517af887bbd` (Apache-2.0; copyright OpenAI / The Formal Conjectures Authors, headers preserved);
  * `formal-conjectures_8bf45ed_*` and `formal-conjectures_main_2026-11-05_*` from `https://github.com/google-deepmind/formal-conjectures` (Apache-2.0; copyright The Formal Conjectures Authors).
* `scan_lean_repo.sh <repo>` — static scan for `sorry`, axioms, escape hatches, `set_option`, foreign imports; prints sizes and pinned dependencies.
* `fetch_and_diff.sh [workdir]` — clones the audited commit, fetches the DeepMind reference, checks hashes, diffs the challenge against the reference and against the solution-side copy, runs the scan.
* `results/` — outputs of the above from 5 November 2026.

Neither script builds the Lean project; see `docs/03`, Section 7 for the kernel check.
