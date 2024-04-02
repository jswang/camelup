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
        RED: 0,
        PURPLE: 0,
        YELLOW: 0,
        BLUE: 1,
        GREEN: 2,
        WHITE: 14,
        BLACK: 15,
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
    round_starting_player = 0
    while not g.game_over:
        # Move the starter round by round
        if not g.turn_taken:
            curr_player = round_starting_player
            round_starting_player = (round_starting_player + 1) % args.n_players
            print(f"New round, starting player: {curr_player}")
        s = "your" if curr_player == args.id else f"Player {curr_player}"
        # Advance to next player if this player made a move
        if g.parse_move(curr_player, move=input(f"Enter {s} move: ")):
            # write to json
            with open(save_file, "w") as f:
                json.dump(g.to_json(), f)
            curr_player = (curr_player + 1) % args.n_players


if __name__ == "__main__":
    main()
