from flask import Flask, render_template, redirect, url_for, request, make_response,session, Blueprint
import MySQLdb as mdb
import random
import GameManager
from db_connector import DbConnector
from query_generator import QueryGenerator


NUM_QUESTIONS_PER_GAME = 5
game_manager = GameManager.GameManager()


release_order_game = Blueprint('release_order_game', __name__, template_folder='templates')
@release_order_game.route('/release_order_game')
def calcQuestionAndAns():
    score = 0

    rand_song_row = DbConnector.get_result_for_query(QueryGenerator.get_release_order_question_query())
    # SELECT albums.album_id, albums.release_month, albums.release_year, songs.name  TODO del
    rand_song_name = rand_song_row[3]

    return render_template('ReleaseOrderGame.html',
                           current_score=score,
                           question='question',
                           option_1=rand_song_name,
                           option_2='song2',
                           option_3='song3',
                           option_4='song4')


