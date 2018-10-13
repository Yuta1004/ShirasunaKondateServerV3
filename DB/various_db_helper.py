import sqlite3
import os

class VariousDBHelper:
    def __init__(self):
        db_dir = os.path.dirname(os.path.abspath(__file__))
        self.db = sqlite3.connect(db_dir + "/various.db")
        self.cur = self.db.cursor()

    def get_data(self, key):
        exists = self.cur.execute("SELECT * FROM data WHERE key=?", (key, )).fetchmany()
        if len(exists) == 0:
            return ""

        value = self.cur.execute("SELECT value FROM data WHERE key=?", (key, )).fetchone()[0]
        
        return value

    def __del__(self):
        self.cur.close()
        self.db.close()
