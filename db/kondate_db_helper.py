import sqlite3
import os


class KondateDBHelper:
    def __init__(self):
        self.db_dir = os.path.dirname(os.path.abspath(__file__))
        self.connect = sqlite3.connect(self.db_dir + "/kondate.db")
        self.cur = self.connect.cursor()

    def db_connect_close(self):
        self.cur.close()
        self.connect.close()
