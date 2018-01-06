from flask import Flask, render_template, make_response
from Games import GameManager

# TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging
app = Flask(__name__)

game_manager = GameManager.GameManager()


@app.route('/GameSelection')
def create_game_selection_page():
    response = make_response(render_template('game_selection.html', current_score=game_manager.score))
    return response


# TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging
if __name__ == '__main__':
    app.run(debug=True)
