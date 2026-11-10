"""Submission contract, checked with the official validator's own function.

Header "frame,label", one row per frame, frames 0..n-1 in order, labels in {H, A, D, X},
no blank cells. Also checks the full-length constant is 199,319.
"""

import pytest

from falafelona import cli, io, pipeline
from falafelona.config import load_config
from falafelona.vendor import games, possession_metrics

FINAL = load_config(io.vendor.REPO_ROOT / "configs" / "final.yaml")


def test_full_length_constant():
    assert pipeline.N_ROWS == 199_319
    assert pipeline.N_ROWS == games.source_frames("tactical", games.GAME)


def test_written_file_passes_the_official_validator(bundle, tmp_path):
    out = pipeline.run(FINAL, tmp_path / "sub.csv", n_frames=bundle["n_frames"])

    table = possession_metrics.read_label_csv(out["path"])
    assert possession_metrics.validate_submission(table, bundle["n_frames"]) is None
    assert out["path"].read_text().startswith("frame,label\n0,")
    assert out["rows"] == bundle["n_frames"]
    assert sum(out["counts"].values()) == bundle["n_frames"]


def test_x_policy_none_writes_no_x(bundle, tmp_path):
    out = pipeline.run(FINAL, tmp_path / "sub.csv", n_frames=bundle["n_frames"])
    assert out["counts"]["X"] == 0


def test_unknown_x_policy_is_rejected():
    with pytest.raises(ValueError, match="x_policy"):
        pipeline.apply_x_policy(None, None, {"output": {"x_policy": "nope"}})


def test_cli_prints_aggregates_only(bundle, tmp_path, capsys):
    out_path = tmp_path / "sub.csv"
    config = io.vendor.REPO_ROOT / "configs" / "final.yaml"
    # The CLI always runs the full length, so check it on a full-length guard instead: here we
    # only exercise argument parsing and printing through pipeline.run with n_frames patched.
    original = pipeline.run
    try:
        pipeline.run = lambda cfg, out: original(cfg, out, n_frames=bundle["n_frames"])
        assert cli.main(["run", "--config", str(config), "--out", str(out_path)]) == 0
    finally:
        pipeline.run = original

    printed = capsys.readouterr().out
    assert "sha256" in printed and "rows    500" in printed
    assert out_path.read_text().count("\n") == bundle["n_frames"] + 1
    assert len(printed.splitlines()) == 7  # wrote, rows, H, A, D, X, sha256: nothing per frame
