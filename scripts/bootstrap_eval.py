# ws:eval: score a submission file and print AGGREGATE metrics.
#
#   python scripts/bootstrap_eval.py outputs/Falafelona.csv [--bootstrap 1000]
#
# Will:
# - score against the public 5-minute GT with vendor possession_metrics.evaluate()
#   (spellF1, macroF1, bootstrap CI), as a PIPELINE SANITY CHECK ONLY, never for tuning (D9)
# - report label-free stats for the whole match: number of possessions, mean/median duration,
#   share of H / A / D / X, flicker (possessions shorter than 1 s)
#
# We have no full-match ground truth, so no full-match score is possible before results day.
