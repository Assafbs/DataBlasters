import MySQLdb as mdb
from query_generator import QueryGenerator

ADDRESS = 'localhost'
USERNAME = 'root'
PASSWORD = 'Armageddon1'
SCHEMA = 'mr_music2'


class DbConnector:

    def __init__(self):
        pass

    @staticmethod
    def get_result_for_query(query):
        con = mdb.connect(ADDRESS, USERNAME, PASSWORD, SCHEMA)
        with con:
            cur = con.cursor()
            cur.execute(query)
            return cur.fetchone()

    @staticmethod
    def get_result_for_query_with_args(query, arguments):
        con = mdb.connect(ADDRESS, USERNAME, PASSWORD, SCHEMA)
        with con:
            cur = con.cursor()
            cur.execute(query, arguments)
            return cur.fetchone()

    @staticmethod
    def get_all_results_for_query(query):
        con = mdb.connect(ADDRESS, USERNAME, PASSWORD, SCHEMA)
        with con:
            cur = con.cursor()
            cur.execute(query)
            return cur.fetchall()

    @staticmethod
    def get_all_results_for_query_with_args(query, arguments):
        con = mdb.connect(ADDRESS, USERNAME, PASSWORD, SCHEMA)
        with con:
            cur = con.cursor()
            cur.execute(query, arguments)
            return cur.fetchall()

    @staticmethod
    def update_game_result(nickname, game_id, score):
        con = mdb.connect(ADDRESS, USERNAME, PASSWORD, SCHEMA)
        with con:
            cur = con.cursor()
            query, tuple_of_vars = QueryGenerator.create_score_update_query(nickname, game_id, score)
            cur.execute(query, tuple_of_vars)

# TODO: Add missing methods
