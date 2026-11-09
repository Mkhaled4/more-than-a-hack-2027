"""Runs the pipeline twice on synthetic data and asserts the two files have the same SHA-256.

The rules require the repo to regenerate the SAME file.
"""

import hashlib

from falafelona import io, pipeline
from falafelona.config import load_config

FINAL = load_config(io.vendor.REPO_ROOT / "configs" / "final.yaml")


def test_two_runs_write_the_same_file(bundle, tmp_path):
    first = pipeline.run(FINAL, tmp_path / "a.csv", n_frames=bundle["n_frames"])
    second = pipeline.run(FINAL, tmp_path / "b.csv", n_frames=bundle["n_frames"])

    assert first["sha256"] == second["sha256"]
    assert (tmp_path / "a.csv").read_bytes() == (tmp_path / "b.csv").read_bytes()


def test_reported_sha256_is_the_file_hash(bundle, tmp_path):
    out = pipeline.run(FINAL, tmp_path / "a.csv", n_frames=bundle["n_frames"])
    assert out["sha256"] == hashlib.sha256((tmp_path / "a.csv").read_bytes()).hexdigest()
