from flask import Flask, render_template, make_response, Blueprint, request, redirect
from Games import GameManager
import Common.common
from db_connector import DbConnector
from query_generator import QueryGenerator


game_manager = GameManager.GameManager(3)

highscores = Blueprint('highscores', __name__, template_folder='templates')
@highscores.route('/highscores')
def create_game_selection_page():
    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    if nickname is None:
        return redirect('/')
    user_score = Common.common.get_value_from_cookie(request, 'score')
    connector = DbConnector()
    top_users = connector.get_all_results_for_query(QueryGenerator.get_top_ten_query())
    connector.close()
    dummy_user = ("", "")
    while len(top_users) < 10: # In case we have less than 10 users, fill with dummy ones.
        top_users = top_users + (dummy_user, )
        print top_users
    response = make_response(render_template('highscores.html',
                                             score=user_score,
                                             nickname=nickname,
                                             user_1=top_users[0][0],
                                             score_user_1=top_users[0][1],
                                             user_2=top_users[1][0],
                                             score_user_2=top_users[1][1],
                                             user_3=top_users[2][0],
                                             score_user_3=top_users[2][1],
                                             user_4=top_users[3][0],
                                             score_user_4=top_users[3][1],
                                             user_5=top_users[4][0],
                                             score_user_5=top_users[4][1],
                                             user_6=top_users[5][0],
                                             score_user_6=top_users[5][1],
                                             user_7=top_users[6][0],
                                             score_user_7=top_users[6][1],
                                             user_8=top_users[7][0],
                                             score_user_8=top_users[7][1],
                                             user_9=top_users[8][0],
                                             score_user_9=top_users[8][1],
                                             user_10=top_users[9][0],
                                             score_user_10=top_users[9][1],
                                             ))
    return response

