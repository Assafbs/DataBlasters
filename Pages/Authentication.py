import MySQLdb as mdb
from flask import redirect, render_template, request, Blueprint, make_response
from passlib.hash import pbkdf2_sha256
from Common.db_connector import DbConnector
from Common.query_generator import QueryGenerator
import Common.common

err = None  # global error variable

log_in = Blueprint('log_in', __name__, template_folder='templates')
sign_up = Blueprint('sign_up', __name__, template_folder='templates')
log_out = Blueprint('log_out', __name__, template_folder='templates')
new_pass = Blueprint('new_pass', __name__, template_folder='templates')


# Change password.
@new_pass.route('/new_pass', methods=['POST', 'GET'])
def new_password():
    # Validation - user is logged in.
    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    if nickname is None:  # if not logged in - send to home page.
        return redirect('/log_in')
    user_score = Common.common.get_value_from_cookie(request, 'score')  # To show the user's score.

    global err
    err = ''
    nick_cookie = Common.common.get_value_from_cookie(request, 'nickname')
    user_score = Common.common.get_value_from_cookie(request, 'score')
    if float(user_score) > 500 and nickname is not None:
        get_bonus = 'true'
    else:
        get_bonus = ''
    if request.method == 'GET':
        return render_template('new_pass.html', score=user_score, nickname=nickname, bonus=get_bonus)
    elif request.method == 'POST':
        nick = mdb.escape_string(request.form['nickname'])
        if nick_cookie != nick:  # Avoid user from changing another user's password.
            err = "You can only change your own password"
            return render_template('new_pass.html', error=err, score=user_score, nickname=nickname, bonus=get_bonus)  # Display error.
        oldPwd = mdb.escape_string(request.form['oldPwd'])
        newPwd = mdb.escape_string(request.form['newPwd'])
        if oldPwd == newPwd:  # Check that user is actually changing password.
            err = "Your new password is identical to your old one."
            return render_template('new_pass.html', error=err, score=user_score, nickname=nickname, bonus=get_bonus)  # Display error.
        con = DbConnector()
        if authenticate(nick, oldPwd):  # Check user gave his current password.
            hased_new = pbkdf2_sha256.hash(newPwd)  # Hash new password.
            con.execute_query(QueryGenerator.update_password(), (hased_new, nick))  # Update password.
            con.close()
            err = "Congrats! You have a new password!"
            return render_template('new_pass.html', error=err, score=user_score, nickname=nickname, bonus=get_bonus)
        else:
            con.close()
            err = "Nickname or password are invalid. Please try again"
            return render_template('new_pass.html', error=err, score=user_score, nickname=nickname, bonus=get_bonus)


# Log into Mr.Music.
@log_in.route('/log_in', methods=['POST', 'GET'])
def login():
    global err
    err = ''
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        # Get user input:
        nick = mdb.escape_string(request.form['nickname'])
        password = request.form['pwd']
        if authenticate(nick, password):  # Verify the address for nickname.
            query = QueryGenerator.get_score()
            connector = DbConnector()
            data = connector.get_one_result_for_query(query, (nick, nick))  # Get user's score.
            connector.close()
            if data[0] is None:  # User has not played any game yet.
                score = 0
            else:
                score = data[0]
            err = None
            response = make_response(redirect('/'))
            return update_cookies_logged_in(nick, score, response)
        else:
            err = 'Invalid nickname or password. Please try again!\n If you are new to Mr. Music, please sign up'
            return render_template('login.html', error=err)


# Verify user's password.
def authenticate(nick, password):
    if not (is_valid_login_input(nick, password)):
        return False
    connector = DbConnector()
    data = connector.get_one_result_for_query(QueryGenerator.get_user_data(), (nick,))
    connector.close()
    if data is None:
        return False
    else:
        if pbkdf2_sha256.verify(password, data[2]):  # Compares to the hash stored in the users table.
            return True
        return False


# Validation checks for login.
def is_valid_login_input(nick, password):
    global err
    res = nick.isalnum()
    if not res:
        err = "Nickname can contain only numbers and letters"
        return False
    res = password.isalnum()
    if not res:
        err = "Password can contain only numbers and letters"
        return False
    return True


# Validate user input in sign up form.
def is_valid_sign_up_input(nick, email, password):
    global err
    if not nick.isalnum():
        err = "Nickname can contain only numbers and letters"
        return False
    if not password.isalnum():
        err = "Password can contain only numbers and letters"
        return False
    connector = DbConnector()
    data = connector.get_one_result_for_query(QueryGenerator.get_user_data(), (nick,))
    if data is not None:
        err = "This nickname is already taken. Please choose a different one"
        return False
    data = connector.get_one_result_for_query(QueryGenerator.get_email(), (email,))
    if data is not None:
        err = "This email is already in use"
        return False
    connector.close()
    return True


# Logout.
@log_out.route('/log_out')
def logout():
    response = make_response(redirect('/'))
    return update_cookies_logged_out(response)


# Sign up to Mr Music.
@sign_up.route('/sign_up', methods=['POST', 'GET'])
def signup():
    global err
    err = ''
    if request.method == 'GET':
        return render_template('signup.html', error=err)
    elif request.method == 'POST':
        # Get user input:
        nick = mdb.escape_string(request.form['nickname'])
        password = request.form['pwd']  # No need to sanitize - going through hash.
        email = mdb.escape_string(str(request.form['email']))

        if is_valid_sign_up_input(nick, email, password):  # Validate input,
            hash_password = pbkdf2_sha256.hash(password)  # Hash the password,
            connector = DbConnector()
            connector.execute_query(QueryGenerator.sign_in_user(), (nick, email, hash_password))  # Insert new user to users table.
            connector.close()
            err = "You have signed up successfully! Let's Play!"
            response = make_response(redirect('/'))
            return update_cookies_logged_in(nick, 0, response)
        return render_template('signup.html', error=err)


# Store user data (nickname and total score) on cookies.
def update_cookies_logged_in(nick, score, response):
    response.set_cookie('nickname', nick)
    response.set_cookie('score', str(score))
    return response


# Clear cookie from user data.
def update_cookies_logged_out(response):
    response.set_cookie('nickname', '', expires=0)
    response.set_cookie('score', '', expires=0)
    return response
