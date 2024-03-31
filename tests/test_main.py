import numpy as np
from camelup.constants import *
from camelup.game import Game, get_rounds, bet_value
from camelup.board import get_winners
import pytest


@pytest.fixture
def game():
    return Game(4)


def test_gameplay(game):
    options = ["optimal", "bet", "ally", "boost", "roll", "winner", "loser", "print"]
    actual_moves = 1000
    while actual_moves < 1000:
        # Advance to next player if this player made a move
        if game.parse_move(curr_player, move):
            curr_player = (curr_player + 1) % game.n_players
