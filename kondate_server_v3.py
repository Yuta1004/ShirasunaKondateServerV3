from flask import Flask, jsonify, request
import json

from db.kondate_db_helper import KondateDBHelper
from utils.check_type import is_float

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route("/")
def index():
    return "Welcome to *-*-*-*-Shirasuna Kondate Server Ver.3-*-*-*-*"


@app.route("/get_kondate", methods=["GET", "POST"])
def get_kondate():
    year = request.args.get("year", None)
    month = request.args.get("month", None)
    day = request.args.get("day", None)

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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=410)
