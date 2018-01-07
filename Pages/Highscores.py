from flask import Flask, render_template, make_response
from Games import GameManager
from db_connector import DbConnector
from query_generator import QueryGenerator

# TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging
app = Flask(__name__)

game_manager = GameManager.GameManager()


@app.route('/highscores')
def create_game_selection_page():
    top_users = DbConnector.get_all_results_for_query(QueryGenerator.get_top_ten_query())
    dummy_user = ("", 0)
    while len(top_users) < 10: # In case we have less than 10 users, fill with dummy ones.
        top_users = top_users + (dummy_user, )
        print top_users
    response = make_response(render_template('highscores.html',
                                             current_score=game_manager.score,
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


# TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging
if __name__ == '__main__':
    app.run(debug=True)
