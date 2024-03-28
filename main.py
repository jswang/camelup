
import itertools
import copy
import tqdm
import numpy as np

RED = 0
YELLOW = 1
BLUE = 2
GREEN = 3
PURPLE = 4
WHITE = 5
BLACK = 6
GREY = 7

N_TILES = 16
CAMELS = [RED, YELLOW, BLUE, GREEN, PURPLE, WHITE, BLACK]
N_CAMELS = len(CAMELS)
N_WIN_CAMELS = N_CAMELS - 2
DICE = [RED, YELLOW, BLUE, GREEN, PURPLE, GREY]
N_DICE = len(DICE)

class Player:
    def __init__(self, id) -> None:
        self.id = id
        self.points = 3
        self.winner_bet = None
        self.loser_bet = None
        self.ally = None
        # List of (color, amount)
        self.bets = []

    def __repr__(self) -> str:
        return f"Player {self.id}, points: {self.points}, ally: {self.ally}, bets: {self.bets}"

def get_num_camels(tile):
    """Return number of camels on a tile"""
    z = np.where(tile != -1)[0]
    if len(z) == 0:
        return 0
    return len(z)

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


def get_color_name(value):
    if value == RED:
        return "red"
    elif value == YELLOW:
        return "yellow"
    elif value == BLUE:
        return "blue"
    elif value == GREEN:
        return "green"
    elif value == PURPLE:
        return "purple"
    elif value == WHITE:
        return "white"
    elif value == BLACK:
        return "black"

class Board:
    def __init__(self, setup : dict=None):
        # List of camels on each tile, -1 if no camel
        self.tiles = np.ones((N_TILES, N_CAMELS), dtype=int)*-1
        # Camel tile index
        self.camels = np.zeros(N_CAMELS, dtype=int)
        # Booster index, 0 if no booster
        self.boosters = np.zeros(N_TILES, dtype=int)
        # Init board with a setup
        self.parse_setup(setup)

    def parse_setup(self, setup):
        """Parse setup dictionary and set up board accordingly"""
        if setup:
            for color, tile in setup.items():
                if color in CAMELS:
                    self.tiles[tile][get_num_camels(self.tiles[tile])] = color
                    self.camels[color] = tile
                elif color == "boosters":
                    self.boosters = tile

    def available_booster_locations(self) -> list:
        """Return a list of available booster locations on the board"""
        booster_indices = np.array(np.nonzero(self.boosters))[0]
        occupied = set(self.camels) | set(booster_indices) | set(booster_indices + 1) | set(booster_indices - 1)

        return [x for x in range(N_TILES) if x not in occupied]


    def get_winners(self, tiles):
        """Returns ordering of camels on board from winner to loser, ignore WHITE and BLACK"""
        res = tiles.flatten()
        res = res[np.logical_and(np.logical_and(res != WHITE, res != BLACK), res != 0)]
        return np.flip(res)


    def simulate_round(self, round : list, tile_cache: dict, camel_cache : dict):
        """
        Simulate moving the camels according to rounds, which is a list of 5 (color, spaces)
        """
        tiles = np.copy(self.tiles)
        camels = np.copy(self.camels)
        landings = np.zeros(N_TILES, dtype=int)
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
                    tiles = np.vstack((tiles, np.ones((new_tile - N_TILES + 1, N_CAMELS), dtype=int)*-1))

                # Move em camels, wraparound to not have negative values
                camels[tiles[my_tile][my_stack_index:]] = new_tile
                camels %= len(tiles) # This will preserve numbers > N_TILEs

                # Fix up tiles
                stack_to_move = get_camels(tiles[my_tile][my_stack_index:])
                tiles[my_tile][my_stack_index:] = -1
                if on_top:
                    new_stack_index = get_num_camels(tiles[new_tile])
                    # Move to new tile
                    tiles[new_tile][new_stack_index:new_stack_index+len(stack_to_move)] = stack_to_move
                else:
                    stack_to_keep = get_camels(tiles[new_tile])
                    tiles[new_tile][0:len(stack_to_move)] = stack_to_move
                    tiles[new_tile][len(stack_to_move):len(stack_to_move)+len(stack_to_keep)] = stack_to_keep
                    tiles[new_tile][len(stack_to_move)+len(stack_to_keep):] = -1

                # Keep track of landings before booster added
                if my_tile + spaces < N_TILES:
                    landings[my_tile + spaces] += len(stack_to_move)

                # End round right away if someone won
                if game_over:
                    winners = self.get_winners(tiles)
                    return winners, tiles, landings

                # Update cache if this could be useful in the future
                if i != len(round) - 1:
                    tile_cache[index] = np.copy(tiles)
                    camel_cache[index] = np.copy(camels)

        winners = self.get_winners(tiles)
        return winners, tiles, landings

def init_rounds() -> list:
    """Initialize all possible permutations of colors + dice rolls for a round"""
    rounds = []
    for color in itertools.permutations(DICE, N_DICE-1):
        for rolls in itertools.product(range(1, 4), repeat=N_DICE-1):
            if GREY in color:
                res1 = []
                res2 = []
                for i in range(N_DICE-1):
                    if color[i] == GREY:
                        res1.append((BLACK, rolls[i]))
                        res2.append((WHITE, rolls[i]))
                    else:
                        res1.append((color[i], rolls[i]))
                        res2.append((color[i], rolls[i]))
                rounds.extend([res1, res2])
            else:
                rounds.append([(color[i], rolls[i]) for i in range(5)])
    return rounds

class Game:
    def __init__(self, n_players : int, setup=None) -> None:
        # Other players
        self.players = [Player(i) for i in range(n_players)]
        # Board
        self.board = Board(setup)
        # bets on who will win overall
        self.winner_bets = []
        # bets on who will lose overall
        self.loser_bets = []
        # Available
        self.available_bets = {}
        for color in CAMELS:
            self.available_bets[color] = [2, 2, 3, 5]
        # Intialize possible rounds due to dice rolls, only do this one time
        self.rounds = init_rounds()

    def player_expected_values(self, first, second):
        """Based on player bets, calculate the expected value of each player's _best_ bet"""
        ev = np.zeros(len(self.players))
        for (i, player) in enumerate(self.players):
            for color, amount in player.bets:
                new_ev = first[color] * amount + second[color] + (1 - first[color] - second[color])*(-1)
                if new_ev > ev[i]:
                    ev[i] = new_ev
        return ev

    def best_available_bet(self, first : np.ndarray, second : np.ndarray) -> tuple:
        """Given the prob of coming in first or second, return the expected value of best bet and associated color"""
        max_val = None
        max_color = None
        vals = []
        colors = []
        for color, bets in self.available_bets.items():
            if bets:
                new_val = first[color] * bets[-1] + second[color] + (1 - first[color] - second[color])*(-1)
                vals.append(new_val)
                colors.append(color)
                if not max_val:
                    max_val = new_val
                    max_color = color
                elif new_val > max_val:
                    max_val = new_val
                    max_color = color
        print(f"{vals}, {colors}: Betting values")
        return max_val, max_color


    def best_booster_bet(self, me, first, second, landings):
        """
        Of the available booster locations, find the one that maximizes payout: x
        Then, calculate the max change in the value of your existing bets: y
        Return x + y, location
        Note: only bets to +1
        """
        # available locations
        booster_locations = self.board.available_booster_locations()
        booster_vals = landings[booster_locations]
        # Just pick the best one for now
        loc = booster_locations[np.argmax(booster_vals)]
        landing_val = booster_vals[loc]

        # What change in bets would i receive?
        new_board = copy.deepcopy(self.board)
        ev = []
        possible_plays = [1, -1]
        for val in possible_plays:
            new_board.boosters[loc] = val
            new_first, new_second, _ = self.win_probabilities(new_board)
            first_delta = new_first - first
            second_delta = new_second - second
            last_delta = (1 - new_first - new_second) - (1- first - second)
            change_ev = np.zeros(N_CAMELS)
            for (color, amount) in me.bets:
                change_ev[color] = first_delta[color] * amount + second_delta[color] + last_delta[color] * (-1)
            ev.append(np.sum(change_ev))
        print(f"{landing_val:.2f}: Boost ev on {loc}")
        print(f"{ev[0]:.2f}: Boost +1 on {loc}")
        print(f"{ev[1]:.2f}: Boost -1 on {loc}")
        return landing_val + max(ev), loc, possible_plays[np.argmax(ev)]


    def optimal_move(self, me: Player):
        """
        Get the optimal move for a player
        Moves available:
        1. Choose available bet
        2. Choose ally
        3. Place tile
        4. Roll dice (+1)
        # TODO
        5. Bet on overall winner
        6. Bet on overall loser
        """
        first_place, second_place, landings = self.win_probabilities(self.board)

        # 1. Choose available bet
        bet_val, bet_color = self.best_available_bet(first_place, second_place)

        # 2. Choose ally, if possible
        player_ev = self.player_expected_values(first_place, second_place)
        for (i, player) in enumerate(self.players):
            if player.id == me.id:
                player_ev[i] = -np.inf
            if player.ally:
                player_ev[i] = -np.inf
        ally_val, ally_index = np.max(player_ev), np.argmax(player_ev)
        if ally_val == -np.inf:
            ally_index = None
            ally_val = 0

        # 3. Place tile
        booster_val, booster_location, boost_type = self.best_booster_bet(me, first_place, second_place, landings)

        print(f"{bet_val:.2f}: Bet {get_color_name(bet_color)}\n{ally_val:.2f}: Ally {self.players[ally_index].id}\n{booster_val:.2f}: Boost {booster_location}, {boost_type}")
        print(f"1.00: Roll dice")


    def win_probabilities(self, board):
        """
        Calculate the probability of each camel winning
        """
        first_place = np.zeros(N_CAMELS, dtype=int)
        second_place =  np.zeros(N_CAMELS, dtype=int)
        total_landings = np.zeros(N_TILES, dtype=int)
        tile_cache = {}
        camel_cache = {}
        for round in tqdm.tqdm(self.rounds):
            winners, _tiles, landings = board.simulate_round(round, tile_cache, camel_cache)
            first_place[winners[0]] += 1
            second_place[winners[1]] += 1
            total_landings += landings
        # Calculate probability of each camel winning
        total = len(self.rounds)
        fp = first_place / total
        sp = second_place / total
        return fp, sp, total_landings / total


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

def main():
    print("Camel Up")

    # Optimal move
    g = Game(4, setup={YELLOW: 0, RED: 0, PURPLE: 0, WHITE: 2, BLUE: 2, GREEN: 2, BLACK:5})
    g.optimal_move(g.players[0])

main()