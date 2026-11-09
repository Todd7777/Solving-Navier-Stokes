"""The SLURM job scripts in audit/kernel-check: shell syntax, the job chain submit_fasrc.sh builds,
and the work-directory checks. Nothing here builds Lean code, downloads anything or needs SLURM."""
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
            if not k.startswith(("SLURM_", "KC_SBATCH")) and k not in ("WORK", "NS_REPO")}
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
