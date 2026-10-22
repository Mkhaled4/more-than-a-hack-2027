# One place for every command. Planned targets:
#
#   make setup           create .venv (Python 3.12), install pinned deps, init the submodule,
#                        enable the git hooks (git config core.hooksPath .githooks)
#   make test            run the tests (synthetic data only, safe for anyone and for CI)
#   make lint            ruff
#   make submission      build outputs/Falafelona.csv from configs/final.yaml, then validate it
#   make validate        run the official validate_submission.py on outputs/Falafelona.csv
#   make check-baseline  run configs/baseline.yaml and compare with the official baseline_smooth50
#   make eval            aggregate metrics for outputs/Falafelona.csv (scripts/bootstrap_eval.py)
#   make results         regenerate experiments/RESULTS.md from experiments/runs/
#   make hash            print the SHA-256 of outputs/Falafelona.csv
#
# `submission`, `check-baseline` and `eval` need MTAH_DATA_DIR and are run by humans, not agents.
