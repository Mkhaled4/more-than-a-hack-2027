# ⚽ Falafelona — More Than a Hack 2027

Team **Falafelona**'s entry for [More Than a Hack 2027](https://landing.mobileworldcapital.com/more-than-a-hack-2027)
(Metrica Sports × FC Barcelona / Barça Innovation Hub × Mobile World Capital Barcelona, Talent Arena).

**Team:** Tala · Chikhani · Dudu · Laila · Abdallah

> **Status:** 🟡 Week 0 (setup) · **Our best spellF1:** — · **Baseline to beat:** **0.2433**

---

## 🎯 The task

For **every frame** of one LaLiga match (FC Barcelona vs Athletic Club, 2024-25, matchday 2), say who has the ball:

| Label | Meaning |
|---|---|
| `H` | Home: FC Barcelona |
| `A` | Away: Athletic Club |
| `D` | Dead ball (out of play, stoppage, restart pending) |
| `X` | Abstain |

Output: one CSV, header `frame,label`, **exactly 199,319 rows**, frames `0 … 199318` in order, no blank cells.

Official spec: [metrica-sports/more-than-a-hack-2027](https://github.com/metrica-sports/more-than-a-hack-2027)
(read README → CHALLENGE → DATA → EVALUATION → SUBMISSION → RULES → FAQ).

---

## 📅 Deadlines

| Date | What |
|---|---|
| 20 Oct 2026 | Data released (challenge-data email arrives within 72h of registering) |
| 25 Oct 2026 | Kick-off call: owners, weekly sync time |
| **10 Nov 2026** | **All 5 members registered with the same team name: `Falafelona`** |
| 14 Nov 2026 | Submission instructions (Google Form) arrive by email · **🧊 code freeze** |
| 16 Nov 2026 | **Our internal submission date** |
| **17 Nov 2026, 23:59 CET** | **Official submission deadline** |
| before 26 Nov 2026 | Results announced. Top 20 go to the Innovation Challenge |
| 2 Mar 2027 | Onsite final, Talent Arena Barcelona |

---

## 📏 How we're scored (read before optimising anything)

- **Ranking metric: `spellF1`.** Each possession is one object. Our possessions are matched one-to-one with the true ones by temporal IoU, and F1 is averaged over IoU thresholds 0.3–0.7. **Flicker (many short possessions) kills the score.**
- **Tie-break: `macroF1`**, per-frame F1 over H/A/D.
- **`X` on a graded frame** is forward-filled with our last label (within the half) for spellF1. That makes it free inside a possession and costly across a hand-over. Under macroF1 it counts as a miss.
- **Graded frames:** 1st half `11,185 – 90,651`, 2nd half `110,808 – 190,197`. All other frames are ignored.
- **Differences below ~0.04 spellF1 are noise.** Use bootstrap CIs before claiming that something is better.
- **No live leaderboard, no feedback.** The public 5-minute GT and `validate_submission.py` are the only signals before the deadline.

### 🏁 Baseline to beat

The official baseline gives the ball to the nearest player's team, then takes a centred majority vote over a window. Scores on the full match:

| Variant | macroF1 | spellF1 |
|---|---|---|
| baseline_raw | 0.6532 | 0.0486 |
| baseline_smooth25 | 0.6752 | 0.1996 |
| **baseline_smooth50** | 0.6724 | **0.2433** ← the published floor |
| baseline_smooth125 | 0.6356 | 0.2242 |

Lessons from this table:
1. Smoothing is the whole game: spellF1 moves 5× while macroF1 barely moves.
2. On the public 5 minutes, `smooth125` looks best, but on the full match it's worse than `smooth50`. **Do not tune on the public 5-minute GT.** It picks the wrong model. Use it only to check that the pipeline is correct.

---

## 📦 Data (not in this repo, ever)

| Asset | Notes |
|---|---|
| Tactical video + tracking (ATD) | **The reference timeline.** ATD `frame_id − 1` = submission row. Positions normalised 0–1 (pitch 105.3 × 68 m). **No player IDs**: 46 track slots that swap identity. **Ball missing on ~41% of graded frames.** |
| Smart Tagging | 638 automatic phases and set pieces with team tags. Every throw-in is tagged `N/A` for team. Treat it as evidence, not truth. |
| Homography | Pitch ↔ pixel, one 3×3 matrix per frame. |
| Broadcast video + ATD | Optional and **not synchronised** with the tactical video. A ~164k-row output means you indexed the wrong video. |
| Public GT | First 5 minutes (17 possessions), shipped in the official repo. |

Keep the data **outside** this repo and point to it with `MTAH_DATA_DIR`:

```bash
export MTAH_DATA_DIR=~/mtah-data      # unpacked bundle, original file names
```

---

## 🚫 Rules: these can disqualify us

- ❌ **No hand labelling.** Every label must come from code in this repo.
- ❌ **No private ground truth**, and no other corrected possession data for this match. Only the public 5 minutes.
- ❌ **Don't redistribute the data.** It never goes into git: no frame-level exports, clips, or tables of tracking.
- ❌ **Never upload match data to a hosted LLM** (ChatGPT, Claude, Gemini, Copilot chat, …). LLMs may help write *code*, but they must not see the data or extracts of it. Local models are fine.
- ✅ Any method is allowed as long as the organisers can inspect and run it (public models and open data are fine; private in-house models are not), **and** the technical doc explains it.
- ✅ Team of 3–5, everyone registered under **Falafelona**.

### Our own team rules

- Logs and prints show **aggregates only** (counts, scores). No `df.head()` of real data in code, PRs or chat.
- **Run the real pipeline yourself, not through an AI agent.** Agents work on code and synthetic data only.
- **Validate the exact file before uploading:** `python evaluation/validate_submission.py Falafelona.csv`.
- Every parameter lives in config. Every experiment gets a row in the Experiment Log.

---

## 📤 Deliverables (one Google Form, one response per team, editable until the deadline)

| # | Deliverable | Owner | Status |
|---|---|---|---|
| 1 | `Falafelona.csv`: the possession file (~1.9 MB) | _TBD_ | ⬜ |
| 2 | This public repo: **regenerates the exact same file** with pinned deps and one command | _TBD_ | ⬜ |
| 3 | `Falafelona.pdf` / `.md`: approach, assets used *and dropped*, possession rules, limitations, reproduction | _TBD_ | ⬜ |

A Google account is needed to upload.

---

## 🚀 Reproduce our submission

> _Placeholder, filled in once the pipeline exists._

```bash
git clone https://github.com/mohammednizar8/Falafelona-hackathon
cd Falafelona-hackathon
# <environment setup: Python version + pinned dependencies>
export MTAH_DATA_DIR=/path/to/mtah2027
# <the one command that writes Falafelona.csv>
python evaluation/validate_submission.py Falafelona.csv
```

Expected: 199,319 rows · SHA-256 `<fill in at freeze>` · runtime `<N> min` on `<machine>`.

---

## 🧭 Approach (draft)

The plan is three components plus glue:

1. **Ball track cleaning:** fill gaps (interpolation / Kalman) and filter out false ball detections.
2. **Dead-ball detector (`D`):** ball out of bounds, players static, Smart Tagging set pieces and restarts.
3. **Possession model (`H`/`A`):** nearest-player and team-control features, plus a rule for "controlled" possession, decoded with an **HMM / Viterbi with minimum durations** to kill flicker.
4. **Integration:** combine, decide where `X` is worth using, write and validate the CSV.

_Details and results are added here as they land. The full write-up goes in the technical doc._

---

## 👥 Workstreams

| # | Workstream | Owner | Scope |
|---|---|---|---|
| 1 | Integration & submission | _TBD_ | Repo, pipeline, validation, reproducibility, final upload |
| 2 | Ball track | _TBD_ | Gap filling, false-detection filtering |
| 3 | Dead ball (`D`) | _TBD_ | Out of bounds, static players, set pieces/restarts |
| 4 | Possession model (`H`/`A`) | _TBD_ | Control features, HMM/Viterbi, min durations |
| 5 | Evaluation & docs | _TBD_ | Experiment log, bootstrap CIs, technical document |

The full split (people, interfaces, every task with due date and "done when", ready to become issues) is in [docs/workstreams.md](docs/workstreams.md).

---

## 🗓 Plan

| Week | Goal | Done when |
|---|---|---|
| **W0: 22–26 Oct** | Kick-off, read the docs, get the data, repo skeleton | Everyone is registered and can run the starter code |
| **W1: 27 Oct – 2 Nov** | Reproduce the baseline from our repo, EDA | `baseline_smooth50` reproduced and validated; EDA findings shared |
| **W2: 3–9 Nov** | Build the three components, first end-to-end file | First full-pipeline CSV passes the validator |
| **W3: 10–16 Nov** | Combine, bootstrap, **freeze 14 Nov**, write the doc, clean-clone test | Form submitted on 16 Nov |

---

## 🧪 Experiments

Saved in the repo: one YAML per run in `experiments/runs/` (aggregate metrics only), summarised in `experiments/RESULTS.md`. Each entry has: ID · git commit · what changed · spellF1 (± bootstrap CI) · macroF1 · notes. See [docs/skeleton-plan.md](docs/skeleton-plan.md#6-experiments-saved-in-the-repo).

| ID | Change | spellF1 | macroF1 | Notes |
|---|---|---|---|---|
| E0 | Official baseline_smooth50 | 0.2433 | 0.6724 | Floor to beat |

---

## 🤝 Working together

- `main` is always runnable. Work on a branch named `<type>/<ws>-<short-desc>` (e.g. `feat/ball-kalman-gapfill`) and open a PR using the template.
- One review before merging, then squash-merge. The reviewer checks that no data and no data extracts are included.
- Tasks live on the **GitHub Projects board**, one issue per task in [docs/workstreams.md](docs/workstreams.md). Updates go in the group chat (async stand-up: *done · next · blocked*).
- **Integration check every Friday** (Saturday as fallback). **Freeze meeting Sat 14 Nov.**
- Decisions are recorded in [docs/decisions.md](docs/decisions.md). The full workflow is in [docs/skeleton-plan.md](docs/skeleton-plan.md).

---

## 🔗 Links

- Official challenge repo: <https://github.com/metrica-sports/more-than-a-hack-2027>
- Landing page: <https://landing.mobileworldcapital.com/more-than-a-hack-2027>
- Questions: hackathon.talentarena@mobileworldcapital.com, or open an issue on the official repo
- Learning: [kloppy](https://kloppy.pysport.org) · [Friends of Tracking (Laurie Shaw)](https://github.com/Friends-of-Tracking-Data-FoTD/LaurieOnTracking) · [hmmlearn](https://hmmlearn.readthedocs.io)

---

## 📄 Licence

Code: _TBD_. The match data is © its owners, licensed for this competition only, and **not included or redistributed here**.
