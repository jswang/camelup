import random
import copy
import itertools
import tqdm
from collections import Counter

RED = 'R'
YELLOW = 'Y'
BLUE = 'B'
GREEN = 'G'
PURPLE = 'P'
WHITE = 'W'
BLACK = 'X'
GREY = 'E'

N_TILES = 16
class Player:
    def __init__(self) -> None:
        self.points = 3
        self.winner_bet = None
        self.loser_bet = None
        self.reset_round()

    def reset_round(self):
        self.ally = None
        self.booster = None
        self.round_bets = []

class Board:
    def __init__(self, setup : dict=None):
        # List of camels on each tile
        self.tiles = [[] for _ in range(N_TILES)]
        # Tile number of each camel
        self.camels = Counter()
        # Init board with a setup
        if setup:
            for color, tile in setup.items():
                self.tiles[tile].append(color)
                self.camels[color] = tile
        # bets on who will win overall
        self.winner_bets = []
        # bets on who will lose overall
        self.loser_bets = []
        self.reset_round()

    def get_winners(self, tiles) -> list:
        """Returns ordering of camels on board from winner to loser, ignore WHITE and BLACK"""
        res = []
        for i in range(len(tiles)-1, -1, -1):
            res.extend([c for c in reversed(tiles[i]) if c not in [WHITE, BLACK]])
        return res

    def reset_round(self):
        """Reset available bets"""
        self.round_bets = {RED: [2, 2, 3, 5], YELLOW: [2, 2, 3, 5], BLUE: [2, 2, 3, 5], GREEN: [2, 2, 3, 5], PURPLE: [2, 2, 3, 5]}

    def simulate_round(self, round : list):
        """
        Simulate moving the camels according to rounds, which is a list of 5 (color, spaces)
        """
        tiles = copy.deepcopy(self.tiles)
        camels = copy.deepcopy(self.camels)
        game_over = False
        for (color, spaces) in round:
            assert len(tiles) == N_TILES
            # If crazy camel rolled, and only one has toppers, move the one with toppers
            if color in [BLACK, WHITE]:
                # who has toppers?
                black_top = len(tiles[camels[BLACK]]) - 1 > tiles[camels[BLACK]].index(BLACK)
                white_top = len(tiles[camels[WHITE]]) - 1 > tiles[camels[WHITE]].index(WHITE)
                if black_top and not white_top:
                    color = BLACK
                if white_top and not black_top:
                    color = WHITE
                spaces = -spaces
            # Move the camel
            my_tile = camels[color]
            my_stack_index = tiles[my_tile].index(color)
            my_stack = tiles[my_tile][my_stack_index:]
            # remove my_stack from the original tile
            tiles[my_tile] = tiles[my_tile][0:my_stack_index]
            # Put my_stack onto new tile
            # TODO: account for -1/+1
            # TODO: wraparound and game winning
            if my_tile + spaces >= N_TILES:
                game_over = True
                tiles.extend([[]*(my_tile + spaces - N_TILES + 1)])

            tiles[my_tile + spaces].extend(my_stack)
            for c in my_stack:
                camels[c] += spaces
            # End round right away if someone won
            if game_over:
                return tiles, camels
        return tiles, camels

    def __repr__(self):
        return f"{self.tiles}"

class Game:
    def __init__(self, n_players : int, setup=None) -> None:
        self.players = [Player() for _ in range(n_players)]
        self.board = Board(setup)
        self.game_over = False
        self.dice_left = 5
        # Intialize possible rounds due to dice rolls
        self.rounds = []
        for color in itertools.permutations([RED, YELLOW, BLUE, GREEN, PURPLE, GREY], 5):
            for rolls in itertools.product(range(1, 4), repeat=5):
                if GREY in color:
                    res1 = []
                    res2 = []
                    for i in range(5):
                        if color[i] == GREY:
                            res1.append((BLACK, rolls[i]))
                            res2.append((WHITE, rolls[i]))
                        else:
                            res1.append((color[i], rolls[i]))
                            res2.append((color[i], rolls[i]))
                    self.rounds.extend([res1, res2])
                else:
                    self.rounds.append([(color[i], rolls[i]) for i in range(5)])

    def __repr__(self) -> str:
        """Handy dandy game representation, e.g.:
        Y G
        RPB          WX
        ----------------
        0123456789111111
                  012345
        """
        tiles = self.board.tiles
        # max height of a stack
        max_stack = max([len(t) for t in tiles])
        res = ""
        for i in range(max_stack-1, -1, -1):
            res += "\n"
            for j in range(N_TILES):
                if len(tiles[j]) > i:
                    res += f"{tiles[j][i]}"
                else:
                    res += " "
        res += "\n"
        res += "-" * N_TILES + "\n" + "0123456789111111" + "\n" + "          012345"
        return res

    def reset_round(self):
        self.dice_left = 5
        for p in self.players:
            p.reset_round()
        self.board.reset_round()

    def optimal_move(self):
        """Get the optimal move for a player
            Moves available:
            1. Roll dice (+1)
            2. Choose available bet
            3. Choose ally
            4. Bet on overall winner
            5. Bet on overall loser
            6. Place tile
            """
        first_place, second_place = self.win_probabilities()


    def win_probabilities(self):
        """
        Calculate the probability of each camel winning
        """
        first_place = {RED: 0, YELLOW: 0, BLUE: 0, GREEN: 0, PURPLE: 0}
        second_place = {RED: 0, YELLOW: 0, BLUE: 0, GREEN: 0, PURPLE: 0}

        for round in tqdm.tqdm(self.rounds):
            tiles, _ = self.board.simulate_round(round)
            winners = self.board.get_winners(tiles)
            first_place[winners[0]] += 1
            second_place[winners[1]] += 1

        # Calculate probability of each camel winning
        total = sum(first_place.values())
        first_place = {k: v/total for k, v in first_place.items()}
        second_place = {k: v/total for k, v in second_place.items()}
        return first_place, second_place


def main():
    print("Camel up")

    g = Game(4, setup={RED: 0, YELLOW: 0, BLUE: 2, GREEN: 2, PURPLE: 1, WHITE: 13, BLACK: 14})
    print(g)
    print(g.board.get_winners(g.board.tiles))
    g.win_probabilities()

main()