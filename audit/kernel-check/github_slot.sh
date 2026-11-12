#!/usr/bin/env bash
# One job ("slot") of the kernel check on a GitHub-hosted runner. .github/workflows/kernel-check.yml
# chains up to 20 slots and hands the work directory from one to the next through the Actions cache.
# A slot carries on with fetch, build and check, in that order, until they are done or its time is
# up, and writes finished=true|false to $GITHUB_OUTPUT. It fails only if a stage fails outright.
#
# Required: WORK (the work directory) and KC_DEADLINE (seconds since the epoch by which this slot
# must stop working). Defaults for a free runner (4 CPUs, 16 GB, 6 hours per job), each overridable:
#   LEANCHECKER_THREADS=1  one module replay at a time, since each holds most of Mathlib in memory
#   LEANCHECKER_PART=300   modules per leanchecker step, so that each step fits in one slot
#   RESUME_CHECK=all       keep every recorded result; rerun only steps that were cut off
#   MAX_STEP_ATTEMPTS=3    give up on a step that has been cut off three times
#   KC_STOP_MARGIN=900     start no new step in the last 15 minutes before KC_DEADLINE
#   KC_MIN_LEFT=60         start no stage with this many seconds or fewer left
set -euo pipefail
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
: "${WORK:?set WORK to the work directory}" "${KC_DEADLINE:?set KC_DEADLINE, in seconds since the epoch}"
export WORK
export LEANCHECKER_THREADS=${LEANCHECKER_THREADS:-1} LEANCHECKER_PART=${LEANCHECKER_PART:-300}
export RESUME_CHECK=${RESUME_CHECK:-all} MAX_STEP_ATTEMPTS=${MAX_STEP_ATTEMPTS:-3}
export STOP_AT=$((KC_DEADLINE - ${KC_STOP_MARGIN:-900}))
export TMPDIR=$WORK/tmp   # the workflow does not carry this directory to the next slot
mkdir -p "$TMPDIR" "$WORK/results"
output=${GITHUB_OUTPUT:-/dev/null}
step_summary=${GITHUB_STEP_SUMMARY:-/dev/null}
slot=${KC_SLOT:-?}

landlock=no
if [ -r /sys/kernel/security/lsm ] && grep -qw landlock /sys/kernel/security/lsm; then landlock=yes; fi
printf '%s start slot %s, run %s attempt %s, on %s: %s CPUs, %s MB, kernel %s, Landlock %s, repository %s\n' \
  "$(date -u +%FT%TZ)" "$slot" "${GITHUB_RUN_ID:-none}" "${GITHUB_RUN_ATTEMPT:-none}" "${RUNNER_NAME:-$(hostname)}" \
  "$(nproc)" "$(awk '/^MemTotal:/{print int($2 / 1024)}' /proc/meminfo)" "$(uname -r)" "$landlock" \
  "$(git -C "$here" rev-parse --short=12 HEAD 2>/dev/null || echo unknown)" | tee -a "$WORK/results/jobs.log"

status=finished
for stage in fetch build check; do
  [ -f "$WORK/results/summary/$stage.done" ] && continue
  left=$((KC_DEADLINE - $(date +%s)))
  if [ "$left" -le "${KC_MIN_LEFT:-60}" ]; then status=continued; break; fi
  rc=0
  timeout --kill-after=60 "$left" bash "$here/kernel_check.sh" "$stage" || rc=$?
  if [ "$rc" -eq 0 ]; then continue; fi
  # 75: kernel_check.sh stopped before a step for lack of time; 124 or 137 at the deadline: cut off.
  if [ "$rc" -eq 75 ] || [ "$rc" -eq 124 ] || [ "$(date +%s)" -ge $((KC_DEADLINE - 5)) ]; then
    echo "slot $slot: out of time during $stage; the next slot carries on" >&2
    status=continued
  else
    echo "slot $slot: $stage failed with status $rc" >&2
    status=failed
  fi
  break
done
printf '%s end   slot %s: %s\n' "$(date -u +%FT%TZ)" "$slot" "$status" | tee -a "$WORK/results/jobs.log"

if [ "$status" = finished ]; then echo "finished=true" >>"$output"; else echo "finished=false" >>"$output"; fi
{
  echo "### Kernel check, slot $slot: $status"
  echo
  echo '```'
  cat "$WORK/results/SUMMARY.txt" 2>/dev/null || echo "(no results yet)"
  echo '```'
} >>"$step_summary"
[ "$status" != failed ]
