"""pipeline.run() wires the stages together. Synthetic data only."""

import numpy as np

from falafelona import io, pipeline
from falafelona.ball import DataCleaner
from falafelona.config import load_config
from falafelona.possession import Possession


def test_stage_classes_import_from_the_package():
    # The import Dudu hit: `from io import Match` found Python's built-in io module.
    from falafelona.io import Match

    assert DataCleaner.__init__.__annotations__["raw_data"] is Match
    assert Possession.__init__.__annotations__["data"] is Match


def test_run_wires_the_stages(bundle, tmp_path):
    cfg = load_config(io.vendor.REPO_ROOT / "configs" / "baseline.yaml")
    out = pipeline.run(cfg, tmp_path / "out.csv", n_frames=bundle["n_frames"])

    assert isinstance(out["match"], io.Match)
    assert out["cleaned"] is out["match"]  # method none: no cleaning yet
    assert out["dead_score"].shape == (bundle["n_frames"],)
    assert out["labels"].shape == (bundle["n_frames"],)
    assert out["path"].is_file()


def test_dead_frames_give_no_team_vote(bundle, tmp_path):
    # Inside the synthetic ball gap the dead score is 1, so with no smoothing the label is D.
    cfg = load_config(io.vendor.REPO_ROOT / "configs" / "baseline.yaml")
    cfg["possession"]["window"] = 0
    out = pipeline.run(cfg, tmp_path / "out.csv", n_frames=bundle["n_frames"])
    lo, hi = bundle["ball_gap"]
    assert (out["labels"][lo:hi] == "D").all()


def test_speeds_are_loaded(bundle):
    match = io.load_match(n_frames=bundle["n_frames"])
    assert match.ball_speed.shape == (bundle["n_frames"],)
    assert match.players_speed.shape == (bundle["n_frames"], 46)
    # Speed is NaN exactly where the position is missing.
    assert np.array_equal(np.isnan(match.ball_speed), np.isnan(match.ball_xy[:, 0]))
    assert np.array_equal(np.isnan(match.players_speed), np.isnan(match.players_xy[..., 0]))
