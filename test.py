import numpy as np
from main import *

def test_booster_locations():
    # Booster locations
    b = Board(setup={BLACK: 0, RED: 2, YELLOW: 2, PURPLE: 4, WHITE: 10, BLUE: 11, GREEN: 11, "boosters": np.array([0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])})
    assert b.available_booster_locations() == [1, 3, 7, 8, 9, 12, 13]

def test_winning_with_booster():
    # Winning with a booster
    b = Board(setup={BLACK: 0, RED: 0, YELLOW: 0, PURPLE: 1, WHITE: 2, BLUE: 2, GREEN: 2, "boosters": np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])})
    winners, tiles, landings = b.simulate_round([(BLACK, 1)], {}, {})
    assert np.all(tiles == np.array([[0, 0, 0, 0, 0, 0, 0],
       [5, 0, 0, 0, 0, 0, 0],
       [6, 3, 4, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [7, 1, 2, 0, 0, 0, 0]]))
    assert np.all(winners == np.array([2, 1, 4, 3, 5]))
    assert np.all(landings == np.array([0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,3]))

def test_hopping_under():
    # Hopping under
    b = Board(setup={YELLOW: 0, RED: 0, PURPLE: 0, WHITE: 2, BLUE: 2, GREEN: 2, BLACK: 5, "boosters": np.array([0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])})
    winners, tiles, landings = b.simulate_round([(RED, 1)], {}, {})
    assert np.all(tiles == np.array([[1, 5, 2, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [6, 3, 4, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0]]))
    assert np.all(winners == np.array([4, 3, 2, 5, 1]))
    assert np.all(landings == np.array([0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0]))

def test_overall_probability():
    # Overall probabilities
    g = Game(4, setup={RED: 0, YELLOW: 0, BLUE: 2, GREEN: 2, PURPLE: 1, WHITE: 13, BLACK: 14})
    first, second, landings = g.win_probabilities(g.board)
    first = first[1:6]
    second = second[1:6]
    assert np.all(np.isclose(first, [0.07398054620276842, 0.25419316623020327, 0.13835889761815687, 0.39801409153261, 0.1354532984162614]))
    assert np.all(np.isclose(second, [0.10978925052999126, 0.15208567153011598, 0.29945753834642724, 0.2764029180695847, 0.16226462152388077]))

def test_optimal_move():
    # Optimal move
    g = Game(4, setup={RED: 0, YELLOW: 0, BLUE: 2, GREEN: 2, PURPLE: 1, WHITE: 13, BLACK: 14})
    g.optimal_move(g.players[0])


test_booster_locations()
test_hopping_under()
test_overall_probability()
test_winning_with_booster()
test_optimal_move()
print("Passed all tests")