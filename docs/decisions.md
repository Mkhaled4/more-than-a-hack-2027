# 🧾 Decision log

One line per decision we don't want to re-argue. Newest at the bottom.
**Status:** ✅ accepted · 💬 proposed (open for discussion on the PR / at the next sync) · ❌ reversed

| # | Date | Decision | Why | Status |
|---|---|---|---|---|
| D1 | 2026-10-22 | Match data lives **outside the repo**, located via `MTAH_DATA_DIR` | A public repo + one `.gitignore` line is too fragile; keeps data out of git and away from AI tools; the organisers' `games.py` already uses `MTAH_DATA_DIR` | ✅ |
| D2 | 2026-10-22 | Derived frame-level files (caches, features) go under `$MTAH_DATA_DIR/cache/`, never in the repo | They count as data under the T&Cs (no derived data that reconstructs it) | ✅ |
| D3 | 2026-10-22 | Official challenge code comes in as a **pinned git submodule** at `vendor/challenge/`, never edited | Validator and metric stay identical to the official scorer; no copy drift or licence questions | ✅ |
| D4 | 2026-10-22 | `CLAUDE.md` + `AGENTS.md` (symlink) + per-tool AI deny lists in the repo | Every agent gets the same data rules; backstop for the "no data to hosted LLMs" T&C | ✅ |
| D5 | 2026-10-22 | Branches named `<type>/<ws>-<desc>`; PR-only into `main`, 1 review, squash-merge, PR template | Clear history, easy review, one place to check the data rules | ✅ |
| D6 | 2026-10-22 | Tasks tracked on a **GitHub Projects board** (board view) | Free, next to the code, everyone already has access, PRs close issues automatically | ✅ |
| D7 | 2026-10-22 | **Experiment results stored in the repo**: one YAML per run in `experiments/runs/`, aggregates only | Versioned with the code that produced them; no merge conflicts; feeds the technical doc | ✅ |
| D8 | 2026-10-22 | Integration check **every Friday** (Saturday as fallback); **freeze meeting Sat 14 Nov**; internal submit Mon 16 Nov | Catch integration problems weekly, not at the deadline; one day of buffer before 17 Nov | ✅ |
| D9 | 2026-10-22 | Do **not** tune on the public 5-minute GT; use it only as a pipeline check; compare runs with bootstrap CIs | Organisers show it picks the wrong model (smooth125 vs smooth50); <0.04 spellF1 is noise | ✅ |
| D10 | 2026-10-22 | Python 3.12, dependencies locked with `uv` (`uv.lock`), one command `make submission` | Reproduction must give the *identical* file | 💬 |
