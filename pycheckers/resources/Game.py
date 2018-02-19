import pickle
from time import time
from math import fabs
from .Board import Board
from .PlayerBlack import PlayerBlack
from .PlayerWhite import PlayerWhite


class Game:
    """

    """
    def __init__(self, game_id, name, gametype, private, creator):
        """
        Game class constructor.
        :param string name: A name for the new game
        :param string gametype: Either 'computer' or 'human'
        :param string private: Either 'private' or 'public'
        :param int creator: ID of the user who created the game
        """
        self.game_id = game_id
        self.name = name
        self.gametype = gametype
        self.timestamp = 0
        self.private = private
        self.creator = creator
        self.guest = False
        self.turn = creator
        self.round = 1
        self.finished = None
        self.save_timestamp()
        self.board = Board()
        self.rows = self.board.get_rows()
        self.columns = self.board.get_columns()
        self.player_black = PlayerBlack()
        self.player_white = PlayerWhite()
        self.update_possible_moves()
        self.update_possible_captures()
        self.check_status()

    def save_game(self):
        try:
            pickle.dump(self, open('games/' + self.game_id + '.p', 'wb'))
            return True
        except:
            return False

    def change_turn(self):
        """
        This method changes the turn of the game.
        It returns False if something's wrong. Should not happen.
        :return boolean:
        """
        ok = False

        if self.turn == self.creator:
            self.turn = self.guest
            ok = True
        elif self.turn == self.guest:
            self.turn = self.creator
            ok = True

        if ok:
            self.round += 1
            self.save_timestamp()

        return ok

    def set_guest(self, guest_id):
        """
        Allows to set guest user ID for use in turns.
        :param int guest_id: Guest user ID
        :return boolean:
        """
        if type(guest_id) is int:
            self.guest = guest_id
            return True
        else:
            return False

    def save_timestamp(self):
        """
        This functions firstly generates a timestamp, and then cuts off the part after the dot.
        This works by converting the stamp to string, and then doing the operation.
        That leaves only 10 first numbers and they are in a string, like this: '1517177788'.
        The string then gets converted back to integer and saved to a Game instance.
        :return:
        """
        timestamp = str(time()).split('.')[0]
        self.timestamp = int(timestamp)
        return

    def get_timestamp(self):
        """
        This simple function returns a timestamp saved in a Game instance.
        :return string: Timestamp as a string.
        """
        return self.timestamp

    def check_status(self):
        if not self.player_black.pieces_with_moves and not self.player_black.pieces_with_captures \
            and not self.player_white.pieces_with_moves and not self.player_white.pieces_with_captures:
            self.finished = True
        else:
            if not self.player_black.pieces or \
                    (not self.player_black.pieces_with_moves and not self.player_black.pieces_with_captures):
                self.finished = self.guest  # White wins
            elif not self.player_white.pieces or \
                    (not self.player_white.pieces_with_moves and not self.player_white.pieces_with_captures):
                self.finished = self.creator # Black wins

        return self.finished

    def check_select(self, coordinate_x, coordinate_y, current_user_id):
        """
        This function checks whether a selected piece belongs to a player who's turn it is.
        It also makes sure that player can only choose a piece that has available capture (if there is a such).
        :param int coordinate_x: X coordinate of the selected piece.
        :param int coordinate_y: Y coordinate of the selected piece.
        :param int current_user_id: ID of the user that tries to make the selection.
        :return boolean: Return True if the selection is valid and allowed.
        """
        if self.turn == self.creator and self.creator == current_user_id:
            if (coordinate_x, coordinate_y) in self.player_black.positions:
                if not self.player_black.pieces_with_moves or \
                        (coordinate_x, coordinate_y) in self.player_black.pieces_with_moves \
                        or not self.player_black.pieces_with_captures or \
                        (coordinate_x, coordinate_y) in self.player_black.pieces_with_captures:
                    return True
        if self.turn == self.guest and self.guest == current_user_id:
            if (coordinate_x, coordinate_y) in self.player_white.positions:
                if not self.player_white.pieces_with_moves or \
                        (coordinate_x, coordinate_y) in self.player_white.pieces_with_moves \
                        or not self.player_white.pieces_with_captures or \
                        (coordinate_x, coordinate_y) in self.player_white.pieces_with_captures:
                    return True

        return False

    def add_kings(self):
        """
        Iterates both players' pieces and turns them into kings if applicable.
        :return boolean: True if some pieces were turned into kings, False otherwise.
        """
        for piece in self.player_black.positions:
            # If row is 0, then black player has a piece at white's base
            if piece[0] == 0 and piece not in self.player_black.kings:
                self.player_black.kings.add(piece)
                return True

        for piece in self.player_white.positions:
            # If row is 7, then white player has a piece at black's base
            if piece[0] == 7 and piece not in self.player_white.kings:
                self.player_white.kings.add(piece)
                return True

        return False

    def handle_move(self, coordinate_x, coordinate_y, to_x, to_y):
        """
        Quite extensive function that handles moving of a piece: either a simple move or a capture.
        This should be broken up into smaller sub-functions for sure.
        TODO: Check for available captures and force them.
        TODO: Don't change turn if another capture possible.
        :param int coordinate_x: X coordinate of selected piece.
        :param int coordinate_y: Y coordinate of selected piece.
        :param int to_x: X coordinate of the desired box to move into.
        :param int to_y: Y coordinate of the desired box to move into.
        :return boolean: True if the move was successful, False otherwise.
        """
        # Black Player
        if self.turn == self.creator and (coordinate_x, coordinate_y) in self.player_black.positions:
            if self.move(coordinate_x, coordinate_y, to_x, to_y):
                self.add_kings()
                self.update_possible_moves()
                return True
        # White Player
        elif self.turn == self.guest and (coordinate_x, coordinate_y) in self.player_white.positions:
            if self.move(coordinate_x, coordinate_y, to_x, to_y):
                self.add_kings()
                self.update_possible_moves()
                return True
        return False

    def move(self, coordinate_x, coordinate_y, to_x, to_y):
        """
        Checks whether a move is by one or two squares (diagonally).
        If the further, then it calls capture() function, as move by two is only possible when capturing.
        :param int coordinate_x: X coordinate of selected piece.
        :param int coordinate_y: Y coordinate of selected piece.
        :param int to_x: X coordinate of the desired box to move into.
        :param int to_y: Y coordinate of the desired box to move into.
        :return boolean: True if the move is valid, False otherwise.
        """
        # 0. If possible captures and piece not able to capture -> WROOONG
        if self.turn == self.creator and len(self.player_black.pieces_with_captures):
            if not (coordinate_x, coordinate_y) in self.player_black.pieces_with_captures:
                return False
        elif self.turn == self.guest and len(self.player_white.pieces_with_captures):
            if not (coordinate_x, coordinate_y) in self.player_white.pieces_with_captures:
                return False
        # 1. If by one square, it's okay
        if fabs(coordinate_x - to_x) <= 1 and fabs(coordinate_y - to_y) <= 1:
            if self.turn == self.creator:  # Black Turn
                if (coordinate_x, coordinate_y) in self.player_black.pieces_with_captures:
                    return False
                if (to_x, to_y) not in self.player_white.positions and (to_x, to_y) not in self.player_black.positions:
                    self.player_black.positions.remove((coordinate_x, coordinate_y))
                    self.player_black.positions.add((to_x, to_y))
                    if (coordinate_x, coordinate_y) in self.player_black.kings:
                        self.player_black.kings.remove((coordinate_x, coordinate_y))
                        self.player_black.kings.add((to_x, to_y))
                    self.update_possible_captures()
                    self.change_turn()
                    return True
                else:
                    return False
            elif self.turn == self.guest:  # White Turn
                if (coordinate_x, coordinate_y) in self.player_white.pieces_with_captures:
                    return False
                if (to_x, to_y) not in self.player_black.positions and (to_x, to_y) not in self.player_white.positions:
                    self.player_white.positions.remove((coordinate_x, coordinate_y))
                    self.player_white.positions.add((to_x, to_y))
                    if (coordinate_x, coordinate_y) in self.player_white.kings:
                        self.player_white.kings.remove((coordinate_x, coordinate_y))
                        self.player_white.kings.add((to_x, to_y))
                    self.update_possible_captures()
                    self.change_turn()
                    return True
                else:
                    return False
        # 2. If by two, then check for capture
        elif fabs(coordinate_x - to_x) <= 2 or fabs(coordinate_y - to_y) <= 2:
            return self.capture(coordinate_x, coordinate_y, to_x, to_y)
        # 3. If by more than two, then it's surely invalid
        else:
            return False

    def capture(self, coordinate_x, coordinate_y, to_x, to_y):
        """
        This function handles capturing if a piece moves by two boxes.
        It calculates coordinates of the square between these two positions,
        and checks whether enemy has got a piece there.
        If so, then this piece should be captured and the move is valid.
        Otherwise, the move is invalid.
        :param int coordinate_x: X coordinate of selected piece.
        :param int coordinate_y: Y coordinate of selected piece.
        :param int to_x: X coordinate of the desired box to move into.
        :param int to_y: Y coordinate of the desired box to move into.
        :return boolean: True for a valid capture, False otherwise.
        """
        med_x = (coordinate_x + to_x) / 2
        med_y = (coordinate_y + to_y) / 2
        if self.turn == self.creator and (med_x, med_y) in self.player_white.positions:
            if (self.player_black.pieces_with_captures and (coordinate_x, coordinate_y) in self.player_black.pieces_with_captures
                    and (to_x, to_y) in self.player_black.pieces_with_captures.get((coordinate_x, coordinate_y))) \
                    or not self.player_black.pieces_with_captures:
                self.player_black.positions.remove((coordinate_x, coordinate_y))
                self.player_black.positions.add((to_x, to_y))
                if (coordinate_x, coordinate_y) in self.player_black.kings:
                    self.player_black.kings.remove((coordinate_x, coordinate_y))
                    self.player_black.kings.add((to_x, to_y))
                self.player_white.positions.remove((med_x, med_y))
                self.player_white.pieces -= 1
                if (med_x, med_y) in self.player_white.kings:
                    self.player_white.kings.remove((med_x, med_y))
                # Update possible captures
                self.update_possible_captures()
            # Check if the moved piece will be able to capture again
            if (to_x, to_y) in self.player_black.pieces_with_captures:
                self.update_possible_captures_for_one(to_x, to_y)
            else:
                self.change_turn()
            return True
        elif self.turn == self.guest and (med_x, med_y) in self.player_black.positions:
            if (self.player_white.pieces_with_captures and (coordinate_x, coordinate_y) in self.player_white.pieces_with_captures) \
                    and (to_x, to_y) in self.player_white.pieces_with_captures.get((coordinate_x, coordinate_y)) \
                    or not self.player_white.pieces_with_captures:
                self.player_white.positions.remove((coordinate_x, coordinate_y))
                self.player_white.positions.add((to_x, to_y))
                if (coordinate_x, coordinate_y) in self.player_white.kings:
                    self.player_white.kings.remove((coordinate_x, coordinate_y))
                    self.player_white.kings.add((to_x, to_y))
                self.player_black.positions.remove((med_x, med_y))
                self.player_black.pieces -= 1
                if (med_x, med_y) in self.player_black.kings:
                    self.player_black.kings.remove((med_x, med_y))
                # Update possible captures
                self.update_possible_captures()
            # Check if the moved piece will be able to capture again
            if (to_x, to_y) in self.player_white.pieces_with_captures:
                self.update_possible_captures_for_one(to_x, to_y)
            else:
                self.change_turn()
            return True

        return False

    def update_possible_captures_for_one(self, coordinate_x, coordinate_y):
        """

        :param coordinate_x:
        :param coordinate_y:
        :return:
        """
        self.player_black.pieces_with_captures.clear()
        self.player_white.pieces_with_captures.clear()

        if (coordinate_x, coordinate_y) in self.player_black.positions:
            possible_captures = self.check_possible_captures(coordinate_x, coordinate_y)
            if possible_captures:
                self.player_black.pieces_with_captures[(coordinate_x, coordinate_y)] = possible_captures
            return True
        elif (coordinate_x, coordinate_y) in self.player_white.positions:
            possible_captures = self.check_possible_captures(coordinate_x, coordinate_y)
            if possible_captures:
                self.player_white.pieces_with_captures[(coordinate_x, coordinate_y)] = possible_captures
            return True
        else:
            return False

    def update_possible_captures(self):
        """

        :return:
        """
        for piece in self.player_black.positions:
            possible_captures = self.check_possible_captures(piece[0], piece[1])
            if possible_captures:
                self.player_black.pieces_with_captures[piece] = possible_captures
        for piece in self.player_white.positions:
            possible_captures = self.check_possible_captures(piece[0], piece[1])
            if possible_captures:
                self.player_white.pieces_with_captures[piece] = possible_captures
        return True

    def check_possible_captures(self, coordinate_x, coordinate_y):
        """
        Checks for all possible captures for a given piece.
        :param coordinate_x:
        :param coordinate_y:
        :return:
        """
        targets = [
            ((coordinate_x + 2), (coordinate_y + 2)),
            ((coordinate_x + 2), (coordinate_y - 2)),
            ((coordinate_x - 2), (coordinate_y + 2)),
            ((coordinate_x - 2), (coordinate_y - 2))
        ]
        mids = [
            ((coordinate_x + targets[0][0]) // 2, (coordinate_y + targets[0][1]) // 2),
            ((coordinate_x + targets[1][0]) // 2, (coordinate_y + targets[1][1]) // 2),
            ((coordinate_x + targets[2][0]) // 2, (coordinate_y + targets[2][1]) // 2),
            ((coordinate_x + targets[3][0]) // 2, (coordinate_y + targets[3][1]) // 2)
        ]

        valid_targets = list()

        for i in range(len(targets)):
            if targets[i][0] in self.board.get_rows() and targets[i][1] in self.board.get_columns():
                if targets[i] not in self.player_black.positions and targets[i] not in self.player_white.positions:
                    if (coordinate_x, coordinate_y) in self.player_black.positions:
                        if targets[i][0] < coordinate_x or \
                                (targets[i][0] > coordinate_x and (coordinate_x, coordinate_y) in self.player_black.kings):
                            if mids[i] in self.player_white.positions:
                                valid_targets.append(targets[i])
                    elif (coordinate_x, coordinate_y) in self.player_white.positions:
                        if targets[i][0] > coordinate_x or \
                                (targets[i][0] < coordinate_x and (coordinate_x, coordinate_y) in self.player_white.kings):
                            if mids[i] in self.player_black.positions:
                                valid_targets.append(targets[i])
        if not valid_targets:
            return False
        return valid_targets

    def update_possible_moves(self):
        """
        Iterate player's pieces and fill the dictionary with all the possible moves.
        :return boolean:
        """
        self.player_black.pieces_with_moves.clear()
        self.player_white.pieces_with_moves.clear()

        for piece in self.player_black.positions:
            possible_moves = self.check_possible_moves(piece[0], piece[1])
            if possible_moves:
                self.player_black.pieces_with_moves[piece] = possible_moves

        for piece in self.player_white.positions:
            possible_moves = self.check_possible_moves(piece[0], piece[1])
            if possible_moves:
                self.player_white.pieces_with_moves[piece] = possible_moves

        return True

    def check_possible_moves(self, coordinate_x, coordinate_y):
        """

        :param int coordinate_x:
        :param int coordinate_y:
        :return boolean|array: Either False or valid_targets array.
        """
        targets_plus_x = [
            ((coordinate_x + 1), (coordinate_y + 1)),
            ((coordinate_x + 1), (coordinate_y - 1))
        ]
        targets_minus_x = [
            ((coordinate_x - 1), (coordinate_y + 1)),
            ((coordinate_x - 1), (coordinate_y - 1))
        ]

        if (coordinate_x, coordinate_y) in self.player_black.positions:
            if (coordinate_x, coordinate_y) in self.player_black.kings:
                targets = targets_plus_x + targets_minus_x
            else:
                targets = targets_minus_x
        elif (coordinate_x, coordinate_y) in self.player_white.positions:
            if (coordinate_x, coordinate_y) in self.player_white.kings:
                targets = targets_plus_x + targets_minus_x
            else:
                targets = targets_plus_x
        else:
            targets = []

        valid_targets = []

        for i in range(len(targets)):
            if targets[i][0] in self.board.get_rows() and targets[i][1] in self.board.get_columns():
                if targets[i] not in self.player_black.positions and targets[i] not in self.player_white.positions:
                    valid_targets.append(targets[i])

        if valid_targets:
            return valid_targets
        return False
