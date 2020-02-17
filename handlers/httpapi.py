import base64
import threading
import time
from handlers.sauce import get_source, comment_builder
from flask import Flask, request, abort, Blueprint, current_app, jsonify, render_template
from handlers import proxyhandler

import cv2
import json
import os

proxyhandler.run()

api = Blueprint('api', __name__)


@api.route('/upload', methods=['GET', 'POST'])
def upload():
    return render_template('upload.html')


@api.route('/proxies')
def proxies():
    if proxyhandler.proxies:
        return jsonify(proxyhandler.proxies)
    else:
        threading.Thread(target=proxyhandler.get_proxies()).start()
        return 'No Proxy'


@api.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        print(f)
        r = get_source.get_source_data(f, force=False, trace=True)
        return comment_builder.build_comment(r)