import numpy as np
from camelup.constants import *
from camelup.game import Game, get_rounds
from camelup.board import get_winners
import timeit
import pytest


@pytest.fixture
def game():
    return Game(4)


def test_check_user_input_easy(game):
    # easy ones
    assert game.check_user_input(0, "") is None
    assert game.check_user_input(0, "blahblah") is None
    assert game.check_user_input(0, "optimal") == "optimal"
    assert game.check_user_input(0, "optimal 2") == "optimal"
    assert game.check_user_input(0, "winner") == "winner"
    assert game.check_user_input(0, "winner 2") == "winner"
    assert game.check_user_input(0, "loser") == "loser"
    assert game.check_user_input(0, "loser 2") == "loser"
    assert game.check_user_input(0, "print") == "print"
    assert game.check_user_input(0, "print 2") == "print"


def test_check_user_input_betting(game):
    # Betting
    assert game.check_user_input(0, "bet red") == ("bet", RED)
    assert game.check_user_input(0, "bet red 3") == ("bet", RED)
    assert game.check_user_input(0, "bet redd") is None
    game.available_bets[RED] = []
    assert game.check_user_input(0, "bet red") is None


def test_check_user_input_ally(game):
    # Allying
    assert game.check_user_input(0, "ally 2") == ("ally", 2)
    assert game.check_user_input(0, "ally 2 lsdf") == ("ally", 2)
    assert game.check_user_input(0, "ally") is None
    assert game.check_user_input(0, "ally 4") is None
    game.players[0].ally = 1
    assert game.check_user_input(0, "ally 1") is None
    assert game.check_user_input(1, "ally 0") is None
    assert game.check_user_input(0, "ally 0") is None


def test_check_user_input_boost(game):
    # Boosting
    assert game.check_user_input(0, "boost 2 1") == ("boost", 2, 1)
    assert game.check_user_input(0, "boost 2 1 blah") == ("boost", 2, 1)
    assert game.check_user_input(0, "boost 2 -1") == ("boost", 2, -1)
    assert game.check_user_input(0, "boost x -1") is None
    assert game.check_user_input(0, "boost 2 x") is None
    assert game.check_user_input(0, "boost 16 1") is None
    assert game.check_user_input(0, "boost -1 1") is None
    assert game.check_user_input(0, "boost 15 2") is None


def test_roll(game):
    # Rolling
    assert game.check_user_input(0, "roll") is None
    assert game.check_user_input(0, "roll red 1") == ("roll", RED, 1)
    assert game.check_user_input(0, "roll purple 3") == ("roll", PURPLE, 3)
    assert game.check_user_input(0, "roll red 4") is None
    assert game.check_user_input(0, "roll asldkjf 1") is None
    game.dice = [RED, YELLOW, BLUE, GREEN]
    assert game.check_user_input(0, "roll purple 1") is None


def test_optimal_move():
    # Optimal move
    g = Game(
        4, setup={RED: 0, YELLOW: 0, BLUE: 2, GREEN: 2, PURPLE: 1, WHITE: 13, BLACK: 14}
    )
    g.optimal_move(g.players[0].id)
    # TODO add an assert


def test_parse_move():
    # Parse move
    g = Game(
        4, setup={RED: 0, YELLOW: 0, BLUE: 2, GREEN: 2, PURPLE: 1, WHITE: 13, BLACK: 14}
    )
    g.parse_move(0, "bet yellow 5")
    assert g.players[0].bets == [(YELLOW, 5)]
    assert g.available_bets[YELLOW] == [2, 2, 3]
    g.parse_move(0, "ally 1")
    assert g.players[0].ally == 1
    g.parse_move(0, "boost 2 1")
    assert g.players[0].boost == 2  # technically this is an illegal boost
    assert np.all(
        g.board.boosters == np.array([0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    )
    g.parse_move(0, "roll red 2")
    assert g.players[0].points == 6
    assert len(g.dice) == N_DICE - 1
    g.parse_move(0, "roll yellow 2")
    g.parse_move(0, "roll blue 2")
    g.parse_move(0, "roll green 2")
    g.parse_move(0, "roll purple 2")
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
    g.parse_move(1, "roll purple 1")
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
    g.parse_move(1, "roll yellow 1")
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
    g.parse_move(1, "roll purple 1")
    # player 0 gets: 3 - 1 + 3 + 2
    # player 1 gets: 3 + 1 (roll) - 1 + 5 + 2
    print(get_winners(g.board.tiles))
    assert g.players[0].points == 7
    assert g.players[1].points == 10


# def test_get_rounds():
#     x = timeit.timeit(lambda: get_rounds(tuple(DICE)), number=1000)
#     print(x)
