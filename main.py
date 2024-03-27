import random
from collections import Counter

class Player:
    def __init__(self) -> None:
        self.points = 3
        self.winner_bet = None
        self.loser_bet = None
        self.booster = None

    def reset_round(self):
        self.booster = None

class Board:
    def __init__(self):
        self.tiles = Counter()

    def visualize(self):
        pass

class Game:
    def __init__(self, n_players) -> None:
        self.players = [Player() for _ in range(4)]
        self.board = Board()
        self.game_over = False
        self.dice_left = 5

    def play(self):
        while not self.game_over:
            self.run_round()
            self.reset_round()

    def reset_round(self):
        self.dice_left = 5
        for p in self.players:
            p.reset_round()

    def get_optimal_move(self, player):
        """ Get the optimal move for a player """
        pass

    def do_move(self, player, action):
        """ Execute the move """
        pass

    def run_round(self):
        while self.dice_left > 0 :
            for p in self.players:
                # get optimal move
                a = self.get_optimal_move(p)
                # do the actual move
                self.do_move(p, a)
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

    g = Game(4)
    g.play()
