import numpy as np
from camelup.constants import *
from camelup.game import Game, get_rounds, bet_value, win_probabilities
from camelup.board import get_winners
import pytest


@pytest.fixture
def game():
    return Game(4)


def test_equality_game():
    g = Game(
        4, setup={YELLOW: 1, PURPLE: 1, GREEN: 1, RED: 2, BLUE: 3, BLACK: 14, WHITE: 14}
    )
    g2 = Game(
        4, setup={YELLOW: 1, PURPLE: 1, GREEN: 1, RED: 2, BLUE: 3, BLACK: 14, WHITE: 14}
    )
    assert g == g2


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
    assert game.check_user_input(0, "help") is None


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
    assert game.check_user_input(0, "boost 3 +") == ("boost", 2, BOOST_POS)
    assert game.check_user_input(0, "boost 3 + blah") == ("boost", 2, BOOST_POS)
    assert game.check_user_input(0, "boost 3 -") == ("boost", 2, BOOST_NEG)
    assert game.check_user_input(0, "boost x -") is None
    assert game.check_user_input(0, "boost 3 1") is None
    assert game.check_user_input(0, "boost 17 +") is None
    assert game.check_user_input(0, "boost 0 +") is None
    assert game.check_user_input(0, "boost 16 +") == ("boost", 15, BOOST_POS)


def test_roll(game):
    # Rolling
    assert game.check_user_input(0, "roll") is None
    assert game.check_user_input(0, "roll red 1") == ("roll", RED, 1)
    assert game.check_user_input(0, "roll purple 3") == ("roll", PURPLE, 3)
    assert game.check_user_input(0, "roll red 4") is None
    assert game.check_user_input(0, "roll asldkjf 1") is None
    game.dice = [RED, YELLOW, BLUE, GREEN, GREY]
    assert game.check_user_input(0, "roll purple 1") is None
    assert game.check_user_input(0, "roll grey 1") is None
    assert game.check_user_input(0, "roll black 1") == ("roll", BLACK, 1)
    game.dice = [RED, YELLOW, BLUE, GREEN, GREY]
    assert game.check_user_input(0, "roll white 2") == ("roll", WHITE, 2)


def test_optimal_move():
    """Sanity check that this runs"""
    # Optimal move
    g = Game(
        4, setup={RED: 1, YELLOW: 1, PURPLE: 2, BLUE: 3, GREEN: 3, WHITE: 14, BLACK: 15}
    )
    g.dice = [GREEN]
    g.optimal_move(g.players[0].id)


def test_parse_move():
    # Parse move
    g = Game(
        4, setup={RED: 1, YELLOW: 1, PURPLE: 2, BLUE: 3, GREEN: 3, WHITE: 14, BLACK: 15}
    )
    g.parse_move(0, "bet yellow 5")
    assert g.players[0].bets == [(YELLOW, 5)]
    assert g.available_bets[YELLOW] == [2, 2, 3]
    g.parse_move(0, "ally 1")
    assert g.players[0].ally == 1
    g.parse_move(0, "boost 2 +")
    assert g.players[0].boost == 1
    assert g.board.booster_tiles() == [1]
    g.parse_move(0, "roll red 1")
    assert g.players[0].points == 6
    assert len(g.dice) == N_DICE - 1
    assert g.board.tiles == {
        0: [],
        1: [PURPLE, BOOST_POS],
        2: [BLUE, GREEN, RED, YELLOW],
        3: [],
        4: [],
        5: [],
        6: [],
        7: [],
        8: [],
        9: [],
        10: [],
        11: [],
        12: [],
        13: [WHITE],
        14: [BLACK],
        15: [],
    }


def test_parse_move_easy(game):
    game.parse_move(0, "winner")
    assert len(game.winner_bets) == 1
    game.parse_move(0, "loser")
    assert len(game.loser_bets) == 1


def test_boost_points():
    g = Game(
        2,
        setup={
            RED: 2,
            BLUE: 3,
            YELLOW: 3,
            PURPLE: 4,
            GREEN: 4,
            BLACK: 14,
            WHITE: 14,
            BOOST_NEG: [5],
        },
    )
    g.players[1].boost = 4
    g.parse_move(1, "roll purple 1")
    assert g.players[1].points == 6


def test_boost_back_under():
    g = Game(
        2,
        setup={
            RED: 4,
            BLUE: 4,
            YELLOW: 4,
            PURPLE: 4,
            GREEN: 4,
            BLACK: 14,
            WHITE: 14,
            BOOST_NEG: [5],
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
            RED: 3,
            YELLOW: 3,
            PURPLE: 3,
            GREEN: 3,
            BLUE: 6,
            BLACK: 12,
            WHITE: 12,
            BOOST_NEG: [4],
        },
    )
    g.dice = [GREEN, PURPLE]
    g.available_bets[BLUE] = None
    g.available_bets[GREEN] = [2, 2]
    g.players[0].bets = [(3, 5), (2, 3), (2, 2)]
    g.players[1].bets = [(3, 3), (2, 5), (2, 2)]
    g.players[1].boost = 3
    g.parse_move(1, "roll purple 1")
    # player 0 gets: 3 - 1 + 3 + 2
    # player 1 gets: 3 + 1 (roll) + 2 (landings) - 1 (loss) + 5 + 2
    print(get_winners(g.board.tiles))
    assert g.players[0].points == 7
    assert g.players[1].points == 12


def test_get_rounds():
    assert get_rounds((RED, GREY)) == [
        [(RED, 1)],
        [(RED, 2)],
        [(RED, 3)],
        [(BLACK, 1)],
        [(WHITE, 1)],
        [(BLACK, 2)],
        [(WHITE, 2)],
        [(BLACK, 3)],
        [(WHITE, 3)],
    ]
    assert len(get_rounds((RED, GREEN, BLUE))) == 54


def test_bet_value():
    assert bet_value(5, 0.3, 0.2) == pytest.approx(5 * 0.3 + 0.2 - 0.5)
    assert bet_value(1, 0.3, 0.2) == pytest.approx(0.3 + 0.2 - 0.5)


def test_bet(game):
    assert game.bet(0, RED)
    assert game.players[0].bets == [(RED, 5)]
    assert game.available_bets[RED] == [2, 2, 3]
    assert game.bet(0, RED)
    assert game.players[0].bets == [(RED, 5), (RED, 3)]
    assert game.available_bets[RED] == [2, 2]
    assert game.bet(0, RED)
    assert game.players[0].bets == [(RED, 5), (RED, 3), (RED, 2)]
    assert game.available_bets[RED] == [2]
    assert game.bet(0, RED)
    assert game.players[0].bets == [(RED, 5), (RED, 3), (RED, 2), (RED, 2)]
    assert game.available_bets[RED] == []
    assert not game.bet(0, RED)


def test_best_ally(game):
    game.bet(2, RED)
    game.bet(3, YELLOW)
    assert game.best_ally(0, [1, 0, 0, 0, 0], [0, 0, 0, 0, 0]) == (5, 2)
    assert game.best_ally(0, [0, 1, 0, 0, 0], [0, 0, 0, 0, 0]) == (5, 3)
    game.bet(1, RED)
    game.players[2].ally = 3
    game.players[3].ally = 2
    # Since 2/3 taken up, best ally is 1 for 3 points
    assert game.best_ally(0, [1, 0, 0, 0, 0], [0, 0, 0, 0, 0]) == (3, 1)


def test_best_available_bet(game):
    first = [0.4, 0.5, 0.2, 0.1, 0]
    second = [0.4, 0.5, 0.2, 0.1, 0]
    assert game.best_available_bet(first, second) == (3, 1)
    game.available_bets[1] = [2, 2]
    assert game.best_available_bet(first, second) == (pytest.approx(2.2), 0)


def test_best_booster_bet():
    g = Game(
        2,
        setup={
            RED: 1,
            PURPLE: 1,
            YELLOW: 1,
            BLUE: 2,
            GREEN: 3,
            WHITE: 15,
            BLACK: 16,
        },
    )
    g.dice = [RED, YELLOW, BLUE, GREEN, PURPLE]
    booster_val, booster_location, boost_type = g.best_booster_bet(
        0,
        [0.07582305, 0.38148148, 0.1409465, 0.24403292, 0.15771605],
        [0.11563786, 0.22088477, 0.18292181, 0.21944444, 0.26111111],
        np.array(
            [
                0.0,
                9.33333333e-01,
                1.39,
                1.92,
                1.12,
                0.68,
                0.17,
                0.043,
                0.0179,
                0.003,
                0,
                0,
                0.0,
                0.0,
                0.0,
                0.0,
            ]
        ),
    )
    assert booster_location == 3
    assert booster_val == pytest.approx(2.1141975)
    assert boost_type == BOOST_NEG


def test_best_booster_bet_2():
    g = Game(
        2,
        setup={
            PURPLE: 10,
            GREEN: 10,
            BLUE: 10,
            RED: 10,
            BLACK: 12,
            WHITE: 13,
            YELLOW: 14,
        },
    )
    g.dice = [RED, YELLOW, BLUE, GREEN, PURPLE]
    first, second, landings = win_probabilities(tuple(g.dice), g.board.to_tuple())
    booster_val, booster_location, boost_type = g.best_booster_bet(
        0, first, second, landings
    )
    assert booster_location == 10
    assert boost_type == BOOST_NEG
    assert booster_val == pytest.approx(1.34701646)


def test_points():
    g = Game(
        2, setup={RED: 1, YELLOW: 1, GREEN: 1, BLUE: 1, PURPLE: 1, WHITE: 16, BLACK: 16}
    )
    g.parse_move(0, "boost 4 -")
    g.parse_move(1, "boost 2 -")
    g.parse_move(0, "bet yellow")
    g.parse_move(1, "bet yellow")
    g.parse_move(1, "ally 0")
    g.parse_move(0, "roll blue 1")  # +1 points player 0, +2 points player 1
    g.parse_move(1, "roll red 1")  # +4 points player 1
    g.parse_move(0, "roll yellow 1")  # +1 points player 0, +4 points player 1
    g.parse_move(1, "roll purple 1")  # +3 points player 1
    g.parse_move(0, "roll green 1")  # +1 points player0, +2 points player 1
    # Player 0 has: 3 points + 5 from winning + 3 from ally + 3 from rolling
    assert g.players[0].points == 3 + 5 + 3 + 3
    # Player 1 has: 3 points + 3 from winning + 5 from ally + 13 from boost + 2 from rolling
    assert g.players[1].points == 3 + 3 + 5 + 13 + 2
