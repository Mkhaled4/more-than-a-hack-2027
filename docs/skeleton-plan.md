# 🏗️ Repo skeleton plan

This is the plan for how the repo is laid out and how we work in it. The skeleton in this PR follows it: **every file exists, but holds only comments describing what will go in it**. No pipeline code yet. Comment on the PR; once it's merged, each workstream fills in its files.
Every choice made here is also recorded in [`decisions.md`](decisions.md).

---

## 1. Target layout

```
Falafelona-hackathon/
├─ README.md                     overview, rules, deadlines, how to reproduce
├─ CLAUDE.md                     instructions for AI coding agents (see §4)
├─ AGENTS.md → CLAUDE.md         symlink, same rules for Codex / Cursor / Gemini / Copilot
├─ Makefile                      `make setup | test | submission | validate | eval`
├─ pyproject.toml                package + Python pin (3.12)
├─ requirements.txt              exact pinned runtime deps (what reproduction uses)
├─ requirements-dev.txt          + pytest, ruff
├─ .gitignore                    data, outputs, caches, videos, PDFs (see §3)
├─ .githooks/pre-commit          runs scripts/check_no_data.py on staged files
├─ .claude/settings.json         Claude Code: deny reading data paths
├─ .cursorignore / .aiexclude / .geminiignore     same deny list for other AI tools
├─ .github/
│  ├─ pull_request_template.md   filled in on every PR
│  └─ workflows/README.md        ci.yml comes later: lint + tests (synthetic data) + no-data check
├─ vendor/challenge/             git submodule → metrica-sports/more-than-a-hack-2027 (pinned)
├─ configs/
│  ├─ baseline.yaml              reproduces baseline_smooth50
│  ├─ final.yaml                 the submitted configuration (frozen 14 Nov)
│  └─ exp/                       one config per experiment
├─ src/falafelona/
│  ├─ vendor.py                  imports the official games.py / possession_metrics from the submodule
│  ├─ config.py                  loads configs/*.yaml
│  ├─ io.py                      loads data via vendor games.asset_paths() + MTAH_DATA_DIR
│  ├─ ball.py                    ws:ball: gap filling, false-detection filter
│  ├─ deadball.py                ws:dead: D detector
│  ├─ possession.py              ws:poss: H/A features + HMM/Viterbi with min durations
│  ├─ pipeline.py                ws:int: glue, writes outputs/Falafelona.csv
│  └─ cli.py                     `python -m falafelona run --config configs/final.yaml`
├─ scripts/
│  ├─ check_no_data.py           guard used by the pre-commit hook and CI
│  ├─ bootstrap_eval.py          ws:eval: public-5-min sanity score + label-free match stats
│  ├─ log_experiment.py          writes an experiment record (see §6)
│  └─ setup_github.sh            labels + list of manual GitHub settings
├─ experiments/
│  ├─ README.md                  how to log a run
│  ├─ runs/                      one YAML per run (aggregate metrics only)
│  └─ RESULTS.md                 summary table, generated from runs/
├─ notebooks/                    exploration only; the pipeline never imports from here
├─ tests/
│  ├─ synthetic.py               generates a SYNTHETIC data bundle in a temp folder at test time
│  ├─ conftest.py                shared fixtures
│  ├─ test_format.py             submission contract (official validator function)
│  ├─ test_determinism.py        run twice → identical SHA-256
│  ├─ test_baseline_equivalence.py   baseline.yaml == official baseline, on synthetic data
│  └─ test_no_data_guard.py      the guard blocks what it should
├─ docs/
│  ├─ skeleton-plan.md           this file
│  ├─ decisions.md               decision log
│  └─ Falafelona.md              the technical document (deliverable 3)
└─ outputs/                      gitignored; Falafelona.csv lands here
```

Each workstream owns its module, so most PRs touch one file plus tests and keep merge conflicts rare.

---

## 2. Official challenge code: pinned git submodule

```bash
git submodule add https://github.com/metrica-sports/more-than-a-hack-2027 vendor/challenge
cd vendor/challenge && git checkout <commit> && cd ../..
git commit -m "chore(int): add official challenge repo as submodule"
```

- This gives us `games.py`, `evaluation/validate_submission.py`, `evaluation/possession_metrics.py` and `starter/baseline.py` **exactly** as the organisers run them.
- **Never edit anything in `vendor/`.** If the organisers push a fix, someone bumps the pinned commit in a `chore/int-bump-challenge` PR.
- Clone with: `git clone --recurse-submodules …`. If you forgot: `git submodule update --init`.

---

## 3. Data: outside the repo, always

```bash
# once per laptop, in ~/.zshrc or ~/.bashrc
export MTAH_DATA_DIR=~/mtah-data
```

```
~/mtah-data/                 ← unpacked bundle, original names; not a git repo; never opened in an editor
├─ tactical/ …
├─ broadcast/ …
└─ cache/                    ← our derived files (cleaned ball, features); also frame-level, so also outside
```

- The code reads the path **only** from `MTAH_DATA_DIR` (through `games.asset_paths()`). If the variable is unset, it stops with a clear error. There is no fallback path.
- Tests generate synthetic data in a temp folder at run time, so not even fake data-shaped files are committed.
- `.gitignore` still lists `data/`, `*.mp4`, `*_atd.*`, `*_smart_tagging.xml`, `*_homography.csv`, `*_possession_gt*.csv`, `*.pkl`, `outputs/`, `*.pdf` as a backstop.
- **Pre-commit hook** (`.githooks/pre-commit`, enable once with `git config core.hooksPath .githooks`) rejects commits that stage those patterns or any file > 5 MB.
- **CI check** fails a PR that contains them.
- **GitHub push ruleset** (repo owner, if available: Settings → Rules → Rulesets → Push ruleset): block those paths/extensions and files > 5 MB at push time, so they never reach the public repo.
- Logs and prints show **aggregates only**. No `df.head()` of real data in code, PRs, issues or chat.

---

## 4. AI tools: CLAUDE.md / AGENTS.md + deny lists

`CLAUDE.md` (with `AGENTS.md` as a symlink to it) tells any coding agent:

- Never read, list, grep or load anything under `$MTAH_DATA_DIR`, `~/mtah-data`, `outputs/`, or any data file type.
- Never run the real pipeline (`make submission`). Only run tests on `tests/fixtures/`. If a task needs real data, ask a human to run it and report aggregate numbers.
- Never write code that prints raw rows or coordinates.
- Don't edit `vendor/`. Thresholds go in `configs/`. Don't tune on the public 5-minute GT. Stay inside the workstream's module unless asked.

Backstops, committed to the repo:
- `.claude/settings.json`: `permissions.deny` on `Read(~/mtah-data/**)`, `Read(./outputs/**)` and the data file patterns.
- `.cursorignore`, `.aiexclude`, `.geminiignore` with the same patterns.
- **Copilot** has no ignore file on personal plans. Turn it off for this workspace.

These configs are best-effort. The real protection is that the data isn't in the repo and that **humans, not agents, run the pipeline on real data**.

---

## 5. Git workflow

### Branch names: `<type>/<workstream>-<short-desc>`

| type | for |
|---|---|
| `feat/` | new pipeline functionality |
| `exp/` | an experiment (may never be merged) |
| `fix/` | bug fixes |
| `docs/` | README, decisions, technical doc |
| `chore/` | setup, deps, CI, tooling |

| workstream | tag |
|---|---|
| Integration & submission | `int` |
| Ball track | `ball` |
| Dead ball | `dead` |
| Possession model | `poss` |
| Evaluation & docs | `eval` |

Examples: `feat/ball-kalman-gapfill` · `exp/poss-hmm-min-duration` · `fix/int-off-by-one-frame` · `docs/eval-technical-doc`

### Rules
- `main` is protected and always runnable. Changes go in **via PR only**, with **1 approving review** and green CI.
- **Squash-merge.** The PR title becomes the commit, written as `type(ws): summary`, e.g. `feat(ball): Kalman gap filling`.
- Keep branches short-lived (a few days). Rebase on `main` often.
- Every PR uses the [PR template](../.github/pull_request_template.md) and links its issue (`Closes #12`).
- **After the 14 Nov freeze:** only `fix/` and `docs/` PRs.
- Labels: `ws:int` `ws:ball` `ws:dead` `ws:poss` `ws:eval` plus `type:exp`, `blocked`.

---

## 6. Experiments: saved in the repo

One small YAML file per run, so parallel PRs never conflict:

```yaml
# experiments/runs/2026-11-04-poss-hmm-mindur50.yaml
id: 2026-11-04-poss-hmm-mindur50
author: <github handle>
branch: exp/poss-hmm-min-duration
commit: <short sha>
config: configs/exp/poss-hmm-mindur50.yaml
change: "HMM with 50-frame minimum duration on top of nearest-player"
public_5min:                 # sanity check only, NEVER tuned on
  spellF1: 0.000
  spellF1_ci: [0.000, 0.000]
  macroF1: 0.000
full_match_stats:            # label-free, no ground truth needed
  n_possessions: 0
  median_possession_s: 0.0
  share: {H: 0.0, A: 0.0, D: 0.0, X: 0.0}
  flicker_lt_1s: 0
verdict: keep | drop | inconclusive
notes: ""
```

- `scripts/log_experiment.py` writes the file, and `make results` regenerates `experiments/RESULTS.md` (a sorted table).
- **Aggregate numbers only.** Never per-frame predictions or anything that reconstructs the data.
- **We have no full-match ground truth**, so no full-match score exists before results day. Records hold the public 5-minute score (sanity only) plus label-free stats over the whole match.
- Differences below ~0.04 spellF1 are noise: compare CIs, not point estimates.
- Seed entry: `E0`, official `baseline_smooth50`, spellF1 **0.2433**, macroF1 0.6724.

---

## 7. Reproducibility

- **One command:** `make submission`. It writes `outputs/Falafelona.csv` and runs `validate_submission.py` on that exact file.
- Pinned Python (3.12) and exact deps (`requirements.txt`, tooling D10). Fixed seeds, no order-dependent parallelism.
- `tests/test_determinism.py` runs the pipeline twice and checks for an identical SHA-256. The final hash goes in the README.
- **Clean-clone test (15 Nov):** on a laptop that has never run the pipeline: fresh clone → `make setup` → `make submission` → same hash.

---

## 8. Team process

### Task board: GitHub Projects (board view)
- Columns: **Backlog → This week → In progress → In review → Done**.
- One issue per task, labelled with its workstream, assigned to one person, with a due date.
- A PR with `Closes #N` moves its card to Done on merge.
- Issue templates can be added later if we find we need them.

### Rhythm

| What | When | How |
|---|---|---|
| **Async stand-up** | Daily or every other day, in the group chat | 3 lines: *done · next · blocked* |
| **Integration check** | **Every Friday** (Saturday if Friday doesn't work): 30 Oct, 6 Nov, 13 Nov | Merge open work, run `make submission`, log one experiment entry, update the board |
| **🧊 Freeze meeting** | **Sat 14 Nov** | Choose `configs/final.yaml`, tag `v1.0-freeze`, assign doc sections and the clean-clone test |
| **Submit check** | Mon 16 Nov | Validate the exact file together, submit the Google Form |

### Decisions
Anything we'd otherwise re-argue later gets a line in [`docs/decisions.md`](decisions.md). It also feeds the technical doc.

---

## 9. Build order (after this PR is merged)

The skeleton files exist now. Next PRs fill them in:

| # | PR | Workstream |
|---|---|---|
| 1 | `chore/int-tooling`: real `pyproject.toml`, pinned requirements, Makefile, `vendor.py`, `config.py` | int |
| 2 | `chore/int-no-data-guard`: `check_no_data.py`, pre-commit hook, `ci.yml`, its test | int |
| 3 | `feat/int-baseline-repro`: `io.py`, `pipeline.py`, `cli.py`, `baseline.yaml` + baseline equivalence tests (by 30 Oct) | int |
| 4 | `chore/eval-experiment-log`: `bootstrap_eval.py`, `log_experiment.py`, `make results` | eval |
| 5 | GitHub settings (owner): labels via `scripts/setup_github.sh`, branch protection, push ruleset, Projects board + issues | int |

Then the workstream branches (`feat/ball-…`, `feat/dead-…`, `feat/poss-…`) start in W1/W2.
