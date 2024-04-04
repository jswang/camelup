from camelup.constants import *
import numpy as np


def get_location(tiles, thing):
    """Returns (tile, stack) location of this thing, None if not found"""
    for i, l in tiles.items():
        if thing in l:
            return i, l.index(thing)
    return None, None


def has_toppers(tiles, color):
    """Does this color exist on the board and have camels on top of it?"""
    tile, stack = get_location(tiles, color)
    has_topper = False
    if tile is not None:
        has_topper = len(tiles[tile][stack:]) > 1
    return has_topper


def get_winners(tiles):
    """Returns ordering of camels on board from winner to loser, ignore WHITE and BLACK"""
    res = []
    for l in tiles.values():
        res.extend(l)
    res.reverse()
    for x in [WHITE, BLACK, BOOST_POS, BOOST_NEG]:
        while x in res:
            res.remove(x)
    return res


class Board:
    def __init__(self, setup: dict = None):
        # List of camels on each tile, -1 if no camel
        self.tiles = {i: [] for i in range(N_TILES)}
        # Init board with a setup
        if setup is not None:
            self.parse_setup(setup)

    def __repr__(self) -> str:
        """Print board, use index by 1 tiles for user readibility"""
        new_tiles = {}
        for i, l in self.tiles.items():
            new_tiles[i + 1] = [color_to_str(x) for x in l]
        return f"Board:\n{new_tiles}\n"

    def __eq__(self, other) -> bool:
        return np.all(self.tiles == other.tiles)

    def to_tuple(self):
        x = []
        for i, l in self.tiles.items():
            x.append((i, tuple(l)))
        return tuple(x)

    @classmethod
    def from_tuple(cls, data: tuple):
        board = cls()
        for i, l in data:
            board.tiles[i] = list(l)
        return board

    def reset_round(self):
        # Remove boosters
        for l in self.tiles.values():
            try:
                l.remove(BOOST_POS)
            except ValueError:
                pass
            try:
                l.remove(BOOST_NEG)
            except ValueError:
                pass

    def booster_tiles(self):
        """Get location of all boosters"""
        res = []
        for tile, l in self.tiles.items():
            if BOOST_POS in l or BOOST_NEG in l:
                res.append(tile)
        return res

    def remove_booster(self, location):
        """Remove booster from location"""
        if BOOST_POS in self.tiles[location]:
            self.tiles[location].remove(BOOST_POS)
            return BOOST_POS
        if BOOST_NEG in self.tiles[location]:
            self.tiles[location].remove(BOOST_NEG)
            return BOOST_NEG

    def add_booster(self, location, booster):
        """Add booster to location"""
        self.tiles[location].append(booster)

    def to_dict(self) -> dict:
        """
        Put self into a setup dictionary.
        Save as 1-indexing for user readability.
        """
        res = {}
        for tile, l in self.tiles.items():
            tile += 1  # Account for 1-indexing by user
            for thing in l:
                if thing in CAMELS:
                    res[thing] = tile
                elif thing == BOOST_POS:
                    if BOOST_POS not in res:
                        res[BOOST_POS] = [tile]
                    else:
                        res[BOOST_POS].append(tile)
                elif thing == BOOST_NEG:
                    if BOOST_NEG not in res:
                        res[BOOST_NEG] = [tile]
                    else:
                        res[BOOST_NEG].append(tile)
        if BOOST_POS in res:
            res[BOOST_POS].sort()
        if BOOST_NEG in res:
            res[BOOST_NEG].sort()
        return res

    def parse_setup(self, setup):
        """
        Parse setup dictionary and set up board accordingly.
        Converts from user 1-indexing to game 0-indexing.
        """
        for thing, tile in setup.items():
            # Account for 1-indexing by user
            try:
                thing = int(thing)
            except ValueError:
                thing = str_to_color(thing)

            if thing in CAMELS:
                tile -= 1
                self.tiles[tile].append(thing)
            if thing == BOOST_POS:
                for t in tile:
                    t -= 1
                    self.tiles[t].append(BOOST_POS)
            if thing == BOOST_NEG:
                for t in tile:
                    t -= 1
                    self.tiles[t].append(BOOST_NEG)

    def available_booster_locations(self) -> list:
        """Return a list of available booster locations on the board"""
        booster_indices = np.array(self.booster_tiles())
        occupied_indices = np.array(
            [x for x in range(N_TILES) if len(self.tiles[x]) > 0]
        )
        occupied = (
            set(occupied_indices)
            | set(booster_indices)
            | set(booster_indices + 1)
            | set(booster_indices - 1)
        )

        return [x for x in range(N_TILES) if x not in occupied]


def simulate_round(tiles: dict, round: list):
    """
    Simulate moving the camels according to rounds, which is a list of (color, spaces)
    """
    landings = [0] * N_TILES
    game_over = False
    # Only persists for this particular tile state.
    tile_cache = {}
    # For each die roll in round, figure out board state
    for i in range(len(round)):
        index = tuple(round[0 : i + 1])
        if index in tile_cache:
            tiles, landings = tile_cache[index][0].copy(), tile_cache[index][1].copy()
        # Otherwise, simulate that round
        else:
            color, spaces = round[i]
            # If crazy camel rolled, and only one has toppers, move the one with toppers
            if color in [BLACK, WHITE]:
                black_top = has_toppers(tiles, BLACK)
                white_top = has_toppers(tiles, WHITE)
                # If only one has it, keep it
                if black_top ^ white_top:
                    color = BLACK if black_top else WHITE
                spaces = -spaces

            # Move the camel
            my_tile, my_stack_index = get_location(tiles, color)

            # New space without booster
            new_tile = my_tile + spaces
            # If you haven't finished game, check boosters
            on_top = True
            if new_tile < N_TILES:
                new_tile %= N_TILES
                if BOOST_NEG in tiles[new_tile]:
                    on_top = False
                    boost = 1 if color in [BLACK, WHITE] else -1
                    new_tile += boost  # Intentionally no %, might win
                elif BOOST_POS in tiles[new_tile]:
                    boost = -1 if color in [BLACK, WHITE] else 1
                    new_tile += boost  # Intentionally no %, might win

            # At this point, new_tile might be > N_TILES and it might be negative (which is ok)
            # Did you win?
            if new_tile >= N_TILES:
                game_over = True
                for i in range(N_TILES, new_tile + 1):
                    tiles[i] = []

            # Move to new tile
            stack_to_move = tiles[my_tile][my_stack_index:].copy()
            del tiles[my_tile][my_stack_index:]
            if on_top:
                tiles[new_tile].extend(stack_to_move)
            else:
                tiles[new_tile] = stack_to_move + tiles[new_tile]

            # Keep track of landings before booster added
            # If stack crosses finish line, ignore - you dont get wraparound points
            if my_tile + spaces < N_TILES:
                landings[my_tile + spaces] += len(stack_to_move)

            # End round right away if someone won
            if game_over:
                winners = get_winners(tiles)
                return winners, tiles, landings, True

            # Update cache
            tile_cache[index] = (tiles.copy(), landings.copy())

    winners = get_winners(tiles)
    return winners, tiles, landings, False
