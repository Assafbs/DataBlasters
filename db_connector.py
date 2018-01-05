import MySQLdb as mdb

class DbConnector:

    def __init__(self):
        self.con = mdb.connect('localhost', 'root', 'Password!1', "my_schema")

    def get_connection(self):
        return self.con

    def get_result_for_query(self, query):
        cur = self.con.cursor(mdb.cursors.DictCursor)
        cur.execute(query)
        return cur.fetchone()

    def get_all_results_for_query(self, query):
        cur = self.con.cursor(mdb.cursors.DictCursor)
        cur.execute(query)
        return cur.fetchall()

    def update_game_result(self, game_id, user_id, score):
        cur = self.con.cursor(mdb.cursors.DictCursor)
        cur.execute(self.create_score_update_query(game_id, user_id, score))

    def create_score_update_query(self, game_id, user_id, score):
        #TODO: replace with the right query
        return "query"

#TODO: Add missing methods