import sqlite3
import os


class RequestsDBHelper:
    def __init__(self):
        self.db_dir = os.path.dirname(os.path.abspath(__file__))
        self.connect = sqlite3.connect(self.db_dir + "/requests.db")
        self.cur = self.connect.cursor()

    def save_requests(self, time, requests):
        self.cur.execute("""INSERT INTO requests VALUES (?, ?)""", (time, requests))
        self.connect.commit()

    def close(self):
        self.cur.close()
        self.connect.close()

    def __del__(self):
        self.close()
