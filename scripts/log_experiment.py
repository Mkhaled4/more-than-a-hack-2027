# ws:eval: record one experiment as experiments/runs/<id>.yaml, and rebuild the summary.
#
#   python scripts/log_experiment.py --id 2026-11-04-poss-hmm-mindur50 \
#       --config configs/exp/poss-hmm-mindur50.yaml --change "..." outputs/Falafelona.csv
#   python scripts/log_experiment.py --summary        # regenerates experiments/RESULTS.md
#
# Will fill in author, branch, commit automatically, plus the metrics from bootstrap_eval.py.
# Aggregates only (D7).
