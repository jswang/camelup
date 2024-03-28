import numpy as np
from main import *

def test_booster_locations():
    # Booster locations
    b = Board(setup={BLACK: 0, RED: 2, YELLOW: 2, PURPLE: 4, WHITE: 10, BLUE: 11, GREEN: 11, "pos_boosters": np.array([15]), "neg_boosters":np.array([5])})
    assert b.available_booster_locations() == [1, 3, 7, 8, 9, 12, 13]

def test_winning_with_booster():
    # Winning with a booster
    b = Board(setup={BLACK: 0, RED: 0, YELLOW: 0, PURPLE: 1, WHITE: 2, BLUE: 2, GREEN: 2, "pos_boosters": np.array([15])})
    winners, tiles, landings = b.simulate_round([(BLACK, 1)], {})

    assert np.all(tiles == np.array([[-1, -1, -1, -1, -1, -1, -1],
       [ 4, -1, -1, -1, -1, -1, -1],
       [ 5,  2,  3, -1, -1, -1, -1],
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
       [ 6,  0,  1, -1, -1, -1, -1]]))
    assert np.all(winners == np.array([1, 0, 3, 2, 4]))
    assert np.all(landings == np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3]))

def test_hopping_under():
    # Hopping under
    b = Board(setup={YELLOW: 0, RED: 0, PURPLE: 0, WHITE: 2, BLUE: 2, GREEN: 2, BLACK: 5, "pos_boosters": np.array([15]), "neg_boosters": np.array([1])})
    winners, tiles, landings = b.simulate_round([(RED, 1)], {})
    assert np.all(tiles == np.array([[0, 4, 1, -1, -1, -1, -1],
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
       [-1, -1, -1, -1, -1, -1, -1]]))
    assert np.all(winners == np.array([3, 2, 1, 4, 0]))
    assert np.all(landings == np.array([0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0]))


def test_overall_probability():
    # Overall probabilities
    g = Game(4, setup={RED: 0, YELLOW: 0, BLUE: 2, GREEN: 2, PURPLE: 1, WHITE: 13, BLACK: 14})
    first, second, landings = g.win_probabilities(g.board)
    first = first[:5]
    second = second[:5]
    assert np.all(np.isclose(first, [0.07398054620276842, 0.25419316623020327, 0.13835889761815687, 0.39801409153261, 0.1354532984162614]))
    assert np.all(np.isclose(second, [0.10978925052999126, 0.15208567153011598, 0.29945753834642724, 0.2764029180695847, 0.16226462152388077]))

def test_optimal_move():
    # Optimal move
    g = Game(4, setup={RED: 0, YELLOW: 0, BLUE: 2, GREEN: 2, PURPLE: 1, WHITE: 13, BLACK: 14})
    g.optimal_move(g.players[0])

def test_parse_move():
    # Parse move
    g = Game(4, setup={RED: 0, YELLOW: 0, BLUE: 2, GREEN: 2, PURPLE: 1, WHITE: 13, BLACK: 14})
    g.parse_move(0, ["bet", "yellow", "5"])
    assert g.players[0].bets == [(YELLOW, 5)]
    assert g.available_bets[YELLOW] == [2, 2, 3]
    g.parse_move(0, ["ally", "1"])
    assert g.players[0].ally == 1
    g.parse_move(0, ["boost", "2", "1"])
    assert g.players[0].boost == 2 # technically this is an illegal boost
    assert np.all(g.board.boosters == np.array([0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))
    g.parse_move(0, ["roll", "red", "2"])
    assert g.players[0].points == 6
    assert len(g.dice) == N_DICE - 1
    g.parse_move(0, ["roll", "yellow", "2"])
    g.parse_move(0, ["roll", "blue", "2"])
    g.parse_move(0, ["roll", "green", "2"])
    g.parse_move(0, ["roll", "purple", "2"])
    # +2 from boost, +5 from roll, +1 from bet
    assert g.players[0].points == 11


test_parse_move()
test_booster_locations()
test_winning_with_booster()
test_hopping_under()
test_overall_probability()
test_optimal_move()
print("Passed all tests")
