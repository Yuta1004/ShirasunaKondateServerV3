from DB.various_db_helper import VariousDBHelper
import requests
import json

def line_notify(message):
    helper = VariousDBHelper()
    access_token = helper.get_data("line_token")

    headers = {
        "Content-Type": "application/json",
        "Access-Token": access_token
    }
    messages = {
        "messages": [
            {"type": "text", "text": message}
        ]
    }

    requests.post("https://nityc-nyuta.work/server_management_line_bot/push", data=json.dumps(messages), headers=headers)
