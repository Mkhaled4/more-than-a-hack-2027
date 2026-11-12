# ws:poss: tests for the team evidence of the HMM. Made-up numbers only, no match data.

import numpy as np
import pytest

from falafelona import possession


def test_margin_costs_favour_the_closer_team_and_are_neutral_when_equal():
    d_home = np.array([1.0, 3.0, 2.0])
    d_away = np.array([3.0, 1.0, 2.0])
    costs = possession.margin_team_costs(
        d_home, d_away, team_cost=1.0, margin_scale=1.0, near_distance=5.0
    )

    assert costs[0, possession.H_STATE] < costs[0, possession.A_STATE]  # home closer
    assert costs[1, possession.A_STATE] < costs[1, possession.H_STATE]  # away closer
    assert costs[2, 0] == pytest.approx(costs[2, 1])  # a 50/50 duel


def test_margin_costs_give_no_evidence_without_a_ball_or_with_nobody_close():
    d_home = np.array([np.inf, 6.0])  # ball missing; nearest player 6 m away
    d_away = np.array([np.inf, 9.0])
    costs = possession.margin_team_costs(
        d_home, d_away, team_cost=1.0, margin_scale=1.0, near_distance=5.0
    )

    assert (costs == 0).all()  # the current owner just holds


def test_team_distances_finds_the_nearest_player_of_each_team():
    players = np.array([[[1.0, 0.0], [5.0, 0.0], [0.0, 2.0], [np.nan, np.nan]]])
    ball = np.array([[0.0, 0.0]])
    d_home, d_away = possession.team_distances(players, ball, np.array(["H", "H", "A", "A"]))

    assert d_home[0] == pytest.approx(1.0) and d_away[0] == pytest.approx(2.0)


def test_dead_costs_add_a_d_column_that_follows_the_dead_score():
    team = np.zeros((2, 2))
    costs = possession.add_dead_costs(team, np.array([0.0, 1.0]), dead_weight=2.0)

    assert costs.shape == (2, 3)
    assert costs[0, possession.D_STATE] == pytest.approx(2.0)  # alive: D is costly
    assert costs[1, possession.D_STATE] == pytest.approx(0.0)  # dead: D is free
    assert costs[1, possession.H_STATE] == pytest.approx(2.0)  # dead: H and A are costly


def test_the_old_nearest_evidence_is_unchanged():
    codes = np.array([possession.Possession.HOME, possession.Possession.AWAY,
                      possession.Possession.NOBODY])
    costs = possession.nearest_team_costs(codes, team_cost=1.0)

    assert costs.tolist() == [[0.0, 1.0], [1.0, 0.0], [0.0, 0.0]]


def test_an_unknown_team_evidence_is_refused():
    section = {
        "method": "hmm",
        "team_evidence": "telepathy",
        "team_cost": 1.0,
        "dead_weight": 2.0,
        "switch_cost": 10.0,
        "to_dead_cost": 6.0,
        "from_dead_cost": 6.0,
    }

    with pytest.raises(ValueError, match="team_evidence"):
        possession._hmm(None, None, section)