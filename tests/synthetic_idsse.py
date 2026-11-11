"""Generator for a small SYNTHETIC match in the IDSSE (DFL XML) layout.

Tests never touch real match data. write_idsse() writes made-up numbers in the file layout that
src/falafelona/devset.py reads (match information XML + positions XML) to a temporary folder at
test time, so no data-shaped file is ever committed. It returns what it wrote, so tests can check
the loader exactly.

The game is scripted so that the right labels are known and a pipeline with a complete ball gets
them all right:
- players stand still: 11 home players on the left, 11 away players on the right
- the ball sits next to home player 0 while home has it, next to away player 0 while away has it,
  and 8 m outside the pitch while it is dead (BallStatus 0)
- possession spells (frames per half, in this order): H, D, A, D, H, A, D, H, A, D ...

Built in on purpose, because the real files have them:
- coordinates count from the CENTRE of the pitch, as in the DFL files (origin="corner" shifts them)
- frame numbers do not start at 0, and the second half continues far above the first
- one ball row is missing in the first half (no BallStatus there: truth must be X)
- a substitute who is only tracked in the second half, referees (not in the match information),
  and an extra-time FrameSet that must be ignored
- ball speed (S) is given
"""

from pathlib import Path

import numpy as np

PITCH = (105.0, 68.0)
FIRST_N0, SECOND_N0 = 10_000, 60_000
SPELL_PATTERN = "HDADHADHAD"        # one letter per spell, repeated; D = dead ball
HOME_IDS = [f"DFL-OBJ-H{i:02d}" for i in range(11)]
AWAY_IDS = [f"DFL-OBJ-A{i:02d}" for i in range(11)]
SUB_ID = "DFL-OBJ-HSUB"
HOME_TEAM, AWAY_TEAM, REF_TEAM = "DFL-CLU-HOME", "DFL-CLU-AWAY", "DFL-CLU-REF"
MISSING_BALL_ROW = 50               # first half: this ball row is left out of the file


def info_name(match_id):
    return f"DFL_02_01_matchinformation_DFL-COM-000001_DFL-MAT-{match_id}.xml"


def positions_name(match_id):
    return f"DFL_04_03_positions_raw_observed_DFL-COM-000001_DFL-MAT-{match_id}.xml"


def scripted_labels(n, spell=120, first_letter=0):
    """H/A/D per frame: spells of `spell` frames following SPELL_PATTERN."""
    pattern = np.array(list(SPELL_PATTERN))
    index = (np.arange(n) // spell + first_letter) % len(pattern)
    return pattern[index]


def _player_xy(side, i):
    """Fixed spot of a player, in centre coordinates."""
    x = (-40.0 + 3.0 * i) if side == "H" else (40.0 - 3.0 * i)
    return x, -20.0 + 4.0 * i


def _ball_xy(label, side_spots):
    if label == "D":
        return -60.0, 0.0                       # 7.5 m past the goal line (centre coordinates)
    x, y = side_spots[label]
    return x + 0.5, y + 0.5                     # half a metre from player 0


def _frames(rows):
    return "\n".join(rows)


def write_idsse(root, match_id="J03WTEST", n_first=1200, n_second=900, spell=120,
                origin="centre", pitch_in_info=True):
    """Write a synthetic IDSSE match under root/ and return what was written.

    Returns a dict with the truth of every frame as the loader should build it (without the
    halftime pad), the ball and player positions in centre coordinates, and the file paths.
    """
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    shift = np.array(PITCH) / 2.0 if origin == "corner" else np.zeros(2)

    spots = {"H": _player_xy("H", 0), "A": _player_xy("A", 0)}
    halves = {"firstHalf": (FIRST_N0, n_first, 0), "secondHalf": (SECOND_N0, n_second, 3)}

    ball_rows = {}
    truth = {}
    ball_xy = {}
    for section, (n0, count, first_letter) in halves.items():
        labels = scripted_labels(count, spell, first_letter)
        truth[section] = labels.copy()
        xy = np.array([_ball_xy(label, spots) for label in labels])
        ball_xy[section] = xy.copy()
        rows = []
        for k in range(count):
            if section == "firstHalf" and k == MISSING_BALL_ROW:
                continue
            alive = int(labels[k] != "D")
            possession = {"H": 1, "A": 2}.get(labels[k], 1)    # dead frames still carry a flag
            speed = 2.0 + (k % 5) * 0.5
            x, y = xy[k] + shift
            rows.append(
                f'<Frame N="{n0 + k}" X="{x:.3f}" Y="{y:.3f}" Z="0.1" S="{speed:.2f}" '
                f'BallPossession="{possession}" BallStatus="{alive}"/>'
            )
        ball_rows[section] = rows
        if section == "firstHalf":
            truth[section][MISSING_BALL_ROW] = "X"

    def player_rows(side, i, section, skip_first=False):
        n0, count, _ = halves[section]
        x, y = _player_xy(side, i)
        x, y = x + shift[0], y + shift[1]
        start = count // 2 if skip_first else 0
        return [
            f'<Frame N="{n0 + k}" X="{x:.3f}" Y="{y:.3f}" S="1.00"/>' for k in range(start, count)
        ]

    framesets = []

    def add(section, team, person, rows):
        framesets.append(
            f'<FrameSet GameSection="{section}" MatchId="DFL-MAT-{match_id}" '
            f'PersonId="{person}" TeamId="{team}">\n{_frames(rows)}\n</FrameSet>'
        )

    for section in ("firstHalf", "secondHalf"):
        for i, person in enumerate(HOME_IDS):
            add(section, HOME_TEAM, person, player_rows("H", i, section))
        for i, person in enumerate(AWAY_IDS):
            add(section, AWAY_TEAM, person, player_rows("A", i, section))
        add(section, REF_TEAM, "DFL-OBJ-REF0", player_rows("H", 5, section))     # ignored
    add("secondHalf", HOME_TEAM, SUB_ID, player_rows("H", 11, "secondHalf", skip_first=True))
    add("firstHalfExtra", HOME_TEAM, HOME_IDS[0], ['<Frame N="90000" X="1.0" Y="1.0" S="1.0"/>'])
    add("firstHalf", "BALL", "DFL-OBJ-0000XT", ball_rows["firstHalf"])
    add("secondHalf", "BALL", "DFL-OBJ-0000XT", ball_rows["secondHalf"])

    positions_path = root / positions_name(match_id)
    positions_path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<PutDataRequest>\n<Positions>\n'
        + "\n".join(framesets)
        + "\n</Positions>\n</PutDataRequest>\n"
    )

    def team_xml(role, team, people):
        persons = "".join(f'<Player PersonId="{p}" ShirtNumber="{i + 1}"/>'
                          for i, p in enumerate(people))
        return f'<Team Role="{role}" TeamId="{team}"><Players>{persons}</Players></Team>'

    environment = f'<Environment PitchX="{PITCH[0]}" PitchY="{PITCH[1]}"/>' if pitch_in_info else ""
    info_path = root / info_name(match_id)
    info_path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<PutDataRequest>\n<MatchInformation>\n'
        f'<General MatchId="DFL-MAT-{match_id}">{environment}</General>\n'
        "<Teams>"
        + team_xml("home", HOME_TEAM, [*HOME_IDS, SUB_ID])
        + team_xml("guest", AWAY_TEAM, AWAY_IDS)
        + "</Teams>\n</MatchInformation>\n</PutDataRequest>\n"
    )

    return {
        "match_id": match_id,
        "n_first": n_first,
        "n_second": n_second,
        "truth_first": truth["firstHalf"],
        "truth_second": truth["secondHalf"],
        "ball_first": ball_xy["firstHalf"],
        "ball_second": ball_xy["secondHalf"],
        "pitch": PITCH,
        "info_path": info_path,
        "positions_path": positions_path,
        "shift": shift,
    }
