import MySQLdb as mdb

# ADDRESS = 'mysqlsrv.cs.tau.ac.il'  # '127.0.0.1'
ADDRESS = 'localhost'  # 'mysqlsrv.cs.tau.ac.il'  # 'localhost'
USERNAME = 'DbMysql09'  # 'root'
PASSWORD = 'DbMysql09'  # 'root'
SCHEMA = 'DbMysql09'  # 'dbmysql09'


class DbConnector:

    def __init__(self):
        self.con = mdb.connect(ADDRESS, USERNAME, PASSWORD, SCHEMA, port=3305)
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
