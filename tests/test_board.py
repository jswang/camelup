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
