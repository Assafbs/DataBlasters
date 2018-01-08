from flask import redirect, url_for, Response


# game manager has an instance per game (for example translate game), and not per the whole application
class GameManager:

    def __init__(self):
        self.score = 0
        self.answer_num = 0

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
            # TODO: call david's method for updating score with SCORE
            a = url_for('create_game_selection_page')
            return redirect('/game_selection') 
        else:
            return None

    def update_cookies_for_new_question(self, response):
        response.set_cookie('questionNum', str(self.answer_num + 1))
        response.set_cookie('allowAccess', 'false')
        response.set_cookie('points', '0')  # setting points back to 0 to prevent cheating

        return response

