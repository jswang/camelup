import numpy as np
from camelup.constants import *
from camelup.board import Board, simulate_round
from camelup.player import Player


def test_init():
    setup = {
        YELLOW: 0,
        RED: 0,
        PURPLE: 0,
        WHITE: 2,
        BLUE: 2,
        GREEN: 2,
        BLACK: 5,
        BOOST_POS: [10, 11, 13],
        BOOST_NEG: [1, 2, 3],
    }
    b = Board(setup=setup)
    x = b.to_dict()
    for c in CAMELS:
        assert x[c] == setup[c]
    assert x[BOOST_POS] == setup[BOOST_POS]
    assert x[BOOST_NEG] == setup[BOOST_NEG]


def test_equality_players():
    p0 = Player(0)
    p1 = Player(0)
    assert p0 == p1


def test_equal_board():
    # Equal board
    b = Board(
        setup={
            BLACK: 0,
            RED: 1,
            YELLOW: 1,
            PURPLE: 2,
            WHITE: 2,
            BLUE: 0,
            GREEN: 0,
            BOOST_POS: [1],
            BOOST_NEG: [7],
        }
    )
    b2 = Board(
        setup={
            BLACK: 0,
            RED: 1,
            YELLOW: 1,
            PURPLE: 2,
            WHITE: 2,
            BLUE: 0,
            GREEN: 0,
            BOOST_POS: [1],
            BOOST_NEG: [7],
        }
    )
    assert b == b2


def test_booster_locations():
    # Booster locations
    b = Board(
        setup={
            BLACK: 0,
            RED: 2,
            YELLOW: 2,
            PURPLE: 4,
            WHITE: 10,
            BLUE: 11,
            GREEN: 11,
            BOOST_POS: [15],
            BOOST_NEG: [5],
        }
    )
    assert b.available_booster_locations() == [1, 3, 7, 8, 9, 12, 13]


def test_winning_with_booster():
    # Winning with a booster
    b = Board(
        setup={
            BLACK: 0,
            RED: 0,
            YELLOW: 0,
            PURPLE: 1,
            WHITE: 2,
            BLUE: 2,
            GREEN: 2,
            BOOST_POS: [15],
        }
    )
    winners, tiles, landings, _ = simulate_round(b.tiles, [(BLACK, 1)])

    assert tiles == {
        0: [],
        1: [4],
        2: [5, 2, 3],
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
        13: [],
        14: [],
        15: [8],
        16: [6, 0, 1],
    }

    assert winners == [1, 0, 3, 2, 4]
    assert landings == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3]


# TODO test all edge cases here
def test_hopping_under():
    # Hopping under
    b = Board(
        setup={
            YELLOW: 0,
            RED: 0,
            PURPLE: 0,
            WHITE: 2,
            BLUE: 2,
            GREEN: 2,
            BLACK: 5,
            BOOST_POS: [15],
            BOOST_NEG: [1],
        }
    )
    winners, tiles, landings, _ = simulate_round(b.tiles, [(RED, 1)])
    assert tiles == {
        0: [0, 4, 1],
        1: [9],
        2: [5, 2, 3],
        3: [],
        4: [],
        5: [6],
        6: [],
        7: [],
        8: [],
        9: [],
        10: [],
        11: [],
        12: [],
        13: [],
        14: [],
        15: [8],
    }
    assert winners == [3, 2, 1, 4, 0]
    assert landings == [0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
