from flask import Flask, render_template, redirect, url_for, request, make_response, Response, Blueprint
import MySQLdb as mdb
from word_scraper import get5PopularWords
import random
import sys
import GameManager
from db_connector import DbConnector
from query_generator import QueryGenerator


GAME_ID = 5
NUM_QUESTIONS_PER_GAME = 5
game_manager = GameManager.GameManager()


translate_game = Blueprint('translate_game', __name__, template_folder='templates')
@translate_game.route('/translate_game')
def translate_game_start():
    game_manager.start_new_game(GAME_ID)

    con = mdb.connect('localhost', 'root', 'Password!1', "mrmusic")  # TODO: use assaf method when ready
    return create_game_page(con)


translate_game_ = Blueprint('translate_game_', __name__, template_folder='templates')
@translate_game_.route('/translate_game_')
def translate_game_mid():

    allow_access = request.cookies.get('allowAccess')
    points = int(request.cookies.get('points'))
    response = game_manager.calc_mid_game(allow_access, points, NUM_QUESTIONS_PER_GAME)

    if response is None:
        con = mdb.connect('localhost', 'root', 'Password!1', "mrmusic")
        return create_game_page(con)
    else:
        return response


def create_game_page(con):
    # Avoiding UnicodeDecodeError
    reload(sys)
    sys.setdefaultencoding('UTF8')

    connector = DbConnector()
    connector.execute_query(QueryGenerator.setting_for_read_hebrew_from_db_query())
    translated_song_row = connector.get_one_result_for_query(QueryGenerator.get_translated_song_question_query())

    translated_lyrics = translated_song_row[3]
    right_answer = translated_song_row[4]
    # TODO: do something if there is less then 5 words. should never happen
    popular_words = get5PopularWords(translated_song_row[1])
    wrong_answers = calc_answers(connector, popular_words, translated_song_row[0],
                                 translated_song_row[4], translated_song_row[2])
    connector.close()
    answers = random.sample(wrong_answers + [right_answer], 4)

    response = make_response(render_template('TranslateGame.html',
                                             question=translated_lyrics.decode('utf-8'),
                                             option_1=answers[0],
                                             option_2=answers[1],
                                             option_3=answers[2],
                                             option_4=answers[3],
                                             current_score=game_manager.score))

    response.set_cookie('correctAnswerNum', str(answers.index(right_answer) + 1))
    return game_manager.update_cookies_for_new_question(response)


def calc_answers(connector, popular_words, answer_song_id, answer_song_name, lyrics_lang):

    rows = connector.get_all_results_for_query(QueryGenerator.get_translated_song_answers_query(),
                                               ('+'+popular_words[0], lyrics_lang, '+'+popular_words[1], lyrics_lang,
                                                '+'+popular_words[2], lyrics_lang, '+'+popular_words[3], lyrics_lang,
                                                '+'+popular_words[4], lyrics_lang, answer_song_id, answer_song_name))

    # TODO: delete those print after testing
    print('translate query: ' + QueryGenerator.get_translated_song_answers_query())
    print('popular words: +' + popular_words[0] + ' +' + popular_words[1] + ' +' + popular_words[2] +
          ' +' + popular_words[3] + ' +' + popular_words[4] + '\nlyricsLang: ' + lyrics_lang + ' ,answerSongId: ' +
          str(answer_song_id) + ' ,answerSongName: ' + answer_song_name)

    res = []
    for row in rows:
        res.append(row[0])
    return res



