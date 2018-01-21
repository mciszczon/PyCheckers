"""
This is Views module.
It allows Flask to run properly, as it stores its routing and template rendering settings.
"""
import math
from pycheckers import app, utils
from flask import render_template, request, redirect, url_for

# TODO: Move variables from below to a new Game object.
# TODO: Allow to create multiple instances of the Game object (store as objects in array).
board_initialized = utils.Board()
rows = board_initialized.get_rows()
columns = board_initialized.get_columns()

player_black = utils.PlayerBlack()
player_white = utils.PlayerWhite()


@app.route('/')
def index():
    """
    A view that displays the homepage.
    :return render_template():
    """

    return render_template('index.html')


@app.route('/board')
def board():
    """
    A basic view that just generates the board.
    :return render_template():
    """

    return render_template('board.html')


@app.route('/board/select/<int:coordinate_x>/<int:coordinate_y>')
def select(coordinate_x, coordinate_y):
    """
    A view that handles player selecting one of his pieces.
    :param int coordinate_x: This is a x coordinate of the piece that player selected.
    :param int coordinate_y: This is a y coordinate of the piece that player selected.
    :return render_template() or redirect():
    """

    if board_initialized.turn == 0 and (coordinate_x, coordinate_y) in player_black.positions\
            or board_initialized.turn == 1 and (coordinate_x, coordinate_y) in player_white.positions:
        return render_template('board.html', coordinate_x=coordinate_x, coordinate_y=coordinate_y)
    else:
        return redirect(url_for('board'))


@app.route('/board/select/<int:coordinate_x>/<int:coordinate_y>/move/<int:to_x>/<int:to_y>')
def move(coordinate_x, coordinate_y, to_x, to_y):
    """
    A view that handles moving a piece from one box to another.
    :param int coordinate_x: This is a x coordinate of the piece we want to move.
    :param int coordinate_y: This is a y coordinate of the piece we want to move.
    :param int to_x: This is a x coordinate of the box to which we want to move the piece.
    :param int to_y: This is a y coordinate of the box to which we want to move the piece.
    :return redirect():
    """

    # Checking whether move is allowed
    # 1. By one square only
    if math.fabs(coordinate_x - to_x) != 1 or math.fabs(coordinate_y - to_y) != 1\
            or to_x not in board_initialized.get_rows() or to_y not in board_initialized.get_columns()\
            or (to_x, to_y) in player_white.positions or (to_x, to_y) in player_black.positions:
        return redirect(url_for('select', coordinate_x=coordinate_x, coordinate_y=coordinate_y))

    # 2. Only into gray boxes
    if not board_initialized.check_if_allowed(to_x, to_y):
        return redirect(url_for('select', coordinate_x=coordinate_x, coordinate_y=coordinate_y))
    if (coordinate_x, coordinate_y) not in player_black.kings\
        and (coordinate_x, coordinate_y) not in player_white.kings\
            and (board_initialized.turn == 0 and coordinate_x <= to_x
                 or board_initialized.turn == 1 and coordinate_x >= to_x):
        return redirect(url_for('select', coordinate_x=coordinate_x, coordinate_y=coordinate_y))

    if board_initialized.turn == 0 and (coordinate_x, coordinate_y) in player_black.positions:
        player_black.positions.remove((coordinate_x, coordinate_y))
        player_black.positions.add((to_x, to_y))
        board_initialized.change_turn()
    elif board_initialized.turn == 1 and (coordinate_x, coordinate_y) in player_white.positions:
        player_white.positions.remove((coordinate_x, coordinate_y))
        player_white.positions.add((to_x, to_y))
        board_initialized.change_turn()

    # Check whether there are pieces to turn into kings
    for piece in player_black.positions:
        if piece[0] == 0:  # Row is 0, so black player has a piece at white's base
            player_black.kings.add(piece)

    for piece in player_white.positions:
        if piece[0] == 7:  # Row is 7, so white player has a piece at black's base
            player_white.kings.add(piece)

    return redirect(url_for('board'))


@app.context_processor
def inject_variables():
    """
    Injects variables into every view.
    Right now it is a very ugly workaround, but just for now.
    :return dict:
    """
    return dict(
        rule=str(request.url_rule),
        board={'rows': rows, 'columns': columns},
        player_black=player_black,
        player_white=player_white,
        turn=board_initialized.turn
    )
