import nHentaiTagBot.nHentaiTagBot as hBot
import os
from flask import Flask, request, abort
import cloudinary.uploader
import cloudinary.api
from hsauce.comment_builder import build_comment
from hsauce.get_source import get_source_data
from sauce import Trace
import base64

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage
)

cloudinary.config(
    cloud_name="fuwa",
    api_key="461525941189854",
    api_secret="2WH2cEgKQH4YOy5IDsJ2Y3xp3Gk"
)

TEMP = ''

app = Flask(__name__)
port = int(os.environ.get('PORT', 33507))

line_bot_api = LineBotApi(
    'Et/GenKz1+jjMORi4d0O3y7gbo6hAxu7QcDhzV2yt+UIEOwTS71OYn1ZaIG'
    'Vl75mwUvmo0jUCBzGDcpZsNYIhU0JPVTSasQR85TY2lqZ9S1j9E2u+Yz'
    'YIIWTFvvhrvzvo73PFli6RDLyPdXokUeLtwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('cf4b093ef93814e87584e46d305357ac')


def handle_command(text):
    if text == "!sauce":
        return build_comment(get_source_data(TEMP))
    if text == "!sauce-anime-ext":
        return Trace.res(TEMP, "ext")
    if text == "!sauce-anime":
        return Trace.res(TEMP)
    m = hBot.processComment(text)
    if m:
        return m


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    m = handle_command(event.message.text)
    type = event.message.source.type

    if type == 'user':
        id = event.message.source.user_id
    if type == 'group':
        id = event.message.source.group_id
    if type == 'room':
        id = event.message.source.room_id

    if m:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=m))


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    global TEMP
    r = b''
    s = ''
    message_content = line_bot_api.get_message_content(event.message.id)
    with open('temp', 'wb') as fd:
        for chunk in message_content.iter_content():
            print(type(chunk))
            r += chunk
            s += base64.decodebytes(chunk)
            fd.write(chunk)
    print('aa', s)
    print('bb', r)
    res = cloudinary.uploader.upload('temp', public_id='', tags="TEMP")
    TEMP = res['url']
    print(TEMP)


app.run(host='0.0.0.0', port=port)
