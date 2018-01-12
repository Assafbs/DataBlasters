from flask import Flask, render_template, make_response
from Pages.GameSelection import game_selection
from Pages.Highscores import highscores
from Games.ReleaseOrderGame import release_order_game, release_order_game_
from Games.TranslationGame import translate_game, translate_game_
from Games.PairsGame import pairs_game, pairs_game_

app = Flask(__name__)
app.register_blueprint(game_selection)
app.register_blueprint(highscores)
app.register_blueprint(release_order_game)
app.register_blueprint(release_order_game_)
app.register_blueprint(translate_game)
app.register_blueprint(translate_game_)
app.register_blueprint(pairs_game)
app.register_blueprint(pairs_game_)


@app.route('/')
def create_game_selection_page():
    # TODO: replace with real score
    response = make_response(render_template('home.html', current_score=0))
    return response


if __name__ == '__main__':
    app.run(debug=True)  # TODO: delete this, this is just for debugging
