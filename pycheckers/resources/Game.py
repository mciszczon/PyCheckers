from . import Board
from . import PlayerBlack
from . import PlayerWhite


class Game:
    def __init__(self, name):
        self.name = name
        self.turn = 0
        self.board = Board.Board()
        self.rows = self.board.get_rows()
        self.columns = self.board.get_columns()

        self.player_black = PlayerBlack.PlayerBlack()
        self.player_white = PlayerWhite.PlayerWhite()

    def change_turn(self):
        """
        This method changes the turn from 0 to 1 or from 1 to 0.
        It returns False if something's wrong and the turn is neither 0 or 1. Should not happen.
        :return boolean:
        """
        if self.turn == 0:
            self.turn = 1
            return True
        elif self.turn == 1:
            self.turn = 0
            return True

        return False
