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
            menu_from_db = self.cur.execute(query, (str_date,)).fetchone()
            query = "SELECT nutritive_list FROM {} WHERE date=?".format(time)
            nutritive_from_db = self.cur.execute(query, (str_date,)).fetchone()

            nutritive_from_db = plaintext_to_list(nutritive_from_db[0])
            nutritive_list = alignment_nutritive_list(nutritive_from_db)

            kondate_data[time]["menu_list"] = plaintext_to_list(menu_from_db[0])
            kondate_data[time]["nutritive_list"] = format_nutritive_list(nutritive_list)

        return kondate_data

    def exsits_data(self, year, month, day):
        str_date = str(year) + str(month).zfill(2) + str(day).zfill(2)

        ret_flag = True
        for time in ["breakfast", "lunch", "dinner"]:
            query = "SELECT * FROM {} WHERE date=?".format(time)
            exsits = self.cur.execute(query, (str_date,)).fetchmany()

            if len(exsits) == 0:
                ret_flag = False

        return ret_flag

    def db_connect_close(self):
        self.cur.close()
        self.connect.close()

    def __del__(self):
        self.db_connect_close()


# PDFによっては栄養情報の並び順がおかしくなるのでこの関数で修正する
def alignment_nutritive_list(nutritive_list):
    if len(nutritive_list) < 2:
        return nutritive_list

    if float(nutritive_list[1]) > 100:
        tmp = nutritive_list[0]
        nutritive_list[:3] = nutritive_list[1:4]
        nutritive_list[3] = tmp

    return nutritive_list


# 栄養情報(リスト)を辞書にして返す
# この関数はalignment_nutritive_listを呼んでから実行すること!!!!
def format_nutritive_list(nutritive_list):
    if len(nutritive_list) < 5:
        return {}

    return {
        "calorie": nutritive_list[0],
        "protein": nutritive_list[1],
        "lipid": nutritive_list[2],
        "carbohydrate": nutritive_list[3],
        "salt": nutritive_list[4]
    }
