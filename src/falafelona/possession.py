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

    def nearest_player_labels(self) -> tuple[np.ndarray, np.ndarray]:
        """Per-frame team of the player closest to the ball: HOME / AWAY / NOBODY.

        Also returns the distance in metres to that player (NaN where NOBODY).
        """
        players = self.data.players_xy
        ball = self.data.ball_xy
        slot = np.asarray(self.data.slot_team)
        team_of_track = np.select([slot == "H", slot == "A"], [self.HOME, self.AWAY], self.NOBODY)

        diff = players - ball[:, None, :]  # (frames, tracks, 2)
        dist2 = np.sum(diff * diff, axis=2)  # squared distance, NaN if missing

        dist2 = np.where(np.isnan(dist2), np.inf, dist2)  # missing -> "infinitely far"
        nearest = np.argmin(dist2, axis=1)  # index of closest track
        best = dist2[np.arange(len(dist2)), nearest]

        found = np.isfinite(best)  # inf means nobody / no ball
        codes = np.where(found, team_of_track[nearest], self.NOBODY).astype(np.int8)
        distance = np.where(found, np.sqrt(best), np.nan).astype(np.float32)
        return codes, distance

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

    def nearest_majority(self, window: int = 50) -> np.ndarray:
        """Official baseline: nearest player, then a +/- `window` majority vote."""
        codes, _ = self.nearest_player_labels()
        return self.smooth(codes, window)

    def decoder(self, codes: np.ndarray, dead_mask: np.ndarray | None = None,
                switch_frames: int = 15) -> np.ndarray:
        """Hysteresis decoder: keeps the current owner instead of voting over a window.

        Walks the frames in order and remembers who has the ball. The other team only takes
        over once it has been nearest for `switch_frames` frames in a row (ball-missing frames
        neither count towards nor break that run); the switch is then back-dated to where the
        run started, so real hand-overs are not reported late. Ball-missing frames keep the
        previous owner; D comes only from `dead_mask`. After a D, the first team seen takes
        the ball straight away.

        dead_mask     : True on frames the dead-ball detector flags; these are always D.
        switch_frames : frames the challenger must stay nearest before possession changes
                        (25 frames = 1 s at 25 fps).
        """
        codes = np.asarray(codes)
        dead = len(LABELS) - 1  # index of "D" in LABELS
        out = np.full(len(codes), dead, dtype=np.int8)  # indices into LABELS: 0=H, 1=A, 2=D
        owner = dead  # start as dead ball
        run_team, run_start, run_len = None, 0, 0  # challenger currently trying to take over

        for i, c in enumerate(codes):
            if dead_mask is not None and dead_mask[i]:  # detected stoppage: always D
                out[i] = dead
                owner = dead
                run_team, run_len = None, 0
                continue

            if c == self.NOBODY:  # ball not visible: keep the current owner
                out[i] = owner
                continue

            if owner == dead:  # restart after dead ball: take it immediately
                owner = c
                run_team, run_len = None, 0
            elif c == owner:
                run_team, run_len = None, 0  # owner confirmed, cancel challenger
            else:
                if run_team != c:
                    run_team, run_start, run_len = c, i, 0
                run_len += 1
                if run_len >= switch_frames:  # challenger held long enough: switch,
                    out[run_start:i] = c  # back-dated to when the run began
                    owner = c
                    run_team, run_len = None, 0
            out[i] = owner

        return np.array(LABELS)[out]

def predict(match: Match, dead_score: np.ndarray, cfg: dict) -> np.ndarray:
    """What pipeline.py calls (docs/architecture.md): H / A / D per frame.

    `match` is the cleaned Match from ball.py, so its ball_xy already holds the cleaned track.
    `ball` (the BallTrack) is accepted for the interface but not used by nearest_majority.
    Frames whose dead score is >= dead_threshold give no team vote, then the centred majority
    vote of +/- window frames runs. Both numbers come from the `possession:` config section.
    """
    section = cfg["possession"]
    method = section["method"]

    possession = Possession(match)
    codes, _ = possession.nearest_player_labels()
    dead = np.asarray(dead_score) >= section["dead_threshold"]
    if method == "decoder":
        return possession.decoder(
            codes,
            dead_mask=dead,
            switch_frames=section.get("switch_frames", 15),
        )
    codes = np.where(dead, Possession.NOBODY, codes).astype(np.int8)
    return possession.smooth(codes, section["window"])
