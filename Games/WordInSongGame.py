from flask import render_template, request, make_response, Blueprint
from Common.word_scraper import get_5_popular_words
import random
import GameManager
from db_connector import DbConnector
from query_generator import QueryGenerator

# TODO: delete after ready: mdb.connect('localhost', 'root', 'Password!1', "mrmusic")

GAME_ID = 4
NUM_QUESTIONS_PER_GAME = 5
game_manager = GameManager.GameManager(GAME_ID)


word_in_song_game = Blueprint('word_in_song_game', __name__, template_folder='templates')
@word_in_song_game.route('/word_in_song_game')
def word_in_song_game_start():
    game_manager.start_new_game()

    return create_game_page()


word_in_song_game_ = Blueprint('word_in_song_game_', __name__, template_folder='templates')
@word_in_song_game_.route('/word_in_song_game_')
def word_in_song_game_mid():

    allow_access = request.cookies.get('allowAccess')
    points = int(request.cookies.get('points'))
    response = game_manager.calc_mid_game(allow_access, points, NUM_QUESTIONS_PER_GAME)

    if response is None:
        return create_game_page()
    else:
        return response


def create_game_page():

    connector = DbConnector()
    song_row = connector.get_one_result_for_query(QueryGenerator.get_word_in_song_question_query())

    lyrics = song_row[2]
    popular_words = get_5_popular_words(lyrics)
    right_answer = popular_words[0];
    wrong_answers = popular_words[1:4]

    connector.close()
    answers = random.sample(wrong_answers + [right_answer], 4)

    try:
        response = make_response(render_template('WordInSongGame.html',
                                                 question=song_row[1],
                                                 option_1=answers[0],
                                                 option_2=answers[1],
                                                 option_3=answers[2],
                                                 option_4=answers[3],
                                                 game=game_manager.answer_num + 1,
                                                 score=game_manager.score,
                                                 current_score=game_manager.score))

        response.set_cookie('correctAnswerNum', str(answers.index(right_answer) + 1))
        return game_manager.update_cookies_for_new_question(response)
    except Exception as e:
        print "Error occurred with response"
        print e.message
        create_game_page()





