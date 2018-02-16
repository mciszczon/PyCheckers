"""
This is Views module.
It allows Flask to run properly, as it stores its routing and template rendering settings.
"""
import os
import pickle
import uuid
from datetime import date
from pycheckers import app, db, bcrypt, login_manager
from flask import render_template, request, redirect, url_for, flash, g, abort, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.exc import IntegrityError
from .resources.Game import Game
from .resources.User import User
from .resources.Utils import is_safe_url, check_for_access, check_for_existence, check_for_guest

games = dict()
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def index():
    """
    A view that displays the homepage.
    :return render_template():
    """
    return render_template('index.html')


@app.route('/license')
def license():
    """
    A view that displays the license.
    :return render_template():
    """
    return render_template('license.html', year=date.today().year)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    registered_user = User.query.filter_by(username=username).first()

    if registered_user is None or not bcrypt.check_password_hash(registered_user.password, request.form['password']):
        flash('Username or password is invalid', 'error')
        return redirect(url_for('login'))

    remember_me = False
    if 'remember_me' in request.form:
        remember_me = True
    login_user(registered_user, remember=remember_me)
    flash('Logged in successfully!', 'success')

    next = request.args.get('next')
    if not is_safe_url(next):
        return abort(400)
    return redirect(next or url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        error = dict()
        if request.form['username'] and request.form['password'] and request.form['repeat-password']:
            if len(request.form['password']) < 6:
                error['password-short'] = 'Password must be at least 6 characters long.'
                flash(error['password-short'], 'error')
            if request.form['password'] != request.form['repeat-password']:
                error['password-different'] = 'Passwords do not match.'
                flash(error['password-different'], 'error')

            password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            user = User(request.form['username'], password)
            try:
                db.session.add(user)
                db.session.commit()
                flash('Registered in successfully.', 'success')
                return redirect(url_for('index'))
            except IntegrityError:
                db.session.rollback()
                error['username-taken'] = 'This username is already taken.'
                flash(error['username-taken'], 'error')

            return render_template('register.html', error=error)
        else:
            flash('Fill all the inputs, please.', 'error')
            return render_template('register.html')
    else:
        return render_template('register.html')


@app.route('/profile')
@login_required
def profile():
    user_games = dict()
    for single_game in games:
        if current_user.id in (games[single_game].creator, games[single_game].guest):
            user_games[single_game] = games[single_game]

    return render_template('profile.html', user=current_user, games=user_games)


@app.route('/new-game', methods=['POST', 'GET'])
@login_required
def start():
    if request.method == 'POST':
        name = request.form['name']
        gametype = request.form['gametype']
        private = request.form['private']
        creator = current_user.id
        if name and gametype and private:
            if private == 'public':
                private = False
            elif private == 'private':
                private = True

            game_id = str(uuid.uuid4())
            games[game_id] = (Game(game_id, name, gametype, private, creator))
            flash('Game started!', 'success')
            if not games[game_id].save_game():
                flash('Error occurred while saving the game!', 'error')
            return redirect(url_for('game', game_id=game_id))
    return render_template('start.html')


@app.route('/games')
@login_required
def active_games():
    public_games = dict()
    for single_game in games:
        if games[single_game].private is False:
            public_games[single_game] = games[single_game]

    users_with_games = dict()
    for single_game in public_games:
        users_with_games[public_games[single_game].creator] = User.query.get(public_games[single_game].creator)
    return render_template('games.html', games=public_games, users=users_with_games)


@app.route('/game/<string:game_id>')
@login_required
def game(game_id):
    """
    A basic view that just generates the board.
    :return render_template():
    """
    if not check_for_existence(games, game_id):
        flash('Such a game does not exist. It might have ended.', 'error')
        return redirect(url_for('index'))
    if not check_for_access(games[game_id], current_user.id):
        flash('You have no access to this game.', 'error')
        return redirect(url_for('active_games'))

    return render_template('board.html', game_id=game_id)


@app.route('/game/<string:game_id>/join')
@login_required
def join(game_id):
    if check_for_existence(games, game_id):
        # No guest and current_user is not creator. All is OK.
        if games[game_id].guest is False and current_user.id != games[game_id].creator:
            games[game_id].set_guest(current_user.id)
            flash('You have joined this game and play as White Player!', 'success')
            games[game_id].save_timestamp()
            if not games[game_id].save_game():
                flash('Error occurred while saving the game!', 'error')
            return redirect(url_for('game', game_id=game_id))
        # There is a guest, or no guest and current_user is creator. Not OK to join.
        elif games[game_id].guest is True or current_user.id == games[game_id].creator:
            flash('You cannot join this game!', 'error')
            return redirect(url_for('game', game_id=game_id))

        if not check_for_access(games[game_id], current_user.id):
            flash('You have no access to this game.', 'error')
            return redirect(url_for('active_games'))
    else:
        flash('Such a game does not exist. It might have ended.', 'error')
        return redirect(url_for('index'))

@app.route('/game/<string:game_id>/select/<int:coordinate_x>/<int:coordinate_y>')
@login_required
def select(game_id, coordinate_x, coordinate_y):
    """
    A view that handles player selecting one of his pieces.
    :param int coordinate_x: This is a x coordinate of the piece that player selected.
    :param int coordinate_y: This is a y coordinate of the piece that player selected.
    :return render_template() or redirect():
    """

    if not check_for_existence(games, game_id):
        flash('Such a game does not exist. It might have ended.', 'error')
        return redirect(url_for('index'))

    if not check_for_access(games[game_id], current_user.id):
        flash('You have no access to this game.', 'error')
        return redirect(url_for('active_games'))

    if not check_for_guest(games[game_id]):
        flash('You must first have an opponent to play with!', 'error')
        return redirect(url_for('game', game_id=game_id))

    if games[game_id].check_select(coordinate_x, coordinate_y, current_user.id):
        return render_template('board.html', game_id=game_id, coordinate_x=coordinate_x, coordinate_y=coordinate_y)
    else:
        flash('You cannot select this piece!', 'error')
        return redirect(url_for('game', game_id=game_id))


@app.route('/game/<string:game_id>/select/<int:coordinate_x>/<int:coordinate_y>/move/<int:to_x>/<int:to_y>')
@login_required
def move(game_id, coordinate_x, coordinate_y, to_x, to_y):
    """
    A view that handles moving a piece from one box to another.
    :param int coordinate_x: This is a x coordinate of the piece we want to move.
    :param int coordinate_y: This is a y coordinate of the piece we want to move.
    :param int to_x: This is a x coordinate of the box to which we want to move the piece.
    :param int to_y: This is a y coordinate of the box to which we want to move the piece.
    :return redirect():
    """

    if not check_for_existence(games, game_id):
        flash('Such a game does not exist. It might have ended.', 'error')
        return redirect(url_for('index'))

    if not check_for_access(games[game_id], current_user.id):
        flash('You have no access to this game.', 'error')
        return redirect(url_for('active_games'))

    if not check_for_guest(games[game_id]):
        flash('You must first have an opponent to play with!', 'error')
        return redirect(url_for('game', game_id=game_id))

    if not games[game_id].check_select(coordinate_x, coordinate_y, current_user.id):
        flash('You cannot select this piece!', 'error')
        return redirect(url_for('game', game_id=game_id))

    # Checking whether move is allowed
    # 1. Not outside the board
    if to_x not in games[game_id].board.get_rows() or to_y not in games[game_id].board.get_columns():
        flash('This move is invalid!', 'error')
        return redirect(url_for('select', game_id=game_id, coordinate_x=coordinate_x, coordinate_y=coordinate_y))

    # 2. Only into gray boxes
    if not games[game_id].board.check_if_allowed(to_x, to_y):
        flash('This move is invalid!', 'error')
        return redirect(url_for('select', game_id=game_id, coordinate_x=coordinate_x, coordinate_y=coordinate_y))

    # 3. Not onto other pieces
    if (to_x, to_y) in games[game_id].player_white.positions or (to_x, to_y) in games[game_id].player_black.positions:
        flash('This move is invalid!', 'error')
        return redirect(url_for('select', game_id=game_id, coordinate_x=coordinate_x, coordinate_y=coordinate_y))

    # 3.A. If not kings, pieces cannot move backwards
    if (games[game_id].turn == games[game_id].creator and (coordinate_x, coordinate_y) not in games[game_id].player_black.kings
            and coordinate_x <= to_x):
        flash('This move is invalid! Only kings can move backwards.', 'error')
        return redirect(url_for('select', game_id=game_id, coordinate_x=coordinate_x, coordinate_y=coordinate_y))
    if (games[game_id].turn == games[game_id].guest and (coordinate_x, coordinate_y) not in games[game_id].player_white.kings
            and coordinate_x >= to_x):
        flash('This move is invalid! Only kings can move backwards.', 'error')
        return redirect(url_for('select', game_id=game_id, coordinate_x=coordinate_x, coordinate_y=coordinate_y))

    # Handle move, finally
    if games[game_id].handle_move(coordinate_x, coordinate_y, to_x, to_y):
        # Check whether there are pieces to turn into kings
        if games[game_id].add_kings():
            flash('A King crowned!', 'black')
        if not games[game_id].save_game():
            flash('Error occurred while saving the game!', 'error')
    else:
        flash('This move is invalid!', 'error')
        return redirect(url_for('select', game_id=game_id, coordinate_x=coordinate_x, coordinate_y=coordinate_y))

    # Check whether there's a player with no pieces left
    if games[game_id].check_status() == 'win-black':
        flash('Black Player wins the match! Congratulations!', 'success')
    elif games[game_id].check_status() == 'win-white':
        flash('White Player wins the match! Congratulations!', 'success')

    return redirect(url_for('game', game_id=game_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/_check_timestamp')
def check_timestamp():
    game_id = request.args.get('game_id', '0', type=str)
    if game_id in games:
        return jsonify(timestamp=games[game_id].get_timestamp())

    return jsonify(timestamp=0, error='Could not get the timestamp!')


@app.before_request
def before_request():
    g.user = current_user


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
            game_id=game_id,
            url=request.url,
            rule=rule,
            name=games[game_id].name,
            private=games[game_id].private,
            board={'rows': games[game_id].rows, 'columns': games[game_id].rows},
            player_black=games[game_id].player_black,
            player_white=games[game_id].player_white,
            turn=games[game_id].turn,
            round=games[game_id].round,
            creator=User.query.filter_by(id=games[game_id].creator).first(),
            guest=User.query.filter_by(id=games[game_id].guest).first(),
            game=games[game_id]
        )
    else:
        return dict(
            rule=rule
        )
