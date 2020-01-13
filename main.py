from handlers.lineHandler import line
from flask import Flask
from threading import Thread

app = Flask(__name__)

app.register_blueprint(line)


@app.route('/')
def home():
    print("Hello")
    return "Hello"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


keep_alive()