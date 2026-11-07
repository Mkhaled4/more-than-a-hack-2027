# ws:int: access to the official challenge code in vendor/challenge (pinned git submodule).
#
# Will:
# - put vendor/challenge and vendor/challenge/evaluation on sys.path
# - re-export `games` (asset_paths, require, source_frames, pitch size) and `possession_metrics`
#   so the rest of the package uses the organisers' code exactly as the official scorer does
# - expose paths to validate_submission.py and the public 5-minute GT
# - fail with a clear message if the submodule is missing ("git submodule update --init")
#
# Never copy or edit the organisers' code (docs/decisions.md D3).


import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]   # see note below
CHALLENGE = REPO / "vendor" / "challenge"

if not (CHALLENGE / "games.py").exists():
    raise RuntimeError(
        f"Challenge submodule missing at {CHALLENGE}. Run: git submodule update --init"
    )

for p in (CHALLENGE, CHALLENGE / "starter"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import games
import load_atd
import load_smart_tagging
import load_homography
import baseline