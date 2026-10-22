# CI (planned)

`ci.yml` will be added here. It isn't committed yet because a workflow file with no jobs shows up as an error on GitHub.

On every push and PR it will:
1. Check out the repo **with the submodule**.
2. Set up Python 3.12 and install the pinned requirements.
3. Run `ruff`.
4. Run `pytest` (synthetic data only: CI never has the match data).
5. Run `scripts/check_no_data.py` on every file in the PR, which fails on data-like files, files over 5 MB, and notebooks with outputs.
