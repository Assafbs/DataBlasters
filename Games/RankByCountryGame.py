from flask import render_template, redirect, request, make_response, Blueprint
import random
import Common.common
import GameManager
from Common.db_connector import DbConnector
from Common.query_generator import QueryGenerator

GAME_ID = 1
game_manager = GameManager.GameManager(GAME_ID)
NUM_QUESTIONS_PER_GAME = 5
COUNTRIES = ["Argentina", "France", "Israel", "Spain", "United Kingdom", "United States"]
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
    response = game_manager.calc_mid_game(allow_access, points, NUM_QUESTIONS_PER_GAME, request)
    if response is None:
        return create_game_page()
    else:
        return response


def create_game_page():
    if game_manager.answer_num % 2 == 0:
        return generate_most_popular_song_question()
    elif game_manager.answer_num == 1:
        return generate_in_which_country_is_most_popular_question()
    else:  # game_manager.answer_num == 3
        return generate_in_which_country_is_least_popular_question()


def generate_most_popular_song_question():
    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    # Make sure user is logged in, otherwise redirect to log in page.
    if nickname is None:
        return redirect('/log_in')

    connector = DbConnector()
    country_index = game_manager.answer_num % len(COUNTRIES)
    result = connector.get_all_results_for_query(QueryGenerator.get_four_ranked_songs_in_country(), (COUNTRIES[country_index], COUNTRIES[country_index], COUNTRIES[country_index], COUNTRIES[country_index]))
    while len(result) == 0:  # Just for safety, shouldn't happen unless DB is corrupted.
        country_index = (country_index + 1) % len(COUNTRIES)
        result = connector.get_all_results_for_query(QueryGenerator.get_four_ranked_songs_in_country(), (COUNTRIES[country_index], COUNTRIES[country_index], COUNTRIES[country_index], COUNTRIES[country_index]))
    connector.close()
    options = result[0]
    right_answer = options[0]
    answers = list(options)
    random.shuffle(answers)

    try:
        user_score = Common.common.get_value_from_cookie(request, 'score')

        if float(user_score) > 500 and nickname is not None:
            get_bonus = 'true'
        else:
            get_bonus = ''
        response = make_response(render_template('RankByCountryGame.html',
                                                 question="Which of the following songs is ranked the highest in " +
                                                          COUNTRIES[country_index] + "?",
                                                 option_1=answers[0],
                                                 option_2=answers[1],
                                                 option_3=answers[2],
                                                 option_4=answers[3],
                                                 game=game_manager.answer_num + 1,
                                                 score=user_score,
                                                 nickname=nickname,
                                                 game_score=game_manager.score,
                                                 bonus=get_bonus))

        response.set_cookie('correctAnswerNum', str(answers.index(right_answer) + 1))
        return game_manager.update_cookies_for_new_question(response)

    # In case there was a problem rendering the template, we will try replacing the question.
    # This is just for safety, and should not happen.
    except Exception as e:
        print "Error occurred with response - rank by country game - most popular song."
        print e.message
        generate_most_popular_song_question()


def generate_in_which_country_is_most_popular_question():
    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    # Make sure user is logged in, otherwise redirect to log in page.
    if nickname is None:
        return redirect('/log_in')

    random_countries = random.sample(COUNTRIES, 4)
    connector = DbConnector()
    result = connector.get_all_results_for_query(QueryGenerator.get_song_ranking_in_four_countries(), (
    random_countries[0], random_countries[1], random_countries[2], random_countries[3]))
    while len(result) == 0:
        random_countries = random.sample(COUNTRIES, 4)
        result = connector.get_all_results_for_query(QueryGenerator.get_song_ranking_in_four_countries(), (
            random_countries[0], random_countries[1], random_countries[2], random_countries[3]))
    connector.close()
    song_name = result[0][0]
    ranking = result[0][1:]
    right_answer = random_countries[ranking.index(min(ranking))]  # The country with highest ranking.

    try:
        user_score = Common.common.get_value_from_cookie(request, 'score')

        if float(user_score) > 500 and nickname is not None:
            get_bonus = 'true'
        else:
            get_bonus = ''
        response = make_response(render_template('RankByCountryGame.html',
                                                 question="In which country the song '" + song_name + "' is ranked the highest?",
                                                 option_1=random_countries[0],
                                                 option_2=random_countries[1],
                                                 option_3=random_countries[2],
                                                 option_4=random_countries[3],
                                                 game=game_manager.answer_num + 1,
                                                 score=user_score,
                                                 nickname=nickname,
                                                 game_score=game_manager.score,
                                                 bonus=get_bonus))

        response.set_cookie('correctAnswerNum', str(random_countries.index(right_answer) + 1))
        return game_manager.update_cookies_for_new_question(response)

    # In case there was a problem rendering the template, we will try replacing the question.
    # This is just for safety, and should not happen.
    except Exception as e:
        print "Error occurred with response - rank by country game - most popular."
        print e.message
        generate_in_which_country_is_most_popular_question()


def generate_in_which_country_is_least_popular_question():
    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    # Make sure user is logged in, otherwise redirect to log in page.
    if nickname is None:
        return redirect('/log_in')

    random_countries = random.sample(COUNTRIES, 4)
    connector = DbConnector()
    result = connector.get_all_results_for_query(QueryGenerator.get_song_ranking_in_four_countries(), (
    random_countries[0], random_countries[1], random_countries[2], random_countries[3]))
    while len(result) == 0:
        random_countries = random.sample(COUNTRIES, 4)
        result = connector.get_all_results_for_query(QueryGenerator.get_song_ranking_in_four_countries(), (
            random_countries[0], random_countries[1], random_countries[2], random_countries[3]))
    connector.close()
    song_name = result[0][0]
    ranking = result[0][1:]
    right_answer = random_countries[ranking.index(max(ranking))]  # The country with highest ranking.

    try:
        user_score = Common.common.get_value_from_cookie(request, 'score')

        if float(user_score) > 500 and nickname is not None:
            get_bonus = 'true'
        else:
            get_bonus = ''
        response = make_response(render_template('RankByCountryGame.html',
                                                 question="In which country the song '" + song_name + "' is ranked the lowest?",
                                                 option_1=random_countries[0],
                                                 option_2=random_countries[1],
                                                 option_3=random_countries[2],
                                                 option_4=random_countries[3],
                                                 game=game_manager.answer_num + 1,
                                                 score=user_score,
                                                 nickname=nickname,
                                                 game_score=game_manager.score,
                                                 bonus=get_bonus))

        response.set_cookie('correctAnswerNum', str(random_countries.index(right_answer) + 1))
        return game_manager.update_cookies_for_new_question(response)

    # In case there was a problem rendering the template, we will try replacing the question.
    # This is just for safety, and should not happen.
    except Exception as e:
        print "Error occurred with response - rank by country game - least popular."
        print e.message
        generate_in_which_country_is_least_popular_question()
