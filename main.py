from camelup.constants import *
from camelup.game import Game
import argparse


def main():
    parser = argparse.ArgumentParser(description="Camel Up Game")

    parser.add_argument(
        "--setup",
        type=str,
        help="Setup dictionary for the game",
        default={YELLOW: 0, PURPLE: 0, GREEN: 0, RED: 1, BLUE: 2, BLACK: 13, WHITE: 13},
    )
    parser.add_argument("--id", type=int, help="Player id", default=0)
    parser.add_argument("--n-players", type=int, help="Number of players", default=2)
    args = parser.parse_args()

    print("Camel Up!!!\n")
    # Set up game
    g = Game(args.n_players, setup=args.setup)
    print(g)
    curr_player = 0
    while not g.game_over:
        if curr_player == args.id:
            s = "your"
        else:
            s = f"Player {curr_player}"
        # Advance to next player if this player made a move
        if g.parse_move(curr_player, move=input(f"Enter {s} move: ")):
            curr_player = (curr_player + 1) % args.n_players
    # TODO give overall winner


if __name__ == "__main__":
    main()
    # TODO: fix setup input, store state locally to restore
    # BUG: didn't get correct number of point for landing on the booster
