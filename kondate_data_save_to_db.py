import sqlite3
import datetime
import os

from download_kondate_pdf import download_kondate_pdf
from utils.pdf_convert import get_kondate_from_pdf
from utils.format import list_to_plaintext


def kondate_data_save_to_db(year=None, month=None):
    now_date = datetime.datetime.now()
    if year is None or year < 2017:
        year = now_date.year
    if month is None:
        month = now_date.month

    ret_code = download_kondate_pdf(year, month)
    if ret_code == 1:
        raise ValueError("PDFファイルがサーバ上に存在しません．年月が正しいか確認してください．")

    par_dir = os.path.dirname(os.path.abspath(__file__))

    kondate_all_data = get_kondate_from_pdf(par_dir, year, month)

    connect = sqlite3.connect(par_dir + "/db/kondate.db")
    cur = connect.cursor()

    # 献立データをforで回してDBに登録していく…
    for kondate in kondate_all_data:
        kondate_data_dict = {
            "breakfast": {
                "date": kondate.date,
                "menu": kondate.breakfast,
                "nutritive": kondate.breakfast_nutritive
            },
            "lunch": {
                "date": kondate.date,
                "menu": kondate.lunch,
                "nutritive": kondate.lunch_nutritive
            },
            "dinner": {
                "date": kondate.date,
                "menu": kondate.dinner,
                "nutritive": kondate.dinner_nutritive
            }

        }

        for table_name in ["breakfast", "lunch", "dinner"]:
            date = kondate_data_dict[table_name]["date"]
            menu = list_to_plaintext(kondate_data_dict[table_name]["menu"], ";")
            nutritive = list_to_plaintext(kondate_data_dict[table_name]["nutritive"], ";")

            date_exists = cur.execute("""SELECT * FROM {} WHERE date=?""".format(table_name), (date, )).fetchmany()
            if len(date_exists) > 0:
                continue

            cur.execute("""INSERT INTO {} VALUES (?, ?, ?)""".format(table_name), (date, menu, nutritive))

            connect.commit()
    cur.close()
    connect.close()


if __name__ == '__main__':
    year_arg = 2018
    month_arg = 8
    try:
        kondate_data_save_to_db(year_arg, month_arg)
    except ValueError:
        print("ValueError: ", year_arg, month_arg)
