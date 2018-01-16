import os
from flask import Flask, render_template, make_response,session

from Games.GameManager import game_conclusion
from Games.PairsGame import pairs_game, pairs_game_
from Games.RankByCountryGame import rank_by_country_game, rank_by_country_game_
from Games.ReleaseOrderGame import release_order_game, release_order_game_
from Games.TranslationGame import translate_game, translate_game_
from Games.DuetsGame import duets_game, duets_game_
from Pages.GameSelection import game_selection
from Pages.Highscores import highscores
from Pages.server import log_in
from Pages.server import sign_up

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

app.secret_key = os.urandom(12)

@app.route('/')
def create_game_selection_page():
    # TODO: replace with real score
    response = make_response(render_template('home.html', current_score=0))
    return response


if __name__ == '__main__':
    app.run(debug=True)  # TODO: delete this, this is just for debugging
