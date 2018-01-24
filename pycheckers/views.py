"""
This is Views module.
It allows Flask to run properly, as it stores its routing and template rendering settings.
"""
import math
import uuid
import pickle
from pycheckers import app
from .resources import Game, Board
from flask import render_template, request, redirect, url_for, flash

app.secret_key = 'C~\xb2\x95\x00:\xca\xc8b\x83\x89\xee\xf7)w&\xed\x96\xbe\x13\xfd\x88\x92\x81'

games = dict()
board = Board.Board()


# def load_games():
#     games = pickle.load(open('games.p', 'rb'))
#
#
# @app.route('/save')
# def save():
#     pickle.dump(games, open('games.p', 'wb'))
#
#
# @app.route('/load')
# def load():
#     load_games()


@app.route('/')
def index():
    """
    A view that displays the homepage.
    :return render_template():
    """
    return render_template('index.html')


@app.route('/start', methods=['POST', 'GET'])
def start():
    if request.method == 'POST':
        name = request.form['name']
        gametype = request.form['gametype']
        if name and gametype:
            return redirect(url_for('create', name=name))
    return render_template('start.html')


@app.route('/create/<string:name>')
def create(name):
    game_id = str(uuid.uuid4())
    games[game_id] = (Game.Game(name))
    flash('Game started!', 'success')

    return redirect(url_for('game', game_id=game_id))


@app.route('/games')
def active_games():
    return render_template('games.html', games=games)


@app.route('/game/<string:game_id>')
def game(game_id):
    """
    A basic view that just generates the board.
    :return render_template():
    """
    if games.get(game_id):
        return render_template('board.html', game_id=game_id)
    else:
        flash('Such a game does not exist. It might have ended.', 'error')
        return redirect(url_for('index'))


@app.route('/game/<string:game_id>/select/<int:coordinate_x>/<int:coordinate_y>')
def select(game_id, coordinate_x, coordinate_y):
    """
    A view that handles player selecting one of his pieces.
    :param int coordinate_x: This is a x coordinate of the piece that player selected.
    :param int coordinate_y: This is a y coordinate of the piece that player selected.
    :return render_template() or redirect():
    """

    if games[game_id].turn == 0 and (coordinate_x, coordinate_y) in games[game_id].player_black.positions\
            or games[game_id].turn == 1 and (coordinate_x, coordinate_y) in games[game_id].player_white.positions:
        return render_template('board.html', game_id=game_id, coordinate_x=coordinate_x, coordinate_y=coordinate_y)
    else:
        flash('You cannot select this piece!', 'error')
        return redirect(url_for('game', game_id=game_id))


@app.route('/game/<string:game_id>/select/<int:coordinate_x>/<int:coordinate_y>/move/<int:to_x>/<int:to_y>')
def move(game_id, coordinate_x, coordinate_y, to_x, to_y):
    """
    A view that handles moving a piece from one box to another.
    :param int coordinate_x: This is a x coordinate of the piece we want to move.
    :param int coordinate_y: This is a y coordinate of the piece we want to move.
    :param int to_x: This is a x coordinate of the box to which we want to move the piece.
    :param int to_y: This is a y coordinate of the box to which we want to move the piece.
    :return redirect():
    """

    # Checking whether move is allowed
    # 1. Not outside the board
    if to_x not in board.get_rows() or to_y not in board.get_columns() \
            or (to_x, to_y) in games[game_id].player_white.positions or (to_x, to_y) in games[game_id].player_black.positions:
        flash('This move is invalid!', 'error')
        return redirect(url_for('select', game_id=game_id, coordinate_x=coordinate_x, coordinate_y=coordinate_y))

    # 2. Only into gray boxes
    if not board.check_if_allowed(to_x, to_y):
        flash('This move is invalid!', 'error')
        return redirect(url_for('select', game_id=game_id, coordinate_x=coordinate_x, coordinate_y=coordinate_y))

    # 3. Not onto other pieces
    if (coordinate_x, coordinate_y) not in games[game_id].player_black.positions\
        and (coordinate_x, coordinate_y) not in games[game_id].player_white.positions:
        flash('This move is invalid!', 'error')
        return redirect(url_for('select', game_id=game_id, coordinate_x=coordinate_x, coordinate_y=coordinate_y))

    # 3.A. If not kings, pieces cannot move backwards
    if (games[game_id].turn == 0 and (coordinate_x, coordinate_y) not in games[game_id].player_black.kings
            and coordinate_x <= to_x)\
            or (games[game_id].turn == 1 and (coordinate_x, coordinate_y) not in games[game_id].player_white.kings
                and coordinate_x >= to_x):
        flash('This move is invalid!', 'error')
        return redirect(url_for('select', game_id=game_id, coordinate_x=coordinate_x, coordinate_y=coordinate_y))

    # 4. By how far
    # 4.1. Black player
    if games[game_id].turn == 0 and (coordinate_x, coordinate_y) in games[game_id].player_black.positions:
        # 1. If by one, it's okay
        if math.fabs(coordinate_x - to_x) <= 1 and math.fabs(coordinate_y - to_y) <= 1:
            games[game_id].player_black.positions.remove((coordinate_x, coordinate_y))
            games[game_id].player_black.positions.add((to_x, to_y))
            if (coordinate_x, coordinate_y) in games[game_id].player_black.kings:
                games[game_id].player_black.kings.remove((coordinate_x, coordinate_y))
                games[game_id].player_black.kings.add((to_x, to_y))
            games[game_id].change_turn()
        # 2. If by two, then check if it is a valid capture
        elif math.fabs(coordinate_x - to_x) <= 2 or math.fabs(coordinate_y - to_y) <= 2:
            med_x = (coordinate_x + to_x) / 2
            med_y = (coordinate_y + to_y) / 2
            if (med_x, med_y) in games[game_id].player_white.positions:
                games[game_id].player_black.positions.remove((coordinate_x, coordinate_y))
                games[game_id].player_black.positions.add((to_x, to_y))
                if (coordinate_x, coordinate_y) in games[game_id].player_black.kings:
                    games[game_id].player_black.kings.remove((coordinate_x, coordinate_y))
                    games[game_id].player_black.kings.add((to_x, to_y))
                games[game_id].player_white.positions.remove((med_x, med_y))
                games[game_id].player_white.pieces -= 1
                if (med_x, med_y) in games[game_id].player_white.kings:
                    games[game_id].player_white.kings.remove((med_x, med_y))
                games[game_id].change_turn()
                flash('A piece was captured!', 'black')
            else:
                flash('This move is invalid!', 'error')
                return redirect(url_for('select', game_id=game_id, coordinate_x=coordinate_x, coordinate_y=coordinate_y))
        # 3. If by more than two, then it's surely invalid
        else:
            flash('This move is invalid!', 'error')
            return redirect(url_for('select', game_id=game_id, coordinate_x=coordinate_x, coordinate_y=coordinate_y))

    # 4.2. White player
    elif games[game_id].turn == 1 and (coordinate_x, coordinate_y) in games[game_id].player_white.positions:
        # 1. If by one, it's okay
        if math.fabs(coordinate_x - to_x) <= 1 and math.fabs(coordinate_y - to_y) <= 1:
            games[game_id].player_white.positions.remove((coordinate_x, coordinate_y))
            games[game_id].player_white.positions.add((to_x, to_y))
            if (coordinate_x, coordinate_y) in games[game_id].player_white.kings:
                games[game_id].player_white.kings.remove((coordinate_x, coordinate_y))
                games[game_id].player_white.kings.add((to_x, to_y))
            games[game_id].change_turn()
        # 2. If by two, then check if it is a valid capture
        elif math.fabs(coordinate_x - to_x) <= 2 or math.fabs(coordinate_y - to_y) <= 2:
            med_x = (coordinate_x + to_x) / 2
            med_y = (coordinate_y + to_y) / 2
            if (med_x, med_y) in games[game_id].player_black.positions:
                games[game_id].player_white.positions.remove((coordinate_x, coordinate_y))
                games[game_id].player_white.positions.add((to_x, to_y))
                if (coordinate_x, coordinate_y) in games[game_id].player_white.kings:
                    games[game_id].player_white.kings.remove((coordinate_x, coordinate_y))
                    games[game_id].player_white.kings.add((to_x, to_y))
                games[game_id].player_black.positions.remove((med_x, med_y))
                games[game_id].player_black.pieces -= 1
                if (med_x, med_y) in games[game_id].player_black.kings:
                    games[game_id].player_black.kings.remove((med_x, med_y))
                games[game_id].change_turn()
                flash('A piece was captured!', 'black')
            else:
                flash('This move is invalid!', 'error')
                return redirect(url_for('select', game_id=game_id, coordinate_x=coordinate_x, coordinate_y=coordinate_y))
        # 3. If by more than two, then it's surely invalid
        else:
            flash('This move is invalid!', 'error')
            return redirect(url_for('select', game_id=game_id, coordinate_x=coordinate_x, coordinate_y=coordinate_y))

    # Check whether there are pieces to turn into kings
    for piece in games[game_id].player_black.positions:
        if piece[0] == 0:  # Row is 0, so black player has a piece at white's base
            games[game_id].player_black.kings.add(piece)
            flash('A Black King crowned!', 'black')

    for piece in games[game_id].player_white.positions:
        if piece[0] == 7:  # Row is 7, so white player has a piece at black's base
            games[game_id].player_white.kings.add(piece)
            flash('A White King crowned!', 'black')

    # Check whether there's a player with no pieces left
    if not games[game_id].player_black.pieces:
        flash('White Player wins the match! Congratulations!', 'success')
    elif not games[game_id].player_white.pieces:
        flash('Black Player wins the match! Congratulations!', 'success')

    return redirect(url_for('game', game_id=game_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.context_processor
def inject_variables():
    """
    Injects variables into every view.
    Right now it is a very ugly workaround, but just for now.
    :return dict:
    """

    rule = str(request.url_rule)

    if 'game/' in rule:
        s = request.url.split('/')
        game_id = s[s.index('game')+1]
        return dict(
            rule=rule,
            name=games[game_id].name,
            board={'rows': games[game_id].rows, 'columns': games[game_id].rows},
            player_black=games[game_id].player_black,
            player_white=games[game_id].player_white,
            turn=games[game_id].turn
        )
    else:
        return dict(
            rule=rule
        )
