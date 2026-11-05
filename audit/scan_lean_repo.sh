#!/usr/bin/env bash
# Static scan of a Lean 4 proof repository for escape hatches and unsoundness vectors.
# Usage: audit/scan_lean_repo.sh /path/to/NavierStokesAndEuler
# This does NOT replace a kernel check (lake build / lake check / Comparator); it is the cheap first pass.
set -euo pipefail
repo="${1:?path to repository}"
cd "$repo"
dirs=(NavierStokes Euler ComparatorChallenges)
printf '%-44s %8s\n' "pattern" "hits"
for pat in '\bsorry\b' '\bsorryAx\b' '^\s*axiom\b' '\bunsafe\b' 'native_decide' 'implemented_by' '@\[extern' \
           '^\s*opaque\b' '^\s*partial\b' 'set_option' 'ofReduceBool' '\badmit\b' 'decide\s*:=\s*true' \
           'run_cmd' 'run_tac' '#eval' '\binitialize\b' 'macro_rules' '\belab\b' 'Classical\.choice' 'propext' 'Quot\.sound' 'local\s+instance'; do
  n=$( (grep -rEn --include='*.lean' -- "$pat" "${dirs[@]}" 2>/dev/null || true) | wc -l)
  printf '%-44s %8d\n' "$pat" "$n"
done
echo
echo "--- every 'sorry' with context (expected: only the intentional challenge placeholders) ---"
grep -rEn --include='*.lean' '\bsorry\b' "${dirs[@]}" || true
echo
echo "--- every 'axiom' declaration (expected: none) ---"
grep -rEn --include='*.lean' '^\s*axiom\b' "${dirs[@]}" || echo "(none)"
echo
echo "--- every 'set_option' (expected: none) ---"
grep -rEn --include='*.lean' 'set_option' "${dirs[@]}" || echo "(none)"
echo
echo "--- imports outside Mathlib and the project (expected: none) ---"
grep -rhoE --include='*.lean' '^import [A-Za-z0-9_.]+' "${dirs[@]}" | sort -u | grep -vE '^import (Mathlib|NavierStokes|Euler)' || echo "(none)"
echo
echo "--- sizes ---"
for d in "${dirs[@]}"; do
  echo "$d: $(find "$d" -name '*.lean' | wc -l) files, $(cat $(find "$d" -name '*.lean') | wc -l) lines, $(grep -rhoE --include='*.lean' '^\s*(theorem|lemma)\b' "$d" | wc -l) theorem/lemma, $(grep -rhoE --include='*.lean' '^\s*(noncomputable )?def\b' "$d" | wc -l) def"
done
echo
echo "--- pinned toolchain and dependencies ---"
cat lean-toolchain
python3 - <<'PY'
import json
m = json.load(open('lake-manifest.json'))
for p in m['packages']:
    print(f"{p['name']:16s} {p['rev']}  ({p['url']})")
PY
