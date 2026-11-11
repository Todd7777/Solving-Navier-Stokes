"""The job scripts in audit/kernel-check and the GitHub workflow that chains them: shell syntax, the
SLURM job chain, the work-directory checks, how a resumed check keeps and redoes steps, and how GitHub
slots hand work on. Nothing here builds or runs Lean, downloads anything, or needs SLURM or GitHub:
the build and check tests use a stand-in for `lake`."""
import os
import pathlib
import shutil
import subprocess
import time

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
KC = ROOT / "audit" / "kernel-check"
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None, reason="needs bash")


def run(script, *args, **env):
    """Run a script from audit/kernel-check outside SLURM, with `env` added to a clean environment."""
    knobs = ("WORK", "NS_REPO", "RESUME_CHECK", "MAX_STEP_ATTEMPTS", "LEANCHECKER_PART", "LEANCHECKER_THREADS",
             "STOP_AT", "SANDBOX", "NANODA", "GITHUB_OUTPUT", "GITHUB_STEP_SUMMARY")
    base = {k: v for k, v in os.environ.items() if not k.startswith(("SLURM_", "KC_")) and k not in knobs}
    return subprocess.run([BASH, str(KC / script), *args], env={**base, **env},
                          capture_output=True, text=True, timeout=60)


def sbatch_lines(stdout):
    return [line for line in stdout.splitlines() if "=$(sbatch " in line]


@pytest.mark.parametrize("script", ["kernel_check.sh", "fasrc.sbatch", "submit_fasrc.sh", "github_slot.sh"])
def test_shell_syntax(script):
    r = subprocess.run([BASH, "-n", str(KC / script)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_dry_run_chains_fetch_build_check(tmp_path):
    work = tmp_path / "work"
    r = run("submit_fasrc.sh", "--dry-run", WORK=str(work))
    assert r.returncode == 0, r.stderr
    jobs = sbatch_lines(r.stdout)
    assert [job.split("=", 1)[0] for job in jobs] == ["fetch", "build", "check"]
    assert "--dependency" not in jobs[0]
    assert "--dependency=afterok:$fetch " in jobs[1]
    assert "--dependency=afterok:$build " in jobs[2]
    for stage, job in zip(["fetch", "build", "check"], jobs):
        assert f"WORK={work}," in job
        assert f"fasrc.sbatch {stage})" in job
    assert not work.exists()  # a dry run creates nothing


def test_resubmitting_the_check_alone_has_no_dependency(tmp_path):
    r = run("submit_fasrc.sh", "--dry-run", "check", WORK=str(tmp_path))
    jobs = sbatch_lines(r.stdout)
    assert len(jobs) == 1 and jobs[0].startswith("check=") and "--dependency" not in jobs[0]


@pytest.mark.parametrize("work", [None, "relative/dir"])
def test_a_missing_or_relative_work_directory_is_refused(work):
    env = {} if work is None else {"WORK": work}
    for script, args in (("submit_fasrc.sh", ["--dry-run"]), ("fasrc.sbatch", ["fetch"])):
        r = run(script, *args, **env)
        assert r.returncode == 2 and "WORK" in r.stderr, (script, r.stderr)


def test_a_node_local_work_directory_is_refused_under_slurm():
    r = run("fasrc.sbatch", "fetch", WORK="/scratch/someone/ns-kernel-check", SLURM_JOB_ID="1")
    assert r.returncode == 2 and "local to one node" in r.stderr


# A stand-in for the built `lake`: it records each call and prints what `#print axioms` would print
# for a clean proof; the Euler --fresh replay is "killed" (exit 137) while $STUB_KILL exists.
STUB_LAKE = r"""#!/usr/bin/env bash
printf '%s\n' "$*" >> "$STUB_LOG"
case "$*" in
  *PrintAxiomsNavierStokes.lean*) set -- NavierStokes.Comparator.navier_stokes_breakdown_R3 NavierStokes.Comparator.navier_stokes_breakdown_periodic ;;
  *PrintAxiomsEuler.lean*) set -- Euler.euler_breakdown_R3 Euler.exists_compact_smooth_euler_singularity ;;
  *"--fresh Euler.Solution"*) if [ -e "$STUB_KILL" ]; then exit 137; fi; exit 0 ;;
  *comparator*NavierStokes*) if [ -e "${STUB_SLOW:-}" ]; then sleep 30; fi; exit 0 ;;
  *) exit 0 ;;
esac
for t in "$@"; do echo "'$t' depends on axioms: [propext, Classical.choice, Quot.sound]"; done
"""


def fake_check_work(tmp_path):
    """A WORK directory holding just enough for the check stage's bookkeeping, with the stand-in lake."""
    work = tmp_path / "work"
    bindir = work / "tools" / "lean-4.34.0-rc2-linux" / "bin"
    bindir.mkdir(parents=True)
    (bindir / "lake").write_text(STUB_LAKE)
    (bindir / "lake").chmod(0o755)
    (work / "tools" / "LANDRUN").write_text("/nowhere/fake-landrun.sh\n")
    challenges = work / "NavierStokesAndEuler" / "ComparatorChallenges"
    challenges.mkdir(parents=True)
    for name in ("NavierStokes", "Euler"):
        (challenges / f"{name}.json").write_text('{"enable_nanoda": true}')
    return work


def check_stage(work, log, kill, resume=False):
    env = {"WORK": str(work), "STUB_LOG": str(log), "STUB_KILL": str(kill)}
    if resume:
        env["RESUME_CHECK"] = "1"
    r = run("kernel_check.sh", "check", **env)
    assert r.returncode == 0, r.stderr
    lines = (work / "results" / "SUMMARY.txt").read_text().splitlines()
    return lines, (log.read_text().splitlines() if log.exists() else [])


def test_a_resumed_check_keeps_what_passed_and_reruns_the_rest(tmp_path):
    work, kill = fake_check_work(tmp_path), tmp_path / "kill"
    kill.touch()
    lines, calls = check_stage(work, tmp_path / "calls1", kill)
    assert len(calls) == 7  # 2 Comparator runs, 2 #print axioms, 3 leanchecker runs
    assert any(line.startswith("leanchecker --fresh Euler.Solution") and "FAIL rc=137" in line for line in lines)
    assert lines[-1].split()[:2] == ["OVERALL", "FAIL"]

    kill.unlink()
    lines, calls = check_stage(work, tmp_path / "calls2", kill, resume=True)
    assert calls == ["env leanchecker --fresh Euler.Solution"]  # only the killed step runs again
    assert not any("FAIL" in line for line in lines)
    assert lines[-1].split() == ["OVERALL", "PASS"]
    assert len(lines) == len(set(lines))  # nothing is recorded twice

    lines, calls = check_stage(work, tmp_path / "calls3", kill)
    assert len(calls) == 7  # without RESUME_CHECK every step runs again
    assert lines[-1].split() == ["OVERALL", "PASS"]


def fake_slot_work(tmp_path):
    """A WORK directory as the first GitHub slot leaves it after the fetch: build and check still to do."""
    work = fake_check_work(tmp_path)
    (work / "tools" / "LANDRUN").unlink()
    summary = work / "results" / "summary"
    summary.mkdir(parents=True)
    (summary / "fetch.txt").write_text("all lake dependencies at pinned revisions".ljust(58) + " PASS\n")
    (summary / "fetch.done").touch()
    lib = work / "NavierStokesAndEuler" / ".lake" / "build" / "lib" / "lean"
    for module in ("NavierStokes/A", "NavierStokes/R3", "NavierStokes/R3/X", "Euler/B", "Euler/C"):
        (lib / module).parent.mkdir(parents=True, exist_ok=True)
        (lib / f"{module}.olean").touch()
    return work


def slot(work, tmp_path, n, seconds, **env):
    """Run GitHub slot n with `seconds` to work; return its finished flag and the stand-in lake's calls."""
    output, log = tmp_path / f"output{n}", tmp_path / f"calls{n}"
    settings = dict(WORK=str(work), KC_DEADLINE=str(int(time.time()) + seconds), KC_SLOT=f"{n:02d}",
                    KC_MIN_LEFT="0", KC_STOP_MARGIN="0", GITHUB_OUTPUT=str(output),
                    GITHUB_STEP_SUMMARY=str(tmp_path / "step-summary.md"), STUB_LOG=str(log),
                    STUB_KILL=str(tmp_path / "no-kill"), SANDBOX="fake", NANODA="0", LEANCHECKER_PART="2")
    r = run("github_slot.sh", **{**settings, **env})
    assert r.returncode == 0, r.stderr
    return output.read_text().strip(), (log.read_text().splitlines() if log.exists() else [])


def test_a_slot_with_enough_time_builds_and_checks_everything_in_parts(tmp_path):
    work = fake_slot_work(tmp_path)
    finished, calls = slot(work, tmp_path, 1, 600)
    assert finished == "finished=true"
    # NavierStokes.R3 stands for its submodule NavierStokes.R3.X; at most 2 modules per part
    assert [c for c in calls if c.startswith("env leanchecker") and "--fresh" not in c] == [
        "env leanchecker Euler.B Euler.C", "env leanchecker NavierStokes.A", "env leanchecker NavierStokes.R3"]
    lines = (work / "results" / "SUMMARY.txt").read_text().splitlines()
    assert any(line.startswith("leanchecker: replay modules, part 3 of 3") for line in lines)
    assert lines[-1].split() == ["OVERALL", "PASS"]
    assert (work / "results" / "summary" / "check.done").exists()
    assert "slot 01: finished" in (tmp_path / "step-summary.md").read_text()


def test_slots_carry_on_after_running_out_of_time_and_give_up_on_a_step_after_max_attempts(tmp_path):
    work = fake_slot_work(tmp_path)
    slow = tmp_path / "slow"
    slow.touch()  # the NavierStokes Comparator step now takes 30 s, longer than any slot below
    env = {"STUB_SLOW": str(slow), "MAX_STEP_ATTEMPTS": "2"}
    assert slot(work, tmp_path, 1, 5, **env)[0] == "finished=false"  # builds, then is cut off in the step
    assert (work / "results" / "summary" / "build.done").exists()
    assert slot(work, tmp_path, 2, 2, **env)[0] == "finished=false"  # cut off in it again
    finished, calls = slot(work, tmp_path, 3, 600, **env)  # gives up on it and finishes the rest
    assert finished == "finished=true"
    assert not any("NavierStokes.no-nanoda" in call for call in calls)  # it was not started a third time
    lines = (work / "results" / "SUMMARY.txt").read_text().splitlines()
    assert any(line.startswith("Comparator: NavierStokes") and "not finished in 2 attempts" in line for line in lines)
    assert lines[-1].split()[:2] == ["OVERALL", "FAIL"]
    assert len(lines) == len(set(lines))


def test_a_slot_that_is_out_of_time_starts_nothing(tmp_path):
    work = fake_slot_work(tmp_path)
    finished, calls = slot(work, tmp_path, 1, 600, KC_STOP_MARGIN="600")  # no new step may start
    assert finished == "finished=false" and calls == []
    assert not (work / "results" / "summary" / "build.done").exists()


def test_the_github_workflow_chains_twenty_slots_through_one_cache_key():
    yaml = pytest.importorskip("yaml")
    workflows = ROOT / ".github" / "workflows"
    caller = yaml.safe_load((workflows / "kernel-check.yml").read_text())
    callee = yaml.safe_load((workflows / "kernel-check-slot.yml").read_text())
    assert set(caller.get("on", caller.get(True))) == {"workflow_dispatch"}  # started by hand only
    jobs = caller["jobs"]
    slots = sorted(name for name in jobs if name.startswith("slot-"))
    assert slots == [f"slot-{i:02d}" for i in range(1, 21)]
    for i, name in enumerate(slots, 1):
        job, prev = jobs[name], f"slot-{i - 1:02d}"
        assert job["uses"] == "./.github/workflows/kernel-check-slot.yml"
        assert (job["with"]["slot"], job["with"]["prev"]) == (f"{i:02d}", f"{i - 1:02d}")
        assert job.get("needs") == (prev if i > 1 else None)
        assert job.get("if") == (f"needs.{prev}.outputs.finished == 'false'" if i > 1 else None)
    assert sorted(jobs["report"]["needs"]) == slots and jobs["report"]["if"] == "always()"

    call = callee.get("on", callee.get(True))["workflow_call"]
    assert set(call["inputs"]) == {"slot", "prev", "nanoda", "sandbox"}
    assert call["outputs"]["finished"]["value"] == "${{ jobs.slot.outputs.finished }}"
    job = callee["jobs"]["slot"]
    assert job["outputs"]["finished"] == "${{ steps.work.outputs.finished }}"
    steps = job["steps"]
    uses = {s["uses"].split("@")[0]: s for s in steps if "uses" in s}
    work = next(s for s in steps if s.get("id") == "work")
    restore, save = uses["actions/cache/restore"], uses["actions/cache/save"]
    assert work["run"] == "audit/kernel-check/github_slot.sh"
    assert restore["with"]["path"] == save["with"]["path"] == "${{ env.KC_STATE }}"
    assert restore["with"]["key"] == save["with"]["key"]
    assert "steps.work.outputs.finished != 'true'" in save["if"]
    assert uses["actions/upload-artifact"]["with"]["name"].startswith("results-slot-")  # what report downloads
    deadline = next(s for s in steps if "KC_DEADLINE" in s.get("run", ""))
    assert "300 * 60" in deadline["run"] and 300 + 30 <= job["timeout-minutes"] <= 360
