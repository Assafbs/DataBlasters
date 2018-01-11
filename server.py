import MySQLdb as mdb
from flask import Flask, redirect, render_template, request, session, url_for
import os
from passlib.hash import pbkdf2_sha256

#TODO logout button
#TODO check out html form validation
#TODO get score on login

app = Flask(__name__)

db= mdb.connect('localhost','root','root','dbmysql09')
cursor = db.cursor()
err = None

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('home.html', current_score=0)#change to total score
    else:
        return render_template('home.html', current_score=1234)


@app.route('/login', methods=['POST','GET'])
def login():
    global err
    err = ''
    if request.method=='GET':
        return render_template('login.html')
    elif request.method=='POST':
        nick =mdb.escape_string(request.form['nickname']) #avoid injection
        password = request.form['pwd']
        if (authenticate(nick,password)):
            session['logged_in'] = True
            session['nickname'] = nick
            err = None
            #get total score
        else:
            err = 'Invalid nickname or password. Please try again!\n If you are new to Mr. Music, please sign up'
            session['logged_in'] = False
            return render_template('login.html', error= err)
        return redirect(url_for('home'))

def authenticate(nick,password):
    if not(is_valid_login_input(nick,password)):
        return False
    #safe selection
    query="SELECT * FROM users WHERE nickname=%s"
    cursor.execute(query,(nick,)) #can change to hash_password instead of *
    data = cursor.fetchone()
    if data is None:
        return False
    else:
        if pbkdf2_sha256.verify(password,data[2]):
            return True
        return False

def is_valid_login_input(nick,password):
    global err
    if len(nick)==0 or len(password)==0:
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

def id_vailid_sign_up_input(nick,email,password):
    #validate nick
    global err
    if len(nick)>20:
        err = "Nickname is too long"
        return False
    if len(nick) == 0 or len(email) == 0 or len(password) == 0:
        err = "Please, fill all fields"
        return False
    if len(password)>20:
        err = "Password is too long"
        return False
    if not nick.isalnum():
        err = "Nickname can contain only numbers and letters"
        return False
    if not password.isalnum():
        err = "Password can contain only numbers and letters"
        return False
    return True

@app.route('/logout')
def logout():
    session['logged_in'] = False
    session.pop(['nickname'],None)
    #pop score
    return redirect(url_for('home'))

@app.route('/signup',methods=['POST','GET'])
def signup():
    global err
    err=''
    if request.method == 'GET':
        return render_template('signup.html', error=err)
    elif request.method == 'POST':
        nick=mdb.escape_string(request.form['nickname'])
        password=request.form['pwd'] #no need to sanitize. going through hash
        email=mdb.escape_string(str(request.form['email']))

        if (id_vailid_sign_up_input(nick,email,password)):
            hash_password=pbkdf2_sha256.hash(password)
            length= len(hash_password)
            query="INSERT INTO dbmysql09.users values(%s,%s,%s)"
            cursor.execute(query,(nick,email,hash_password))
            db.commit()
            session['logged_in'] = True
            session['nickname'] = nick
            err = "You have signed up successfully! Let's play!"
        return render_template('signup.html', error = err)


@app.route('/hishscores',)
def hiscores():
    return render_template('hishscores.html')

@app.route('/levels',)
def levels():
    return render_template('levels.html')

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='0.0.0.0', port=8888)