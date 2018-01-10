import random
import sys
from flask import Flask, render_template, request, make_response, Blueprint
import GameManager
from db_connector import DbConnector

app = Flask(__name__)  # TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging

NUM_QUESTIONS_PER_GAME = 5
game_manager = GameManager.GameManager()
pairs_game = Blueprint('pairs_game', __name__, template_folder='templates')
pairs_game_ = Blueprint('pairs_game_', __name__, template_folder='templates')


@pairs_game.route('/pairs_game')
def translate_game_start():
    game_manager.start_new_game()
    return create_game_page()


@pairs_game_.route('/pairs_game_')
def translate_game_mid():
    allow_access = request.cookies.get('allowAccess')
    points = int(request.cookies.get('points'))
    response = game_manager.calc_mid_game(allow_access, points, NUM_QUESTIONS_PER_GAME)

    if response is None:
        return create_game_page()
    else:
        return response


def get_all_songs():
    lst_of_artists = DbConnector.get_n_random_artists(7)
    winner_artist = random.randint(0, 6)
    lst_of_bad_songs = list()
    winner_songs = list()
    for i in range(7):
        if i == winner_artist:
            winner_songs = DbConnector.get_n_random_songs_from_artist(2, lst_of_artists[i])
        else:
            lst_of_bad_songs.append(DbConnector.get_n_random_songs_from_artist(1, lst_of_artists[i]))
    return winner_songs, lst_of_bad_songs


def create_game_page():
    reload(sys)
    sys.setdefaultencoding('UTF8')
    DbConnector.create_view_songs_per_artists()  # need to drop view when finish game

    winner_songs, lst_of_bad_songs = get_all_songs()

    right_answer = winner_songs[0][0] + " | | " + winner_songs[1][0]
    wrong_answers = calc_answers(lst_of_bad_songs)
    answers = random.sample(wrong_answers + [right_answer], 4)

    response = make_response(render_template('PairsGame.html',
                                             question=" Which of these pairs of songs were released by the same artist?",
                                             option_1=answers[0],
                                             option_2=answers[1],
                                             option_3=answers[2],
                                             option_4=answers[3],
                                             current_score=game_manager.score))
    response.set_cookie('correctAnswerNum', str(answers.index(right_answer) + 1))
    return game_manager.update_cookies_for_new_question(response)


def calc_answers(bad_songs):
    lst_of_answers = list()
    for i in range(3):
        lst_of_answers.append(bad_songs.pop()[0][0] + " | | " + bad_songs.pop()[0][0])
    return lst_of_answers


# TODO: delete the / route, this is just for debugging
@app.route('/')
def hello_world():
    return "Imagine Assaf's Level Selection Page"


# TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging
if __name__ == '__main__':
    app.run(debug=True)
