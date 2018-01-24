from . import Player


class PlayerWhite(Player.Player):
    """
    Inherits from Player class.
    Stores data about a player playing white pieces.
    """
    def __init__(self):
        self.positions = {
            (0, 1), (0, 3), (0, 5), (0, 7),
            (1, 0), (1, 2), (1, 4), (1, 6),
            (2, 1), (2, 3), (2, 5), (2, 7)
        }
        self.kings = set()
        self.pieces = len(self.positions)
