from flask import render_template, make_response, Blueprint, request, redirect
import Common.common

bonus = Blueprint('bonus', __name__, template_folder='templates')


@bonus.route('/bonus')
def create_bonus_page():
    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    # Make sure user is logged in, otherwise redirect to log in page.
    if nickname is None:
        return redirect('/log_in')
    score = Common.common.get_value_from_cookie(request, 'score')
    user_score = Common.common.get_value_from_cookie(request, 'score')
    if float(user_score) > 500 and nickname is not None:
        get_bonus = 'true'
    else:
        get_bonus = ''
        return render_template('404.html'), 404
    response = make_response(render_template('bonus.html', score=score, nickname=nickname, bonus=get_bonus))
    return response
