from camelup.constants import *
from camelup.game import Game
import argparse
import json


def main():
    parser = argparse.ArgumentParser(description="Camel Up Game")

    parser.add_argument(
        "--id",
        type=int,
        help="Your player id relative to Player 0 (first one to go)",
        default=0,
    )
    parser.add_argument("--n-players", type=int, help="Number of players", default=2)
    parser.add_argument(
        "--save-file", type=str, help="Old game setup to use", default=None
    )
    parser.add_argument(
        "--setup",
        type=str,
        help="File to load setup from",
        default="default_setup.json",
    )
    args = parser.parse_args()

    print("Camel Up!!!\n")

    # If specified, load game from save file
    if args.save_file:
        save_file = args.save_file
        with open(save_file, "r") as f:
            data = json.load(f)
            g = Game.from_json(data)
    else:
        save_file = "current_game.json"
        with open(args.setup, "r") as f:
            data = json.load(f)
        print(f"data: {data}")
        g = Game(args.n_players, data)
    round_starting_player = 0
    curr_player = round_starting_player
    while not g.game_over:
        # Move the starter round by round
        if g.round_concluded:
            round_starting_player = (round_starting_player + 1) % args.n_players
            curr_player = round_starting_player
            g.round_concluded = False
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


"""
add an undo?

make tile entry match the board

seems like this should be - not +:
3.87: Boost location 10 +
3.31: Bet yellow
1.00: Roll dice
0.00: Ally Player 0
Enter your move: print

Board:
{0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: ['purple', 'green', 'blue', 'red'], 10: [], 11: ['black'], 12: ['white'], 13: ['yellow'], 14: [], 15: []}

Players: [Player 0: (points: 46, ally: None, boost: None, bets: []), Player 1: (points: 42, ally: None, boost: None, bets: [])]
Dice left: red, yellow, blue, green, purple, grey,
Available bets: red: 5, yellow: 5, blue: 5, green: 5, purple: 5,
Winner bets: [0]
Loser bets: []
"""
