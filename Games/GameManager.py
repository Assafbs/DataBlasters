import time
from flask import redirect, Response, render_template, Blueprint
from db_connector import DbConnector
from query_generator import QueryGenerator
from server import session


# game manager has an instance per game (for example translate game), and not per the whole application
class GameManager:

    def __init__(self, game_id):
        self.score = 0
        self.answer_num = 0
        self.game_id = game_id

    def start_new_game(self):
        self.score = 0
        self.answer_num = 0

    # if this function returns None, need to call the function for generating new question page
    def calc_mid_game(self, allow_access, points, num_questions_per_game):
        if allow_access != 'true':
            return Response('You are not authorized to refresh in order to change question!', 401,
                            {'WWWAuthenticate': 'Basic realm="Login Required"'})
        self.score += points
        self.answer_num += 1

        if self.answer_num == num_questions_per_game:
            # self.update_game_result() #TODO: fix nickname bug here
            return redirect('/game_conclusion/' + str(self.score))
        else:
            return None

    def update_cookies_for_new_question(self, response):
        response.set_cookie('questionNum', str(self.answer_num + 1))
        response.set_cookie('allowAccess', 'false')
        response.set_cookie('points', '0')  # setting points back to 0 to prevent cheating

        return response

    def update_game_result(self):
        # nickname = session['nickname']
        nickname = 'David'
        connector = DbConnector()
        connector.execute_query(QueryGenerator.create_score_update_query(), (nickname, time.strftime('%Y-%m-%d %H:%M:%S'), self.game_id, self.score))
        connector.close()


game_conclusion = Blueprint('game_conclusion', __name__, template_folder='templates')
@game_conclusion.route('/game_conclusion/<int:points>')
def create_game_conclusion_page(points):
    mood_gif = "https://s-media-cache-ak0.pinimg.com/originals/35/84/79/35847900475295ef1ae9b2bff189a9a6.gif"
    label = "Congratulation"
    if points == 0:
        mood_gif = "https://static.tumblr.com/04027311832137002618110a602e2631/v3arm60/92Hoxigo1/tumblr_static_tumblr_static_crv29h2v35wg444s84g08osks_640.gif"
        label = ""

    return render_template('gameConclusion.html',
                           label=label,
                           points=points,
                           mood_gif=mood_gif)

