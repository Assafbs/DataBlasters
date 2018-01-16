from flask import render_template, request, make_response, Blueprint, redirect
from Common.word_scraper import get_5_popular_words
import random
import Common.common
import sys
import GameManager
from Common.db_connector import DbConnector
from Common.query_generator import QueryGenerator

# TODO: delete after ready: mdb.connect('localhost', 'root', 'Password!1', "mrmusic")

GAME_ID = 5
NUM_QUESTIONS_PER_GAME = 5
game_manager = GameManager.GameManager(GAME_ID)


translate_game = Blueprint('translate_game', __name__, template_folder='templates')
@translate_game.route('/translate_game')
def translate_game_start():
    game_manager.start_new_game()

    return create_game_page()


translate_game_ = Blueprint('translate_game_', __name__, template_folder='templates')
@translate_game_.route('/translate_game_')
def translate_game_mid():

    allow_access = request.cookies.get('allowAccess')
    points = int(request.cookies.get('points'))
    response = game_manager.calc_mid_game(allow_access, points, NUM_QUESTIONS_PER_GAME, request)

    if response is None:
        return create_game_page()
    else:
        return response


def create_game_page():
    # Avoiding UnicodeDecodeError
    reload(sys)
    sys.setdefaultencoding('UTF8')

    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    if nickname is None:
        return redirect('/')

    connector = DbConnector()
    connector.execute_query(QueryGenerator.setting_for_read_hebrew_from_db_query())
    translated_song_row = connector.get_one_result_for_query(QueryGenerator.get_translated_song_question_query())

    translated_lyrics = translated_song_row[3]
    right_answer = translated_song_row[4]
    popular_words = get_5_popular_words(translated_song_row[1])
    wrong_answers = calc_answers(connector, popular_words, translated_song_row[0],
                                 translated_song_row[4], translated_song_row[2])
    connector.close()
    answers = random.sample(wrong_answers + [right_answer], 4)

    try:
        user_score = Common.common.get_value_from_cookie(request, 'score')
        response = make_response(render_template('TranslateGame.html',
                                                 question=translated_lyrics.decode('utf-8'),
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


def calc_answers(connector, popular_words, answer_song_id, answer_song_name, lyrics_lang):

    rows = connector.get_all_results_for_query(QueryGenerator.get_translated_song_answers_query(),
                                               ('+'+popular_words[0], lyrics_lang, '+'+popular_words[1], lyrics_lang,
                                                '+'+popular_words[2], lyrics_lang, '+'+popular_words[3], lyrics_lang,
                                                '+'+popular_words[4], lyrics_lang, answer_song_id, answer_song_name))

    res = []
    for row in rows:
        res.append(row[0])
    return res



