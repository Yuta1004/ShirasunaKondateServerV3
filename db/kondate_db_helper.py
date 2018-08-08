import sqlite3
import os
from utils.format import plaintext_to_list


class KondateDBHelper:
    def __init__(self):
        self.db_dir = os.path.dirname(os.path.abspath(__file__))
        self.connect = sqlite3.connect(self.db_dir + "/kondate.db")
        self.cur = self.connect.cursor()

    def get_kondate_data(self, year, month, day):
        str_date = str(year) + str(month).zfill(2) + str(day).zfill(2)

        kondate_data = {
            "date": str_date,
            "breakfast": {
                "menu_list": [],
                "nutritive_list": []
            },
            "lunch": {
                "menu_list": [],
                "nutritive_list": []
            },
            "dinner": {
                "menu_list": [],
                "nutritive_list": []
            }
        }

        for time in ["breakfast", "lunch", "dinner"]:
            query = "SELECT menu_list FROM {} WHERE date=?".format(time)
            menu_from_db = self.cur.execute(query, (str_date, )).fetchone()
            query = "SELECT nutritive_list FROM {} WHERE date=?".format(time)
            nutritive_from_db = self.cur.execute(query, (str_date, )).fetchone()

            kondate_data[time]["menu_list"] = plaintext_to_list(menu_from_db[0])
            kondate_data[time]["nutritive_list"] = plaintext_to_list(nutritive_from_db[0])

        return kondate_data

    def exsits_data(self, year, month, day):
        str_date = str(year) + str(month).zfill(2) + str(day).zfill(2)

        ret_flag = True
        for time in ["breakfast", "lunch", "dinner"]:
            query = "SELECT * FROM {} WHERE date=?".format(time)
            exsits = self.cur.execute(query, (str_date, )).fetchmany()

            if len(exsits) == 0:
                ret_flag = False

        return ret_flag

    def db_connect_close(self):
        self.cur.close()
        self.connect.close()
