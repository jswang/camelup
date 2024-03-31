# Game constants
EMPTY = -1
RED = 0
YELLOW = 1
BLUE = 2
GREEN = 3
PURPLE = 4
WHITE = 5
BLACK = 6
GREY = 7
BOOST_POS = 8
BOOST_NEG = 9


N_TILES = 16
CAMELS = [RED, YELLOW, BLUE, GREEN, PURPLE, WHITE, BLACK]
WIN_CAMELS = [RED, YELLOW, BLUE, GREEN, PURPLE]
N_CAMELS = len(CAMELS)
DICE = [RED, YELLOW, BLUE, GREEN, PURPLE, GREY]
N_DICE = len(DICE)


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
    elif value == "grey":
        return GREY
    elif value == "boost_pos":
        return BOOST_POS
    elif value == "boost_neg":
        return BOOST_NEG
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
    elif value == GREY:
        return "grey"
    elif value == BOOST_POS:
        return "boost_pos"
    elif value == BOOST_NEG:
        return "boost_neg"
    return None
