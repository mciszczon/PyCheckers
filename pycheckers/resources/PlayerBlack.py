from . import Player


class PlayerBlack(Player.Player):
    """
    Inherits from Player class.
    Stores data about a player playing black pieces.
    """
    def __init__(self):
        self.positions = {
            (5, 0), (5, 2), (5, 4), (5, 6),
            (6, 1), (6, 3), (6, 5), (6, 7),
            (7, 0), (7, 2), (7, 4), (7, 6)
        }
        self.kings = set()
        self.pieces = len(self.positions)
        self.pieces_with_captures = dict()
        self.pieces_with_moves = dict()
