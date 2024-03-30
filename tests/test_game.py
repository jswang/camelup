import numpy as np
from camelup.constants import *
from camelup.game import Game
from camelup.board import get_winners


def test_overall_probability():
    # Overall probabilities
    g = Game(
        4, setup={RED: 0, YELLOW: 0, BLUE: 2, GREEN: 2, PURPLE: 1, WHITE: 13, BLACK: 14}
    )
    first, second, landings = g.win_probabilities(g.board)
    first = first[:5]
    second = second[:5]
    assert np.all(
        np.isclose(
            first,
            [
                0.07398054620276842,
                0.25419316623020327,
                0.13835889761815687,
                0.39801409153261,
                0.1354532984162614,
            ],
        )
    )
    assert np.all(
        np.isclose(
            second,
            [
                0.10978925052999126,
                0.15208567153011598,
                0.29945753834642724,
                0.2764029180695847,
                0.16226462152388077,
            ],
        )
    )


def test_optimal_move():
    # Optimal move
    g = Game(
        4, setup={RED: 0, YELLOW: 0, BLUE: 2, GREEN: 2, PURPLE: 1, WHITE: 13, BLACK: 14}
    )
    g.optimal_move(g.players[0].id)


def test_parse_move():
    # Parse move
    g = Game(
        4, setup={RED: 0, YELLOW: 0, BLUE: 2, GREEN: 2, PURPLE: 1, WHITE: 13, BLACK: 14}
    )
    g.parse_move(0, ["bet", "yellow", "5"])
    assert g.players[0].bets == [(YELLOW, 5)]
    assert g.available_bets[YELLOW] == [2, 2, 3]
    g.parse_move(0, ["ally", "1"])
    assert g.players[0].ally == 1
    g.parse_move(0, ["boost", "2", "1"])
    assert g.players[0].boost == 2  # technically this is an illegal boost
    assert np.all(
        g.board.boosters == np.array([0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    )
    g.parse_move(0, ["roll", "red", "2"])
    assert g.players[0].points == 6
    assert len(g.dice) == N_DICE - 1
    g.parse_move(0, ["roll", "yellow", "2"])
    g.parse_move(0, ["roll", "blue", "2"])
    g.parse_move(0, ["roll", "green", "2"])
    g.parse_move(0, ["roll", "purple", "2"])
    # +2 from boost, +5 from roll, +1 from bet
    assert g.players[0].points == 11


def test_boost_points():
    g = Game(
        2,
        setup={
            RED: 1,
            BLUE: 2,
            YELLOW: 2,
            PURPLE: 3,
            GREEN: 3,
            BLACK: 13,
            WHITE: 13,
            "neg_boosters": np.array([4]),
        },
    )
    g.players[1].boost = 4
    g.parse_move(1, ["roll", "purple", "1"])
    assert g.players[1].points == 6


def test_boost_back_under():
    g = Game(
        2,
        setup={
            RED: 3,
            BLUE: 3,
            YELLOW: 3,
            PURPLE: 3,
            GREEN: 3,
            BLACK: 13,
            WHITE: 13,
            "neg_boosters": np.array([4]),
        },
    )
    g.players[1].boost = 4
    g.parse_move(1, ["roll", "yellow", "1"])
    # player 1 gets 3 + 1 + 3 points
    assert g.players[1].points == 7
    assert np.all(g.board.tiles[3][0:5] == np.array([YELLOW, PURPLE, GREEN, RED, BLUE]))


def test_conclude_round():
    g = Game(
        2,
        setup={
            RED: 2,
            YELLOW: 2,
            PURPLE: 2,
            GREEN: 2,
            BLUE: 5,
            BLACK: 11,
            WHITE: 11,
            "neg_boosters": np.array([3]),
        },
    )
    g.dice = [GREEN, PURPLE]
    g.available_bets[BLUE] = None
    g.available_bets[GREEN] = [2, 2]
    g.players[0].bets = [(3, 5), (2, 3), (2, 2)]
    g.players[1].bets = [(3, 3), (2, 5), (2, 2)]
    g.parse_move(1, ["roll", "purple", "1"])
    # player 0 gets: 3 - 1 + 3 + 2
    # player 1 gets: 3 + 1 (roll) - 1 + 5 + 2
    print(get_winners(g.board.tiles))
    assert g.players[0].points == 7
    assert g.players[1].points == 10
