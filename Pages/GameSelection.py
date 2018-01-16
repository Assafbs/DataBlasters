from flask import Flask, render_template, make_response, Blueprint, request, redirect
from query_generator import QueryGenerator

game_selection = Blueprint('game_selection', __name__, template_folder='templates')


@game_selection.route('/game_selection')
def create_game_selection_page():
    # TODO: replace with real score
    cookie_state=request.cookies.get('nickname')
    if(cookie_state is None):
        return redirect("http://127.0.0.1:5000/sign_up")
    score=request.cookies.get('score')
    response = make_response(render_template('game_selection.html', current_score=score))
    return response
