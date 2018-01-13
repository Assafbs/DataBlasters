from flask import Flask, render_template, redirect, url_for, request, make_response, Response, Blueprint
import MySQLdb as mdb
import random
import sys
import GameManager
from db_connector import DbConnector
from query_generator import QueryGenerator


GAME_ID = 1
game_manager = GameManager.GameManager(GAME_ID)
NUM_QUESTIONS_PER_GAME = 5
COUNTRIES = ["Argentina", "France", "Israel", "Spain", "United Kingdom", "United States"]
game_manager = GameManager.GameManager(GAME_ID)
rank_by_country_game = Blueprint('rank_by_country_game', __name__, template_folder='templates')
rank_by_country_game_ = Blueprint('rank_by_country_game_', __name__, template_folder='templates')


@rank_by_country_game.route('/rank_by_country_game')
def rank_by_country_game_start():
    game_manager.start_new_game()
    random.shuffle(COUNTRIES)
    return create_game_page()


@rank_by_country_game_.route('/rank_by_country_game_')
def rank_by_country_game_mid():
    allow_access = request.cookies.get('allowAccess')
    points = int(request.cookies.get('points'))
    response = game_manager.calc_mid_game(allow_access, points, NUM_QUESTIONS_PER_GAME)
    if response is None:
        return create_game_page()
    else:
        return response


def create_game_page():
    connector = DbConnector()
    result = connector.get_all_results_for_query(QueryGenerator.get_four_ranked_songs_in_country(), (COUNTRIES[0], COUNTRIES[0], COUNTRIES[0], COUNTRIES[0]))
    connector.close()
    options = result[0]
    print options
    right_answer = options[0]
    answers = list(options)
    random.shuffle(answers)
    print answers

    response = make_response(render_template('RankByCountryGame.html',
                                             country=COUNTRIES[game_manager.answer_num],
                                             option_1=answers[0],
                                             option_2=answers[1],
                                             option_3=answers[2],
                                             option_4=answers[3],
                                             current_score=game_manager.score))

    response.set_cookie('correctAnswerNum', str(answers.index(right_answer) + 1))
    return game_manager.update_cookies_for_new_question(response)