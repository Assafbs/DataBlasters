from flask import render_template, make_response, Blueprint, request, redirect, Markup
import Common.common
from Common.db_connector import DbConnector
from Common.query_generator import QueryGenerator


highscores = Blueprint('highscores', __name__, template_folder='templates')
@highscores.route('/highscores')
def create_highscores_page():
    return create_highscores_page("All Games", 1)

highscores_ranking_by_country = Blueprint('highscores_ranking_by_country', __name__, template_folder='templates')
@highscores_ranking_by_country.route('/highscores_ranking_by_country')
def create_highscores_page():
    return create_highscores_page("Ranking By Country", 2)

highscores_who_sang_with_who = Blueprint('highscores_who_sang_with_who', __name__, template_folder='templates')
@highscores_who_sang_with_who.route('/highscores_who_sang_with_who')
def create_highscores_page():
    return create_highscores_page("Who Sang With Who", 3)

highscores_pairs_matching = Blueprint('highscores_pairs_matching', __name__, template_folder='templates')
@highscores_pairs_matching.route('/highscores_pairs_matching')
def create_highscores_page():
    return create_highscores_page("Pairs Matching", 4)

highscores_word_in_commom = Blueprint('highscores_word_in_commom', __name__, template_folder='templates')
@highscores_word_in_commom.route('/highscores_word_in_commom')
def create_highscores_page():
    return create_highscores_page("Word In Common", 5)

highscores_translation = Blueprint('highscores_translation', __name__, template_folder='templates')
@highscores_translation.route('/highscores_translation')
def create_highscores_page():
    return create_highscores_page("Translations", 6)

highscores_release_order = Blueprint('highscores_release_order', __name__, template_folder='templates')
@highscores_release_order.route('/highscores_release_order')
def create_highscores_page():
    return create_highscores_page("Release Order", 7)

def create_highscores_page(category, num):
    nickname = Common.common.get_value_from_cookie(request, 'nickname')
    if nickname is None:
        return redirect('/log_in')
    user_score = Common.common.get_value_from_cookie(request, 'score')
    connector = DbConnector()
    top_users = get_relevant_result(connector, num)
    users_scores = get_relevant_user_scores(connector, num, nickname)
    connector.close()
    dummy_user = ("", "")
    while len(top_users) < 10: # In case we have less than 10 users, fill with dummy ones.
        top_users = top_users + (dummy_user, )
    response = make_response(render_template('highscores.html',
                                             category=category,
                                             score=user_score,
                                             nickname=nickname,
                                             user_score=users_scores[0][0],
                                             user_total_points=users_scores[0][1],
                                             tab1=get_tab_class(1, num),
                                             tab2=get_tab_class(2, num),
                                             tab3=get_tab_class(3, num),
                                             tab4=get_tab_class(4, num),
                                             tab5=get_tab_class(5, num),
                                             tab6=get_tab_class(6, num),
                                             tab7=get_tab_class(7, num),
                                             user_1=mark_if_user(top_users[0][0], nickname),
                                             score_user_1=clean(top_users[0][1]),
                                             user_2=mark_if_user(top_users[1][0], nickname),
                                             score_user_2=clean(top_users[1][1]),
                                             user_3=mark_if_user(top_users[2][0], nickname),
                                             score_user_3=clean(top_users[2][1]),
                                             user_4=mark_if_user(top_users[3][0], nickname),
                                             score_user_4=clean(top_users[3][1]),
                                             user_5=mark_if_user(top_users[4][0], nickname),
                                             score_user_5=clean(top_users[4][1]),
                                             user_6=mark_if_user(top_users[5][0], nickname),
                                             score_user_6=clean(top_users[5][1]),
                                             user_7=mark_if_user(top_users[6][0], nickname),
                                             score_user_7=clean(top_users[6][1]),
                                             user_8=mark_if_user(top_users[7][0], nickname),
                                             score_user_8=clean(top_users[7][1]),
                                             user_9=mark_if_user(top_users[8][0], nickname),
                                             score_user_9=clean(top_users[8][1]),
                                             user_10=mark_if_user(top_users[9][0], nickname),
                                             score_user_10=clean(top_users[9][1]),
                                             ))
    return response

def get_tab_class(tab_num, num):
    if tab_num == num:
        return "active"
    else:
        return ""

def get_relevant_result(connector, num):
        if num == 1:
            return connector.get_all_results_for_query(QueryGenerator.get_top_ten_query())
        else:
            return connector.get_all_results_for_query(QueryGenerator.get_top_ten_query_for_game(),(num-1,num-1))

def get_relevant_user_scores(connector, num, nickname):
    if num == 1:
        users_scores = connector.get_all_results_for_query(QueryGenerator.get_score_and_total_points(), (nickname, nickname))
    else:
        users_scores = connector.get_all_results_for_query(QueryGenerator.get_user_scores_for_game(), (num - 1, nickname, num - 1, nickname))
    if len(users_scores) == 0 or users_scores[0][0] is None:
        users_scores = [(0, 0)]
    return users_scores

def clean(arg):
    if arg is None:
        return 0
    return arg

def mark_if_user(arg, nickname):
    if arg == nickname:
        return Markup("<b>"+arg+"</b>")
    else:
        return arg