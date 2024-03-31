from camelup.constants import *
import numpy as np


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


def get_location(tiles, color):
    """Returns location of this color in tiles, None if not found"""
    rows, cols = np.where(tiles == color)
    if len(rows) == len(cols) and len(rows) == 1:
        return rows[0], cols[0]
    return None, None


def get_winners(tiles):
    """Returns ordering of camels on board from winner to loser, ignore WHITE and BLACK"""
    res = tiles.flatten()
    res = res[np.logical_and(np.logical_and(res != WHITE, res != BLACK), res != EMPTY)]
    return np.flip(res)


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
        return f"Player {self.id}: (points: {self.points}, ally: {self.ally}, boost: {self.boost}, bets: {self.bets})"

    def __eq__(self, other) -> bool:
        return (
            self.id == other.id
            and self.points == other.points
            and self.winner_bet == other.winner_bet
            and self.loser_bet == other.loser_bet
            and self.ally == other.ally
            and self.boost == other.boost
            and self.bets == other.bets
        )

    def to_json(self):
        return {
            "id": self.id,
            "points": self.points,
            "winner_bet": self.winner_bet,
            "loser_bet": self.loser_bet,
            "ally": self.ally,
            "boost": self.boost,
            "bets": self.bets,
        }

    @classmethod
    def from_json(cls, data):
        player = cls(data["id"])
        player.points = data["points"]
        player.winner_bet = data["winner_bet"]
        player.loser_bet = data["loser_bet"]
        player.ally = data["ally"]
        player.boost = data["boost"]
        player.bets = data["bets"]
        return player


class Board:
    def __init__(self, setup: dict = None):
        # List of camels on each tile, -1 if no camel
        self.tiles = np.ones((N_TILES, N_CAMELS), dtype=int) * EMPTY
        # Booster index, 0 if no booster
        self.boosters = np.zeros(N_TILES, dtype=int)
        # Init board with a setup
        self.parse_setup(setup)

    def __repr__(self) -> str:
        res = ""
        # Print out camels on each tile
        for tile_index, t in enumerate(self.tiles):
            for stack_index, c in enumerate(get_camels(t)):
                res += f"{color_to_str(c)}: tile: {tile_index}, stack: {stack_index}\n"
        # Booster locations
        res += f"positive boosters: {np.where(self.boosters > 0)[0]}\n"
        res += f"negative boosters: {np.where(self.boosters < 0)[0]}\n"
        return res

    def __eq__(self, other) -> bool:
        return np.all(self.tiles == other.tiles) and np.all(
            self.boosters == other.boosters
        )

    def to_json(self):
        return {"tiles": self.tiles.tolist(), "boosters": self.boosters.tolist()}

    @classmethod
    def from_json(cls, data):
        board = cls()
        board.tiles = np.array(data["tiles"].copy())
        board.boosters = np.array(data["boosters"].copy())
        return board

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
        occupied = (
            set(locations)
            | set(booster_indices)
            | set(booster_indices + 1)
            | set(booster_indices - 1)
        )

        return [x for x in range(N_TILES) if x not in occupied]

    def simulate_round(self, round: list, tile_cache: dict):
        """
        Simulate moving the camels according to rounds, which is a list of 5 (color, spaces)
        """
        tiles = np.copy(self.tiles)
        landings = np.zeros(N_TILES, dtype=int)
        game_over = False
        # For each die roll in round, figure out board state
        for i in range(len(round)):
            index = tuple(round[0 : i + 1])
            if index in tile_cache:
                tiles, landings = np.copy(tile_cache[index][0]), np.copy(
                    tile_cache[index][1]
                )
            # Otherwise, simulate that round
            else:
                color, spaces = round[i]
                # If crazy camel rolled, and only one has toppers, move the one with toppers
                if color in [BLACK, WHITE]:
                    # who has toppers?
                    black_tile, black_stack = get_location(tiles, BLACK)
                    if black_tile is not None:
                        black_top = (
                            black_tile < N_CAMELS - 1
                            and tiles[black_tile][black_stack + 1] != EMPTY
                        )
                    else:
                        black_top = False

                    white_tile, white_stack = get_location(tiles, WHITE)
                    if white_tile is not None:
                        white_top = (
                            white_tile < N_CAMELS - 1
                            and tiles[white_tile][white_stack + 1] != EMPTY
                        )
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
                    tiles = np.vstack(
                        (
                            tiles,
                            np.ones((new_tile - N_TILES + 1, N_CAMELS), dtype=int)
                            * EMPTY,
                        )
                    )

                # Fix up tiles
                stack_to_move = get_camels(tiles[my_tile][my_stack_index:])
                tiles[my_tile][my_stack_index:] = EMPTY
                if on_top:
                    new_stack_index = get_num_camels(tiles[new_tile])
                    # Move to new tile
                    tiles[new_tile][
                        new_stack_index : new_stack_index + len(stack_to_move)
                    ] = stack_to_move
                else:
                    stack_to_keep = get_camels(tiles[new_tile])
                    tiles[new_tile][0 : len(stack_to_move)] = stack_to_move
                    tiles[new_tile][
                        len(stack_to_move) : len(stack_to_move) + len(stack_to_keep)
                    ] = stack_to_keep
                    tiles[new_tile][len(stack_to_move) + len(stack_to_keep) :] = EMPTY

                # Keep track of landings before booster added
                if my_tile + spaces < N_TILES:
                    landings[my_tile + spaces] += len(stack_to_move)

                # End round right away if someone won
                if game_over:
                    winners = get_winners(tiles)
                    return winners, tiles, landings, True

                # Update cache if this could be useful in the future
                if i != len(round) - 1:
                    tile_cache[index] = (np.copy(tiles), np.copy(landings))

        winners = get_winners(tiles)
        return winners, tiles, landings, False
