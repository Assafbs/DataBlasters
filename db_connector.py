import MySQLdb as mdb
from server import session
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
    def update_game_result(game_id, score):
        con = mdb.connect(ADDRESS, USERNAME, PASSWORD, SCHEMA)
        nickname = session['nickname']
        with con:
            cur = con.cursor()
            query, tuple_of_vars = QueryGenerator.create_score_update_query(nickname, game_id, score)
            cur.execute(query, tuple_of_vars)

    @staticmethod
    def create_view_songs_per_artists():
        con = mdb.connect(ADDRESS, USERNAME, PASSWORD, SCHEMA)
        with con:
            cur = con.cursor()
            cur.execute(QueryGenerator.create_view_songs_per_artists())

    @staticmethod
    def drop_view_songs_per_artists():
        con = mdb.connect(ADDRESS, USERNAME, PASSWORD, SCHEMA)
        with con:
            cur = con.cursor()
            cur.execute(QueryGenerator.drop_view_songs_per_artists())

    @staticmethod
    def get_n_random_artists(n):
        con = mdb.connect(ADDRESS, USERNAME, PASSWORD, SCHEMA)
        lst_of_artists = list()
        with con:
            cur = con.cursor()
            query, tuple_of_vars = QueryGenerator.get_n_random_artists(n)
            cur.execute(query, tuple_of_vars)
            for i in range(cur.rowcount):
                lst_of_artists.append((cur.fetchone()[0]))
            return lst_of_artists

    @staticmethod
    def get_n_random_songs_from_artist(n, artist_id):
        con = mdb.connect(ADDRESS, USERNAME, PASSWORD, SCHEMA)
        lst_of_songs = list()
        with con:
            cur = con.cursor()
            cur.execute(QueryGenerator.drop_view_songs_by_artist())
            query, tuple_of_vars = QueryGenerator.create_view_songs_by_artist(artist_id)
            cur.execute(query, tuple_of_vars)
            query, tuple_of_vars = QueryGenerator.get_n_random_songs_by_artist(n)
            cur.execute(query, tuple_of_vars)
            for i in range(cur.rowcount):
                row = cur.fetchone()
                lst_of_songs.append((row[0], row[1]))
            # cur.execute(QueryGenerator.drop_view_songs_by_artist())
        return lst_of_songs

    @staticmethod
    def get_artist_name_by_id(artist_id):
        con = mdb.connect(ADDRESS, USERNAME, PASSWORD, SCHEMA)
        with con:
            cur = con.cursor()
        query, tuple_of_vars = QueryGenerator.get_artist_name_by_id(artist_id)
        cur.execute(query, tuple_of_vars)
        return cur.fetchone[0]

# TODO: Add missing methods
