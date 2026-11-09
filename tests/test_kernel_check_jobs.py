"""The job scripts in audit/kernel-check: shell syntax, the job chain submit_fasrc.sh builds, the
work-directory checks, and how a resumed check keeps and redoes steps. Nothing here builds or runs
Lean, downloads anything or needs SLURM: the check-stage test uses a stand-in for `lake`."""
import os
import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
KC = ROOT / "audit" / "kernel-check"
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None, reason="needs bash")


def run(script, *args, **env):
    """Run a script from audit/kernel-check outside SLURM, with `env` added to a clean environment."""
    base = {k: v for k, v in os.environ.items()
            if not k.startswith(("SLURM_", "KC_SBATCH")) and k not in ("WORK", "NS_REPO", "RESUME_CHECK")}
    return subprocess.run([BASH, str(KC / script), *args], env={**base, **env},
                          capture_output=True, text=True, timeout=60)


def sbatch_lines(stdout):
    return [line for line in stdout.splitlines() if "=$(sbatch " in line]


@pytest.mark.parametrize("script", ["kernel_check.sh", "fasrc.sbatch", "submit_fasrc.sh"])
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
