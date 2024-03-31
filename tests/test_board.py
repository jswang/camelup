import numpy as np
from camelup.constants import *
from camelup.board import Board, Player


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
            "pos_boosters": np.array([1]),
            "neg_boosters": np.array([7]),
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
            "pos_boosters": np.array([1]),
            "neg_boosters": np.array([7]),
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
            "pos_boosters": np.array([15]),
            "neg_boosters": np.array([5]),
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
            "pos_boosters": np.array([15]),
        }
    )
    winners, tiles, landings, _ = b.simulate_round([(BLACK, 1)], {})

    assert np.all(
        tiles
        == np.array(
            [
                [-1, -1, -1, -1, -1, -1, -1],
                [4, -1, -1, -1, -1, -1, -1],
                [5, 2, 3, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [6, 0, 1, -1, -1, -1, -1],
            ]
        )
    )
    assert np.all(winners == np.array([1, 0, 3, 2, 4]))
    assert np.all(
        landings == np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3])
    )


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
            "pos_boosters": np.array([15]),
            "neg_boosters": np.array([1]),
        }
    )
    winners, tiles, landings, _ = b.simulate_round([(RED, 1)], {})
    assert np.all(
        tiles
        == np.array(
            [
                [0, 4, 1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [5, 2, 3, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [6, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1],
            ]
        )
    )
    assert np.all(winners == np.array([3, 2, 1, 4, 0]))
    assert np.all(
        landings == np.array([0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    )
