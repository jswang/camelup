import json
from camelup.game import Game
from camelup.constants import *


def test_json():
    g = Game(
        4, setup={YELLOW: 0, PURPLE: 0, GREEN: 0, RED: 1, BLUE: 2, BLACK: 13, WHITE: 13}
    )
    g.winner_bets = [0, 2]
    g.loser_bets = [1, 3]
    g.available_bets[RED] = []

    with open("test.json", "w") as f:
        json.dump(g.to_json(), f)
    with open("test.json", "r") as f:
        data = json.load(f)
        g2 = Game.from_json(data)
        assert g == g2
