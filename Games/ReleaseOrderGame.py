from flask import Flask, render_template, redirect, url_for, request, make_response,session, Blueprint
import MySQLdb as mdb
import random


release_order_game = Blueprint('release_order_game', __name__, template_folder='templates')
@release_order_game.route('/release_order_game')
def calcQuestionAndAns():
    score = 0
    return render_template('ReleaseOrderGame.html',
                           current_score=score,
                           question='question',
                           option_1='option_1',
                           option_2='option_2',
                           option_3='option_3',
                           option_4='option_4')

