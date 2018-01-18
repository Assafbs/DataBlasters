from flask import render_template, request, make_response, Blueprint, redirect
import random
import Common.common
import GameManager
from Common.db_connector import DbConnector
from Common.query_generator import QueryGenerator

# TODO: delete after ready: mdb.connect('localhost', 'root', 'Password!1', "mrmusic")

GAME_ID = 2
NUM_QUESTIONS_PER_GAME = 5
game_manager = GameManager.GameManager(GAME_ID)

duets_game = Blueprint('duets_game', __name__, template_folder='templates')


@duets_game.route('/duets_game')
def duets_game_start():
    game_manager.start_new_game()

    return create_game_page()


duets_game_ = Blueprint('duets_game_', __name__, template_folder='templates')


@duets_game_.route('/duets_game_')
def duets_game_mid():
    allow_access = request.cookies.get('allowAccess')
    points = int(request.cookies.get('points'))
    response = game_manager.calc_mid_game(allow_access, points, NUM_QUESTIONS_PER_GAME, request)

    if response is None:
        return create_game_page()
    else:
        return response


def create_game_page():
    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    if nickname is None:
        return redirect('/log_in')

    connector = DbConnector()
    answer_row = connector.get_one_result_for_query(QueryGenerator.get_duets_question_query())

    right_answer = answer_row[2]  # seconed artist name
    wrong_answers = calc_answers(connector, answer_row[0])  # first artist id
    connector.close()
    answers = random.sample(wrong_answers + [right_answer], 4)

    try:
        user_score = Common.common.get_value_from_cookie(request, 'score')
        response = make_response(render_template('DuetsGame.html',
                                                 question=answer_row[1],  # first artist name
                                                 option_1=answers[0],
                                                 option_2=answers[1],
                                                 option_3=answers[2],
                                                 option_4=answers[3],
                                                 game=game_manager.answer_num + 1,
                                                 score=user_score,
                                                 nickname=nickname,
                                                 game_score=game_manager.score))

        response.set_cookie('correctAnswerNum', str(answers.index(right_answer) + 1))
        return game_manager.update_cookies_for_new_question(response)
    except Exception as e:
        print "Error occurred with response"
        print e.message
        create_game_page()


def calc_answers(connector, answer_artist_id):
    # find 3 artist that didn't sing with answer_artist_id

    rows = connector.get_all_results_for_query(QueryGenerator.get_duets_answers_query(),
                                               ('% & %', '% feat%', '% and %', answer_artist_id, answer_artist_id))

    res = []
    for row in rows:
        res.append(row[0])
    return res
