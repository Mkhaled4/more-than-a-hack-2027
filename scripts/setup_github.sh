#!/bin/sh
# One-off GitHub setup, run by someone with admin rights on the repo (uses the gh CLI).
#
# Will create the labels:
#   ws:int  ws:ball  ws:dead  ws:poss  ws:eval  type:exp  blocked
#
# Manual steps, done in GitHub settings (they can't live in a file):
# - branch protection on main: PR required, 1 approving review, CI must pass, squash-merge only
# - push ruleset (if available): block data paths/extensions and files > 5 MB
# - GitHub Projects board: Backlog -> This week -> In progress -> In review -> Done
