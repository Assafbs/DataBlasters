from flask import Flask, render_template, redirect, url_for, request, make_response,session, Blueprint
import random
import GameManager
import sys
from db_connector import DbConnector
from query_generator import QueryGenerator


NUM_QUESTIONS_PER_GAME = 5
game_manager = GameManager.GameManager()

err = None
ordered_answers = []
curr_question_points = 0


release_order_game = Blueprint('release_order_game', __name__, template_folder='templates')
@release_order_game.route('/release_order_game',  methods=['POST','GET'])
def release_order_game_start():
    return handle_route(request)


release_order_game_ = Blueprint('release_order_game_', __name__, template_folder='templates')
@release_order_game_.route('/release_order_game_',  methods=['POST','GET'])
def release_order_game_mid():
    allow_access = request.cookies.get('allowAccess')
    global curr_question_points
    response = game_manager.calc_mid_game(allow_access, curr_question_points, NUM_QUESTIONS_PER_GAME)

    if response is None:
        return handle_route(request)
    else:
        return response


def handle_route(request):
    if request.method == 'GET':
        game_manager.start_new_game()
        return create_game_page()
    elif request.method == 'POST':
        global ordered_answers
        user_ordered_answers = [request.form['song1'], request.form['song2'],
                                request.form['song3'], request.form['song4']]
        num_correct_songs = 0
        for i in range(4):
            if user_ordered_answers[i] == ordered_answers[i]:
                num_correct_songs += 1
        global curr_question_points
        curr_question_points = num_correct_songs*5
        return render_template('ReleaseOrderGameScore.html',
                               num_correct=num_correct_songs,
                               points=curr_question_points)

def create_game_page():
    # Avoiding UnicodeDecodeError
    reload(sys)
    sys.setdefaultencoding('UTF8')

    rand_song_row = DbConnector.get_result_for_query(QueryGenerator.get_release_order_question_query())
    rand_song_name = rand_song_row[3]

    album_id = rand_song_row[0]
    release_month = rand_song_row[1]
    release_year = rand_song_row[2]

    answers_rows = DbConnector.get_all_results_for_query_with_args(
        QueryGenerator.get_release_order_answers_query(),
        (release_year, release_month, release_year, release_month, release_year, release_month, release_year, album_id))

    global ordered_answers
    ordered_answers = []
    inserted_rand_song_row = False
    for i in range(3):
        if int(answers_rows[i][0]) > 0 and not inserted_rand_song_row:
            ordered_answers.append(rand_song_name)
            inserted_rand_song_row = True
        ordered_answers.append(answers_rows[i][1])

    rand_order_answers = random.sample(ordered_answers, 4)

    response = make_response(render_template('ReleaseOrderGame.html',
                           current_score=game_manager.score,
                           question='"' + '",  "'.join(rand_order_answers) + '"',
                           option_1=rand_order_answers[0],
                           option_2=rand_order_answers[1],
                           option_3=rand_order_answers[2],
                           option_4=rand_order_answers[3]))

    return game_manager.update_cookies_for_new_question(response)


