from flask import Flask, render_template, redirect, url_for, request, make_response,session
import MySQLdb as mdb
import random

app = Flask(__name__) # TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging



@app.route('/release-order-game')
def calcQuestionAndAns():
    score = 0
    return render_template('ReleaseOrderGame.html',
                           current_score=score,
                           question='question',
                           option_1='option_1',
                           option_2='option_2',
                           option_3='option_3',
                           option_4='option_4')




# TODO: delete the / route, this is just for debugging
@app.route('/')
def hello_world():
    return 'Hello World!'

# TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging
if __name__ == '__main__':
    app.run()
