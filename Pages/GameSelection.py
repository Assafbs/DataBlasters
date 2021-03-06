from flask import render_template, make_response, Blueprint, request, redirect
import Common.common

game_selection = Blueprint('game_selection', __name__, template_folder='templates')


@game_selection.route('/game_selection')
def create_game_selection_page():
    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    # Make sure user is logged in, otherwise redirect to log in page.
    if nickname is None:
        return redirect('/log_in')
    user_score = Common.common.get_value_from_cookie(request, 'score')
    if float(user_score) > 500 and nickname is not None:
        get_bonus = 'true'
    else:
        get_bonus = ''
    score = Common.common.get_value_from_cookie(request, 'score')
    response = make_response(render_template('game_selection.html', score=score, nickname=nickname, bonus=get_bonus))
    return response
