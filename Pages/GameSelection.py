from flask import render_template, make_response, Blueprint, request, redirect
import Common.common

game_selection = Blueprint('game_selection', __name__, template_folder='templates')


@game_selection.route('/game_selection')
def create_game_selection_page():
    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    if nickname is None:
        return redirect('/log_in')
    score = Common.common.get_value_from_cookie(request, 'score')
    response = make_response(render_template('game_selection.html', score=score, nickname=nickname))
    return response
