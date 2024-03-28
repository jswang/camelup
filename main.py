
import itertools
import tqdm
import numpy as np

RED = 1
YELLOW = 2
BLUE = 3
GREEN = 4
PURPLE = 5
WHITE = 6
BLACK = 7
GREY = 8

COLORS = [RED, YELLOW, BLUE, GREEN, PURPLE, WHITE, BLACK]
N_TILES = 16
N_CAMELS = 7
N_WIN_CAMELS = N_CAMELS - 2

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

def get_num_camels(tile):
    """Return number of camels on a tile"""
    z = np.nonzero(tile)
    if len(z) == 0:
        return 0
    return len(z[0])

def get_camels(tile):
    """Get all camels on this tile"""
    x = get_num_camels(tile)
    return np.copy(tile[0:x])

def get_color(value):
    if value == RED:
        return "R"
    elif value == YELLOW:
        return "Y"
    elif value == BLUE:
        return "B"
    elif value == GREEN:
        return "G"
    elif value == PURPLE:
        return "P"
    elif value == WHITE:
        return "W"
    elif value == BLACK:
        return "X"

class Board:
    def __init__(self, setup : dict=None):
        # List of camels on each tile
        self.tiles = np.zeros((N_TILES, N_CAMELS), dtype=int)
        # Camel tile index
        self.camels = np.zeros(N_CAMELS+1, dtype=int)
        # Booster index, 0 if no booster
        self.boosters = np.zeros(N_TILES, dtype=int)

        # Init board with a setup
        self.parse_setup(setup)

        # bets on who will win overall
        self.winner_bets = []
        # bets on who will lose overall
        self.loser_bets = []
        self.reset_round()

    def parse_setup(self, setup):
        if setup:
            for color, tile in setup.items():
                if color in COLORS:
                    self.tiles[tile][get_num_camels(self.tiles[tile])] = color
                    self.camels[color] = tile
                elif color == "boosters":
                    self.boosters = tile


    def get_winners(self, tiles):
        """Returns ordering of camels on board from winner to loser, ignore WHITE and BLACK"""
        res = tiles.flatten()
        res = res[np.logical_and(np.logical_and(res != WHITE, res != BLACK), res != 0)]
        return np.flip(res)

    def reset_round(self):
        """Reset available bets"""
        self.round_bets = {RED: [2, 2, 3, 5], YELLOW: [2, 2, 3, 5], BLUE: [2, 2, 3, 5], GREEN: [2, 2, 3, 5], PURPLE: [2, 2, 3, 5]}

    def simulate_round(self, round : list, tile_cache: dict, camel_cache : dict):
        """
        Simulate moving the camels according to rounds, which is a list of 5 (color, spaces)
        """
        tiles = np.copy(self.tiles)
        camels = np.copy(self.camels)
        game_over = False
        # For each die roll in round, figure out board state
        for i in range(len(round)):
            index = tuple(round[0:i+1])
            if index in tile_cache:
                tiles = np.copy(tile_cache[index])
                camels = np.copy(camel_cache[index])
            # Otherwise, simulate that round
            else:
                color, spaces = round[i]
                # If crazy camel rolled, and only one has toppers, move the one with toppers
                if color in [BLACK, WHITE]:
                    # who has toppers?
                    black_loc = np.where(tiles[camels[BLACK]] == BLACK)[0][0]
                    black_top = black_loc < N_CAMELS-1 and tiles[camels[BLACK]][black_loc+1] != 0
                    white_loc = np.where(tiles[camels[WHITE]] == WHITE)[0][0]
                    white_top = white_loc < N_CAMELS-1 and tiles[camels[WHITE]][white_loc+1] != 0
                    if black_top and not white_top:
                        color = BLACK
                    if white_top and not black_top:
                        color = WHITE
                    spaces = -spaces

                # Move the camel
                my_tile = camels[color]
                my_stack_index = np.where(tiles[my_tile] == color)[0][0]

                # New space without booster
                new_tile = my_tile + spaces
                on_top = True
                # If you haven't finished game, check boosters
                if new_tile < N_TILES:
                    new_tile %= N_TILES
                    if self.boosters[new_tile] < 0:
                        on_top = False
                    # Intentionally no %, might win
                    new_tile += self.boosters[new_tile]

                # At this point, new_tile might be > N_TILES and it might be negative
                # Did you win?
                if new_tile >= N_TILES:
                    game_over = True
                    tiles = np.vstack((tiles, np.zeros((new_tile - N_TILES + 1, N_CAMELS), dtype=int)))

                # Move em camels, wraparound to not have negative values
                camels[tiles[my_tile][my_stack_index:]] = new_tile
                camels %= len(tiles) # This will preserve numbers > N_TILEs

                # Fix up tiles
                if on_top:
                    new_stack_index = get_num_camels(tiles[new_tile])
                    l = min(len(tiles[new_tile][new_stack_index:]), len(tiles[my_tile][my_stack_index:]))
                    # Move to new tile
                    tiles[new_tile][new_stack_index:new_stack_index+l] = tiles[my_tile][my_stack_index:my_stack_index+l]
                    # Clean up old tile
                    tiles[my_tile][my_stack_index:] = np.zeros(N_CAMELS - my_stack_index, dtype=int)
                else:
                    stack_to_move = get_camels(tiles[my_tile][my_stack_index:])
                    tiles[my_tile][my_stack_index:] = 0
                    stack_to_keep  = get_camels(tiles[new_tile])
                    tiles[new_tile][0:len(stack_to_move)] = stack_to_move
                    tiles[new_tile][len(stack_to_move):len(stack_to_move)+len(stack_to_keep)] = stack_to_keep
                    tiles[new_tile][len(stack_to_move)+len(stack_to_keep):] = 0

                # End round right away if someone won
                if game_over:
                    winners = self.get_winners(tiles)
                    return winners, tiles

                # Update cache if this could be useful in the future
                if i != len(round) - 1:
                    tile_cache[index] = np.copy(tiles)
                    camel_cache[index] = np.copy(camels)

        winners = self.get_winners(tiles)
        return winners, tiles


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
        res = ""
        for j in range(N_CAMELS-1, -1, -1):
            res += "\n"
            for i in range(N_TILES):
                if tiles[i][j] != 0:
                    res += get_color(tiles[i][j])
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
        first_place = np.zeros(N_WIN_CAMELS, dtype=int)
        second_place =  np.zeros(N_WIN_CAMELS, dtype=int)
        tile_cache = {}
        camel_cache = {}
        for round in tqdm.tqdm(self.rounds):
            winners, tiles = self.board.simulate_round(round, tile_cache, camel_cache)
            first_place[winners[0]-1] += 1
            second_place[winners[1]-1] += 1
        # Calculate probability of each camel winning
        total = np.sum(first_place)
        fp = first_place / total
        sp = second_place / total
        return fp, sp


def main():
    print("Camel Up")

    # Winning with a booster
    b = Board(setup={BLACK: 0, RED: 0, YELLOW: 0, PURPLE: 1, WHITE: 2, BLUE: 2, GREEN: 2, "boosters": np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])})
    winners, tiles = b.simulate_round([(BLACK, 1)], {}, {})
    assert np.all(tiles == np.array([[0, 0, 0, 0, 0, 0, 0],
       [5, 0, 0, 0, 0, 0, 0],
       [6, 3, 4, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [7, 1, 2, 0, 0, 0, 0]]))
    assert np.all(winners == np.array([2, 1, 4, 3, 5]))

    # Hopping under
    b = Board(setup={YELLOW: 0, RED: 0, PURPLE: 0, WHITE: 2, BLUE: 2, GREEN: 2, "boosters": np.array([0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])})
    winners, tiles = b.simulate_round([(RED, 1)], {}, {})
    assert np.all(tiles == np.array([[1, 5, 2, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [6, 3, 4, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0]]))
    assert np.all(winners == np.array([4, 3, 2, 5, 1]))

    # Overall probabilities
    g = Game(4, setup={RED: 0, YELLOW: 0, BLUE: 2, GREEN: 2, PURPLE: 1, WHITE: 13, BLACK: 14})
    first, second = g.win_probabilities()
    assert np.all(np.isclose(first, [0.07398054620276842, 0.25419316623020327, 0.13835889761815687, 0.39801409153261, 0.1354532984162614]))
    assert np.all(np.isclose(second, [0.10978925052999126, 0.15208567153011598, 0.29945753834642724, 0.2764029180695847, 0.16226462152388077]))

main()