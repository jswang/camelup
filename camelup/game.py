import numpy as np
import copy
from tqdm import tqdm
import itertools
from functools import cache

from camelup.constants import *
from camelup.board import Board, simulate_round
from camelup.player import Player


@cache
def get_rounds(dice: tuple) -> list:
    """Initialize all possible permutations of colors + dice rolls for a round"""
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
    return rounds


@cache
def win_probabilities(dice: tuple, board: tuple):
    """
    Calculate the probability of each camel winning
    """
    first_place = np.zeros(len(WIN_CAMELS), dtype=int)
    second_place = np.zeros(len(WIN_CAMELS), dtype=int)
    total_landings = np.zeros(N_TILES, dtype=int)
    rounds = get_rounds(dice)
    for round in tqdm(rounds):
        winners, _tiles, landings, _ = simulate_round(
            Board.from_tuple(board).tiles, round
        )
        first_place[winners[0]] += 1
        second_place[winners[1]] += 1
        total_landings += landings
    # Calculate probability of each camel winning
    total = len(rounds)
    fp = first_place / total
    sp = second_place / total
    return fp, sp, total_landings / total


def bet_value(amount: int, first_prob: float, second_prob: float):
    """Given first and second place probabilities, return expected value of a bet amount"""
    return first_prob * amount + second_prob + (1 - first_prob - second_prob) * (-1)


class Game:
    def __init__(self, n_players: int = 2, setup=None) -> None:
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
        self.available_bets = {color: [2, 2, 3, 5] for color in WIN_CAMELS}
        # game over
        self.game_over = False
        # A turn has been taken this round
        self.round_concluded = False

    def __eq__(self, other):
        return (
            self.board == other.board
            and self.players == other.players
            and self.dice == other.dice
            and self.winner_bets == other.winner_bets
            and self.loser_bets == other.loser_bets
            and self.available_bets == other.available_bets
            and self.game_over == other.game_over
        )

    def to_json(self):
        return {
            "players": [p.to_json() for p in self.players],
            "board": self.board.to_dict(),
            "dice": self.dice,
            "winner_bets": self.winner_bets,
            "loser_bets": self.loser_bets,
            "available_bets": self.available_bets,
            "game_over": self.game_over,
        }

    # construct Game from json
    @classmethod
    def from_json(cls, data):
        game = cls(len(data["players"]))
        game.players = [Player.from_json(i) for i in data["players"]]
        game.board = Board(setup=data["board"])
        game.dice = data["dice"]
        game.winner_bets = data["winner_bets"]
        game.loser_bets = data["loser_bets"]
        game.available_bets = {int(k): v for k, v in data["available_bets"].items()}
        game.game_over = data["game_over"]
        return game

    def add_booster(self, player_id: int, location: int, value: int):
        """Add booster to location. value should be BOOST_POS or BOOST_NEG"""
        assert value in [BOOST_POS, BOOST_NEG]
        if self.players[player_id].boost is not None:
            self.board.remove_booster(self.players[player_id].boost)
        self.players[player_id].boost = location
        self.board.add_booster(location, value)

    def bet(self, player_id: int, color: int):
        """Place a bet on a color"""
        if len(self.available_bets[color]) == 0:
            return False
        self.players[player_id].bets.append((color, self.available_bets[color].pop()))
        return True

    def best_ally(self, me_id: int, first: list, second: list):
        """Get the best ally for player_id, return value and index of ally"""
        ally_val = np.zeros(len(self.players), dtype=int)
        for i, player in enumerate(self.players):
            if player.id != me_id and player.ally is None and len(player.bets) > 0:
                player_bet_vals = [
                    bet_value(amount, first[color], second[color])
                    for color, amount in player.bets
                ]
                ally_val[i] = max(player_bet_vals)

        ally_val, ally_index = np.max(ally_val), np.argmax(ally_val)

        return ally_val, ally_index

    def best_available_bet(self, first: np.ndarray, second: np.ndarray) -> tuple:
        """Given the prob of coming in first or second, return the expected value of best bet and associated color"""
        vals = []
        colors = []
        for color, bets in self.available_bets.items():
            if bets:
                new_val = bet_value(bets[-1], first[color], second[color])
                vals.append(new_val)
                colors.append(color)
        i = np.argmax(vals)
        return vals[i], colors[i]

    def booster_value(self, me_id: int, loc: int, board: Board):
        """If you were to remove the booster at loc, what value would it have?"""
        first, second, landings = win_probabilities(tuple(self.dice), board.to_tuple())
        booster_type = board.remove_booster(loc)
        removed_first, removed_second, _ = win_probabilities(
            tuple(self.dice), board.to_tuple()
        )
        first_delta = removed_first - first
        second_delta = removed_second - second
        change_ev = [
            bet_value(amount, first_delta[color], second_delta[color])
            for color, amount in self.players[me_id].bets
        ]
        # Add it back
        board.add_booster(loc, booster_type)
        return np.sum(change_ev) + landings[loc]

    def best_booster_bet(self, me_id: int, landings: list):
        """
        Best place to put a booster
        1. Figure out the value of going from no booster to the current booster value
        2. To avoid many board calculations, use maximal landings with current board state
        3. Calculate the expected payout of putting booster there as +1 and -1
        4. Calculate the change in expected value of existing bets of putting booster there as +1 and -1
        5. Return the best location and type of booster, as well as the previous booster value
        """
        new_board = copy.deepcopy(self.board)
        # 1. Maximal landings without your current booster, since you're considering moving it
        current_val = 0
        if self.players[me_id].boost is not None:
            # What value does the current booster add?
            current_val = self.booster_value(
                me_id, self.players[me_id].boost, new_board
            )
            new_board.remove_booster(self.players[me_id].boost)

        # 2. Maximal landings with current booster state
        booster_locations = new_board.available_booster_locations()
        booster_vals = landings[booster_locations]
        index_best = np.argmax(booster_vals)
        loc = booster_locations[index_best]
        ev = []
        possible_plays = [BOOST_POS, BOOST_NEG]
        for val in possible_plays:
            new_board.add_booster(loc, val)
            ev.append(self.booster_value(me_id, loc, new_board))
            new_board.remove_booster(loc)
        return (
            max(ev),
            loc,
            possible_plays[np.argmax(ev)],
            current_val,
        )

    def optimal_move(self, player_id: int):
        """
        Get the optimal move for player_id
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
        first_place, second_place, landings = win_probabilities(
            tuple(self.dice), self.board.to_tuple()
        )

        # 1. Choose available bet
        bet_val, bet_color = self.best_available_bet(first_place, second_place)

        # 2. Choose ally, if possible
        ally_val, ally_index = self.best_ally(player_id, first_place, second_place)

        # 3. Place tile
        booster_val, booster_location, boost_type, current_val = self.best_booster_bet(
            player_id, landings
        )
        vals = [bet_val, ally_val, booster_val, 1]
        # Converts to 1-indexing for user readability
        options = [
            f"Bet {color_to_str(bet_color)}",
            f"Ally Player {self.players[ally_index].id}",
            f"Boost location {booster_location + 1} {color_to_str(boost_type)} (current_val: {current_val:.2f})",
            "Roll dice",
        ]
        indices = np.flip(np.argsort(vals))
        for i in indices:
            print(f"{vals[i]:.2f}: {options[i]}")

    def reset_round(self):
        """Reset a round"""
        self.dice = DICE.copy()
        self.available_bets = {color: [2, 2, 3, 5] for color in WIN_CAMELS}
        self.turn_taken = False
        self.board.reset_round()
        for player in self.players:
            player.reset_round()

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
        self.round_concluded = True
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

    def check_user_input(self, curr_player: int, move: str) -> tuple:
        """Check user input for formatting and validity. Return tuple of move or None if invalid"""
        if len(move) == 0:
            return None
        move = move.lower().strip().split(" ")

        # help
        if move[0] == "help":
            print(
                f"Enter one of the following: optimal, bet <color>, ally <player_id>, boost <location> <+/->, roll <color> <amount>, winner, loser, print"
            )
            return None

        # optimal
        elif move[0] == "optimal":
            return "optimal"

        # bet <color>
        elif move[0] == "bet":
            if len(move) < 2:
                return None
            color = str_to_color(move[1])
            if color is None:
                print(f"Invalid color: {move[1]}. Please try again.")
                return None
            if color not in WIN_CAMELS:
                print(f"Invalid color: {color_to_str(color)}. Please try again.")
                return None
            if len(self.available_bets[color]) == 0:
                print(f"Invalid move: {move}. Please try again.")
                return None
            print(
                f"Player {curr_player} bet on {color_to_str(color)} with value {self.available_bets[color][-1]}"
            )
            return ("bet", color)

        # ally <player_id>
        elif move[0] == "ally":
            if len(move) < 2:
                return None
            try:
                player_id = int(move[1])
            except:
                print(f"Invalid player id: {move[1]}. Please try again.")
                return None
            if player_id not in [self.players[i].id for i in range(len(self.players))]:
                print(f"Invalid player id: {player_id}. Please try again.")
                return None
            if self.players[player_id].ally is not None:
                print(f"Invalid ally: Player {player_id} already has an ally")
                return None
            if self.players[curr_player].ally is not None:
                print(f"Invalid ally: Player {curr_player} already has an ally")
                return None
            if curr_player == player_id:
                print(f"Invalid ally: Player {curr_player} cannot ally with themselves")
                return None
            print(f"Player {curr_player} allied Player {player_id}")
            return ("ally", player_id)

        # boost <location> <+/->
        elif move[0] == "boost":
            # Converts from user index by 1 to game index by 0
            try:
                viewer_location = int(move[1])
                location = viewer_location - 1
                value = move[2]
            except:
                print(f"Invalid move: {move}. Please try again.")
                return None
            if location < 0 or location >= N_TILES or value not in ["+", "-"]:
                print(
                    f"Invalid location: {viewer_location} and value: {value}. Please try again."
                )
                return None
            print(
                f"Player {curr_player} placed booster at {viewer_location} with value {value}"
            )
            value = BOOST_POS if value == "+" else BOOST_NEG
            return ("boost", location, value)

        # roll <color> <amount>
        elif move[0] == "roll":
            if len(move) < 3:
                print(f"Invalid move: {move}. Please try again.")
                return None
            else:
                color = str_to_color(move[1])
                if color is None:
                    print(f"Invalid color: {move[1]}. Please try again.")
                    return None
                # Special checks for black/white mapping to grey
                if color in [BLACK, WHITE] and GREY not in self.dice:
                    print(f"Invalid color: {move[1]}. Please try again.")
                    return None
                elif color not in [BLACK, WHITE] and color not in self.dice:
                    print(f"Invalid color: {move[1]}. Please try again.")
                    return None
                # Can't roll a grey, must enter black or white
                if color == GREY:
                    print(
                        f"Invalid color: {move[1]}, use black or white. Please try again."
                    )
                    return None
                try:
                    amount = int(move[2])
                except:
                    print(
                        f"Invalid Non integer roll amount: {move[2]}. Please try again."
                    )
                    return None
                if amount < 1 or amount > 3:
                    print(f"Invalid roll amount: {amount}. Please try again.")
                    return None
            print(f"Player {curr_player} rolled {color_to_str(color)} {amount}")
            return ("roll", color, amount)

        # winner
        elif move[0] == "winner":
            return "winner"
        # loser
        elif move[0] == "loser":
            return "loser"
        # print
        elif move[0] == "print":
            return "print"
        else:
            return None

    def parse_move(self, curr_player: int, move: list) -> bool:
        """Parse move from player. Return 0 if no valid move was made, 1 otherwise"""
        cmd = self.check_user_input(curr_player, move)
        if cmd is None:
            return False

        # optimal
        if cmd == "optimal":
            self.optimal_move(curr_player)
            return False
        # print
        elif cmd == "print":
            print(self)
            return False

        # bet <color>
        elif cmd[0] == "bet":
            color = cmd[1]
            self.bet(curr_player, color)

        # ally <player_id>
        elif cmd[0] == "ally":
            player_id = cmd[1]
            self.players[curr_player].ally = player_id
            self.players[player_id].ally = curr_player

        # boost <location> <+/->
        elif cmd[0] == "boost":
            location = cmd[1]
            value = cmd[2]
            self.add_booster(curr_player, location, value)

        # roll <color> <amount>
        elif cmd[0] == "roll":
            color = cmd[1]
            amount = cmd[2]
            # Update board
            self.players[curr_player].points += 1
            winners, tiles, landings, game_over = simulate_round(
                self.board.tiles, [(color, amount)]
            )
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
            if game_over:
                self.game_over = True
                print("Game over")
        # winner
        elif cmd == "winner":
            self.winner_bets.append(curr_player)
            print(f"Player {curr_player} bet on overall winner")
        # loser
        elif cmd == "loser":
            self.loser_bets.append(curr_player)
            print(f"Player {curr_player} bet on overall loser")
        else:
            print(f"Invalid move: {move}. Please try again.")
            return False

        return True
