"""Frozen audit inputs and published kernel-check results must not change after the fact.

Each directory with a SHA256SUMS manifest must contain exactly the files it lists (besides the manifest and a
README) with exactly those hashes, and the run that docs/03 cites must be the one it describes.
"""
import hashlib
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFESTS = [ROOT / "audit" / "reference" / "SHA256SUMS",
             *sorted((ROOT / "audit" / "results").glob("kernel-check-*/SHA256SUMS"))]
UNLISTED = {"SHA256SUMS", "README.md"}
CITED_RUN = ROOT / "audit" / "results" / "kernel-check-2026-11-13"


def read_manifest(path):
    entries = {}
    for line in path.read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        entries[name.lstrip("*")] = digest
    return entries


@pytest.mark.parametrize("manifest", MANIFESTS, ids=lambda p: p.parent.name)
def test_frozen_files_match_their_manifest(manifest):
    here = manifest.parent
    entries = read_manifest(manifest)
    present = {p.relative_to(here).as_posix() for p in here.rglob("*") if p.is_file()} - UNLISTED
    assert present == set(entries), f"not listed: {sorted(present - set(entries))}, missing: {sorted(set(entries) - present)}"
    for name, digest in entries.items():
        assert hashlib.sha256((here / name).read_bytes()).hexdigest() == digest, f"{name} changed"


def test_the_kernel_check_cited_in_docs_03_passed():
    assert (CITED_RUN / "SHA256SUMS") in MANIFESTS
    assert "audit/results/kernel-check-2026-11-13/" in (ROOT / "docs" / "03-audit-openai-lean-formalization.md").read_text()
    summary = (CITED_RUN / "SUMMARY.txt").read_text().splitlines()
    assert summary[-1].split() == ["OVERALL", "PASS"]
    assert not [line for line in summary if " FAIL" in line or line.startswith("FATAL")]
