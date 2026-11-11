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


def viterbi(costs: np.ndarray, switch_cost) -> np.ndarray:
    """The cheapest state sequence: int[n] of state indices, given costs float[n, k].

    switch_cost: one number (every change costs the same) or a [k, k] table where
    switch_cost[a, b] is the cost of going from state a to state b (diagonal = 0).
    Total cost = sum of costs[t, state_t] + the switch cost of every change.
    Deterministic: on ties, staying beats switching and a lower state index beats a higher one.
    """
    costs = np.asarray(costs, dtype=np.float64)
    n, k = costs.shape
    if n == 0:
        return np.zeros(0, dtype=np.int64)
    if np.ndim(switch_cost) == 0:
        transition = np.full((k, k), float(switch_cost))
        np.fill_diagonal(transition, 0.0)
    else:
        transition = np.asarray(switch_cost, dtype=np.float64)
        if transition.shape != (k, k):
            raise ValueError(f"switch_cost table must be {k}x{k}, got {transition.shape}")

    order = np.array([[s, *[p for p in range(k) if p != s]] for s in range(k)])

    back = np.zeros((n, k), dtype=np.int8)
    total = costs[0].copy()
    for t in range(1, n):
        candidates = total[order] + transition[order, np.arange(k)[:, None]]  # [state, prev]
        pick = np.argmin(candidates, axis=1)
        back[t] = order[np.arange(k), pick]
        total = candidates[np.arange(k), pick] + costs[t]

    path = np.empty(n, dtype=np.int64)
    path[-1] = int(np.argmin(total))
    for t in range(n - 1, 0, -1):
        path[t - 1] = back[t, path[t]]
    return path


def no_evidence_within(codes: np.ndarray, margin: int) -> np.ndarray:
    """bool[n]: no frame within +/- margin has a team (HOME or AWAY). The baseline's D."""
    has_team = codes != Possession.NOBODY
    cumulative = np.concatenate(([0], np.cumsum(has_team)))
    index = np.arange(len(codes))
    low = np.maximum(0, index - margin)
    high = np.minimum(len(codes), index + margin + 1)
    return (cumulative[high] - cumulative[low]) == 0


def decode_switch_cost(codes: np.ndarray, switch_cost: float, dead_margin: int) -> np.ndarray:
    """H / A / D per frame from team evidence codes (HOME / AWAY / NOBODY)."""
    costs = np.zeros((len(codes), 2))
    costs[codes == Possession.AWAY, 0] = 1.0   # evidence against H
    costs[codes == Possession.HOME, 1] = 1.0   # evidence against A
    team = np.array(["H", "A"])[viterbi(costs, switch_cost)]
    return np.where(no_evidence_within(codes, dead_margin), "D", team).astype("<U1")


STATES = ("H", "A", "D")
H_STATE, A_STATE, D_STATE = 0, 1, 2
def hmm_costs(codes: np.ndarray, dead_score: np.ndarray, team_cost: float,
              dead_weight: float) -> np.ndarray:
    """float[n, 3]: the cost of H, A and D on every frame. Low cost = this state fits.

    Team evidence: the nearest player's team makes the OTHER team cost `team_cost`.
    A frame with no ball (NOBODY) costs nothing for either team, so the owner holds.
    Dead-ball evidence: dead_score p in 0..1. D costs dead_weight * (1 - p),
    H and A each cost dead_weight * p. p = 0.5 is neutral.
    """
    n = len(codes)
    costs = np.zeros((n, 3))
    costs[codes == Possession.AWAY, H_STATE] = team_cost     # away nearest: evidence against H
    costs[codes == Possession.HOME, A_STATE] = team_cost     # home nearest: evidence against A

    p = np.clip(np.nan_to_num(np.asarray(dead_score, dtype=np.float64)), 0.0, 1.0)
    costs[:, D_STATE] += dead_weight * (1.0 - p)              # alive-looking frames: D is costly
    costs[:, H_STATE] += dead_weight * p                       # dead-looking frames: H and A
    costs[:, A_STATE] += dead_weight * p                       #   are costly
    return costs


def switch_table(switch_cost: float, to_dead_cost: float, from_dead_cost: float) -> np.ndarray:
    """[3, 3] switch costs between H, A and D (rows = from, columns = to)."""
    return np.array([
        [0.0, switch_cost, to_dead_cost],          # from H
        [switch_cost, 0.0, to_dead_cost],          # from A
        [from_dead_cost, from_dead_cost, 0.0],     # from D
    ])


def _number(section, key, *, whole=False):
    """A config value that must be a number >= 0 (and a whole number if `whole`)."""
    if key not in section:
        raise ValueError(f"possession method {section['method']!r} needs {key!r} in the config")
    value = section[key]
    ok = isinstance(value, int) if whole else isinstance(value, int | float)
    if isinstance(value, bool) or not ok or not np.isfinite(value) or value < 0:
        kind = "a whole number" if whole else "a number"
        raise ValueError(f"possession.{key} must be {kind} >= 0, got {value!r}")
    return value


def _team_codes(match, dead_score, section):
    """Nearest-player team per frame, NOBODY where the dead score is >= dead_threshold."""
    codes, _ = Possession(match).nearest_player_labels()
    dead = np.asarray(dead_score) >= section["dead_threshold"]
    return np.where(dead, Possession.NOBODY, codes).astype(np.int8)


def _hmm(match, dead_score, section):
    """3-state HMM: H, A and D decoded together with Viterbi."""
    team_cost = _number(section, "team_cost")
    dead_weight = _number(section, "dead_weight")
    table = switch_table(_number(section, "switch_cost"),
                         _number(section, "to_dead_cost"),
                         _number(section, "from_dead_cost"))
    codes, _ = Possession(match).nearest_player_labels()
    costs = hmm_costs(codes, dead_score, team_cost, dead_weight)
    return np.array(STATES)[viterbi(costs, table)]

def _nearest_majority(match, dead_score, section):
    codes = _team_codes(match, dead_score, section)
    return Possession(match).smooth(codes, section["window"])

def _decoder(match, dead_score, section):
    codes, _ = Possession(match).nearest_player_labels()
    dead = np.asarray(dead_score) >= section["dead_threshold"]
    return Possession(match).decoder(
        codes, dead_mask=dead, switch_frames=section.get("switch_frames", 15)
    )

def _switch_cost(match, dead_score, section):
    switch_cost = _number(section, "switch_cost")
    dead_margin = _number(section, "dead_margin", whole=True)
    _number(section, "dead_threshold")
    return decode_switch_cost(_team_codes(match, dead_score, section), switch_cost, dead_margin)


# method name in configs/*.yaml -> function(match, dead_score, cfg["possession"]) -> labels
METHODS = {
    "nearest_majority": _nearest_majority,
    "switch_cost": _switch_cost,
    "decoder": _decoder,
    "hmm": _hmm,
}

def predict(match: Match, dead_score: np.ndarray, cfg: dict) -> np.ndarray:
    """What pipeline.py calls (docs/architecture.md): H / A / D per frame.

    `match` is the cleaned Match from ball.py, so its ball_xy already holds the cleaned track.
    `dead_score` comes from deadball.detect. The `possession.method` key of the config picks
    the method from METHODS; each method reads its own settings from the same section.
    """
    section = cfg["possession"]
    method = section["method"]
    if method not in METHODS:
        raise ValueError(
            f"unknown possession method {method!r}; choose from {sorted(METHODS)}"
        )
    return METHODS[method](match, dead_score, section)
