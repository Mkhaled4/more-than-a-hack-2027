# ws:int: locate and load the match data.
#
# Will:
# - read the data location ONLY from MTAH_DATA_DIR; fail loudly if unset, no fallback (D1).
#   This deliberately bypasses vendor games.py's own fallback, which is vendor/challenge/data/,
#   i.e. INSIDE our repo folder via the submodule.
# - refuse to run if MTAH_DATA_DIR (after resolving ~ and symlinks) points anywhere inside this
#   repo, vendor/ included. The data must live outside, e.g. ~/mtah-data
# - get file paths via vendor games.asset_paths() / require(), never spell file names out
# - parse the tactical ATD (metadata XML + raw text) into arrays in METRES:
#     ball (n_frames, 2), players (n_frames, n_slots, 2), team_of_slot (n_slots,)
#   alignment: submission row = ATD frame_id - 1 (see vendor/challenge/starter/load_atd.py)
#   46 track slots are tracklets, NOT players: identities swap
# - cache parsed arrays under $MTAH_DATA_DIR/cache/, never in the repo (D2)
# - optionally load Smart Tagging and homography for the other workstreams
#
# Never print or log raw rows. Shapes and counts only.
import os
from pathlib import Path
import numpy as np
import json

import vendor

games = vendor.games
REPO = vendor.REPO
load_atd_vendor = vendor.load_atd
load_smart_tagging_vendor = vendor.load_smart_tagging
load_homography_vendor = vendor.load_homography


def data_dir():
    """The data folder from MTAH_DATA_DIR. Checked: set, and outside the repo."""
    raw = os.environ.get("MTAH_DATA_DIR")
    if not raw:
        raise RuntimeError("MTAH_DATA_DIR is not set.")
    path = Path(raw).expanduser().resolve()
    if path == REPO or REPO in path.parents:
        raise RuntimeError(f"MTAH_DATA_DIR ({path}) is inside the repo. Move the data outside.")
    return path


#Creates a dataframe from the atd data
def load_atd(game=games.GAME):
    ds = load_atd_vendor.load(game, str(data_dir()))      # pass data_dir, so no fallback
    df = ds.to_df()
    return df

def load_smart_tagging(game=games.GAME):
    return load_smart_tagging_vendor.load(game, str(data_dir()))

def load_homography(game=games.GAME):
    matrices, err, valid =load_homography_vendor.load(game, str(data_dir()))
    return matrices, err, valid

load_atd()
load_smart_tagging()