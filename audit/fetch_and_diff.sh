#!/usr/bin/env bash
# Reproduce the audit inputs: clone OpenAI's repository at the audited commit, fetch Google DeepMind's
# Formal Conjectures reference at the commit OpenAI cites, check hashes against audit/reference/SHA256SUMS,
# and diff the challenge statement against the upstream reference.
# Usage: audit/fetch_and_diff.sh [workdir]
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
work="${1:-$(mktemp -d)}"
commit=f9e8bc5b38b6e212696e8a30e3e91517af887bbd
upstream=8bf45ed70d48b2b2a501de9c00b26bfa38c573ee
mkdir -p "$work" && cd "$work"
if [ ! -d NavierStokesAndEuler ]; then
  git clone --filter=blob:none https://github.com/openai/NavierStokesAndEuler.git
fi
git -C NavierStokesAndEuler checkout --quiet "$commit"
curl -sSfL -o formal-conjectures_NavierStokes.lean \
  "https://raw.githubusercontent.com/google-deepmind/formal-conjectures/$upstream/FormalConjectures/Millenium/NavierStokes.lean"
echo "--- hash check against audit/reference/SHA256SUMS ---"
tmp=$(mktemp)
{
  for f in ComparatorChallenges/NavierStokes.lean ComparatorChallenges/Euler.lean ComparatorChallenges/NavierStokes.json \
           ComparatorChallenges/Euler.json formalization.yaml lakefile.toml lake-manifest.json lean-toolchain NavierStokes/ComparatorSolution.lean; do
    sha256sum "NavierStokesAndEuler/$f"
  done
  sha256sum formal-conjectures_NavierStokes.lean
} | awk '{print $1}' | sort > "$tmp"
awk '{print $1}' "$here/reference/SHA256SUMS" | sort > "$tmp.ref"
if comm -13 "$tmp.ref" "$tmp" | grep -q .; then echo "HASH MISMATCH: some fetched file differs from the audited copy"; else echo "all fetched files match the audited copies (by SHA256)"; fi
echo
echo "--- diff: Formal Conjectures reference vs OpenAI challenge (whitespace-insensitive) ---"
diff <(sed 's/^[[:space:]]*//' formal-conjectures_NavierStokes.lean) \
     <(sed 's/^[[:space:]]*//' NavierStokesAndEuler/ComparatorChallenges/NavierStokes.lean) || true
echo
echo "--- diff: OpenAI challenge vs OpenAI solution-side copy of the definitions ---"
diff <(sed 's/^[[:space:]]*//' NavierStokesAndEuler/ComparatorChallenges/NavierStokes.lean) \
     <(sed 's/^[[:space:]]*//' NavierStokesAndEuler/NavierStokes/ComparatorDefinitions.lean) || true
echo
echo "--- static scan ---"
"$here/scan_lean_repo.sh" "$work/NavierStokesAndEuler"
