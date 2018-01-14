import math
from pycheckers import app, utils
from flask import render_template, request, redirect, url_for

board_initialized = utils.Board()
rows = board_initialized.get_rows()
columns = board_initialized.get_columns()

player_black = utils.PlayerBlack()
player_white = utils.PlayerWhite()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/board')
def board():
    return render_template('board.html')


@app.route('/board/select/<int:coordinate_x>/<int:coordinate_y>')
def select(coordinate_x, coordinate_y):
    return render_template('board.html', coordinate_x=coordinate_x, coordinate_y=coordinate_y)


@app.route('/board/select/<int:coordinate_x>/<int:coordinate_y>/move/<int:to_x>/<int:to_y>')
def move(coordinate_x, coordinate_y, to_x, to_y):

    if math.fabs(coordinate_x - to_x) > 1 or math.fabs(coordinate_y - to_y) > 1:
        return redirect(url_for('select', coordinate_x=coordinate_x, coordinate_y=coordinate_y))

    if (coordinate_x, coordinate_y) in player_white.positions:
        player_white.positions.remove((coordinate_x, coordinate_y))
        player_white.positions.add((to_x, to_y))
    elif (coordinate_x, coordinate_y) in player_black.positions:
        player_black.positions.remove((coordinate_x, coordinate_y))
        player_black.positions.add((to_x, to_y))

    return redirect(url_for('board'))


@app.context_processor
def inject_variables():

    return dict(
        rule=str(request.url_rule),
        board={'rows': rows, 'columns': columns},
        player_black=player_black,
        player_white=player_white
    )
