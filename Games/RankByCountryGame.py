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
    if game_manager.answer_num % 2 == 0:
        return generate_most_popular_song_question()
    elif game_manager.answer_num == 1:
        return generate_in_which_country_is_most_popular_question()
    else: # game_manager.answer_num == 3
        return generate_in_which_country_is_least_popular_question()


def generate_most_popular_song_question():
    connector = DbConnector()
    country_index = game_manager.answer_num
    result = connector.get_all_results_for_query(QueryGenerator.get_four_ranked_songs_in_country(), (COUNTRIES[country_index], COUNTRIES[country_index], COUNTRIES[country_index], COUNTRIES[country_index]))
    connector.close()
    options = result[0]
    right_answer = options[0]
    answers = list(options)
    random.shuffle(answers)

    response = make_response(render_template('RankByCountryGame.html',
                                             question="Which of the following songs is ranked the highest in " + COUNTRIES[country_index] +"?",
                                             option_1=answers[0],
                                             option_2=answers[1],
                                             option_3=answers[2],
                                             option_4=answers[3],
                                             current_score=game_manager.score))

    response.set_cookie('correctAnswerNum', str(answers.index(right_answer) + 1))
    return game_manager.update_cookies_for_new_question(response)

def generate_in_which_country_is_most_popular_question():
    random_countries = random.sample(COUNTRIES, 4)
    connector = DbConnector()
    result = connector.get_all_results_for_query(QueryGenerator.get_song_ranking_in_four_countries(), (random_countries[0], random_countries[1], random_countries[2], random_countries[3]))
    while len(result) == 0:
        random_countries = random.sample(COUNTRIES, 4)
        result = connector.get_all_results_for_query(QueryGenerator.get_song_ranking_in_four_countries(), (
        random_countries[0], random_countries[1], random_countries[2], random_countries[3]))
    connector.close()
    song_name = result[0][0]
    ranking = result[0][1:]
    right_answer = random_countries[ranking.index(min(ranking))] # The country with highest ranking.

    response = make_response(render_template('RankByCountryGame.html',
                                             question="In which country the song '" + song_name + "' is ranked the highest?" ,
                                             option_1=random_countries[0],
                                             option_2=random_countries[1],
                                             option_3=random_countries[2],
                                             option_4=random_countries[3],
                                             current_score=game_manager.score))

    response.set_cookie('correctAnswerNum', str(random_countries.index(right_answer) + 1))
    return game_manager.update_cookies_for_new_question(response)

def generate_in_which_country_is_least_popular_question():
    random_countries = random.sample(COUNTRIES, 4)
    connector = DbConnector()
    result = connector.get_all_results_for_query(QueryGenerator.get_song_ranking_in_four_countries(), (random_countries[0], random_countries[1], random_countries[2], random_countries[3]))
    while len(result) == 0:
        random_countries = random.sample(COUNTRIES, 4)
        result = connector.get_all_results_for_query(QueryGenerator.get_song_ranking_in_four_countries(), (
        random_countries[0], random_countries[1], random_countries[2], random_countries[3]))
    connector.close()
    song_name = result[0][0]
    ranking = result[0][1:]
    right_answer = random_countries[ranking.index(max(ranking))] # The country with highest ranking.

    response = make_response(render_template('RankByCountryGame.html',
                                             question="In which country the song '" + song_name + "' is ranked the lowest?" ,
                                             option_1=random_countries[0],
                                             option_2=random_countries[1],
                                             option_3=random_countries[2],
                                             option_4=random_countries[3],
                                             current_score=game_manager.score))

    response.set_cookie('correctAnswerNum', str(random_countries.index(right_answer) + 1))
    return game_manager.update_cookies_for_new_question(response)