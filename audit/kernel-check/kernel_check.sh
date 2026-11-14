#!/usr/bin/env bash
# Independent rebuild and kernel check of OpenAI's Lean proof of Clay statements (C)/(D)
# (github.com/openai/NavierStokesAndEuler @ f9e8bc5), plus its unforced-Euler companion.
#
# Usage:  kernel_check.sh [fetch|build|check|all]      (default: all)
#   fetch  downloads only (Lean release, the audited repository, pinned dependencies,
#          the DeepMind reference statement); verifies every hash. Safe on a login node.
#   build  compiles the TRUSTED part only: Mathlib (from source by default) and the
#          checking tools (Comparator, lean4export, optionally landrun and nanoda).
#          OpenAI's files are NOT compiled here (Comparator assumption 2).
#   check  runs Comparator for Navier-Stokes and Euler (which builds the solution inside
#          its sandbox), then #print axioms, leanchecker (incl. --fresh), and a static scan.
#          Writes results/SUMMARY.txt.
#
# The stages can run as separate jobs (fasrc.sbatch runs them under SLURM, github_slot.sh on
# GitHub-hosted runners). Re-running a stage is safe: downloads and finished Lake builds in WORK
# are reused, and the stage's lines in SUMMARY.txt are replaced, not appended to. A stage that
# completes leaves results/summary/<stage>.done.
#
# Environment knobs:
#   WORK=/path            working directory (default: $PWD/ns-kernel-check)
#   USE_MATHLIB_CACHE=1   download Mathlib's binary cache instead of compiling it (faster;
#                         adds trust in the cache, see Comparator README). Default 0.
#   SANDBOX=auto|landrun|fake   landrun needs Go >= 1.24 and Landlock (Linux >= 5.13);
#                         'fake' uses Comparator's own unsandboxed shim. Default auto.
#   NANODA=auto|1|0       the nanoda second kernel, at the pinned NANODA_COMMIT: fetch downloads its
#                         source and locked crates, build compiles it offline, and Comparator runs it.
#                         Needs Rust's cargo for fetch and build. 1 stops at once without cargo;
#                         auto uses nanoda if cargo is on PATH. Default auto.
#   LEAN_ZIP_PATH=/path   reuse an already-downloaded copy of the Lean release zip.
#   LEAN_NUM_THREADS=n    worker threads of Lake, Comparator and leanchecker. Lean's default is
#                         every CPU of the machine, not the CPUs a batch job was given.
#   LEANCHECKER_THREADS=n modules replayed at once by `leanchecker NavierStokes Euler`. Each
#                         replay reads its own copy of the .olean files it imports (most of
#                         Mathlib), so memory is the limit. Default min(CPUs, GB of RAM / 16): one
#                         replay at a time fit on GitHub's 16 GB runners on 12-13 November 2026.
#   RESUME_CHECK=1        continue an interrupted or partly failed check: steps already recorded
#                         as PASS are kept and skipped; everything else runs again. Default 0.
#   RESUME_CHECK=all      continue an interrupted check: every recorded result, PASS or FAIL, is
#                         kept; only steps without one run again.
#   MAX_STEP_ATTEMPTS=n   in a resumed check, a step that has already been started n times without
#                         finishing is recorded as FAIL instead of starting again. Default 0 (no limit).
#   LEANCHECKER_PART=n    replay the NavierStokes.* and Euler.* modules in parts of about n modules
#                         each, every part a step of its own. Default 0 (one step for all).
#   STOP_AT=t             do not start another step after time t (seconds since the epoch): exit
#                         with status 75 instead, so that a resumed run carries on. Default: none.
set -euo pipefail

# ---------------------------------------------------------------- pinned inputs
LEAN_VERSION=4.34.0-rc2
LEAN_ZIP=lean-${LEAN_VERSION}-linux.zip
LEAN_URL=https://github.com/leanprover/lean4/releases/download/v${LEAN_VERSION}/${LEAN_ZIP}
# SHA-256 of the official release asset as downloaded on 2026-11-07 (records what was audited).
LEAN_ZIP_SHA256=6556f597afc0509a6a3f70330ee59d07c32f3b1ea584409840d6f2a6f0388b4b
LEAN_COMMIT=6a10ac8c22beadecabdbb0919c2b50214762f91d
OPENAI_URL=https://github.com/openai/NavierStokesAndEuler.git
OPENAI_COMMIT=f9e8bc5b38b6e212696e8a30e3e91517af887bbd
FC_URL=https://raw.githubusercontent.com/google-deepmind/formal-conjectures/8bf45ed70d48b2b2a501de9c00b26bfa38c573ee/FormalConjectures/Millenium/NavierStokes.lean
FC_SHA256=f446284f2aa54375f558c263a580b34e2e7bc9f44a28829637199cc72257d25d
LANDRUN_URL=https://github.com/zouuup/landrun.git
NANODA_URL=https://github.com/ammkrn/nanoda_lib.git
# nanoda_lib master on 2026-11-07 (version 0.4.32). It reads export format 3.1.0 up to, not including,
# 3.2.0; the pinned lean4export (cacf989) writes 3.1.0.
NANODA_COMMIT=0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929
EXPECTED_HASHES='0cd193b8d5cbd0266e6e2f72e68dd5abcdcf2430ebd435dd9289737e9aa7da61  ComparatorChallenges/NavierStokes.lean
b11e9bafc220c8126142a9c9281cfeab4872d8f74a7d4899fed206f7f6e1d4f7  ComparatorChallenges/Euler.lean
7610ecead7b390d80ff7f4229a3ff8f18d630e046f7ad1de4f92c7e8e76845b8  ComparatorChallenges/NavierStokes.json
56bc185a931f68d9a0f0265a3c00cb12771dccc85384eaf6546b37844b8adc84  ComparatorChallenges/Euler.json
52950d5d618a8d34c9bfbdb16641c81c276e97b6d7fd2a76c08577353f0b0227  NavierStokes/ComparatorSolution.lean
97b2804da5b9a2cd0aaf44ce42b7c39e9947beff9d2ac01a11e0d3d867af1c09  lakefile.toml
5ec1dc8e009008d0efb9601cd38f6ba54e753fd538b0e5f8c3e6c5ec72ee1e09  lake-manifest.json
8190e75a201741065fe508b28955dd64dd72d090babe5f70ce6848879d68ae88  lean-toolchain'
MAIN_THEOREMS='NavierStokes.Comparator.navier_stokes_breakdown_R3
NavierStokes.Comparator.navier_stokes_breakdown_periodic
Euler.euler_breakdown_R3
Euler.exists_compact_smooth_euler_singularity'

# ---------------------------------------------------------------- settings
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
WORK=${WORK:-$PWD/ns-kernel-check}
mkdir -p "$WORK" && WORK=$(cd "$WORK" && pwd)   # absolute: later steps cd into the project
USE_MATHLIB_CACHE=${USE_MATHLIB_CACHE:-0}
SANDBOX=${SANDBOX:-auto}
NANODA=${NANODA:-auto}
LEAN_ZIP_PATH=${LEAN_ZIP_PATH:-}
LEANCHECKER_THREADS=${LEANCHECKER_THREADS:-}
RESUME_CHECK=${RESUME_CHECK:-0}
MAX_STEP_ATTEMPTS=${MAX_STEP_ATTEMPTS:-0}
LEANCHECKER_PART=${LEANCHECKER_PART:-0}
STOP_AT=${STOP_AT:-}
case $RESUME_CHECK in 0|1|all) ;; *) echo "RESUME_CHECK must be 0, 1 or all" >&2; exit 2 ;; esac
case $NANODA in auto|0|1) ;; *) echo "NANODA must be auto, 1 or 0" >&2; exit 2 ;; esac
case $MAX_STEP_ATTEMPTS$LEANCHECKER_PART$STOP_AT in
  *[!0-9]*) echo "MAX_STEP_ATTEMPTS, LEANCHECKER_PART and STOP_AT must be whole numbers" >&2; exit 2 ;;
esac
PROJ=$WORK/NavierStokesAndEuler
TOOLS=$WORK/tools
LEANBIN=$TOOLS/lean-${LEAN_VERSION}-linux/bin
RESULTS=$WORK/results
CARGO_DIR=$WORK/cargo   # CARGO_HOME for nanoda: its crates are downloaded by fetch and reused offline
mkdir -p "$TOOLS" "$RESULTS/summary"
LOG=$RESULTS/run.log
STAGE=none

log()    { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" | tee -a "$LOG" >&2; }
# SUMMARY.txt is assembled from one file per stage, so re-running a stage replaces its lines.
summarize() { cat "$RESULTS"/summary/{fetch,build,check}.txt >"$RESULTS/SUMMARY.txt" 2>/dev/null || true; }
record() { printf '%-58s %s\n' "$1" "$2" | tee -a "$RESULTS/summary/$STAGE.txt" >&2; summarize; }
record_once() { # record, unless this exact line is already there (a resumed check)
  grep -Fxq -- "$(printf '%-58s %s' "$1" "$2")" "$RESULTS/summary/$STAGE.txt" 2>/dev/null || record "$1" "$2"
}
die()    { log "FATAL: $*"; record "FATAL" "$*"; exit 1; }
resuming() { [ "$STAGE" = check ] && [ "$RESUME_CHECK" != 0 ]; }
kept_result() { # kept_result <label>: if this resumed check keeps a result for <label>, print it
  resuming || return 1
  awk -v l="$1" -v keep_fail="$([ "$RESUME_CHECK" = all ] && echo 1 || echo 0)" '
    index($0, l " ") == 1 { s = substr($0, length(l) + 2); sub(/^ +/, "", s); if (keep_fail || s ~ /^PASS/) { r = s; f = 1 } }
    END { if (f) print r; exit !f }' "$RESULTS/summary/$STAGE.txt"
}
begin()  { # begin <stage>: start a stage on this machine (a resumed check keeps earlier results)
  STAGE=$1
  local part=$RESULTS/summary/$STAGE.txt drop='^(OVERALL|FATAL) |(^| )FAIL( |$)'
  rm -f "$RESULTS/summary/$STAGE.done"
  if resuming && [ -f "$part" ]; then
    if [ "$RESUME_CHECK" = all ]; then drop='^(OVERALL|FATAL) '; fi
    grep -vE "$drop" "$part" >"$part.kept" || true
    mv "$part.kept" "$part"
  else
    : >"$part"
    : >"$RESULTS/machine-$STAGE.txt"
    rm -f "$RESULTS/summary/$STAGE.attempts"
  fi
  summarize
  { echo "host $(hostname)  cpus $(nproc)  mem $(free -g | awk '/Mem:/{print $2}')G  kernel $(uname -r)  Landlock $(landlock_active && echo yes || echo no)"
    date -u; } >>"$RESULTS/machine-$STAGE.txt"
  log "stage $STAGE on $(hostname)$(resuming && echo ", resuming (RESUME_CHECK=$RESUME_CHECK)")"
}
end_stage() { : >"$RESULTS/summary/$STAGE.done"; log "stage $STAGE complete"; }
timed()  { # timed <label> <logfile> <cmd...> : run, log output, record PASS/FAIL and seconds
  local label=$1 out=$2 kept n; shift 2
  if kept=$(kept_result "$label"); then log "kept from an earlier run: $label: $kept"; [[ $kept == PASS* ]]; return; fi
  if [ -n "$STOP_AT" ] && [ "$(date +%s)" -ge "$STOP_AT" ]; then log "out of time, not starting: $label"; exit 75; fi
  if resuming && [ "$MAX_STEP_ATTEMPTS" -gt 0 ]; then
    n=$(grep -Fxc -- "$label" "$RESULTS/summary/check.attempts" 2>/dev/null || true)
    if [ "${n:-0}" -ge "$MAX_STEP_ATTEMPTS" ]; then
      record "$label" "FAIL not finished in $n attempts (cut off by time limits)"; return 1
    fi
  fi
  if [ "$STAGE" = check ]; then printf '%s\n' "$label" >>"$RESULTS/summary/check.attempts"; fi
  local t0=$SECONDS rc=0
  log "start: $label"
  "$@" >"$out" 2>&1 || rc=$?
  if [ $rc -eq 0 ]; then record "$label" "PASS ($((SECONDS - t0)) s)"; else record "$label" "FAIL rc=$rc ($((SECONDS - t0)) s) see $(basename "$out")"; fi
  return $rc
}

# ---------------------------------------------------------------- environment
# Only the pinned toolchain in $LEANBIN may be used: drop variables that would point Lake or
# Lean at another toolchain, compiler, search path or package URL.
unset LEAN LEAN_PATH LEAN_SRC_PATH LEAN_SYSROOT LEAN_CC LEAN_AR LEAN_GITHASH LAKE LAKE_HOME \
      LAKE_OVERRIDE_LEAN LAKE_PKG_URL_MAP LAKE_RESTORE_ARTIFACTS ELAN ELAN_HOME ELAN_TOOLCHAIN
if [ "$USE_MATHLIB_CACHE" != 1 ]; then
  # From source means no prebuilt artifact enters the build. `--no-cache` only stops downloads:
  # this Lake also restores modules from a local artifact cache by default (~/.cache/lake or an
  # elan toolchain cache), which may hold artifacts built elsewhere. Turn that off and keep any
  # cache directory Lake touches inside WORK. (Comparator's fake shim passes these on to its own
  # `lake build`; a real landrun sandbox passes only PATH, HOME and LEAN_ABORT_ON_PANIC.)
  export LAKE_NO_CACHE=1 LAKE_ARTIFACT_CACHE=false LAKE_CACHE_DIR=$WORK/lake-cache
fi

# ---------------------------------------------------------------- fetch
fetch_lean() {
  local zip=$TOOLS/$LEAN_ZIP
  if [ ! -f "$zip" ]; then
    if [ -n "$LEAN_ZIP_PATH" ]; then cp "$LEAN_ZIP_PATH" "$zip"; else curl -fL --retry 5 --retry-delay 5 -o "$zip" "$LEAN_URL"; fi
  fi
  local h; h=$(sha256sum "$zip" | cut -d' ' -f1)
  [ "$h" = "$LEAN_ZIP_SHA256" ] || die "Lean release zip sha256 $h differs from the audited $LEAN_ZIP_SHA256"
  if [ ! -x "$LEANBIN/lean" ]; then
    # -I everywhere: never import Python modules from the current directory (it may be the
    # downloaded project) or from user site-packages.
    python3 -I - "$zip" "$TOOLS" <<'PY'
import os, sys, zipfile
z = zipfile.ZipFile(sys.argv[1])
for info in z.infolist():
    p = z.extract(info, sys.argv[2])
    mode = (info.external_attr >> 16) & 0o777
    if mode:
        os.chmod(p, mode)
PY
  fi
  "$LEANBIN/lean" --version | tee "$RESULTS/lean-version.txt" >&2
  grep -q "$LEAN_COMMIT" "$RESULTS/lean-version.txt" || die "unexpected Lean commit"
  record "Lean $LEAN_VERSION release: zip SHA-256 and commit" "PASS"
}

fetch_repo() {
  if [ ! -d "$PROJ/.git" ]; then git clone --filter=blob:none "$OPENAI_URL" "$PROJ"; fi
  git -C "$PROJ" -c advice.detachedHead=false checkout -q "$OPENAI_COMMIT"
  [ "$(git -C "$PROJ" rev-parse HEAD)" = "$OPENAI_COMMIT" ] || die "OpenAI repository is not at $OPENAI_COMMIT"
  [ -z "$(git -C "$PROJ" status --porcelain --untracked-files=no)" ] || die "tracked files of the OpenAI repository are modified"
  (cd "$PROJ" && printf '%s\n' "$EXPECTED_HASHES" | sha256sum -c -) >"$RESULTS/hash-check.txt" 2>&1 \
    || die "a pinned file of the OpenAI repository does not match the audited hash (see hash-check.txt)"
  record "audited files match frozen SHA-256 hashes" "PASS"
  curl -fsSL --retry 5 -o "$WORK/formal-conjectures_NavierStokes.lean" "$FC_URL"
  local h; h=$(sha256sum "$WORK/formal-conjectures_NavierStokes.lean" | cut -d' ' -f1)
  [ "$h" = "$FC_SHA256" ] || die "DeepMind reference statement hash $h differs from the audited one"
  diff <(sed 's/^[[:space:]]*//' "$WORK/formal-conjectures_NavierStokes.lean") \
       <(sed 's/^[[:space:]]*//' "$PROJ/ComparatorChallenges/NavierStokes.lean") >"$RESULTS/diff-reference-vs-challenge.txt" || true
  record "DeepMind reference fetched, diff written" "PASS"
}

fetch_deps() {
  mkdir -p "$PROJ/.lake/packages"
  : >"$RESULTS/dependencies.txt"
  python3 -I - "$PROJ/lake-manifest.json" >"$WORK/deps.tsv" <<'PY'
import json, sys
for p in json.load(open(sys.argv[1]))["packages"]:
    print("\t".join([p["name"], p["url"], p["rev"]]))
PY
  while IFS=$'\t' read -r name url rev; do
    local d=$PROJ/.lake/packages/$name
    if [ ! -d "$d/.git" ]; then
      mkdir -p "$d"
      git -C "$d" init -q && git -C "$d" remote add origin "$url"
      local i ok=0
      for i in 1 2 3 4 5; do if git -C "$d" fetch -q --depth 1 origin "$rev"; then ok=1; break; fi; sleep $((2 ** i)); done
      [ $ok = 1 ] || die "could not fetch $name@$rev"
      git -C "$d" -c advice.detachedHead=false checkout -q FETCH_HEAD
    fi
    [ "$(git -C "$d" rev-parse HEAD)" = "$rev" ] || die "$name is not at the pinned revision $rev"
    printf '%-18s %s\n' "$name" "$rev" >>"$RESULTS/dependencies.txt"
  done <"$WORK/deps.tsv"
  record "all lake dependencies at pinned revisions" "PASS"
}

# The nanoda second kernel: does this run use it (NANODA=1, or auto with cargo on PATH)?
nanoda_wanted() { [ "$NANODA" = 1 ] || { [ "$NANODA" = auto ] && command -v cargo >/dev/null 2>&1; }; }
require_cargo() { # with NANODA=1, stop before any work if fetch or build could not handle nanoda
  [ "$NANODA" != 1 ] || command -v cargo >/dev/null 2>&1 \
    || die "NANODA=1 but cargo is not on PATH: install Rust (rustup) and start again, or set NANODA=0"
}
# Run cargo and rustc in nanoda's own directory, never in the audited project's: rustup and cargo read
# toolchain and configuration files (rust-toolchain.toml, .cargo/config.toml) from the current directory.
in_nanoda() { (cd "$TOOLS/nanoda_lib" && CARGO_HOME=$CARGO_DIR "$@"); }
nanoda_source() { # the pinned nanoda source, and the crates its Cargo.lock names, inside WORK
  local d=$TOOLS/nanoda_lib i ok=0
  if [ "$(git -C "$d" rev-parse HEAD 2>/dev/null)" != "$NANODA_COMMIT" ]; then
    rm -rf "$d" "$TOOLS/nanoda.crates"
    mkdir -p "$d"
    git -C "$d" init -q && git -C "$d" remote add origin "$NANODA_URL"
    for i in 1 2 3 4 5; do if git -C "$d" fetch -q --depth 1 origin "$NANODA_COMMIT"; then ok=1; break; fi; sleep $((2 ** i)); done
    [ $ok = 1 ] || die "could not fetch nanoda@$NANODA_COMMIT"
    git -C "$d" -c advice.detachedHead=false checkout -q FETCH_HEAD
  fi
  [ "$(git -C "$d" rev-parse HEAD)" = "$NANODA_COMMIT" ] || die "nanoda is not at the pinned revision $NANODA_COMMIT"
  [ -z "$(git -C "$d" status --porcelain --untracked-files=no)" ] || die "tracked files of nanoda are modified"
  if [ ! -f "$TOOLS/nanoda.crates" ]; then
    in_nanoda cargo fetch --locked >"$RESULTS/nanoda-fetch.log" 2>&1 \
      || die "could not download nanoda's crates (see nanoda-fetch.log)"
    : >"$TOOLS/nanoda.crates"
  fi
}
fetch_nanoda() {
  nanoda_wanted || return 0
  nanoda_source
  record "nanoda ${NANODA_COMMIT:0:7}: source and locked crates fetched" "PASS"
}

# ---------------------------------------------------------------- build (trusted part only)
lean_env() { export PATH="$LEANBIN:$PATH"; cd "$PROJ"; }

landlock_active() { [ -r /sys/kernel/security/lsm ] && grep -qw landlock /sys/kernel/security/lsm; }

build_tools() {
  # Sandbox: real landrun when possible, else Comparator's own unsandboxed shim (recorded).
  local mode=$SANDBOX
  if [ "$mode" = auto ]; then
    if command -v go >/dev/null 2>&1 && landlock_active; then mode=landrun; else mode=fake; fi
  fi
  if [ "$mode" = landrun ]; then
    [ -d "$TOOLS/landrun/.git" ] || git clone -q --depth 1 "$LANDRUN_URL" "$TOOLS/landrun"
    (cd "$TOOLS/landrun" && go build -o landrun cmd/landrun/main.go)
    echo "$TOOLS/landrun/landrun" >"$TOOLS/LANDRUN"
    record "sandbox" "landrun $(git -C "$TOOLS/landrun" rev-parse --short HEAD); Landlock active: $(landlock_active && echo yes || echo no)"
  else
    echo "$PROJ/.lake/packages/Comparator/scripts/fake-landrun.sh" >"$TOOLS/LANDRUN"
    record "sandbox" "NONE (Comparator fake-landrun shim; Landlock active: $(landlock_active && echo yes || echo no))"
  fi
  if nanoda_wanted; then
    nanoda_source   # a no-op when the fetch stage has already downloaded it
    timed "build nanoda ${NANODA_COMMIT:0:7} (cargo --frozen, offline)" "$RESULTS/build-nanoda.log" \
      in_nanoda cargo build --release --frozen || die "nanoda did not build (see build-nanoda.log)"
    echo "$TOOLS/nanoda_lib/target/release/nanoda_bin" >"$TOOLS/NANODA"
    record "second kernel" "nanoda ${NANODA_COMMIT:0:7}, $(in_nanoda rustc --version 2>/dev/null || echo 'rustc version unknown')"
  elif [ "$NANODA" = 0 ]; then
    rm -f "$TOOLS/NANODA"
    record "second kernel" "NOT RUN (NANODA=0)"
  else
    rm -f "$TOOLS/NANODA"
    record "second kernel" "NOT RUN (no cargo; set NANODA=1 after installing Rust)"
  fi
}

build() {
  lean_env
  build_tools   # landrun and nanoda first: a problem with them shows in minutes, not after Mathlib
  if [ "$USE_MATHLIB_CACHE" = 1 ]; then
    timed "Mathlib binary cache download (trusted cache)" "$RESULTS/mathlib-cache.log" lake exe cache get
    timed "build Mathlib (on top of cache)" "$RESULTS/build-mathlib.log" lake build +Mathlib
  else
    record "Lake build caches" "none (no downloads, no local artifact cache)"
    timed "build Mathlib from source (no cache)" "$RESULTS/build-mathlib.log" lake build --no-cache +Mathlib
  fi
  timed "build Comparator and lean4export" "$RESULTS/build-tools.log" lake build --no-cache @Comparator/comparator @lean4export/lean4export
}

# ---------------------------------------------------------------- check
comparator_run() { # comparator_run <name> <config>
  local name=$1 cfg=$2
  local nanoda_file=$TOOLS/NANODA
  export COMPARATOR_LANDRUN; COMPARATOR_LANDRUN=$(cat "$TOOLS/LANDRUN")
  export COMPARATOR_LEAN4EXPORT=$PROJ/.lake/packages/lean4export/.lake/build/bin/lean4export
  if [ -f "$nanoda_file" ]; then
    export COMPARATOR_NANODA; COMPARATOR_NANODA=$(cat "$nanoda_file")
  else
    # Same challenge, theorems and axioms; only the nanoda flag is dropped (recorded in SUMMARY).
    python3 -I - "$cfg" "$RESULTS/$name.no-nanoda.json" <<'PY'
import json, sys
c = json.load(open(sys.argv[1])); c.pop("enable_nanoda", None)
json.dump(c, open(sys.argv[2], "w"), indent=2)
PY
    cfg=$RESULTS/$name.no-nanoda.json
  fi
  timed "Comparator: $name (statement match, axioms, kernel replay$([ -f "$nanoda_file" ] && echo ', nanoda'))" \
    "$RESULTS/comparator-$name.log" lake env "$PROJ/.lake/packages/Comparator/.lake/build/bin/comparator" "$cfg"
}

check_axioms() {
  local f out rc=0 kept label="main theorems use only propext/choice/Quot.sound"
  if kept=$(kept_result "$label"); then log "kept from an earlier run: $label: $kept"; return 0; fi
  for f in PrintAxiomsNavierStokes PrintAxiomsEuler; do
    out=$RESULTS/$f.txt
    timed "#print axioms ($f)" "$out" lake env lean "$HERE/$f.lean" || rc=1
  done
  # Every main theorem must depend on exactly {propext, Classical.choice, Quot.sound}.
  python3 -I - "$RESULTS" "$MAIN_THEOREMS" <<'PY' || rc=1
import re, sys, pathlib
text = "".join(p.read_text() for p in pathlib.Path(sys.argv[1]).glob("PrintAxioms*.txt"))
ok = True
for thm in sys.argv[2].split():
    m = re.search(r"'%s' depends on axioms: \[([^\]]*)\]" % re.escape(thm), text)
    got = set(a.strip() for a in m.group(1).split(",")) if m else None
    good = got == {"propext", "Classical.choice", "Quot.sound"}
    ok &= good
    print(("PASS " if good else "FAIL ") + thm + " axioms=" + (", ".join(sorted(got)) if got else "NOT FOUND"))
sys.exit(0 if ok else 1)
PY
  if [ $rc -eq 0 ]; then record "$label" "PASS"; else record "$label" "FAIL"; fi
}

static_scan() {
  local pat n out=$RESULTS/static-scan.txt
  : >"$out"
  for pat in '\bsorry\b' '^\s*axiom\b' '\bunsafe\b' 'native_decide' 'implemented_by' '@\[extern' '^\s*opaque\b' \
             '^\s*partial\b' 'set_option' 'ofReduceBool' '\badmit\b' 'run_cmd' 'run_tac' '#eval' '^\s*initialize\b' 'macro_rules' '\belab\b'; do
    n=$( (grep -rEn --include='*.lean' -- "$pat" "$PROJ/NavierStokes" "$PROJ/Euler" 2>/dev/null || true) | wc -l)
    printf '%-24s %6d\n' "$pat" "$n" >>"$out"
  done
  # In the solution trees only docstring mentions are expected; any code-level hit must be inspected.
  record_once "static scan of NavierStokes/ and Euler/" "written (inspect static-scan.txt)"
}

leanchecker_threads() { # min(CPUs, GB of RAM / 16), at least 1
  local n; n=$(awk '/^MemTotal:/{print int($2 / 1048576 / 16)}' /proc/meminfo)
  [ "$n" -le "$(nproc)" ] || n=$(nproc)
  [ "$n" -ge 1 ] || n=1
  echo "$n"
}

leanchecker_parts() { # leanchecker_parts <n>: the built NavierStokes.* and Euler.* modules as lines of
  # leanchecker arguments, about <n> modules per line. leanchecker takes module-name prefixes, so a
  # module with submodules (NavierStokes.R3) is named once and stands for its subtree. The library
  # roots NavierStokes and Euler are left out: their files contain only imports.
  python3 -I - "$PROJ/.lake/build/lib/lean" "$1" <<'PY'
import pathlib, sys
lib, size = pathlib.Path(sys.argv[1]), int(sys.argv[2])
mods = sorted(".".join(p.relative_to(lib).parts)[:-len(".olean")]
              for top in ("NavierStokes", "Euler") if (lib / top).is_dir()
              for p in (lib / top).rglob("*.olean"))
names = set(mods)
def root(m):  # the shortest module that m lies under (m itself if none)
    parts = m.split(".")
    return next(".".join(parts[:i]) for i in range(2, len(parts) + 1) if ".".join(parts[:i]) in names)
count = {}
for m in mods:
    count[root(m)] = count.get(root(m), 0) + 1
line, n = [], 0
for r in sorted(count):
    if line and n + count[r] > size:
        print(" ".join(line))
        line, n = [], 0
    line.append(r)
    n += count[r]
if line:
    print(" ".join(line))
PY
}

check() {
  lean_env
  [ -f "$TOOLS/LANDRUN" ] || die "run '$0 build' first"
  [ "$NANODA" != 1 ] || [ -f "$TOOLS/NANODA" ] || die "NANODA=1 but nanoda was not built: run the build stage with NANODA=1"
  # The check may run on a different machine from the build: record the sandbox where Comparator runs.
  record_once "sandbox on this machine" "$(basename "$(cat "$TOOLS/LANDRUN")"); Landlock active: $(landlock_active && echo yes || echo no)"
  comparator_run NavierStokes ComparatorChallenges/NavierStokes.json || true
  comparator_run Euler ComparatorChallenges/Euler.json || true
  check_axioms || true
  # Lean maps each .olean at a fixed address; a second concurrent import of the same file in one
  # process is read into the heap instead. Parallel replays therefore each hold a private copy.
  local lct=${LEANCHECKER_THREADS:-$(leanchecker_threads)}
  log "leanchecker: $lct modules at a time"
  if [ "$LEANCHECKER_PART" -gt 0 ]; then
    local k=0 parts roots
    # A resumed check keeps the parts it started with, so that "part k of n" always names the same modules.
    if ! resuming || [ ! -s "$RESULTS/leanchecker-parts.txt" ]; then
      leanchecker_parts "$LEANCHECKER_PART" >"$RESULTS/leanchecker-parts.txt"
    fi
    parts=$(($(wc -l <"$RESULTS/leanchecker-parts.txt")))
    [ "$parts" -gt 0 ] || record_once "leanchecker: replay modules" "FAIL no built NavierStokes.* or Euler.* module found"
    while IFS= read -r roots <&3; do
      k=$((k + 1))
      # shellcheck disable=SC2086  # one argument per module name
      timed "leanchecker: replay modules, part $k of $parts" "$RESULTS/leanchecker-modules-$k.log" \
        env LEAN_NUM_THREADS="$lct" lake env leanchecker $roots || true
    done 3<"$RESULTS/leanchecker-parts.txt"
  else
    timed "leanchecker: replay every NavierStokes.* and Euler.* module" "$RESULTS/leanchecker-modules.log" \
      env LEAN_NUM_THREADS="$lct" lake env leanchecker NavierStokes Euler || true
  fi
  timed "leanchecker --fresh NavierStokes.ComparatorSolution (whole env)" "$RESULTS/leanchecker-fresh-ns.log" \
    lake env leanchecker --fresh NavierStokes.ComparatorSolution || true
  timed "leanchecker --fresh Euler.Solution (whole env)" "$RESULTS/leanchecker-fresh-euler.log" \
    lake env leanchecker --fresh Euler.Solution || true
  static_scan
  if grep -qE 'FAIL|FATAL' "$RESULTS/SUMMARY.txt"; then record "OVERALL" "FAIL (see above)"; else record "OVERALL" "PASS"; fi
  log "done; results in $RESULTS"
}

case "${1:-all}" in
  fetch) begin fetch; require_cargo; fetch_lean; fetch_repo; fetch_deps; fetch_nanoda; end_stage ;;
  build) begin build; require_cargo; build; end_stage ;;
  check) begin check; check; end_stage ;;
  all)   begin fetch; require_cargo; fetch_lean; fetch_repo; fetch_deps; fetch_nanoda; end_stage
         begin build; build; end_stage
         begin check; check; end_stage ;;
  *) echo "usage: $0 [fetch|build|check|all]" >&2; exit 2 ;;
esac
