# 🧪 Experiments

One YAML file per run in `runs/`, so parallel PRs never conflict. `RESULTS.md` is generated from them (`make results`).

**Aggregate numbers only.** Never per-frame predictions or anything that reconstructs the data.

## What we can and can't measure
We have **no full-match ground truth**, so there's no full-match score before results day. Each record holds:
- **Public 5-minute score** (spellF1, macroF1, bootstrap CI): a **pipeline sanity check only**. Never tune on it (decisions D9).
- **Label-free stats over the whole match:** number of possessions, mean/median duration, share of H/A/D/X, and flicker (possessions < 1 s). A real match has far fewer, longer possessions than a flickery model.
- **Verdict:** keep / drop / inconclusive, with a reason.

## Record format (`runs/<date>-<ws>-<slug>.yaml`)
```yaml
id: 2026-11-04-poss-hmm-mindur50
author: <github handle>
branch: exp/poss-hmm-min-duration
commit: <short sha>
config: configs/exp/poss-hmm-mindur50.yaml
change: "HMM with 50-frame minimum duration on top of nearest-player"
public_5min:            # sanity check only
  spellF1: 0.000
  spellF1_ci: [0.000, 0.000]
  macroF1: 0.000
full_match_stats:       # no ground truth needed
  n_possessions: 0
  median_possession_s: 0.0
  share: {H: 0.0, A: 0.0, D: 0.0, X: 0.0}
  flicker_lt_1s: 0
verdict: keep | drop | inconclusive
notes: ""
```
`scripts/log_experiment.py` will write these for you.
