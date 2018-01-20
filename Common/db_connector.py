import MySQLdb as mdb

ADDRESS = 'mysqlsrv.cs.tau.ac.il'
# ADDRESS = 'localhost'
USERNAME = 'DbMysql09'
PASSWORD = 'DbMysql09'
SCHEMA = 'DbMysql09'


class DbConnector:

    def __init__(self):
        self.con = mdb.connect(ADDRESS, USERNAME, PASSWORD, SCHEMA, port=3306)  # connect to Nova DB
        self.cur = self.con.cursor()

    # commit and close connection
    def close(self):
        self.con.commit()
        self.con.close()

    # execute query with optional arguments. This is used for insert/update statements
    def execute_query(self, query, arguments=None):
        if arguments is None:
            self.cur.execute(query)
        else:
            self.cur.execute(query, arguments)
        self.con.commit()

    #  execute query with optional arguments, return first result
    def get_one_result_for_query(self, query, arguments=None):
        if arguments is None:
            self.cur.execute(query)
        else:
            self.cur.execute(query, arguments)
        return self.cur.fetchone()

    # execute query with optional arguments, return all results
    def get_all_results_for_query(self, query, arguments=None):
        if arguments is None:
            self.cur.execute(query)
        else:
            self.cur.execute(query, arguments)
        return self.cur.fetchall()
