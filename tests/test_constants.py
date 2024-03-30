# Tests for constants.py

from camelup import constants


def test_str_to_color():
    assert constants.str_to_color("PURPLE") == constants.PURPLE
    assert constants.str_to_color("PurplE") == constants.PURPLE
    assert constants.str_to_color("purple") == constants.PURPLE
    assert constants.str_to_color(" purple ") == constants.PURPLE
    assert constants.str_to_color("red") == constants.RED
    assert constants.str_to_color("yellow") == constants.YELLOW
    assert constants.str_to_color("blue") == constants.BLUE
    assert constants.str_to_color("green") == constants.GREEN
    assert constants.str_to_color("white") == constants.WHITE
    assert constants.str_to_color("black") == constants.BLACK
    assert constants.str_to_color("grey") == constants.GREY
    assert constants.str_to_color("LSDKJF") == None


def test_color_to_str():
    assert constants.color_to_str(constants.PURPLE) == "purple"
    assert constants.color_to_str(constants.RED) == "red"
    assert constants.color_to_str(constants.YELLOW) == "yellow"
    assert constants.color_to_str(constants.BLUE) == "blue"
    assert constants.color_to_str(constants.GREEN) == "green"
    assert constants.color_to_str(constants.WHITE) == "white"
    assert constants.color_to_str(constants.BLACK) == "black"
    assert constants.color_to_str(constants.GREY) == "grey"
    assert constants.color_to_str(23423) == None
