# Falafelona: technical document

Deliverable 3. A few pages. Exported to Falafelona.pdf only at submission time (PDFs are gitignored).

Each section has one owner, who writes it and opens a `docs/<ws>-...` PR.
Laila (eval) collects the sections, edits for one voice and exports the PDF (task 5.7b, 16 Nov).
Aggregates only: no rows, coordinates or screenshots of match data.

## 1. Approach
Owner: Dudu + Abdallah (task 4.8)
The pipeline end to end, and why the H/A/D decoder is the centre of it (D13).

### 1.1 Ball track
Owner: Abdallah (task 2.7)
How we clean the ball: false detections removed, gaps filled, and methods we tried and dropped.

### 1.2 Dead ball and restarts
Owner: Chikhani (task 3.8)
How the dead-ball score is built and how restarts are found.

Draft notes (to be written up by 15 Nov):
- The dead-ball stage gives every frame a score from 0 (alive) to 1 (dead). It is evidence for the
  H/A/D decoder, not a final answer (D13). The method is chosen in the `deadball:` section of the config.
- `ball_missing` (the official baseline): dead wherever the tracking has no ball. Simple, but the ball
  is also missing in live play, so it calls far too much dead ball.
- `out_of_bounds`: dead where the ball is past a touchline or goal line by more than `out_margin`
  (1 m for now). The margin is there because tracking is noisy near the lines, and a ball on the line
  is still in play. A missing ball scores 0 here: not seeing the ball says nothing about where it is.
- Still to come: players standing still, Smart Tagging restarts, the second-half kickoff, and one
  combined score.

## 2. Assets used (and dropped)
Owner: Tala
Which provided files we use (tracking, Smart Tagging, homography, video) and which we don't, and why.

## 3. Training data (required)
Owner: Laila
The IDSSE dev set: what it is, how it is used for tuning, organiser approval (official issue #16),
and the citation (Bassek et al., Scientific Data 12, 195, 2025). No hand labels on this match.

## 4. Possession rules
Owner: Dudu + Abdallah (task 4.8)
How our labels follow the official possession definitions in CHALLENGE.md.

## 5. Results
Owner: Laila
Dev-set spellF1 on IDSSE, label-free stats on this match, and the baseline (0.2433) for comparison.

## 6. Limitations
Owner: Laila (collects one or two lines from each owner)
What we know is weak, e.g. random ball gaps on the dev set only approximate our real gaps.

## 7. Reproduction
Owner: Tala
One command, the SHA-256 of the file, runtime and machine.