from camelup.constants import *
from camelup.game import Game
import argparse
import json


def main():
    parser = argparse.ArgumentParser(description="Camel Up Game")

    parser.add_argument("--id", type=int, help="Player id", default=0)
    parser.add_argument("--n-players", type=int, help="Number of players", default=2)
    parser.add_argument(
        "--save-file", type=str, help="Old game setup to use", default=None
    )
    args = parser.parse_args()

    print("Camel Up!!!\n")
    # TODO make inputting setup easier
    setup = {
        YELLOW: 0,
        PURPLE: 0,
        GREEN: 0,
        RED: 1,
        BLUE: 2,
        BLACK: 13,
        WHITE: 13,
        "pos_boosters": [],
        "neg_boosters": [],
    }

    # If specified, load game from save file
    if args.save_file:
        save_file = args.save_file
        with open(save_file, "r") as f:
            data = json.load(f)
            g = Game.from_json(data)
    else:
        save_file = "current_game.json"
        g = Game(args.n_players, setup)

    while not g.game_over:
        if curr_player == args.id:
            s = "your"
        else:
            s = f"Player {curr_player}"
        # Advance to next player if this player made a move
        if g.parse_move(curr_player, move=input(f"Enter {s} move: ")):
            # write to json
            with open(save_file, "w") as f:
                json.dump(g.to_json(), f)
            curr_player = (curr_player + 1) % args.n_players


if __name__ == "__main__":
    main()
    # TODO: fix setup input, store state locally to restore

"""
add caching during optimal move check as well
add boost function

red: tile: 0, stack: 0
purple: tile: 0, stack: 1
yellow: tile: 0, stack: 2
blue: tile: 1, stack: 0
green: tile: 2, stack: 0
white: tile: 14, stack: 0
black: tile: 15, stack: 0
positive boosters: []
negative boosters: []

Players: [Player 0: (points: 3, ally: None, boost: None, bets: []), Player 1: (points: 3, ally: None, boost: None, bets: [])]
Dice left: red, yellow, blue, green, purple, grey,
Available bets: red: 5, yellow: 5, blue: 5, green: 5, purple: 5,
Winner bets: []
Loser bets: []

.95: Boost location 3, 1
1.71: Bet yellow
1.00: Roll dice
0.00: Ally Player 0

seems like should be boost -1 not boost +2
"""
