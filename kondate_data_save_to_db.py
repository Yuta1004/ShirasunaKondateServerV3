import sqlite3
import datetime
from dateutil.relativedelta import relativedelta
import os

from Utils.download_kondate_pdf import download_kondate_pdf
from Utils.pdf_convert import get_kondate_from_pdf
from Utils.format import list_to_plaintext


def kondate_data_save_to_db(year=None, month=None):
    now_date = datetime.datetime.now()
    if year is None:
        year = now_date.year
    if month is None:
        month = now_date.month

    ret_code = download_kondate_pdf(year, month)
    if ret_code == 1:
        raise ValueError("PDFファイルがサーバ上に存在しません．年月が正しいか確認してください．")

    par_dir = os.path.dirname(os.path.abspath(__file__))

    kondate_all_data = get_kondate_from_pdf(par_dir, year, month)

    connect = sqlite3.connect(par_dir + "/DB/kondate.db")
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

            cur.execute("""REPLACE INTO {} VALUES (?, ?, ?)""".format(table_name), (date, menu, nutritive))

            connect.commit()
    cur.close()
    connect.close()


def kondate_data_save_to_db_now(varbose=True):
    today = datetime.datetime.today()
    next_month = today + relativedelta(months=1)

    years = [today.year, next_month.year]
    months = [today.month, next_month.month]

    for year, month in zip(years, months):
        try:
            kondate_data_save_to_db(year, month)
            if varbose: print("Success Save to DB: ", year, month)
        except ValueError:
            if varbose: print("ValueError")


if __name__ == '__main__':
    kondate_data_save_to_db_now(varbose=True)
