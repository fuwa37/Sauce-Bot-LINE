from flask import Flask
from threading import Thread
from handlers.lineHandler import line
import time
import datetime

startTime = time.time()

app = Flask('')
app.register_blueprint(line)


@app.route('/')
def main():
    return "Your bot is alive!\n\nUptime:\n" + getuptime()


def getuptime():
    uptime = time.time() - startTime
    return str(datetime.timedelta(seconds=uptime)).split(".")[0]


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    server = Thread(target=run)
    server.start()
