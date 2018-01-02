from flask import Flask, render_template, redirect, url_for, request, make_response,session
import MySQLdb as mdb
import random

app = Flask(__name__) # TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging


@app.route('/releaseOrderGame')
def calcQuestionAndAns():
    score = 0




# TODO: delete the / route, this is just for debugging
@app.route('/')
def hello_world():
    return 'Hello World!'

# TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging
if __name__ == '__main__':
    app.run()
