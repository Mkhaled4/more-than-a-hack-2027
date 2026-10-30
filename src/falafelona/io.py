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
