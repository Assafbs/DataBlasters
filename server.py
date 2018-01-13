import MySQLdb as mdb
from flask import Flask, redirect, render_template, request, session, url_for
import os
from passlib.hash import pbkdf2_sha256
from db_connector import DbConnector
import query_generator

# TODO logout button
# TODO check out html form validation
# TODO get score on login

# db= mdb.connect('localhost','root','root','dbmysql09')
# cursor = db.cursor()
err = None

login_signup = Blueprint('login_signup', __name__, template_folder='templates')
login_signup.route('/') #might need to change
def home():
    if not session.get('logged_in'):
        user_score=session.get('score')
        return render_template('home.html')
    else:
        return render_template('home.html', current_score=user_score)


login_signup.route('/login', methods=['POST', 'GET'])
def login():
    global err
    err = ''
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        nick = mdb.escape_string(request.form['nickname'])  # avoid injection
        password = request.form['pwd']
        if authenticate(nick, password):
            session['logged_in'] = True
            session['nickname'] = nick
            err = None
            # get total score
        else:
            err = 'Invalid nickname or password. Please try again!\n If you are new to Mr. Music, please sign up'
            session['logged_in'] = False
            return render_template('login.html', error=err)
        return redirect(url_for('home'))


def authenticate(nick, password):
    if not (is_valid_login_input(nick, password)):
        return False
    # safe selection
    # query = "SELECT * FROM users WHERE nickname=%s"
    # cursor.execute(query, (nick,))  # can change to hash_password instead of *
    # data = cursor.fetchone()
    data = DbConnector.get_result_for_query_with_args("SELECT * FROM users WHERE nickname = %s", (nick,))
    if data is None:
        return False
    else:
        if pbkdf2_sha256.verify(password, data[2]):
            return True
        return False


def is_valid_login_input(nick, password):
    global err
    if len(nick) == 0 or len(password) == 0:
        err = "Please, fill all fields"
        return False
    res = nick.isalnum()
    if not res:
        err = "Nickname can contain only numbers and letters"
        return False
    res = password.isalnum()
    if not res:
        err = "Password can contain only numbers and letters"
        return False
    return True


def id_valid_sign_up_input(nick, email, password):
    # validate nick
    global err
    if len(nick) > 20:
        err = "Nickname is too long"
        return False
    if len(nick) == 0 or len(email) == 0 or len(password) == 0:
        err = "Please, fill all fields"
        return False
    if len(password) > 20:
        err = "Password is too long"
        return False
    if not nick.isalnum():
        err = "Nickname can contain only numbers and letters"
        return False
    if not password.isalnum():
        err = "Password can contain only numbers and letters"
        return False
    return True


login_signup.route('/logout')
def logout():
    session['logged_in'] = False
    session.pop(['nickname'], None)
    # pop score
    return redirect(url_for('home'))


login_signup.route('/sign_up', methods=['POST', 'GET'])
def signup():
    global err
    err = ''
    if request.method == 'GET':
        return render_template('signup.html', error=err)
    elif request.method == 'POST':
        nick = mdb.escape_string(request.form['nickname'])
        password = request.form['pwd']  # no need to sanitize. going through hash
        email = mdb.escape_string(str(request.form['email']))

        if id_valid_sign_up_input(nick, email, password):
            hash_password = pbkdf2_sha256.hash(password)
            length = len(hash_password)
            query = "INSERT INTO dbmysql09.users VALUES(%s,%s,%s)"
            connector = DbConnector()
            connector.execute_query(query, (nick, email, hash_password))
            query = "INSET INTO dbmysql09.score VALUES(%s,%s,%s,%s)"
            connector.execute_query(query,(nick,))
            session['logged_in'] = True
            session['nickname'] = nick
            err = "You have signed up successfully! Let's play!"
        return render_template('signup.html', error=err)


login_signup.route('/highscores', )
def highscores():
    return render_template('highscores.html')


login_signup.route('/game_selection', )
def levels():
    return render_template('game_selection.html')


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='0.0.0.0', port=8888)
