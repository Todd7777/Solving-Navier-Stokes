#!/bin/bash
#SBATCH --job-name=ns-kc
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=sapphire
#SBATCH --cpus-per-task=64
#SBATCH --mem=256G
#SBATCH --time=0-08:00
#SBATCH --output=%x-%j.out
#
# One stage of audit/kernel-check/kernel_check.sh as a SLURM job on Harvard FASRC Cannon.
#
#   sbatch [options] audit/kernel-check/fasrc.sbatch fetch|build|check
#
# The stages need different resources, so each runs as its own job. submit_fasrc.sh submits all
# three, each starting only if the one before succeeded; `submit_fasrc.sh --dry-run` prints the
# exact sbatch commands. The defaults above are the build stage's.
#
# Set WORK in the submitting shell (sbatch exports it) to a directory on storage that every node
# mounts, e.g. $SCRATCH/<lab>/Lab/$USER/ns-kernel-check. Everything is kept there, so a stage that
# hits its time limit can be submitted again and carries on: downloads and built modules are reused.
#
# Also read from the environment:
#   NS_REPO=/path    this repository's checkout (default: the directory sbatch was run from)
#   KC_TMPDIR=/path  parent of the job's temporary directory (default: node-local /scratch, else
#                    $WORK/tmp). Comparator writes the solution's export there for nanoda.
#   USE_MATHLIB_CACHE, SANDBOX, NANODA, LEAN_NUM_THREADS, LEANCHECKER_THREADS: see kernel_check.sh.
# Optional tools are found on the PATH you submit with: cargo for the nanoda second kernel, Go for
# landrun (which also needs Landlock, Linux >= 5.13; Cannon's compute nodes run 4.18).
set -euo pipefail

stage=${1:-}
case $stage in
  fetch|build|check) ;;
  *) echo "usage: sbatch [options] fasrc.sbatch fetch|build|check" >&2; exit 2 ;;
esac

if [ -z "${WORK:-}" ]; then
  echo "WORK is not set; e.g. export WORK=\$SCRATCH/<lab>/Lab/\$USER/ns-kernel-check before sbatch" >&2
  exit 2
fi
case $WORK in
  /*) ;;
  *) echo "WORK must be an absolute path, not '$WORK'" >&2; exit 2 ;;
esac
if [ -n "${SLURM_JOB_ID:-}" ]; then
  case $WORK in
    /scratch|/scratch/*|/tmp|/tmp/*|/dev/shm|/dev/shm/*)
      echo "WORK=$WORK is local to one node, but the stages may run on different nodes" >&2; exit 2 ;;
  esac
fi

# SLURM runs a copy of this file from its spool directory, so find kernel_check.sh another way.
if [ -n "${NS_REPO:-}" ]; then
  kc=$NS_REPO/audit/kernel-check/kernel_check.sh
elif [ -z "${SLURM_JOB_ID:-}" ]; then
  kc=$(dirname "${BASH_SOURCE[0]}")/kernel_check.sh
else
  kc=${SLURM_SUBMIT_DIR:-$PWD}/audit/kernel-check/kernel_check.sh
  [ -f "$kc" ] || kc=${SLURM_SUBMIT_DIR:-$PWD}/kernel_check.sh
fi
if [ ! -f "$kc" ]; then
  echo "cannot find audit/kernel-check/kernel_check.sh from ${NS_REPO:-${SLURM_SUBMIT_DIR:-$PWD}};" \
       "submit from the repository root or set NS_REPO" >&2
  exit 2
fi
kc_dir=$(cd "$(dirname "$kc")" && pwd)

# Size Lean's thread pools by this job, not by the node (Lean's default is every CPU of the node).
cpus=${SLURM_CPUS_PER_TASK:-$(nproc)}
if [ "${SLURM_MEM_PER_NODE:-0}" -gt 0 ]; then
  mem_mb=$SLURM_MEM_PER_NODE
elif [ "${SLURM_MEM_PER_CPU:-0}" -gt 0 ]; then
  mem_mb=$((SLURM_MEM_PER_CPU * cpus))
else
  mem_mb=$(awk '/^MemTotal:/{print int($2 / 1024)}' /proc/meminfo)
fi
export LEAN_NUM_THREADS=${LEAN_NUM_THREADS:-$cpus}
if [ -z "${LEANCHECKER_THREADS:-}" ]; then   # budget 12 GB per parallel leanchecker replay
  n=$((mem_mb / 12288))
  [ "$n" -le "$cpus" ] || n=$cpus
  [ "$n" -ge 1 ] || n=1
  export LEANCHECKER_THREADS=$n
fi

user=${USER:-$(id -un)}
if [ -n "${KC_TMPDIR:-}" ]; then
  tmp_root=$KC_TMPDIR
elif [ -n "${SLURM_JOB_ID:-}" ] && [ -d /scratch ] && [ -w /scratch ]; then
  tmp_root=/scratch/$user
else
  tmp_root=$WORK/tmp
fi
export TMPDIR=$tmp_root/ns-kernel-check.${SLURM_JOB_ID:-$$}
mkdir -p "$TMPDIR" "$WORK/results"

# Provenance: one line per job start and end in results/jobs.log.
jobs_log=$WORK/results/jobs.log
rev=$(git -C "$kc_dir" rev-parse --short=12 HEAD 2>/dev/null || echo unknown)
if [ -n "$(git -C "$kc_dir" status --porcelain --untracked-files=no -- . 2>/dev/null)" ]; then
  rev="$rev with local changes to audit/kernel-check"
fi
printf '%s start %-5s job %s on %s (partition %s): %s CPUs, %s MB, LEAN_NUM_THREADS=%s, LEANCHECKER_THREADS=%s, repository %s\n' \
  "$(date -u +%FT%TZ)" "$stage" "${SLURM_JOB_ID:-none}" "$(hostname)" "${SLURM_JOB_PARTITION:-none}" \
  "$cpus" "$mem_mb" "$LEAN_NUM_THREADS" "$LEANCHECKER_THREADS" "$rev" | tee -a "$jobs_log"
# shellcheck disable=SC2329  # called by the EXIT trap
finish() {
  local rc=$?
  rm -rf "$TMPDIR"
  printf '%s end   %-5s job %s rc=%s\n' "$(date -u +%FT%TZ)" "$stage" "${SLURM_JOB_ID:-none}" "$rc" | tee -a "$jobs_log"
}
trap finish EXIT
trap 'exit 143' TERM   # time limit or scancel: still clean up and log

rc=0
bash "$kc" "$stage" || rc=$?
if [ "$stage" = check ] && [ "$rc" -eq 0 ]; then
  cat "$WORK/results/SUMMARY.txt"
  grep -Eq '^OVERALL +PASS$' "$WORK/results/SUMMARY.txt" || rc=1   # any FAIL marks the job FAILED
fi
exit "$rc"
