import numpy as np
from camelup.constants import *
from camelup.board import Board, simulate_round
from camelup.player import Player


def test_init():
    setup = {
        YELLOW: 1,
        RED: 1,
        PURPLE: 1,
        WHITE: 3,
        BLUE: 3,
        GREEN: 3,
        BLACK: 6,
        BOOST_POS: [11, 12, 14],
        BOOST_NEG: [2, 3, 4],
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
            BLACK: 1,
            RED: 2,
            YELLOW: 2,
            PURPLE: 3,
            WHITE: 3,
            BLUE: 1,
            GREEN: 1,
            BOOST_POS: [2],
            BOOST_NEG: [8],
        }
    )
    b2 = Board(
        setup={
            BLACK: 1,
            RED: 2,
            YELLOW: 2,
            PURPLE: 3,
            WHITE: 3,
            BLUE: 1,
            GREEN: 1,
            BOOST_POS: [2],
            BOOST_NEG: [8],
        }
    )
    assert b == b2


def test_booster_locations():
    # Booster locations
    b = Board(
        setup={
            BLACK: 1,
            RED: 3,
            YELLOW: 3,
            PURPLE: 5,
            WHITE: 11,
            BLUE: 12,
            GREEN: 12,
            BOOST_POS: [16],
            BOOST_NEG: [6],
        }
    )
    assert b.available_booster_locations() == [1, 3, 7, 8, 9, 12, 13]
