import random
from collections import Counter

RED = 'R'
YELLOW = 'Y'
BLUE = 'B'
GREEN = 'G'
PURPLE = 'P'
WHITE = 'W'
BLACK = 'X'

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
    def __init__(self, setup=None):
        # List of camels on each tile
        self.tiles = [[] for _ in range(16)]
        # Tile number of each camel
        self.camels = Counter()
        # If starting with a setup:
        if setup:
            for color, tile in setup.items():
                self.tiles[tile].append(color)
                self.camels[color] = tile

        self.winner_bets = []
        self.loser_bets = []
        self.reset_round()

    def get_winners(self) -> list:
        first = None
        second = None
        for i in range(15, -1, -1):
            if self.tiles[i]:
                for j in range(len(self.tiles[i])-1, -1, -1):
                    if self.tiles[i][j] not in [WHITE, BLACK]:
                        if not first:
                            first = self.tiles[i][j]
                        else:
                            second = self.tiles[i][j]
                            return [first, second]

    def reset_round(self):
        self.round_bets = {RED: [2, 2, 3, 5], YELLOW: [2, 2, 3, 5], BLUE: [2, 2, 3, 5], GREEN: [2, 2, 3, 5], PURPLE: [2, 2, 3, 5]}

    def __repr__(self):
        return f"{self.tiles}"

class Game:
    def __init__(self, n_players, setup=None) -> None:
        self.players = [Player() for _ in range(4)]
        self.board = Board(setup)
        self.game_over = False
        self.dice_left = 5

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
            for j in range(16):
                if len(tiles[j]) > i:
                    res += f"{tiles[j][i]}"
                else:
                    res += " "
        res += "\n"
        res += "-" * 16 + "\n" + "0123456789111111" + "\n" + "          012345"
        return res

    def play(self):
        while not self.game_over:
            self.run_round()
            self.reset_round()

    def reset_round(self):
        self.dice_left = 5
        for p in self.players:
            p.reset_round()
        self.board.reset_round()


    def move(self, moves):
        """
        Moves is a list of 5 (color, spaces)
        Move the camels accordingly
        """
        for (color, spaces) in moves:
            # If crazy camel rolled, and only one has toppers, move the one with toppers
            if color in [BLACK, WHITE]:
                # who has toppers?
                black_top = self.tiles[self.camels[BLACK]].len() - 1 > self.tiles[self.camels[BLACK]].index(BLACK)
                white_top = self.tiles[self.camels[WHITE]].len() - 1 > self.tiles[self.camels[WHITE]].index(WHITE)
                if black_top and not white_top:
                    color = BLACK
                if white_top and not black_top:
                    color = WHITE
                spaces = -spaces
            # Move the camel
            my_tile = self.camels[color]
            my_stack_index = self.tiles[my_tile].index(color)
            my_stack = self.tiles[my_stack_index:]
            self.tiles[my_tile] = self.tiles[my_tile][0:my_stack_index]
            self.tiles[my_tile + spaces].extend(my_stack)
            for c in my_stack:
                self.camels[c] += spaces



    def do_optimal_move(self, player):
        """ Get the optimal move for a player
            Moves available:
            1. Roll dice (+1)
            2. Choose available bet
            3. Choose ally
            4. Bet on overall winner
            5. Bet on overall loser
            6. Place tile
        """
        pass



    def run_round(self):
        while self.dice_left > 0 :
            for p in self.players:
                # do optimal move
                self.do_optimal_move(p)
                # check if game is over TOOD
                if self.game_over:
                    return True


class Camel:
    def __init__(self, color, dir):
        self.color = color
        self.dir = dir
        self.position = None
        self.stack_position = 0
        self.move()

    def __eq__(self, other: object) -> bool:
        self.color == other.color

    def move(self):
        """ Move this camel and every camel on top of it"""
        spaces = random.randint(1, 3)

        if self.dir == 'clockwise':
            self.position += spaces
        else:
            self.position = (self.position - spaces) % 16

        self.stack_position = board.tiles[self.position]
        board.tiles[self.position] += self

    def __str__(self):
        return "Camel {} at position {}".format(self.color, self.position)



def main():
    print("Camel up")

    g = Game(4, setup={RED: 0, YELLOW: 0, BLUE: 2, GREEN: 2, PURPLE: 1, WHITE: 13, BLACK: 14})
    print(g)
    print(g.board.get_winners())
    g.play()

main()