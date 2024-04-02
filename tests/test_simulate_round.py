from camelup.board import Board, simulate_round
from camelup.constants import *


def test_moving_black_camel():
    """Black has stack, white rolled"""
    b = Board(
        setup={BLACK: 13, RED: 13, WHITE: 12, BLUE: 11, GREEN: 2, YELLOW: 2, PURPLE: 2}
    )
    _, tiles, _, _ = simulate_round(b.tiles, [(WHITE, 2)])
    assert tiles[11] == [BLUE, BLACK, RED]
    assert tiles[12] == [WHITE]
    assert tiles[10] == []


def test_moving_white_camel():
    """White has stack, black moved"""
    b = Board(
        setup={WHITE: 13, RED: 13, BLACK: 12, BLUE: 11, GREEN: 2, YELLOW: 2, PURPLE: 2}
    )
    _, tiles, _, _ = simulate_round(b.tiles, [(BLACK, 2)])
    assert tiles[11] == [BLUE, WHITE, RED]
    assert tiles[12] == [BLACK]
    assert tiles[10] == []


def test_moving_black_black():
    """Both have stack, black rolled, black moves"""
    b = Board(
        setup={WHITE: 13, RED: 13, BLACK: 12, BLUE: 12, GREEN: 2, YELLOW: 2, PURPLE: 2}
    )
    _, tiles, _, _ = simulate_round(b.tiles, [(BLACK, 2)])
    assert tiles[10] == [BLACK, BLUE]
    assert tiles[13] == [WHITE, RED]


def test_moving_white_white():
    """Both have stack, white rolled, white moves"""
    b = Board(
        setup={WHITE: 13, RED: 13, BLACK: 12, BLUE: 12, GREEN: 2, YELLOW: 2, PURPLE: 2}
    )
    _, tiles, _, _ = simulate_round(b.tiles, [(WHITE, 2)])
    assert tiles[11] == [WHITE, RED]
    assert tiles[12] == [BLACK, BLUE]
    assert tiles[10] == []


def test_hopping_under():
    # red+purple hopping under purple
    b = Board(
        setup={
            YELLOW: 14,
            RED: 14,
            PURPLE: 14,
            WHITE: 7,
            BLUE: 7,
            GREEN: 7,
            BLACK: 7,
            BOOST_NEG: [15],
        }
    )
    winners, tiles, landings, _ = simulate_round(b.tiles, [(RED, 1)])
    assert tiles[14] == [RED, PURPLE, YELLOW]
    assert tiles[15] == [BOOST_NEG]
    assert tiles[7] == [WHITE, BLUE, GREEN, BLACK]
    assert winners == [YELLOW, PURPLE, RED, GREEN, BLUE]
    assert landings == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2]


def test_winning_boost_neg():
    """
    If you cross finish line, -1 on the other side doesn't matter
    14  15  0
    X      -1
    """
    b = Board(
        setup={
            RED: 14,
            PURPLE: 7,
            YELLOW: 7,
            BLUE: 7,
            GREEN: 7,
            BLACK: 7,
            WHITE: 7,
            BOOST_NEG: [0],
        }
    )
    winners, tiles, landings, game_over = simulate_round(b.tiles, [(RED, 2)])
    assert tiles[16] == [RED]
    assert winners == [RED, GREEN, BLUE, YELLOW, PURPLE]
    assert landings == [0] * N_TILES
    assert game_over


def test_winning_with_boost():
    """
    Cross finish with a positive boost
    14  15  0
    X   +1
    """
    b = Board(
        setup={
            RED: 14,
            PURPLE: 7,
            YELLOW: 7,
            BLUE: 7,
            GREEN: 7,
            BLACK: 7,
            WHITE: 7,
            BOOST_POS: [15],
        }
    )
    winners, tiles, landings, game_over = simulate_round(b.tiles, [(RED, 1)])
    assert tiles[16] == [RED]
    assert winners == [RED, GREEN, BLUE, YELLOW, PURPLE]
    landings == [0] * N_TILES
    assert game_over


def test_winning_backwards():
    """
    Cross 0->15, then back over with +1
    14  15  0
        +1  X
    """
    b = Board(
        setup={
            BLACK: 0,
            RED: 0,
            YELLOW: 0,
            PURPLE: 7,
            BLUE: 7,
            GREEN: 7,
            WHITE: 7,
            BOOST_POS: [15],
        }
    )
    winners, tiles, landings, game_over = simulate_round(b.tiles, [(BLACK, 1)])
    assert game_over
    assert tiles[7] == [PURPLE, BLUE, GREEN, WHITE]
    assert tiles[16] == [BLACK, RED, YELLOW]
    assert winners == [YELLOW, RED, GREEN, BLUE, PURPLE]
    landings == [0] * (N_TILES - 1)
    assert landings[-1] == 3


def test_crazy_camel_negative():
    """If a crazy camel lands on a -1, it should go clockwise"""
    b = Board(
        setup={
            BLUE: 5,
            PURPLE: 10,
            BLACK: 10,
            RED: 10,
            GREEN: 12,
            WHITE: 12,
            YELLOW: 12,
            BOOST_NEG: [11],
        }
    )
    winners, tiles, landings, game_over = simulate_round(b.tiles, [(WHITE, 1)])
    assert not game_over
    assert tiles[10] == [PURPLE, BLACK, RED]
    assert tiles[12] == [WHITE, YELLOW, GREEN]
    assert winners == [GREEN, YELLOW, RED, PURPLE, BLUE]
    assert landings[11] == 2
