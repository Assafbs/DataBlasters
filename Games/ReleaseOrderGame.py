from flask import render_template, request, make_response, Blueprint, redirect
import random
import GameManager
import Common.common
import sys
from Common.db_connector import DbConnector
from Common.query_generator import QueryGenerator

GAME_ID = 6
NUM_QUESTIONS_PER_GAME = 5
game_manager = GameManager.GameManager(GAME_ID)

ordered_answers = []
curr_question_points = 0

release_order_game = Blueprint('release_order_game', __name__, template_folder='templates')


@release_order_game.route('/release_order_game', methods=['POST', 'GET'])
def release_order_game_start():
    if request.method == 'GET':
        # we want to start new game only in case of get, and not in case of post (since it is mid game)
        game_manager.start_new_game()
    return handle_route(request)


release_order_game_ = Blueprint('release_order_game_', __name__, template_folder='templates')


@release_order_game_.route('/release_order_game_', methods=['POST', 'GET'])
def release_order_game_mid():
    allow_access = request.cookies.get('allowAccess')
    # the curr_question_points is updated when handling post of previous question
    global curr_question_points
    response = game_manager.calc_mid_game(allow_access, curr_question_points, NUM_QUESTIONS_PER_GAME, request)

    if response is None:
        # we are in the middle of a game
        return handle_route(request)
    else:
        return response


def handle_route(my_request):
    if my_request.method == 'GET':
        return create_game_page()
    elif my_request.method == 'POST':
        # the user sent his answer to the question

        nickname = Common.common.get_value_from_cookie(my_request, 'nickname')
        # Make sure the user is logon before accessing this page
        if nickname is None:
            return redirect('/log_in')

        # the ordered_answers is updated when handling the get request
        #   (when rendering the page and generate the question)
        global ordered_answers
        user_ordered_answers = [my_request.form['song1'], my_request.form['song2'],
                                my_request.form['song3'], my_request.form['song4']]
        num_correct_songs = 0
        for i in range(4):
            if user_ordered_answers[i] == ordered_answers[i]:
                num_correct_songs += 1

        global curr_question_points
        curr_question_points = num_correct_songs * 5
        next_button_content = 'Next Question'
        if (game_manager.answer_num + 1) == NUM_QUESTIONS_PER_GAME:
            next_button_content = 'Finish Game'

        user_score = Common.common.get_value_from_cookie(my_request, 'score')

        if float(user_score) > 500 and nickname is not None:
            get_bonus = 'true'
        else:
            get_bonus = ''
        return render_template('ReleaseOrderGameScore.html',
                               score=user_score,
                               nickname=nickname,
                               num_correct=num_correct_songs,
                               points=curr_question_points,
                               next_content=next_button_content,
                               bonus=get_bonus)


def create_game_page():
    # Avoiding UnicodeDecodeError
    reload(sys)
    sys.setdefaultencoding('UTF8')

    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    # Make sure the user is logon before accessing this page
    if nickname is None:
        return redirect('/log_in')

    connector = DbConnector()
    rand_song_row = connector.get_one_result_for_query(QueryGenerator.get_release_order_question_query())
    rand_song_name = rand_song_row[3]

    album_id = rand_song_row[0]
    release_month = rand_song_row[1]
    release_year = rand_song_row[2]

    answers_rows = connector.get_all_results_for_query(
        QueryGenerator.get_release_order_answers_query(),
        (release_year, release_month, release_year, release_month, release_year,
         release_month, release_year, rand_song_name, album_id))
    connector.close()

    # order the 4 songs by the release date (merge rand_song_name with answers_rows)
    global ordered_answers
    ordered_answers = []
    inserted_rand_song_row = False
    for i in range(3):
        if int(answers_rows[i][0]) > 0 and not inserted_rand_song_row:
            ordered_answers.append(rand_song_name)
            inserted_rand_song_row = True
        ordered_answers.append(answers_rows[i][1])
    if not inserted_rand_song_row:
        ordered_answers.append(rand_song_name)

    rand_order_answers = random.sample(ordered_answers, 4)

    try:
        user_score = Common.common.get_value_from_cookie(request, 'score')

        if float(user_score) > 500 and nickname is not None:
            get_bonus = 'true'
        else:
            get_bonus = ''
        response = make_response(render_template('ReleaseOrderGame.html',
                                                 game=game_manager.answer_num + 1,
                                                 score=user_score,
                                                 nickname=nickname,
                                                 game_score=game_manager.score,
                                                 question='"' + '",  "'.join(rand_order_answers) + '"',
                                                 option_1=rand_order_answers[0],
                                                 option_2=rand_order_answers[1],
                                                 option_3=rand_order_answers[2],
                                                 option_4=rand_order_answers[3],
                                                 bonus=get_bonus))

        return game_manager.update_cookies_for_new_question(response)
    except Exception as e:
        # in case there was a problem with rendering question page, we will try again
        print "Error occurred with response - release order game"
        print e.message
        create_game_page()
