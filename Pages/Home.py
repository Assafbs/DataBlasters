import os
import Common.common
from flask import Flask, render_template, make_response,request

from Games.GameManager import game_conclusion
from Games.PairsGame import pairs_game, pairs_game_
from Games.RankByCountryGame import rank_by_country_game, rank_by_country_game_
from Games.ReleaseOrderGame import release_order_game, release_order_game_
from Games.TranslationGame import translate_game, translate_game_
from Games.DuetsGame import duets_game, duets_game_
from Games.WordInSongs import word_in_songs,word_in_songs_
from Pages.GameSelection import game_selection
from Pages.Highscores import highscores
from Pages.server import log_in,sign_up,log_out


app = Flask(__name__)
app.register_blueprint(game_selection)
app.register_blueprint(game_conclusion)
app.register_blueprint(highscores)
app.register_blueprint(release_order_game)
app.register_blueprint(release_order_game_)
app.register_blueprint(translate_game)
app.register_blueprint(translate_game_)
app.register_blueprint(duets_game)
app.register_blueprint(duets_game_)
app.register_blueprint(pairs_game)
app.register_blueprint(pairs_game_)
app.register_blueprint(rank_by_country_game)
app.register_blueprint(rank_by_country_game_)
app.register_blueprint(log_in)
app.register_blueprint(sign_up)
app.register_blueprint(log_out)
app.register_blueprint(word_in_songs)
app.register_blueprint(word_in_songs_)
app.secret_key = os.urandom(12)

@app.route('/')
def create_game_selection_page():
    # TODO: replace with real score
    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    score = Common.common.get_value_from_cookie(request, 'score')
    user_logon = ''
    if nickname is not None:
        user_logon = 'true'
    response = make_response(render_template('home.html', nickname=nickname, user_logon=user_logon, score=score))
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0')
