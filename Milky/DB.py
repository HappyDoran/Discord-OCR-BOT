import pymysql


class Connection:
    def __init__(self):
        self.host = 'milkydb.cxxuxsbuezoc.ap-northeast-2.rds.amazonaws.com'
        self.user = 'root'
        self.pw = 'milky123!'
        self.db = 'fuckingdb'
        self.conn = pymysql.connect(host=self.host, user=self.user, password=self.pw, database=self.db, charset="utf8")
        self.cur = self.conn.cursor(pymysql.cursors.DictCursor)
        print("[알림] DB Connect")

    def __del__(self):
        self.conn.close()
        print("[알림] DB Disconnect")

    def getConnection(self):
        self.conn.ping()
        return self.conn, self.cur


connection = Connection()
