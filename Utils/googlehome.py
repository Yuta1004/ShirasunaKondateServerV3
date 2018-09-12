import os, sys
sys.path.append(os.getcwd())

from DB.kondate_db_helper import KondateDBHelper


def get_read_kondate_txt(year, month, day, _type):
    read_txt = "献立データが存在しません"

    helper = KondateDBHelper()
    if not helper.exsits_data(year, month, day):
        return read_txt
    
    read_txt = ""

    kondate_data = helper.get_kondate_data(year, month, day)
    types = ["breakfast", "lunch", "dinner"]
    types_japanese = {"breakfast": "朝食", "lunch": "昼食", "dinner": "夕食"}
    
    if _type != 3:
        types = [types[_type]]

    for _type in types:
        read_txt += types_japanese[_type] + "\n\n"
        menu_list = kondate_data[_type]["menu_list"]

        for menu in menu_list:
            read_txt += menu + "\n"
        read_txt += kondate_data[_type]["nutritive_list"]["calorie"] + "キロカロリーです\n"

    read_txt += "以上です"
    return read_txt
