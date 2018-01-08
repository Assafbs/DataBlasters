from flask import Flask, render_template, make_response

# TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging
app = Flask(__name__)


@app.route('/game-selection')
def create_game_selection_page():
    # TODO: replace with real score
    response = make_response(render_template('game_selection.html', current_score=0))
    return response


# TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging
if __name__ == '__main__':
    app.run(debug=True)
