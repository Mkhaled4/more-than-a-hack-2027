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
