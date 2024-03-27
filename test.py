from main import *

def test_print():
    g = Game(4, setup={RED: 0, YELLOW: 0, BLUE: 2, GREEN: 2, PURPLE: 1, WHITE: 13, BLACK: 14})
    print(g)
    print(g.board.get_winners())

def test_winners():
    """Get the winners, from first to last"""
    g = Game(4, setup={RED: 0, YELLOW: 0, BLUE: 2, GREEN: 2, PURPLE: 1, WHITE: 13, BLACK: 14})
    assert g.board.get_winners() == [GREEN, BLUE, PURPLE, YELLOW, RED]

def test_mess(arr):
    arr[0] = 100

test_print()
test_winners()
a = [1,2,3]
test_mess(a)
print(a)