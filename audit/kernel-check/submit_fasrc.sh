#!/usr/bin/env bash
# Submit the kernel check to SLURM on Harvard FASRC Cannon as three chained jobs,
# fetch -> build -> check, each starting only if the one before succeeded.
#
#   export WORK=$SCRATCH/<lab>/Lab/$USER/ns-kernel-check
#   audit/kernel-check/submit_fasrc.sh [--dry-run] [fetch|build|check]
#
# The stage argument is where the chain starts (default fetch): `submit_fasrc.sh build` resubmits
# the build and then the check, `submit_fasrc.sh check` only the check. --dry-run prints the sbatch
# commands instead of running them. Extra sbatch options, placed after the defaults so they win:
#   KC_SBATCH_ALL     every job, e.g. "--account=<lab> --mail-type=END,FAIL"
#   KC_SBATCH_FETCH, KC_SBATCH_BUILD, KC_SBATCH_CHECK   one stage, e.g. "--time=2-12:00"
set -euo pipefail
set -f   # option strings are split into words below; never glob them
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
repo=$(cd "$here/../.." && pwd)

# Default resources (see README.md). Cannon, per FASRC's docs: `test` allows 12 hours and 5 jobs
# per user and is exempt from fairshare; `sapphire` nodes have 112 cores and 990 GB, allow 3 days,
# and cost the least fairshare of the general CPU partitions (0.6 per core-hour).
resources() {
  case $1 in
    fetch) echo "--partition=test --cpus-per-task=2 --mem=2G --time=0-00:30" ;;
    build) echo "--partition=sapphire --cpus-per-task=64 --mem=256G --time=0-08:00" ;;
    check) echo "--partition=sapphire --cpus-per-task=16 --mem=256G --time=2-00:00" ;;
  esac
}
extra() {
  case $1 in
    fetch) echo "${KC_SBATCH_FETCH:-}" ;;
    build) echo "${KC_SBATCH_BUILD:-}" ;;
    check) echo "${KC_SBATCH_CHECK:-}" ;;
  esac
}
shq() { # one argument as shell input, quoted only if it needs to be
  case $1 in
    *[!A-Za-z0-9_./:=,%@+-]*) printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")" ;;
    *) printf '%s' "$1" ;;
  esac
}

dry=0
first=fetch
for arg in "$@"; do
  case $arg in
    --dry-run) dry=1 ;;
    fetch|build|check) first=$arg ;;
    *) sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//' >&2; exit 2 ;;
  esac
done
if [ -z "${WORK:-}" ]; then
  echo "WORK is not set; e.g. export WORK=\$SCRATCH/<lab>/Lab/\$USER/ns-kernel-check" >&2
  exit 2
fi
case $WORK in
  /*) ;;
  *) echo "WORK must be an absolute path, not '$WORK'" >&2; exit 2 ;;
esac
case $WORK$repo in
  *,*) echo "sbatch --export cannot pass paths that contain commas" >&2; exit 2 ;;
esac
case $first in
  fetch) stages="fetch build check" ;;
  build) stages="build check" ;;
  check) stages="check" ;;
esac

if [ "$dry" = 1 ]; then
  printf 'mkdir -p %s\n' "$(shq "$WORK/slurm")"
else
  command -v sbatch >/dev/null || { echo "sbatch not found: run this on a cluster login node" >&2; exit 1; }
  mkdir -p "$WORK/slurm"
fi

prev=
ids=
for s in $stages; do
  cmd=(sbatch --parsable "--job-name=ns-kc-$s" "--output=$WORK/slurm/%x-%j.out"
       "--export=ALL,WORK=$WORK,NS_REPO=$repo")
  if [ -n "$prev" ]; then cmd+=("--dependency=afterok:$prev" --kill-on-invalid-dep=yes); fi
  # shellcheck disable=SC2206,SC2207  # the option strings are meant to be split into words
  cmd+=($(resources "$s") ${KC_SBATCH_ALL:-} $(extra "$s") "$here/fasrc.sbatch" "$s")
  if [ "$dry" = 1 ]; then
    # Print a runnable line; the previous job's id is the shell variable named after its stage
    # (--parsable prints "id" or "id;cluster").
    line=
    for a in "${cmd[@]}"; do
      case $a in
        --dependency=afterok:\$*) line="$line $a" ;;
        *) line="$line $(shq "$a")" ;;
      esac
    done
    # shellcheck disable=SC2016  # the $( and ${ are meant for the shell that runs the printed line
    printf '%s=$(%s); %s=${%s%%%%;*}\n' "$s" "${line# }" "$s" "$s"
    prev="\$$s"
  else
    id=$("${cmd[@]}")
    id=${id%%;*}
    echo "submitted $s: job $id"
    prev=$id
    ids=$ids${ids:+,}$id
  fi
done
if [ "$dry" = 0 ]; then
  echo "job output: $WORK/slurm/    summary: $WORK/results/SUMMARY.txt"
  echo "follow with: squeue -u ${USER:-$(id -un)}   or   sacct -j $ids -o JobID,JobName%12,State,Elapsed,MaxRSS,ReqMem"
fi
