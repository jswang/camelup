import numpy as np
import copy
from tqdm import tqdm
import random
import itertools

from camelup.constants import *
from camelup.board import Board, Player

dice_cache = {}


def get_rounds(dice: list) -> list:
    """Initialize all possible permutations of colors + dice rolls for a round"""
    if tuple(dice) in dice_cache:
        return dice_cache[tuple(dice)]
    rounds = []
    n_dice = len(dice)
    for color in itertools.permutations(dice, n_dice - 1):
        for rolls in itertools.product(range(1, 4), repeat=n_dice - 1):
            if GREY in color:
                res1 = []
                res2 = []
                for i in range(n_dice - 1):
                    if color[i] == GREY:
                        res1.append((BLACK, rolls[i]))
                        res2.append((WHITE, rolls[i]))
                    else:
                        res1.append((color[i], rolls[i]))
                        res2.append((color[i], rolls[i]))
                rounds.extend([res1, res2])
            else:
                rounds.append([(color[i], rolls[i]) for i in range(n_dice - 1)])
    dice_cache[tuple(dice)] = rounds
    return rounds


class Game:
    def __init__(self, n_players: int, setup=None) -> None:
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
        for color in WIN_CAMELS:
            self.available_bets[color] = [2, 2, 3, 5]

    def player_expected_values(self, first, second):
        """Based on player bets, calculate the expected value of each player's _best_ bet"""
        ev = np.zeros(len(self.players))
        for i, player in enumerate(self.players):
            for color, amount in player.bets:
                new_ev = (
                    first[color] * amount
                    + second[color]
                    + (1 - first[color] - second[color]) * (-1)
                )
                if new_ev > ev[i]:
                    ev[i] = new_ev
        return ev

    def best_available_bet(self, first: np.ndarray, second: np.ndarray) -> tuple:
        """Given the prob of coming in first or second, return the expected value of best bet and associated color"""
        max_val = None
        max_color = None
        vals = []
        colors = []
        for color, bets in self.available_bets.items():
            if bets:
                new_val = (
                    first[color] * bets[-1]
                    + second[color]
                    + (1 - first[color] - second[color]) * (-1)
                )
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
        index_best = np.argmax(booster_vals)
        loc = booster_locations[index_best]
        landing_val = booster_vals[index_best]

        # What change in bets would i receive?
        new_board = copy.deepcopy(self.board)
        ev = []
        possible_plays = [1, -1]
        for val in possible_plays:
            new_board.boosters[loc] = val
            new_first, new_second, _ = self.win_probabilities(new_board)
            first_delta = new_first - first
            second_delta = new_second - second
            last_delta = (1 - new_first - new_second) - (1 - first - second)
            change_ev = np.zeros(N_CAMELS)
            for color, amount in me.bets:
                change_ev[color] = (
                    first_delta[color] * amount
                    + second_delta[color]
                    + last_delta[color] * (-1)
                )
            ev.append(np.sum(change_ev))
        return landing_val + max(ev), loc, possible_plays[np.argmax(ev)]

    def optimal_move(self, player_id: int):
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
        for i, player in enumerate(self.players):
            if player.id == player_id:
                player_ev[i] = -np.inf
                me = player
            if player.ally is not None:
                player_ev[i] = -np.inf
        ally_val, ally_index = np.max(player_ev), np.argmax(player_ev)
        if ally_val == -np.inf:
            ally_index = None
            ally_val = 0

        # 3. Place tile
        booster_val, booster_location, boost_type = self.best_booster_bet(
            me, first_place, second_place, landings
        )
        vals = [bet_val, ally_val, booster_val, 1]
        options = [
            f"Bet {color_to_str(bet_color)}",
            f"Ally Player {self.players[ally_index].id}",
            f"Boost location {booster_location}, {boost_type}",
            "Roll dice",
        ]
        indices = np.flip(np.argsort(vals))
        for i in indices:
            print(f"{vals[i]:.2f}: {options[i]}")

    def win_probabilities(self, board):
        """
        Calculate the probability of each camel winning
        """
        first_place = np.zeros(N_CAMELS, dtype=int)
        second_place = np.zeros(N_CAMELS, dtype=int)
        total_landings = np.zeros(N_TILES, dtype=int)
        tile_cache = {}
        rounds = get_rounds(self.dice)
        for round in tqdm(rounds):
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
        for color in WIN_CAMELS:
            self.available_bets[color] = [2, 2, 3, 5]

    def conclude_round(self, winners):
        """Distribute winnings and reset"""
        for player in self.players:
            max_win = 0
            # Deal out winnings
            if len(player.bets) > 0:
                for color, amount in player.bets:
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
                if player.ally is not None:
                    self.players[player.ally].points += max_win
        self.reset_round()

    def __repr__(self) -> str:
        """
        Print the game status
        """
        res = f"\n{self.board}\n"
        res += f"Players: {self.players}\n"
        res += f"Dice left: "
        for d in self.dice:
            res += f"{color_to_str(d)}, "
        res += f"\nAvailable bets: "
        for k, v in self.available_bets.items():
            if len(v) == 0:
                res += f"{color_to_str(k)}: None, "
            else:
                res += f"{color_to_str(k)}: {v[-1]}, "
        res += "\n"
        res += f"Winner bets: {self.winner_bets}\n"
        res += f"Loser bets: {self.loser_bets}\n"
        return res

    def parse_move(self, curr_player: int, move: str) -> bool:
        """Parse move from player. Return True if move actually was made. print and optimal don't do anything"""
        # optimal
        if move[0] == "optimal":
            self.optimal_move(curr_player)
            return False
        # bet <color>
        elif move[0] == "bet":
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
            print(
                f"Player {curr_player} placed booster at {location} with value {value}"
            )
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
            if color == BLACK or color == WHITE:
                color = GREY
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
