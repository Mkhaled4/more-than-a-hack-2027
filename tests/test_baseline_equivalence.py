"""configs/baseline.yaml must reproduce the official baseline exactly (task 1.5).

Runs the organisers' baseline.py and our pipeline on the same synthetic data, for windows
0 / 25 / 50 / 125, and asserts the labels and the written files are identical.
"""

import copy

import numpy as np
import pytest

from falafelona import io, pipeline
from falafelona.config import load_config
from falafelona.vendor import games

BASELINE = load_config(io.vendor.REPO_ROOT / "configs" / "baseline.yaml")


def official_labels(official_baseline, bundle, window):
    """Labels the organisers' code gives for the synthetic bundle."""
    meta_path, raw_path = games.require(["atd_meta", "atd_raw"], games.GAME, str(bundle["root"]))
    codes = official_baseline.nearest_player_labels(
        raw_path,
        official_baseline.team_of_each_track(meta_path),
        bundle["n_frames"],
        games.GAMES[games.GAME]["pitch"],
    )
    return official_baseline.smooth(codes, window)


def test_baseline_config_is_smooth50():
    assert BASELINE["possession"]["window"] == 50
    assert ("baseline_smooth50", 50) in pipeline.possession.VARIANTS


@pytest.mark.parametrize("name,window", pipeline.possession.VARIANTS)
def test_matches_official_baseline(official_baseline, bundle, tmp_path, name, window):
    cfg = copy.deepcopy(BASELINE)
    cfg["possession"]["window"] = window

    ours = pipeline.run(cfg, tmp_path / "ours.csv", n_frames=bundle["n_frames"])
    theirs = official_labels(official_baseline, bundle, window)

    assert np.array_equal(ours["labels"], theirs), f"{name}: labels differ"

    their_path = official_baseline.write_submission(str(tmp_path / f"{name}.csv"), theirs)
    assert ours["path"].read_bytes() == (tmp_path / f"{name}.csv").read_bytes(), their_path


def test_synthetic_bundle_exercises_every_label(bundle, tmp_path):
    # Guard against a vacuous equivalence test: the synthetic match must produce H, A and D.
    # Without smoothing, because +/- 50 frames votes straight across the 40-frame synthetic gap.
    cfg = copy.deepcopy(BASELINE)
    cfg["possession"]["window"] = 0
    out = pipeline.run(cfg, tmp_path / "ours.csv", n_frames=bundle["n_frames"])
    assert out["counts"]["H"] > 0 and out["counts"]["A"] > 0 and out["counts"]["D"] > 0
