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
why didn't it suggest -1 on 13?
Enter Player 1 move: optimal
Calculating optimal move
2.00: Ally Player 0
1.72: Bet purple
1.54: Boost location 13 +
1.00: Roll dice
Enter Player 1 move: bet purple
Player 1 bet on purple with value 3
Enter your move: optimal
Calculating optimal move
1.38: Bet blue
1.00: Roll dice
1.00: Ally Player 1
0.56: Boost location 13 -
Enter your move: bet blue
Player 0 bet on blue with value 5
Enter Player 1 move: print

Board:
{1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: ['yellow'], 11: [], 12: ['green', 'red', 'blue'], 13: [], 14: ['black'], 15: ['purple', 'white'], 16: []}

Players: [Player 0: (points: 52, ally: None, boost: None, bets: [(4, 5), (2, 5)]), Player 1: (points: 36, ally: None, boost: None, bets: [(4, 3)])]
Dice left: red, yellow, blue, green, purple, grey,
Available bets: red: 5, yellow: 5, blue: 3, green: 5, purple: 2,
Winner bets: [1, 0]
Loser bets: [1]
"""
