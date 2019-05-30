import nHentaiTagBot.nHentaiTagBot as hBot
import os
from flask import Flask, request, abort
import cloudinary.uploader
import cloudinary.api
from hsauce.comment_builder import build_comment
from hsauce.get_source import get_source_data
import sauce
import base64

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage
)

cloudinary.config(
    cloud_name="fuwa",
    api_key="461525941189854",
    api_secret="2WH2cEgKQH4YOy5IDsJ2Y3xp3Gk"
)

versioning_dic = {}

app = Flask(__name__)
port = int(os.environ.get('PORT', 33507))

line_bot_api = LineBotApi(
    'Et/GenKz1+jjMORi4d0O3y7gbo6hAxu7QcDhzV2yt+UIEOwTS71OYn1ZaIG'
    'Vl75mwUvmo0jUCBzGDcpZsNYIhU0JPVTSasQR85TY2lqZ9S1j9E2u+Yz'
    'YIIWTFvvhrvzvo73PFli6RDLyPdXokUeLtwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('cf4b093ef93814e87584e46d305357ac')


def handle_command(text, iid):
    url = "https://res.cloudinary.com/fuwa/image/upload/v" + versioning_dic.get(str(iid)) + '/' + iid
    if text == "!sauce":
        return build_comment(get_source_data(url))
    if text == "!sauce-anime":
        return sauce.res(url)
    if text == "!sauce-anime-mini":
        return sauce.res(url, "mini")
    if text == "!sauce-anime-raw":
        return sauce.res(url, 'raw')
    m = hBot.processComment(text)
    if m:
        return ('hbot', m)


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
    stype = event.source.type
    iid = ''
    if stype == 'user':
        iid = event.source.user_id
    if stype == 'group':
        iid = event.source.group_id
    if stype == 'room':
        iid = event.source.room_id

    m = handle_command(event.message.text, iid)

    if m[1]:
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text=m[1])])
    else:
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text="None")])


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    r = b''
    iid = ''
    stype = event.source.type
    if stype == 'user':
        iid = event.source.user_id
    if stype == 'group':
        iid = event.source.group_id
    if stype == 'room':
        iid = event.source.room_id
    message_content = line_bot_api.get_message_content(event.message.id)
    for chunk in message_content.iter_content():
        r += chunk
    img = base64.b64encode(r).decode('utf-8')
    res = cloudinary.uploader.upload('data:image/jpg;base64,' + img, public_id=iid, tags="TEMP")
    versioning_dic.update({str(iid): res['version']})


app.run(host='0.0.0.0', port=port)
