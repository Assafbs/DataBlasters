from flask import Flask, render_template, make_response

app = Flask(__name__)


@app.route('/')
def create_game_selection_page():
    # TODO: replace with real score
    response = make_response(render_template('home.html', current_score=0))
    return response


if __name__ == '__main__':
    app.run(debug=True)  # TODO: delete this, this is just for debugging
