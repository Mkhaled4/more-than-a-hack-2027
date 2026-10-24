# 👥 Workstreams: who does what

How the work is split across the five of us. Every task below becomes **one GitHub issue** on the Projects board (title, `ws:` label, due date and "done when" are already written). Owners are in §1.
Layout, git workflow and rhythm are in [`skeleton-plan.md`](skeleton-plan.md); decisions in [`decisions.md`](decisions.md).

---

## 0. Interfaces (agree at the kick-off, before anyone codes)

So that `ball`, `dead` and `poss` don't wait for `io.py`, we fix the function signatures now. Every module is built and tested against `tests/synthetic.py` from day one.

```python
# io.py  (int)
Match:
  n_frames: int                # 199,319
  fps: float                   # from metadata
  period: int8[n]              # 1, 2, or 0 = ungraded / outside play
  ball_xy: float[n, 2]         # metres, NaN where missing
  players_xy: float[n, 46, 2]  # metres, NaN where slot empty
  slot_team: str[46]           # 'H' / 'A' / '?'  (slots are tracklets, not players)
  tags: list[Event]            # Smart Tagging: start, end, type, team ('H' / 'A' / None)

# ball.py  (ball)
clean(match, cfg) -> BallTrack:
  xy: float[n, 2]              # NaN where still unknown
  source: int8[n]              # OBSERVED / INTERPOLATED / REJECTED / UNKNOWN
  speed: float[n]

# deadball.py  (dead)
detect(match, ball, cfg) -> dead: bool[n]     # + optional score: float[n] in 0..1

# possession.py  (poss)
predict(match, ball, dead, cfg) -> labels: str[n] in {H, A, D, X}

# pipeline.py  (int)
run(cfg) -> writes outputs/Falafelona.csv, returns {sha256, counts}
```

**Dead ball vs possession (v1):** `D` from `deadball` overrides; `possession` labels only the live stretches. A joint H/A/D decoder may replace this later (task 4.6), recorded as a decision when it happens.

---

## 1. The split

| Role | Workstream | Owner | Helper | Profile | W0–W1 | W2 | W3 |
|---|---|---|---|---|---|---|---|
| **P1** | Integration & submission (`int`) | **Tala** | — | Infra, Python packaging, git | Tooling, guard, synthetic data, `io.py`, baseline repro | Maintenance + **help `poss`** | Freeze, clean-clone test, upload |
| **P2** | Ball track (`ball`) | **Abdallah** | — | Signal processing, numpy | EDA, outlier filter | Gap filling | Doc section |
| **P3** | Dead ball (`dead`) | **Chikhani** | Laila | ⚽ **Knows football rules well** | EDA, baseline method | Rules + combining them | Joint decoding with `poss` (4.6) |
| **P4** | Possession model (`poss`) | **Dudu + Abdallah** | Tala | Modelling / stats (⚽ helps) | Baseline + features | **HMM + min durations** | Tuning via CIs, doc section |
| **P5** | Evaluation & docs (`eval`) | **Laila** | — | Metrics, writing | Eval tooling | Metric study, PR reviews, **help `dead`** | **Owns the technical doc** |

- **Tala** owns `int` and helps Dudu and Abdallah on `poss` once the baseline is reproduced (from W2), e.g. the HMM decoder (4.3 / 4.4).
- **Abdallah** owns `ball` and co-owns `poss` with Dudu. `ball` is front-loaded (W1–W2), so his time shifts to `poss` as the ball tasks finish.
- **Laila** owns `eval/docs` and helps Chikhani on `dead`, e.g. checking each dead-ball rule against the label-free stats and Smart Tagging.
- **Abdallah and Chikhani work closely:** long ball gaps are a shared `ball`/`dead` signal. Agree the threshold in one short call in W1.

### ⚽ Where football knowledge matters

| Role | Need | Why |
|---|---|---|
| **P3 dead** | **High** | Out of play, fouls, offside, goals → kick-off, injuries, subs, VAR; *when* each restart (throw-in, goal kick, corner, free kick) comes back to life; reading Smart Tagging labels |
| **P4 poss** | **High** | A pass keeps possession even when the ball is nearest an opponent; loose balls, 50/50s, headers, deflections; goalkeeper; realistic minimum possession lengths |
| **P5 eval** | Medium | Plausibility checks (number of possessions, H/A split); writing the "Possession rules" section for Metrica / Barça judges |
| P1 int, P2 ball | Low | Engineering and physics |

Chikhani (P3) also acts as **football reviewer on every `poss` PR**. Chikhani, Dudu and Abdallah read the official **CHALLENGE.md possession definitions** first: the labels follow Metrica's rules, not general intuition. Watching the public 5 minutes next to its 17 labelled possessions is fine for *understanding* the convention, never for tuning (D9).

---

## 2. Tasks per workstream

Issue title = the task title. Labels: the `ws:` label, plus `type:exp` for experiments. Weeks: **W0** 22–26 Oct · **W1** 27 Oct – 2 Nov · **W2** 3–9 Nov · **W3** 10–16 Nov.

### WS1 · Integration & submission (`ws:int`): Tala
**Owns:** `vendor.py`, `config.py`, `io.py`, `pipeline.py`, `cli.py`, `Makefile`, no-data guard, CI, `test_format` / `test_determinism` / `test_baseline_equivalence`, GitHub settings, final upload.
**Mission:** `main` always produces a valid file with one command, reproducible bit for bit by anyone.

| # | Task | Due | Depends | Done when |
|---|---|---|---|---|
| 1.1 | `chore(int): tooling`: pyproject, pinned requirements, Makefile targets, submodule pinned, `vendor.py`, `config.py` | 27 Oct | D10 closed | `make setup` works on two laptops |
| 1.2 | `chore(int): no-data guard`: `check_no_data.py`, pre-commit hook, `ci.yml`, `test_no_data_guard` | 29 Oct | 1.1 | CI is green and rejects a fake `*_atd.txt` |
| 1.3 | `test(int): synthetic data bundle` with ball gaps, out-of-bounds stretches, slot swaps **← unblocks everyone** | 28 Oct | 1.1 | `bundle` fixture loads through `io.py` |
| 1.4 | `feat(int): io.py loads the ATD`: metres, `frame_id − 1` alignment, cache in `$MTAH_DATA_DIR/cache/`, refuses a data dir inside the repo | 29 Oct | 1.1 | Loads the real match (run by a human); prints shapes only |
| 1.5 | `feat(int): reproduce baseline_smooth50`: pipeline + CLI + `baseline.yaml`, equivalence test for windows 0/25/50/125 | **30 Oct** | 1.3, 1.4 | `make check-baseline` matches the official file |
| 1.6 | `chore(int): GitHub setup`: labels, branch protection, push ruleset, Projects board, issues from this file | 26 Oct | — | Board live with every task below |
| 1.7 | `feat(int): load Smart Tagging + homography into Match` | 3 Nov | 1.4 | `match.tags` available to `dead` / `poss` |
| 1.8 | `chore(int): Friday integration run`: merge, `make submission`, validate, log one experiment | 30 Oct · 6 Nov · 13 Nov | — | Experiment record merged |
| 1.9 | `chore(int): freeze + clean-clone test`: tag `v1.0-freeze`, SHA-256 + runtime in README | 14–15 Nov | all | Fresh clone gives the same SHA-256 |
| 1.10 | `chore(int): registration + submission`: all 5 registered as `Falafelona`, Google Form | **10 Nov** · 16 Nov | — | Form submitted, file validated |

### WS2 · Ball track (`ws:ball`): Abdallah
**Owns:** `ball.py`, the `ball:` config section, `notebooks/ball-*.ipynb`.
**Mission:** a trustworthy ball position on as many frames as possible, and a clear "unknown" everywhere else.

| # | Task | Due | Depends | Done when |
|---|---|---|---|---|
| 2.1 | `docs(ball): EDA of the ball track`: gap-length histogram, missing share per half, speed distribution, share of jumps (aggregates only) | 31 Oct | 1.4 | Findings posted in chat as numbers |
| 2.2 | `feat(ball): method none` (passthrough for the baseline) | 29 Oct | 1.3 | Baseline config runs through `ball.clean` |
| 2.3 | `feat(ball): false-detection filter`: impossible speeds (e.g. > 40 m/s), ball far from every player | 4 Nov | 2.1 | Synthetic fake jumps are rejected; experiment logged |
| 2.4 | `feat(ball): short-gap interpolation`: gaps ≤ N frames (N in config); long gaps stay NaN and feed `dead` | 6 Nov | 2.3 | Synthetic gaps filled; experiment logged |
| 2.5 | `exp(ball): Kalman / RTS smoother` as a second method | 9 Nov | 2.4 | Compared with 2.4 by CI; keep or drop |
| 2.6 | `exp(ball): estimate missing ball from player positions` (only if time allows) | 12 Nov | 2.4 | Experiment logged |
| 2.7 | `docs(ball): technical doc section "Ball track"`, including methods dropped | 15 Nov | — | Section merged |

### WS3 · Dead ball (`ws:dead`): Chikhani ⚽, helped by Laila
**Owns:** `deadball.py`, the `deadball:` config section.
**Mission:** decide which frames are `D`. Dead spells are scored like any other, so their **boundaries** matter as much as their coverage.

| # | Task | Due | Depends | Done when |
|---|---|---|---|---|
| 3.1 | `feat(dead): method ball_missing` (baseline behaviour) | 29 Oct | 1.3 | Baseline config runs through `deadball.detect` |
| 3.2 | `feat(dead): ungraded frames → D` (before kick-off, half-time, after the final whistle) | 30 Oct | 1.4 | Tested on synthetic periods |
| 3.3 | `docs(dead): EDA: Smart Tagging vs ball gaps vs out of bounds` (counts and overlaps only) | 2 Nov | 1.7 | Findings posted in chat |
| 3.4 | `feat(dead): ball out of bounds` (105.3 × 68 m plus margin, on the cleaned ball) | 4 Nov | 2.3 | Synthetic test; experiment logged |
| 3.5 | `feat(dead): players static` (mean speed below a threshold for at least T s) | 5 Nov | 1.4 | Synthetic test; experiment logged |
| 3.6 | `feat(dead): Smart Tagging restarts / set pieces as evidence` (not truth; throw-ins are team `N/A`) | 7 Nov | 1.7 | Experiment logged |
| 3.7 | `feat(dead): combine rules into one score + min-duration smoothing` (no 3-frame `D` blips) | 10 Nov | 3.4–3.6 | Experiment logged, CI vs baseline |
| 3.8 | `docs(dead): technical doc section on dead ball and restarts` | 15 Nov | — | Section merged |

### WS4 · Possession model (`ws:poss`): Dudu + Abdallah, helped by Tala
**Owns:** `possession.py`, the `possession:` config section.
**Mission:** turn per-frame evidence into **few, long, correct** H/A spells. spellF1 is mostly about removing flicker.

| # | Task | Due | Depends | Done when |
|---|---|---|---|---|
| 4.1 | `feat(poss): method nearest_majority` (baseline: nearest player's team + centred majority vote ±w) | 30 Oct | 1.3 | Equivalence test passes for w = 0/25/50/125 |
| 4.2 | `feat(poss): per-frame features`: nearest distance H / A and difference, ball speed, "controlled" flag, ball direction changes | 4 Nov | 2.3 | Features computed on synthetic data |
| 4.3 | `feat(poss): HMM / Viterbi decoder` with H/A states and a switch penalty (simple version first) | 6 Nov | 4.2 | Experiment logged; fewer possessions than baseline |
| 4.4 | `exp(poss): minimum possession durations` (chained sub-states or post-merge of short spells) | 8 Nov | 4.3 | Compared by CI; keep or drop |
| 4.5 | `feat(poss): carry the last confident team through ball gaps` | 9 Nov | 4.3 | Experiment logged |
| 4.6 | `exp(poss): joint H/A/D decoding with the dead-ball score` (with Chikhani) | 12 Nov | 3.7, 4.3 | Compared by CI; decision recorded |
| 4.7 | `docs(poss): X policy decision` (probably never use `X`: it costs macroF1 and only forward-fills for spellF1) | 7 Nov | 5.5 | Line in `decisions.md` |
| 4.8 | `docs(poss): technical doc sections "Approach" and "Possession rules"` | 15 Nov | — | Sections merged |

### WS5 · Evaluation & docs (`ws:eval`): Laila
**Owns:** `bootstrap_eval.py`, `log_experiment.py`, `experiments/`, `docs/Falafelona.md`, `decisions.md`.
**Mission:** tell the team whether a change is actually better, without full-match ground truth. Own the final document.

| # | Task | Due | Depends | Done when |
|---|---|---|---|---|
| 5.1 | `feat(eval): public 5-minute score with bootstrap CI` (vendor metric, unchanged) | 30 Oct | 1.1 | Baseline 5-min score reproduced |
| 5.2 | `feat(eval): label-free match stats`: number of possessions, median length, H/A/D share, flicker < 1 s, possessions per minute | 31 Oct | 5.1 | Printed for the baseline file |
| 5.3 | `feat(eval): plausibility anchors`: expected ~300–400 possessions (public 5 min ≈ 3.4 / min); agreement with Smart Tagging team-tagged phases | 4 Nov | 1.7, 5.2 | Both numbers in every experiment record |
| 5.4 | `chore(eval): log_experiment.py + make results` | 31 Oct | 5.2 | `RESULTS.md` regenerated from `runs/` |
| 5.5 | `exp(eval): metric study on synthetic labels`: how spellF1 reacts to flicker, shifted boundaries and `X` | 6 Nov | 5.1 | Short summary posted for `poss` |
| 5.6 | `chore(eval): review output-changing PRs` (experiment record present, CI honest) | ongoing | — | — |
| 5.7 | `docs(eval): technical doc draft → PDF`: skeleton by 9 Nov, collect sections, export 16 Nov | 9 Nov → 16 Nov | — | `Falafelona.pdf` uploaded with the form |
| 5.8 | `docs(eval): keep decisions.md up to date` after each sync | ongoing | — | — |

---

## 3. How we write and run tasks

- **One issue = one PR = at most 2 days of work.** If it's bigger, split it.
- Every issue has a `ws:` label, **one** assignee, a due date and its "done when" line from the tables above.
- Every PR that changes the output links a `configs/exp/*.yaml` and an `experiments/runs/*.yaml`. `configs/final.yaml` only changes through such a PR.
- Stuck? Add the `blocked` label and @mention the person you're waiting on in the group chat. Don't wait silently.
- Board columns: **Backlog → This week → In progress → In review → Done**. On Monday, each owner moves that week's issues into *This week*.

---

## 4. Critical path

```
25 Oct  kick-off: owners, interfaces (§0), D10 closed, board seeded
28 Oct  synthetic data (1.3) → ball / dead / poss code without waiting for real data
30 Oct  ✅ baseline reproduced from OUR repo (1.5)  ← biggest risk
 6 Nov  ✅ first end-to-end file from new components passes the validator
10 Nov  ✅ all 5 registered as "Falafelona"; doc skeleton filled
13 Nov  last integration check: pick final.yaml by CI, not point estimate
14 Nov  🧊 freeze (only fix/ and docs/ PRs after this)
15 Nov  clean-clone test → identical SHA-256
16 Nov  submit
```

If 1.5 slips past 30 Oct, everything shifts: Laila moves onto `io.py` for a few days (eval tooling can wait).
