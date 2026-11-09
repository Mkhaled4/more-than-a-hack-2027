# ws:poss: turn per-frame evidence into H / A / D possessions.
#
# spellF1 punishes flicker, so turning frames into clean possessions matters more than the
# per-frame guess.
#
# Ideas:
# - nearest player's team (official baseline), team-control features
# - a rule for a "controlled" possession vs a loose ball / challenge
# - H/A/D decoder (HMM / Viterbi) with a switch cost: the core of the system (docs/decisions.md D13)
# - modest minimum durations; very short possessions may count in the ground truth
# - official baseline smoothing: centred majority vote over +/- 50 frames (spellF1 0.2433)
#
# Methods are selected via the `possession:` section of the config.

import os

import numpy as np

from falafelona.io import Match

# The four published baseline variants: (name, half-width of the vote window in frames).
VARIANTS = (
    ("baseline_raw", 0),
    ("baseline_smooth25", 25),
    ("baseline_smooth50", 50),
    ("baseline_smooth125", 125),
)
LABELS = ("H", "A", "D")


class Possession:
    """Turns the cleaned data into H / A / D per frame (PR #9 structure). Task 4.1, Dudu."""

    HOME, AWAY, NOBODY = 0, 1, -1

    def __init__(self, data: Match):
        self.data = data

    # ------------------------------------------------------------------ step 1: nearest player
    def nearest_player_labels(self) -> tuple[np.ndarray, np.ndarray]:
        """Per-frame team of the player closest to the ball: HOME / AWAY / NOBODY.

        Also returns the distance in metres to that player (NaN where NOBODY).
        """
        players = self.data.players_xy
        ball = self.data.ball_xy
        slot = np.asarray(self.data.slot_team)
        team_of_track = np.select([slot == "H", slot == "A"], [self.HOME, self.AWAY], self.NOBODY)

        scale = np.asarray(self.data.pitch, dtype=np.float32)  # turn 0-1 into metres,
        players_m = players * scale  # otherwise the short axis
        ball_m = ball * scale  # counts as long as the long one

        diff = players_m - ball_m[:, None, :]  # (frames, tracks, 2)
        dist2 = np.sum(diff * diff, axis=2)  # squared distance, NaN if missing

        dist2 = np.where(np.isnan(dist2), np.inf, dist2)  # missing -> "infinitely far"
        nearest = np.argmin(dist2, axis=1)  # index of closest track
        best = dist2[np.arange(len(dist2)), nearest]

        found = np.isfinite(best)  # inf means nobody / no ball
        codes = np.where(found, team_of_track[nearest], self.NOBODY).astype(np.int8)
        distance = np.where(found, np.sqrt(best), np.nan).astype(np.float32)
        return codes, distance

    # ------------------------------------------------------------------ step 2: majority vote
    def smooth(self, codes: np.ndarray, window: int) -> np.ndarray:
        """Majority vote over a centred window of +/- `window` frames. D where nobody has the ball.

        Computed with cumulative sums, so the cost does not grow with the window -- a 125-frame
        window over 199319 frames is the same work as a 1-frame one.

        Ties go to the home side. With an odd-sized window over two classes a tie needs the two
        counts to be exactly equal, which is rare and never worth a coin flip.
        """
        if window <= 0:
            return np.where(codes == self.HOME, "H", np.where(codes == self.AWAY, "A", "D"))

        home_cumulative = np.concatenate(([0], np.cumsum(codes == self.HOME)))
        away_cumulative = np.concatenate(([0], np.cumsum(codes == self.AWAY)))

        index = np.arange(len(codes))
        low = np.maximum(0, index - window)
        high = np.minimum(len(codes), index + window + 1)
        home = home_cumulative[high] - home_cumulative[low]
        away = away_cumulative[high] - away_cumulative[low]

        labels = np.full(len(codes), "D", dtype="<U1")
        seen = (home + away) > 0
        labels[seen] = np.where(home[seen] >= away[seen], "H", "A")
        return labels

    # ------------------------------------------------------------------ the method
    def nearest_majority(self, window: int = 50) -> np.ndarray:
        """Official baseline: nearest player, then a +/- `window` majority vote."""
        codes, _ = self.nearest_player_labels()
        return self.smooth(codes, window)

    # ------------------------------------------------------------------ output
    @staticmethod
    def write_submission(path: str, labels: np.ndarray) -> str:
        """A frame,label CSV -- the whole submission format."""
        folder = os.path.dirname(path)
        if folder and not os.path.isdir(folder):
            os.makedirs(folder)
        with open(path, "w") as handle:
            handle.write("frame,label\n")
            handle.writelines(f"{frame},{label}\n"
                              for frame, label in enumerate(labels))
        return path

    def write_variants(self, out_dir: str, windows=None) -> list[str]:
        """Write the published baseline variants (or the given windows) and print class counts.

        Step 1 runs once; only the cheap smoothing is repeated per window.
        """
        variants = ([(f"baseline_smooth{w}" if w else "baseline_raw", w)
                     for w in windows] if windows else list(VARIANTS))

        codes, _ = self.nearest_player_labels()
        seen = int(np.sum(codes != self.NOBODY))
        print(f"ball located on {seen} of {len(codes)} frames ({100.0 * seen / len(codes):.1f}%)\n")

        paths = []
        for name, window in variants:
            labels = self.smooth(codes, window)
            path = self.write_submission(os.path.join(out_dir, f"{name}.csv"), labels)
            counts = {label: int(np.sum(labels == label)) for label in LABELS}
            print("{:<20} window +/-{:<4} H {:>6}  A {:>6}  D {:>6}  -> {}".format(
                name, window, counts["H"], counts["A"], counts["D"], path))
            paths.append(path)

        print("\nNow score them:  python evaluation/run_evaluation.py")
        return paths