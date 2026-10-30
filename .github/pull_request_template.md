## What & why
<!-- One or two sentences. What does this change, and why? -->

Closes #<!-- issue number -->

**Workstream:** <!-- int / ball / dead / poss / eval -->
**Type:** <!-- feat / exp / fix / docs / chore -->

## Results
<!-- Only if this changes the output. Delete otherwise. Full-match estimates with bootstrap CI; never tuned on the public 5 minutes. -->

| | spellF1 (95% CI) | macroF1 | # possessions |
|---|---|---|---|
| `main` before | | | |
| this PR | | | |

Experiment record: `experiments/runs/<!-- file -->.yaml`

## How to check it
<!-- What should the reviewer run or look at? -->

## Checklist
- [ ] Branch name follows `<type>/<ws>-<short-desc>`
- [ ] **No match data**, extracts, frame-level exports, or screenshots of data in this PR
- [ ] No match data was shared with a hosted AI tool while making this
- [ ] Nothing tuned on the public 5-minute GT
- [ ] New thresholds/parameters live in `configs/`, not hard-coded
- [ ] `vendor/challenge/` untouched
- [ ] Tests pass (`make test`, once it exists)
- [ ] If the pipeline output changed: the file still passes `validate_submission.py`
- [ ] Decision worth remembering? Added to `docs/decisions.md`
