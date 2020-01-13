import os
from handlers.lineHandler import line
from flask import Flask

app = Flask(__name__)
port = int(os.environ.get('PORT', 33507))

app.register_blueprint(line)

@app.route('/')
def home():
    print("Hello")
    return "Hello"

app.run(host='0.0.0.0',port=8080)