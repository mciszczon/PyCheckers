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

turn = {'black', 'white'}


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

    # TODO: This check should be more sophisticated with user turns implemented.
    if coordinate_x in board_initialized.get_rows() and coordinate_y in board_initialized.get_columns():
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

    if math.fabs(coordinate_x - to_x) != 1 or math.fabs(coordinate_y - to_y) != 1\
            or to_x not in board_initialized.get_rows() or to_y not in board_initialized.get_columns()\
            or (to_x, to_y) in player_white.positions or (to_x, to_y) in player_black.positions:
        return redirect(url_for('select', coordinate_x=coordinate_x, coordinate_y=coordinate_y))

    # TODO: This should happen based on which player's turn it is.
    if (coordinate_x, coordinate_y) in player_white.positions:
        player_white.positions.remove((coordinate_x, coordinate_y))
        player_white.positions.add((to_x, to_y))
    elif (coordinate_x, coordinate_y) in player_black.positions:
        player_black.positions.remove((coordinate_x, coordinate_y))
        player_black.positions.add((to_x, to_y))

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
        player_white=player_white
    )
