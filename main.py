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
    # TODO make this better
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

    curr_player = 0
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
    # TODO give overall winner


if __name__ == "__main__":
    main()
    # TODO: fix setup input, store state locally to restore
    # BUG: didn't get correct number of point for landing on the booster
