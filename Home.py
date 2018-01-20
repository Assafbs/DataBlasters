import os

from flask import Flask, render_template, make_response, request

import Common.common
from Games.DuetsGame import duets_game, duets_game_
from Games.GameManager import game_conclusion
from Games.PairsGame import pairs_game, pairs_game_
from Games.RankByCountryGame import rank_by_country_game, rank_by_country_game_
from Games.ReleaseOrderGame import release_order_game, release_order_game_
from Games.TranslationGame import translate_game, translate_game_
from Games.WordInSongs import word_in_songs, word_in_songs_
from Pages.Authentication import log_in, sign_up, log_out, new_pass
from Pages.GameSelection import game_selection
from Pages.Bonus import bonus
from Pages.Highscores import highscores, highscores_ranking_by_country, highscores_who_sang_with_who, highscores_pairs_matching, highscores_word_in_commom, highscores_translation, \
    highscores_release_order

app = Flask(__name__)
app.register_blueprint(bonus)
app.register_blueprint(game_selection)
app.register_blueprint(game_conclusion)
app.register_blueprint(highscores)
app.register_blueprint(highscores_ranking_by_country)
app.register_blueprint(highscores_who_sang_with_who)
app.register_blueprint(highscores_pairs_matching)
app.register_blueprint(highscores_word_in_commom)
app.register_blueprint(highscores_translation)
app.register_blueprint(highscores_release_order)
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
app.register_blueprint(new_pass)
app.register_blueprint(word_in_songs)
app.register_blueprint(word_in_songs_)
app.secret_key = os.urandom(12)


@app.route('/')
def create_home_page():
    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    user_logon = ''
    if nickname is not None:
        user_logon = 'true'
    user_score = Common.common.get_value_from_cookie(request, 'score')
    response = make_response(render_template('home.html', nickname=nickname, user_logon=user_logon, score=user_score))
    return response


# Show a custom page in case of a 404 error.
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(port=40557, host='0.0.0.0')
    # app.run(debug=True)
