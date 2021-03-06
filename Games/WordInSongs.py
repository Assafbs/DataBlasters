from Common.word_scraper import get_dict_word_count
from Common.db_connector import DbConnector
from flask import Blueprint, render_template, request, make_response, redirect
from Common.query_generator import QueryGenerator
import Common.common
import GameManager
import random
from Common.word_scraper import get_5_popular_words

GAME_ID = 4
NUM_QUESTIONS_PER_GAME = 5
game_manager = GameManager.GameManager(GAME_ID)

word_in_songs = Blueprint('word_in_songs', __name__, template_folder='templates')


# initialize game
@word_in_songs.route('/word_in_songs')
def word_in_songs_game_start():
    game_manager.start_new_game()
    return create_game_page()


word_in_songs_ = Blueprint('word_in_songs_', __name__, template_folder='templates')


# Get here in middle of game. Checks if user got here legally and calculates current score
@word_in_songs_.route('/word_in_songs_')
def word_in_songs_game_mid():
    allow_access = request.cookies.get('allowAccess')
    points = int(request.cookies.get('points'))
    response = game_manager.calc_mid_game(allow_access, points, NUM_QUESTIONS_PER_GAME, request)

    if response is None:
        return create_game_page()
    else:
        return response


def create_game_page():
    if game_manager.answer_num % 2 == 1:
        return create_words_in_song_game_page()  # generate that kind of question when question number is odd
    else:
        return create_3_songs_game_page()  # generate that kind of questions when question number is even


# creates question page for "Which one of the words appear in all the following songs:"
def create_3_songs_game_page():
    # validate user logged in. if not- send to login page
    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    if nickname is None:
        return redirect('/log_in')

    connector = DbConnector()
    query = "SELECT word FROM frequent_words ORDER BY RAND() LIMIT 1"
    correct_answer = connector.get_one_result_for_query(query)[0]  # get a frequent word randomly
    # get 3 song(titles) containging the word
    data = connector.get_all_results_for_query(QueryGenerator.get_songs_lyrics_contain(), (correct_answer, correct_answer))
    while len(data) < 3:  # if returned less than 3 titles
        correct_answer = connector.get_one_result_for_query(query)[0]  # change word
        data = connector.get_all_results_for_query(QueryGenerator.get_songs_lyrics_contain(),
                                                   (correct_answer, correct_answer))  # get 3 songs for new word
    songs = [tup[0] for tup in data]
    wrong_answers = get_wrong_answers(connector, correct_answer, songs, query)  # get 3 words that do not appear in all 3 songs
    connector.close()
    answers = random.sample(wrong_answers + [correct_answer], 4)  # randomize the order of the 4 options
    question_kind = "Which one of the words appear in all the following songs:"
    question = ", ".join(songs[0:3])
    try:
        user_score = Common.common.get_value_from_cookie(request, 'score')

        if float(user_score) > 500 and nickname is not None:
            get_bonus = 'true'
        else:
            get_bonus = ''
        response = make_response(render_template('WordInSongGame.html',
                                                 question=question,
                                                 question_kind=question_kind,
                                                 option_1=answers[0],
                                                 option_2=answers[1],
                                                 option_3=answers[2],
                                                 option_4=answers[3],
                                                 game=game_manager.answer_num + 1,
                                                 score=user_score,
                                                 nickname=nickname,
                                                 game_score=game_manager.score,
                                                 bonus=get_bonus))
        # store correct answer in cookie for further use
        response.set_cookie('correctAnswerNum', str(answers.index(correct_answer) + 1))
        return game_manager.update_cookies_for_new_question(response)
    except Exception as e:
        print "Error occurred with response"
        print e.message
        create_game_page()


# returns 3 words, each one of them do not appear in at least one song in "songs"
def get_wrong_answers(connector, correct_answer, songs, query):
    res = []  # keep the words here
    while len(res) < 3:
        answer = connector.get_one_result_for_query(query)[0]  # pick a word randomly from frequent_words table
        while answer == correct_answer or answer in res:  # in case we've randomly picked the word in all songs we've found before
            answer = connector.get_one_result_for_query(query)[0]
        for song in songs:  # every answer should have at least one song it does not appear in
            data = connector.get_all_results_for_query(QueryGenerator.get_songs_lyrics_not_contain(),
                                                       (answer, answer, song))
            if len(data) > 0:  # if we get back the name of the song, answer is not in it
                res.append(answer)
                break
            else:
                continue
    return res


def create_words_in_song_game_page():
    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    if nickname is None:
        return redirect('/log_in')

    connector = DbConnector()
    song_row = connector.get_one_result_for_query(QueryGenerator.get_word_in_song_question_query())

    lyrics = song_row[2]
    popular_words = get_5_popular_words(lyrics)
    right_answer = popular_words[0]
    wrong_answers = popular_words[1:4]

    connector.close()
    answers = random.sample(wrong_answers + [right_answer], 4)
    question_kind = "Which of the following words appears the most in the song? "

    try:
        user_score = Common.common.get_value_from_cookie(request, 'score')

        if float(user_score) > 500 and nickname is not None:
            get_bonus = 'true'
        else:
            get_bonus = ''
        response = make_response(render_template('WordInSongGame.html',
                                                 question=song_row[1],
                                                 question_kind=question_kind,
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
    except Exception as e:
        print "Error occurred with response"
        print e.message
        create_words_in_song_game_page()


############################

# The following code was used to build data for frequent_words table

frq_word_dict = dict()
ign_words = ['he', 'she', 'her', 'has', 'his', 'hers', 'them', 'not', 'their', 'theirs'
                                                                               'they', 'him', 'shes', 'hes', 'your', 'youre', 'be', 'by', 'thats', 'in', 'into', 'was', 'were', 'wanna', 'gonna',
             'this',
             'im', 'have', 'has', 'what', 'let', 'can', 'cant', 'even', 'more', 'few', 'non', 'none', 'wanna',
             'use', 'only', 'commercial', '', 'lyrics', 'which', 'we', 'our', 'at', 'and', 'dont']


def build_frq_word_dict():
    global frq_word_dict
    query = "SELECT lyrics FROM lyrics WHERE lyrics_language=%s"
    con = DbConnector()
    data = con.get_all_results_for_query(query, ('en',))
    con.close()
    for lyc in data:
        words_count = get_dict_word_count(lyc[0])
        for word in words_count:
            if word not in ign_words:
                if word not in frq_word_dict:
                    frq_word_dict.update({word: 1})
                else:
                    frq_word_dict.update({word: frq_word_dict[word] + 1})
    del_lst = []
    for key in frq_word_dict:
        if frq_word_dict[key] < 20 or len(key) < 2:
            del_lst.append(key)
    for key in del_lst:
        frq_word_dict.pop(key, None)
    return

# build_frq_word_dict()
