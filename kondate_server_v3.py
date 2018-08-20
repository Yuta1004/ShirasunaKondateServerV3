from flask import Flask, jsonify, request
import json

from DB.kondate_db_helper import KondateDBHelper
from Utils.check_type import is_float

base_url = ""

app = Flask(__name__)


@app.before_request
def before_request():
    app.config['JSON_AS_ASCII'] = True


@app.route(base_url + "/")
def index():
    return "Welcome to *-*-*-*-Shirasuna Kondate Server Ver.3-*-*-*-*"


@app.route(base_url + "/get_kondate", methods=["GET", "POST"])
def get_kondate():
    year = request.args.get("year", None)
    month = request.args.get("month", None)
    day = request.args.get("day", None)
    non_ascii = request.args.get("ascii", None)

    # APIを叩く時にasciiをFalseにするとUTF-8にエンコーディングしてブラウザ上に表示する
    # 通常はASCIIで返す
    # ブラウザデバッグ用の引数．ASCIIではないjsonは構文エラーを引き起こす可能性がある!!
    if non_ascii == "False":
        app.config['JSON_AS_ASCII'] = False

    if (year is None) or (month is None) or (day is None):
        return jsonify({"code": 400, "error": "Bad Request. Arguments is missing."})

    if not (is_float(year) and is_float(month) and is_float(day)):
        return jsonify({"code": 400, "error": "Bad Request. Argument value is incorrect."})

    year = int(year)
    month = int(month)
    day = int(day)

    helper = KondateDBHelper()
    if helper.exsits_data(year, month, day):
        kondate_data = helper.get_kondate_data(year, month, day)
        kondate_data["code"] = 200
    else:
        kondate_data = {"code": 404, "error": "Data is not registered."}

    return jsonify(kondate_data)


@app.route("/search_kondate")
def search_kondate():
    search_word = request.args.get("keyword", None)

    if search_word is None:
        return jsonify({"code": 400, "error": "Bad Request. Arguments is missing."})

    helper = KondateDBHelper()

    return jsonify(helper.search_kondate_data(search_word))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=410)
