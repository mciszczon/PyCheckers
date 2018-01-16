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
    
    def __init__(self):
        self.columns = 8
        self.rows = 8
    
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


class Player:
    """
    A basic object that stores data about a single player,
    i.e. where he has got his pieces and which of them are kings.
    """
    pieces = 12
    positions = {}
    kings = {}

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

    kings = {

    }


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

    kings = {

    }
