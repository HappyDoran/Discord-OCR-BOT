import pymysql


class Connection:
    def __init__(self):
        self.host = '127.0.0.1'
        self.user = 'root'
        self.pw = '3860'
        self.db = 'Haccrew'
        self.conn = pymysql.connect(host=self.host, user=self.user, password=self.pw, database=self.db, charset="utf8")
        self.cur = self.conn.cursor()
        print("[알림] DB Connect")

    def __del__(self):
        self.conn.close()
        print("[알림] DB Disconnect")

    def getConnection(self):
        self.conn.ping()
        return self.conn, self.cur


connection = Connection()
