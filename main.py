
import itertools
import copy
import tqdm
import numpy as np
import argparse
import random

EMPTY = -1
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
DICE = [RED, YELLOW , BLUE, GREEN, PURPLE, GREY]
N_DICE = len(DICE)

class Player:
    def __init__(self, id) -> None:
        self.id = id
        self.points = 3
        self.winner_bet = None
        self.loser_bet = None
        # id of ally, None if none
        self.ally = None
        # List of (color, amount)
        self.bets = []
        # location of boost
        self.boost = None

    def __repr__(self) -> str:
        return f"Player {self.id}: (points: {self.points}, ally: {self.ally}, bets: {self.bets})"

def get_num_camels(tile):
    """Return number of camels on a tile"""
    z = np.where(tile != EMPTY)[0]
    if len(z) == 0:
        return 0
    return len(z)

def get_camels(tile):
    """Get all camels on this tile"""
    x = get_num_camels(tile)
    return np.copy(tile[0:x])

def str_to_color(value: str):
    value = value.lower().strip()
    if value == "red":
        return RED
    elif value == "yellow":
        return YELLOW
    elif value == "blue":
        return BLUE
    elif value == "green":
        return GREEN
    elif value == "purple":
        return PURPLE
    elif value == "white":
        return WHITE
    elif value == "black":
        return BLACK
    return None

def color_to_str(value):
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

def get_location(tiles, color):
    rows, cols = np.where(tiles == color)
    if len(rows) == len(cols) and len(rows) == 1:
        return rows[0], cols[0]
    return None, None

class Board:
    def __init__(self, setup : dict=None):
        # List of camels on each tile, -1 if no camel
        self.tiles = np.ones((N_TILES, N_CAMELS), dtype=int)*EMPTY
        # Booster index, 0 if no booster
        self.boosters = np.zeros(N_TILES, dtype=int)
        # Init board with a setup
        self.parse_setup(setup)


    def __repr__(self) -> str:
        res = ""
        for c in CAMELS:
            tile,stack = get_location(self.tiles, c)
            res += f"{color_to_str(c)}: tile: {tile}, stack: {stack}\n"
        res += "\n"
        # indices of positive boosters
        res += f"positive boosters: {np.where(self.boosters > 0)[0]}\n"
        res += f"negative boosters: {np.where(self.boosters < 0)[0]}\n"
        return res

    def parse_setup(self, setup):
        """Parse setup dictionary and set up board accordingly"""
        if setup:
            for color, tile in setup.items():
                if color in CAMELS:
                    self.tiles[tile][get_num_camels(self.tiles[tile])] = color
                elif color == "pos_boosters":
                    self.boosters[tile] = 1
                elif color == "neg_boosters":
                    self.boosters[tile] = -1

    def available_booster_locations(self) -> list:
        """Return a list of available booster locations on the board"""
        booster_indices = np.array(np.nonzero(self.boosters))[0]
        locations = np.where(np.any(self.tiles != EMPTY, axis=1))[0]
        occupied = set(locations) | set(booster_indices) | set(booster_indices + 1) | set(booster_indices - 1)

        return [x for x in range(N_TILES) if x not in occupied]


    def get_winners(self, tiles):
        """Returns ordering of camels on board from winner to loser, ignore WHITE and BLACK"""
        res = tiles.flatten()
        res = res[np.logical_and(np.logical_and(res != WHITE, res != BLACK), res != EMPTY)]
        return np.flip(res)


    def simulate_round(self, round : list, tile_cache: dict):
        """
        Simulate moving the camels according to rounds, which is a list of 5 (color, spaces)
        """
        tiles = np.copy(self.tiles)
        landings = np.zeros(N_TILES, dtype=int)
        game_over = False
        # For each die roll in round, figure out board state
        for i in range(len(round)):
            index = tuple(round[0:i+1])
            if index in tile_cache:
                tiles, landings = np.copy(tile_cache[index][0]), np.copy(tile_cache[index][1])
            # Otherwise, simulate that round
            else:
                color, spaces = round[i]
                # If crazy camel rolled, and only one has toppers, move the one with toppers
                if color in [BLACK, WHITE]:
                    # who has toppers?
                    black_tile, black_stack = get_location(tiles, BLACK)
                    if black_tile is not None:
                        black_top = black_tile < N_CAMELS-1 and tiles[black_tile][black_stack+1] != EMPTY
                    else:
                        black_top = False

                    white_tile, white_stack = get_location(tiles, WHITE)
                    if white_tile is not None:
                        white_top = white_tile < N_CAMELS-1 and tiles[white_tile][white_stack+1] != EMPTY
                    else:
                        white_top = False

                    if black_top and not white_top:
                        color = BLACK
                    if white_top and not black_top:
                        color = WHITE
                    spaces = -spaces

                # Move the camel
                my_tile, my_stack_index = get_location(tiles, color)

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
                    tiles = np.vstack((tiles, np.ones((new_tile - N_TILES + 1, N_CAMELS), dtype=int)*EMPTY))

                # Fix up tiles
                stack_to_move = get_camels(tiles[my_tile][my_stack_index:])
                tiles[my_tile][my_stack_index:] = EMPTY
                if on_top:
                    new_stack_index = get_num_camels(tiles[new_tile])
                    # Move to new tile
                    tiles[new_tile][new_stack_index:new_stack_index+len(stack_to_move)] = stack_to_move
                else:
                    stack_to_keep = get_camels(tiles[new_tile])
                    tiles[new_tile][0:len(stack_to_move)] = stack_to_move
                    tiles[new_tile][len(stack_to_move):len(stack_to_move)+len(stack_to_keep)] = stack_to_keep
                    tiles[new_tile][len(stack_to_move)+len(stack_to_keep):] = EMPTY

                # Keep track of landings before booster added
                if my_tile + spaces < N_TILES:
                    landings[my_tile + spaces] += len(stack_to_move)

                # End round right away if someone won
                if game_over:
                    winners = self.get_winners(tiles)
                    return winners, tiles, landings

                # Update cache if this could be useful in the future
                if i != len(round) - 1:
                    tile_cache[index] = (np.copy(tiles), np.copy(landings))

        winners = self.get_winners(tiles)
        return winners, tiles, landings

def get_rounds(dice) -> list:
    """Initialize all possible permutations of colors + dice rolls for a round"""
    rounds = []
    n_dice = len(dice)
    for color in itertools.permutations(dice, n_dice-1):
        for rolls in itertools.product(range(1, 4), repeat=n_dice-1):
            if GREY in color:
                res1 = []
                res2 = []
                for i in range(n_dice-1):
                    if color[i] == GREY:
                        res1.append((BLACK, rolls[i]))
                        res2.append((WHITE, rolls[i]))
                    else:
                        res1.append((color[i], rolls[i]))
                        res2.append((color[i], rolls[i]))
                rounds.extend([res1, res2])
            else:
                rounds.append([(color[i], rolls[i]) for i in range(n_dice-1)])
    return rounds

class Game:
    def __init__(self, n_players : int, setup=None) -> None:
        # Other players
        self.players = [Player(i) for i in range(n_players)]
        # Board
        self.board = Board(setup)
        # Dice remaining
        self.dice = DICE.copy()
        # bets on who will win overall
        self.winner_bets = []
        # bets on who will lose overall
        self.loser_bets = []
        # Available
        self.available_bets = {}
        for color in CAMELS:
            self.available_bets[color] = [2, 2, 3, 5]

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
        print(f"Calculating optimal move")
        first_place, second_place, landings = self.win_probabilities(self.board)

        # 1. Choose available bet
        bet_val, bet_color = self.best_available_bet(first_place, second_place)

        # 2. Choose ally, if possible
        player_ev = self.player_expected_values(first_place, second_place)
        for (i, player) in enumerate(self.players):
            if player.id == me.id:
                player_ev[i] = -np.inf
            if player.ally is not None:
                player_ev[i] = -np.inf
        ally_val, ally_index = np.max(player_ev), np.argmax(player_ev)
        if ally_val == -np.inf:
            ally_index = None
            ally_val = 0

        # 3. Place tile
        booster_val, booster_location, boost_type = self.best_booster_bet(me, first_place, second_place, landings)
        vals = [bet_val, ally_val, booster_val, 1]
        options = [f"Bet {color_to_str(bet_color)}", f"Ally Player {self.players[ally_index].id}", f"Boost location {booster_location}, {boost_type}", "Roll dice"]
        indices = np.flip(np.argsort(vals))
        for i in indices:
            print(f"{vals[i]:.2f}: {options[i]}")


    def win_probabilities(self, board):
        """
        Calculate the probability of each camel winning
        """
        first_place = np.zeros(N_CAMELS, dtype=int)
        second_place =  np.zeros(N_CAMELS, dtype=int)
        total_landings = np.zeros(N_TILES, dtype=int)
        tile_cache = {}
        rounds = get_rounds(self.dice)
        for round in rounds:
            winners, _tiles, landings = board.simulate_round(round, tile_cache)
            first_place[winners[0]] += 1
            second_place[winners[1]] += 1
            total_landings += landings
        # Calculate probability of each camel winning
        total = len(rounds)
        fp = first_place / total
        sp = second_place / total
        return fp, sp, total_landings / total

    def reset_round(self):
        """Reset a round"""
        self.dice = DICE.copy()
        self.available_bets = {}
        for color in CAMELS:
            self.available_bets[color] = [2, 2, 3, 5]

    def conclude_round(self, winners):
        """Distribute winnings and reset"""
        for player in self.players:
            max_win = 0
            # Deal out winnings
            if len(player.bets) > 0:
                for (color, amount) in player.bets:
                    if color == winners[0]:
                        win = amount
                    elif color == winners[1]:
                        win = 1
                    else:
                        win = -1
                    if win > max_win:
                        max_win = win
                    player.points += win
                # Dont forget ally winnings
                self.players[player.ally].points += max_win
        self.reset_round()

    def __repr__(self) -> str:
        """
        Print the game status
        """
        res = f"{self.board}\n"
        res += f"Players: {self.players}\n"
        res += f"Available bets: "
        for k,v in self.available_bets.items():
            if len(v) == 0:
                res += f"{color_to_str(k)}: None, "
            else:
                res += f"{color_to_str(k)}: {v[-1]}, "
        res += "\n"
        res += f"Winner bets: {self.winner_bets}\n"
        res += f"Loser bets: {self.loser_bets}\n"
        return res

    def parse_move(self, curr_player, move: str) -> bool:
        # bet <color>
        if move[0] == "bet":
            color = str_to_color(move[1])
            if len(self.available_bets[color]) == 0:
                print(f"Invalid move: {move}. Please try again.")
                return False
            amount = self.available_bets[color][-1]
            self.players[curr_player].bets.append((color, amount))
            self.available_bets[color].pop()
            print(f"Player {curr_player} bet on {move[1]} for {amount}")
        # ally <player_id>
        elif move[0] == "ally":
            player_id = int(move[1])
            self.players[curr_player].ally = player_id
            self.players[player_id].ally = curr_player
            print(f"Player {curr_player} allied Player {player_id}")
        # boost <location> <1/-1>
        elif move[0] == "boost":
            location = int(move[1])
            value = int(move[2])
            # Remove old booster
            if self.players[curr_player].boost is not None:
                self.board.boosters[self.players[curr_player].boost[0]] = 0
            # Place new booster
            self.players[curr_player].boost = location
            self.board.boosters[location] = value
            print(f"Player {curr_player} placed booster at {location} with value {value}")
        # roll <color> <amount>
        elif move[0] == "roll":
            # Fixed roll
            if len(move) == 3:
                color = str_to_color(move[1])
                amount = int(move[2])
            # Random roll
            else:
                color = random.choice(self.dice)
                amount = random.randint(1, 3)
            # Update board
            self.players[curr_player].points += 1
            winners, tiles, landings = self.board.simulate_round([(color, amount)], {})
            self.board.tiles = tiles
            self.dice.remove(color)
            # Handout boost points
            for player in self.players:
                if player.boost is not None:
                    player.points += landings[player.boost]
            # Conclude if necessary
            if len(self.dice) == 1:
                print(f"Concluding round")
                self.conclude_round(winners)
            print(f"Player {curr_player} rolled {color_to_str(color)} {amount}")
        # winner
        elif move[0] == "winner":
            self.winner_bets.append(curr_player)
            print(f"Player {curr_player} bet on overall winner")
        # loser
        elif move[0] == "loser":
            self.loser_bets.append(curr_player)
            print(f"Player {curr_player} bet on overall loser")
        # print
        elif move[0] == "print":
            print(self)
            return False
        else:
            print(f"Invalid move: {move}. Please try again.")
            return False
        return True

def main():
    parser = argparse.ArgumentParser(description='Camel Up Game')

    parser.add_argument('--setup', type=str, help='Setup dictionary for the game', default={YELLOW:0, PURPLE:0, GREEN:0, RED:1, BLUE:2, BLACK:13, WHITE:13})
    parser.add_argument('--id', type=int, help='Player id', default=1)
    parser.add_argument('--n-players', type=int, help='Number of players', default=2)
    args = parser.parse_args()

    print("Camel Up!!!\n")
    # Set up game
    g = Game(args.n_players, setup=args.setup)
    print(g)
    curr_player = 0
    while True:
        move_made = False
        # Enter what other people do
        if curr_player != args.id:
            while not move_made:
                move = input(f"Enter Player {curr_player} move: ").lower().strip().split(' ')
                if g.parse_move(curr_player, move):
                    curr_player = (curr_player + 1) % args.n_players
                    move_made = True
        # Calculate optimal move:
        else:
            g.optimal_move(g.players[args.id])

            while not move_made:
                move = input(f"Enter your move: ").lower().strip().split(' ')
                if g.parse_move(curr_player, move):
                    curr_player = (curr_player + 1) % args.n_players
                    move_made = True
if __name__ == "__main__":
    main()
    # TODO: fix setup input, see optimal other player move
"""
This is probably a bug:
red: tile: 1, stack: 0
yellow: tile: 1, stack: 1
blue: tile: 5, stack: 0
green: tile: 5, stack: 1
purple: tile: 1, stack: 2
white: tile: 13, stack: 1
black: tile: 13, stack: 0

positive boosters: []
negative boosters: []

Players: [Player 0: (points: 5, ally: None, bets: [(3, 5), (4, 5)]), Player 1: (points: 4, ally: None, bets: [(3, 3), (3, 2), (3, 2)])]
Available bets: red: 5, yellow: 5, blue: 5, green: None, purple: 3, white: 5, black: 5,
Winner bets: []
Loser bets: []
"""