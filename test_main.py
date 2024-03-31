import numpy as np

from camelup.constants import *
from camelup.game import Game
from tqdm import tqdm


def main():
    np.random.seed(0)
    game = Game(
        4, setup={YELLOW: 0, PURPLE: 0, GREEN: 0, RED: 1, BLUE: 2, BLACK: 13, WHITE: 13}
    )
    options = ["roll", "optimal", "bet", "ally", "boost", "winner", "loser", "print"]
    moves = np.random.choice(
        options, 1000, p=[0.2, 0.125, 0.125, 0.125, 0.125, 0.1, 0.1, 0.1]
    )
    curr_player = 0
    for i, move in tqdm(enumerate(moves)):
        if move == "bet":
            move += f" {color_to_str(np.random.choice(WIN_CAMELS))}"
        elif move == "ally":
            move += f" {np.random.randint(0, len(game.players))}"
        elif move == "boost":
            move += f" {np.random.randint(0, N_TILES)} {np.random.choice([-1, 1])}"
        elif move == "roll":
            d = np.random.choice(game.dice)
            if d == GREY:
                d = np.random.choice([BLACK, WHITE])
            move += f" {color_to_str(d)} {np.random.randint(1, 4)}"
        elif move == "winner":
            move += f" {np.random.choice(WIN_CAMELS)}"
        elif move == "loser":
            move += f" {np.random.choice(WIN_CAMELS)}"
        print(f"\ni: {i}, move: {move}")
        # Advance to next player if this player made a move
        if game.parse_move(curr_player, move):
            curr_player = (curr_player + 1) % len(game.players)
        if game.game_over:
            break


if __name__ == "__main__":
    main()
