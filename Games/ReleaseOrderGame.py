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
def release_order_game_start():
    game_manager.start_new_game()

    return create_game_page()


def create_game_page():
    rand_song_row = DbConnector.get_result_for_query(QueryGenerator.get_release_order_question_query())
    rand_song_name = rand_song_row[3]

    album_id = rand_song_row[0]
    release_month = rand_song_row[1]
    release_year = rand_song_row[2]

    answers_rows = DbConnector.get_all_results_for_query_with_args(
        QueryGenerator.get_release_order_answers_query(),
        (release_year, release_month, release_year, release_month, release_year, release_month, release_year, album_id))

    ordered_answers = []
    inserted_rand_song_row = False
    for i in range(3):
        if int(answers_rows[i][0]) > 0 and not inserted_rand_song_row:
            ordered_answers.append(rand_song_name)
            inserted_rand_song_row = True
        ordered_answers.append(answers_rows[i][1])

    rand_order_answers = random.sample(ordered_answers, 4)

    return render_template('ReleaseOrderGame.html',
                           current_score=game_manager.score,
                           question='"' + '",  "'.join(rand_order_answers) + '"',
                           option_1=rand_order_answers[0],
                           option_2=rand_order_answers[1],
                           option_3=rand_order_answers[2],
                           option_4=rand_order_answers[3])