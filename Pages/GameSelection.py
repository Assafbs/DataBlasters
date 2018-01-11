from flask import Flask, render_template, make_response, Blueprint
from query_generator import QueryGenerator

game_selection = Blueprint('game_selection', __name__, template_folder='templates')


@game_selection.route('/game_selection')
def create_game_selection_page():
    # TODO: replace with real score
    response = make_response(render_template('game_selection.html', current_score=0))
    return response
