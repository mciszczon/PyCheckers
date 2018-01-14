class Board:
    """
    Stores the basic board set up.
    """
    columns = rows = 8
    
    def __init__(self):
        self.columns = 8
        self.rows = 8
    
    def get_rows(self):
        """
        Returns an iterable list of rows.
        """
        return range(self.rows)
    
    def get_columns(self):
        """
        Returns an iterable list of columns.
        """
        return range(self.columns)


class Player:
    pieces = 12
    positions = {}

    def __init__(self):
        self.pieces = 12


class PlayerWhite(Player):
    positions = {
        (0, 1), (0, 3), (0, 5), (0, 7),
        (1, 0), (1, 2), (1, 4), (1, 6),
        (2, 1), (2, 3), (2, 5), (2, 7)
    }

    kings = {

    }


class PlayerBlack(Player):
    positions = {
        (5, 0), (5, 2), (5, 4), (5, 6),
        (6, 1), (6, 3), (6, 5), (6, 7),
        (7, 0), (7, 2), (7, 4), (7, 6)
    }

    kings = {

    }
