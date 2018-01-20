import random
import sys

from flask import render_template, request, make_response, Blueprint, redirect

import Common.common
import GameManager
from Common.db_connector import DbConnector
from Common.query_generator import QueryGenerator

connector = DbConnector()
NUM_QUESTIONS_PER_GAME = 5
GAME_ID = 3
game_manager = GameManager.GameManager(GAME_ID)
pairs_game = Blueprint('pairs_game', __name__, template_folder='templates')
pairs_game_ = Blueprint('pairs_game_', __name__, template_folder='templates')


# initialize game
@pairs_game.route('/pairs_game')
def pairs_game_start():
    game_manager.start_new_game()
    return create_game_page()


# Get here in middle of game. Checks if user got here legally and calculates current score
@pairs_game_.route('/pairs_game_')
def pairs_game_mid():
    allow_access = request.cookies.get('allowAccess')
    points = int(request.cookies.get('points'))
    response = game_manager.calc_mid_game(allow_access, points, NUM_QUESTIONS_PER_GAME, request)

    if response is None:
        return create_game_page()
    else:
        return response


# Receives query and argument, and returns all results in a list
def get_list_of_results(query, n):
    lst_of_artists = list()
    rows = connector.get_all_results_for_query(query, (n,))
    for row in rows:
        lst_of_artists.append((row[0]))
    return lst_of_artists


# invokes query to get n random songs by given artist and returns list of songs by that artist
def get_n_random_songs_from_artist(n, artist_id):
    lst_of_songs = list()
    rows = connector.get_all_results_for_query(QueryGenerator.get_n_random_songs_by_artist(), (artist_id, n))
    for row in rows:
        lst_of_songs.append((row[0], row[1]))
    return lst_of_songs


# gets all song pairs for the game, the right and the wrong ones
def get_all_songs():
    lst_of_artists = get_list_of_results(QueryGenerator.get_n_random_artists(), 7)  # get a list of 7 random artists
    winner_artist = random.randint(0, 6)
    lst_of_bad_songs = list()
    winner_songs = list()
    for i in range(7):
        if i == winner_artist:
            winner_songs = get_n_random_songs_from_artist(2, lst_of_artists[i])  # get 2 random songs from one artist
        else:
            lst_of_bad_songs.append(get_n_random_songs_from_artist(1, lst_of_artists[i]))  # get 1 random song from artist
    return winner_songs, lst_of_bad_songs


# gets list of ids and returns list of artist names
def translate_artist_id_list_to_artist_name_list(ids):
    lst_of_names = list()
    for artist_id in ids:
        lst_of_names.append(connector.get_one_result_for_query(QueryGenerator.get_artist_name_by_id(), (artist_id,))[0])
    return lst_of_names


# return 2 random artist from 1 random country
def get_winning_artists_from_countries():
    lst_of_artists = list()
    country = connector.get_all_results_for_query(QueryGenerator.get_n_random_countries(), (1,))[0][0]  # get 1 random country
    rows = connector.get_all_results_for_query(QueryGenerator.get_n_artists_from_country(), (country, 2))  # get 2 random artists from that country
    for row in rows:
        lst_of_artists.append((row[0]))
    return lst_of_artists


# get 1 random artists from 2 random countries (1 from each)
def get_bad_artists_from_countries():
    lst_of_artists = list()
    for i in range(3):
        countries = connector.get_all_results_for_query(QueryGenerator.get_n_random_countries(), (2,))  # get 2 random countries
        for country in countries:
            country = country[0]
            lst_of_artists.append(connector.get_all_results_for_query(QueryGenerator.get_n_artists_from_country(), (country, 1))[0])  # get 1 random artist from country
    return lst_of_artists


# get a list of n random album covers from given artist
def get_n_random_covers_from_artist(n, artist_id):
    lst_of_covers = list()
    rows = connector.get_all_results_for_query(QueryGenerator.get_n_album_covers_from_artist(), (artist_id, n))
    for row in rows:
        lst_of_covers.append(row[0])
    return lst_of_covers


# get all pairs of covers, for right and wrong answers
def get_all_covers():
    lst_of_artists = get_list_of_results(QueryGenerator.get_n_random_artists_from_possible_artists(), 7)  # get 7 random artists that have more than one real album cover
    winner_artist = random.randint(0, 6)
    bad_covers = list()
    winner_covers = list()
    for i in range(7):
        if i == winner_artist:
            winner_covers = get_n_random_covers_from_artist(2, lst_of_artists[i])  # get 2 random album covers from artist
        else:
            bad_covers.append(get_n_random_covers_from_artist(1, lst_of_artists[i]))  # get 1 random album cover from artist
    return winner_covers, bad_covers


# generate a different question every turn
def create_game_page():
    if game_manager.answer_num == 0 or game_manager.answer_num == 3:
        return generate_covers_game()
    elif game_manager.answer_num == 1 or game_manager.answer_num == 4:
        return generate_countries_game()
    else:  # game_manager.answer_num == 2
        return generate_songs_game()


def generate_covers_game():
    reload(sys)
    sys.setdefaultencoding('UTF8')

    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    if nickname is None:
        return redirect('/log_in')

    winner_covers, bad_covers = get_all_covers()  # get right and wrong answers
    right_answer = winner_covers[0] + "!@" + winner_covers[1]
    wrong_answers = calc_answers_cover_pairs(bad_covers)
    answers = random.sample(wrong_answers + [right_answer], 4)  # mix the anwswers
    try:
        user_score = Common.common.get_value_from_cookie(request, 'score')

        if float(user_score) > 500 and nickname is not None:
            get_bonus = 'true'
        else:
            get_bonus = ''
        response = make_response(render_template('PairsGameCovers.html',
                                                 question=" Which of these pairs of album covers are by the same artist?",
                                                 option_1_1=answers[0].split('!@')[0],
                                                 option_1_2=answers[0].split('!@')[1],
                                                 option_2_1=answers[1].split('!@')[0],
                                                 option_2_2=answers[1].split('!@')[1],
                                                 option_3_1=answers[2].split('!@')[0],
                                                 option_3_2=answers[2].split('!@')[1],
                                                 option_4_1=answers[3].split('!@')[0],
                                                 option_4_2=answers[3].split('!@')[1],
                                                 game=game_manager.answer_num + 1,
                                                 score=user_score,
                                                 nickname=nickname,
                                                 game_score=game_manager.score,
                                                 bonus=get_bonus))
        response.set_cookie('correctAnswerNum', str(answers.index(right_answer) + 1))  # update num of right answer
        return game_manager.update_cookies_for_new_question(response)  # prepare next question
    except Exception as e:
        print "Error occurred with response"
        print e.message
        generate_covers_game()


def generate_countries_game():
    reload(sys)
    sys.setdefaultencoding('UTF8')

    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    if nickname is None:
        return redirect('/log_in')

    winner_artists = translate_artist_id_list_to_artist_name_list(get_winning_artists_from_countries())  # get the right answer
    lst_of_bad_artists = translate_artist_id_list_to_artist_name_list(get_bad_artists_from_countries())  # get the wrong answers
    right_answer = winner_artists[0] + "!@" + winner_artists[1]
    wrong_answers = calc_answers_artist_pairs(lst_of_bad_artists)
    answers = random.sample(wrong_answers + [right_answer], 4)  # mix the answers

    try:
        user_score = Common.common.get_value_from_cookie(request, 'score')

        if float(user_score) > 500 and nickname is not None:
            get_bonus = 'true'
        else:
            get_bonus = ''
        response = make_response(render_template('PairsGame.html',
                                                 question=" Which of these pairs of artists come from the same country?",
                                                 option_1_1=answers[0].split('!@')[0],
                                                 option_1_2=answers[0].split('!@')[1],
                                                 option_2_1=answers[1].split('!@')[0],
                                                 option_2_2=answers[1].split('!@')[1],
                                                 option_3_1=answers[2].split('!@')[0],
                                                 option_3_2=answers[2].split('!@')[1],
                                                 option_4_1=answers[3].split('!@')[0],
                                                 option_4_2=answers[3].split('!@')[1],
                                                 game=game_manager.answer_num + 1,
                                                 score=user_score,
                                                 nickname=nickname,
                                                 game_score=game_manager.score,
                                                 bonus=get_bonus))
        response.set_cookie('correctAnswerNum', str(answers.index(right_answer) + 1))  # update num of right answer
        return game_manager.update_cookies_for_new_question(response)  # prepare next question
    except Exception as e:
        print "Error occurred with response"
        print e.message
        generate_countries_game()


def generate_songs_game():
    reload(sys)
    sys.setdefaultencoding('UTF8')

    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    if nickname is None:
        return redirect('/log_in')

    winner_songs, lst_of_bad_songs = get_all_songs()  # get right and wrong answers
    right_answer = winner_songs[0][0] + "!@" + winner_songs[1][0]
    wrong_answers = calc_answers_song_pairs(lst_of_bad_songs)
    answers = random.sample(wrong_answers + [right_answer], 4)  # mix answers
    try:

        user_score = Common.common.get_value_from_cookie(request, 'score')
        if float(user_score) > 500 and nickname is not None:
            get_bonus = 'true'
        else:
            get_bonus = ''
        response = make_response(render_template('PairsGame.html',
                                                 question=" Which of these pairs of songs were released by the same artist?",
                                                 option_1_1=answers[0].split('!@')[0],
                                                 option_1_2=answers[0].split('!@')[1],
                                                 option_2_1=answers[1].split('!@')[0],
                                                 option_2_2=answers[1].split('!@')[1],
                                                 option_3_1=answers[2].split('!@')[0],
                                                 option_3_2=answers[2].split('!@')[1],
                                                 option_4_1=answers[3].split('!@')[0],
                                                 option_4_2=answers[3].split('!@')[1],
                                                 game=game_manager.answer_num + 1,
                                                 score=user_score,
                                                 nickname=nickname,
                                                 game_score=game_manager.score,
                                                 bonus=get_bonus))
        response.set_cookie('correctAnswerNum', str(answers.index(right_answer) + 1))  # update num of right answer
        return game_manager.update_cookies_for_new_question(response)  # prepare next question
    except Exception as e:
        print "Error occurred with response"
        print e.message
        generate_songs_game()


#  prepare wrong answer
def calc_answers_song_pairs(bad_songs):
    lst_of_answers = list()
    for i in range(3):
        lst_of_answers.append(bad_songs.pop()[0][0] + "!@" + bad_songs.pop()[0][0])
    return lst_of_answers


#  prepare wrong answer
def calc_answers_artist_pairs(bad_artists):
    lst_of_answers = list()
    for i in range(3):
        lst_of_answers.append(bad_artists.pop() + "!@" + bad_artists.pop())
    return lst_of_answers


#  prepare wrong answer
def calc_answers_cover_pairs(bad_covers):
    lst_of_answers = list()
    for i in range(3):
        lst_of_answers.append(bad_covers.pop()[0] + "!@" + bad_covers.pop()[0])
    return lst_of_answers
