from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "Welcome to *-*-*-*-Shirasuna Kondate Server Ver.3-*-*-*-*"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=410)
