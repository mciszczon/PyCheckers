"""
This is Utils module.
It stores basic functions that allow the game to work.
TODO: Prepare better architecture, i.e. store each object in its own file.
"""


class Board:
    """
    Stores the basic board setup, i.e. the dimensions.
    """
    columns = rows = 8
    turn = 0
    
    def __init__(self):
        self.columns = 8
        self.rows = 8
        self.turn = 0  # 0 for Black and 1 for White
    
    def get_rows(self):
        """
        Returns an iterable list of rows.
        :return list:
        """
        return range(self.rows)
    
    def get_columns(self):
        """
        Returns an iterable list of columns.
        :return list:
        """
        return range(self.columns)

    @staticmethod
    def check_if_allowed(row, column):
        if (row % 2 == 0 and column % 2 != 0) or (row % 2 != 0 and column % 2 == 0):
            return True
        else:
            return False

    def change_turn(self):
        if self.turn == 0:
            self.turn = 1
        elif self.turn == 1:
            self.turn = 0
        else:
            print('Error!')



class Player:
    """
    A basic object that stores data about a single player,
    i.e. where he has got his pieces and which of them are kings.
    """
    pieces = 12
    positions = set()
    kings = set()

    def __init__(self):
        self.pieces = 12


class PlayerWhite(Player):
    """
    Inherits from Player class.
    Stores data about a player playing white pieces.
    """
    positions = {
        (0, 1), (0, 3), (0, 5), (0, 7),
        (1, 0), (1, 2), (1, 4), (1, 6),
        (2, 1), (2, 3), (2, 5), (2, 7)
    }

    kings = set()


class PlayerBlack(Player):
    """
    Inherits from Player class.
    Stores data about a player playing black pieces.
    """
    positions = {
        (5, 0), (5, 2), (5, 4), (5, 6),
        (6, 1), (6, 3), (6, 5), (6, 7),
        (7, 0), (7, 2), (7, 4), (7, 6)
    }

    kings = set()
