import MySQLdb as mdb
from flask import Flask, redirect, render_template, request, session, url_for, Blueprint, Response
import os
from passlib.hash import pbkdf2_sha256
from db_connector import DbConnector
from query_generator import QueryGenerator

# TODO logout button
# TODO check out html form validation

err = None

log_in= Blueprint('log_in', __name__, template_folder='templates')
sign_up= Blueprint('sign_up', __name__, template_folder='templates')

@log_in.route('/log_in', methods=['POST', 'GET'])
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
            query=QueryGenerator.get_score()
            connector=DbConnector()
            data=connector.get_one_result_for_query(query,(nick,nick))
            if (data[0]==None):
                score=0
            else:
                score=data[0]
                score=1234 #TODO remove this
            session['score']=score
            err = None
            return render_template('home.html', current_score=score)
        else:
            err = 'Invalid nickname or password. Please try again!\n If you are new to Mr. Music, please sign up'
            session['logged_in'] = False
            return render_template('login.html', error=err)


def authenticate(nick, password):
    if not (is_valid_login_input(nick, password)):
        return False
    query="SELECT * FROM users WHERE nickname = %s"
    connector=DbConnector()
    data = connector.get_one_result_for_query(query, (nick,))
    connector.close()
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


#log_in.route('/logout')
#def logout():
#    session['logged_in'] = False
#    session.pop(nickname, None)
#    # pop score
#    return redirect(url_for('home'))


@sign_up.route('/sign_up', methods=['POST', 'GET'])
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
            query = "INSERT INTO users VALUES(%s,%s,%s)"
            connector = DbConnector()
            connector.execute_query(query, (nick, email, hash_password))
            connector.close()
            session['logged_in'] = True
            session['nickname'] = nick
            session['score'] = 0
            err = "You have signed up successfully! Let's play!"
        return render_template('signup.html', error=err)

# def update_cookies_logged_in(nick,score,response):
#     response.set_coockies('nickname',nick)
#     response.set_coockies('logged_in',True)
#     response.set_coockies('score',score)
#     return response
#
# def update_cookies_logged_out(response):
#     response.set_coockies('sessionID','',expires=0)