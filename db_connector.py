import MySQLdb as mdb

ADDRESS = 'localhost'
USERNAME = 'root'
PASSWORD = 'root'   #'Armageddon1'
SCHEMA = 'dbmysql09'           #'mr_music2'


class DbConnector:

    def __init__(self):
        self.con = mdb.connect(ADDRESS, USERNAME, PASSWORD, SCHEMA)
        self.cur = self.con.cursor()

    def close(self):
        self.con.commit()
        self.con.close()

    def execute_query(self, query, arguments=None):
        if arguments is None:
            self.cur.execute(query)
        else:
            self.cur.execute(query, arguments)
        self.con.commit()

    def get_one_result_for_query(self, query, arguments=None):
        if arguments is None:
            self.cur.execute(query)
        else:
            self.cur.execute(query, arguments)
        return self.cur.fetchone()

    def get_all_results_for_query(self, query, arguments=None):
        if arguments is None:
            self.cur.execute(query)
        else:
            self.cur.execute(query, arguments)
        return self.cur.fetchall()

