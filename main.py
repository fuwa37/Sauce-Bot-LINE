import nHentaiTagBot.nHentaiTagBot as hBot
import os
from flask import Flask, request, abort
import cloudinary.uploader
import cloudinary.api
from hsauce.comment_builder import build_comment
from hsauce.get_source import get_source_data
import sauce
import base64
import threading
import time

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, VideoSendMessage
)

cloudinary.config(
    cloud_name="fuwa",
    api_key="461525941189854",
    api_secret="2WH2cEgKQH4YOy5IDsJ2Y3xp3Gk"
)

versioning_dic = {}
is_sleep = {'trace': False,
            'sauce': False}
is_dead = {'trace': False,
           'sauce': False}

bot_commands = {'!sauce',
                '!sauce-anime',
                '!sauce-anime-raw',
                '!sauce-anime-ext',
                '!sauce-anime-ext+',
                '!sauce-anime-mini'}
sleep_time = {'trace': 0,
              'sauce': 0}
death_time = {'trace': 0,
              'sauce': 0}
status = {'trace': 1,
          'sauce': 1}

base_url = "https://res.cloudinary.com/fuwa/image/upload/v"

app = Flask(__name__)
port = int(os.environ.get('PORT', 33507))

line_bot_api = LineBotApi(
    'Et/GenKz1+jjMORi4d0O3y7gbo6hAxu7QcDhzV2yt+UIEOwTS71OYn1ZaIG'
    'Vl75mwUvmo0jUCBzGDcpZsNYIhU0JPVTSasQR85TY2lqZ9S1j9E2u+Yz'
    'YIIWTFvvhrvzvo73PFli6RDLyPdXokUeLtwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('cf4b093ef93814e87584e46d305357ac')


def handle_command(text, iid):
    global sleep_time
    global is_sleep
    global status

    if text[:1] == '!':
        m = hBot.processComment(text)
        if m:
            return {'source': 'hbot',
                    'reply': m}
        if text in bot_commands:
            url = base_url + versioning_dic.get(str(iid)) + '/' + iid

            if text == "!sauce":
                return build_comment(get_source_data(url))

            if is_sleep["trace"]:
                return {
                    'status': "(-_-) zzz\nBot is exhausted\n\nPlease wait for " + str(sleep_time['trace']) + " second"}
            if is_dead["trace"]:
                return {'status': "(-_-) zzz\nBot is dead\n\nPlease wait for resurrection in " + str(
                    death_time['trace']) + " second"}
            if text == "!sauce-anime":
                return sauce.reply(sauce.res(url))
            if text == "!sauce-anime-ext":
                return sauce.reply(sauce.res(url, 'ext'))
            if text == "!sauce-anime-ext+":
                return sauce.reply(sauce.res(url, 'ext+'))
            if text == "!sauce-anime-mini":
                return sauce.reply(sauce.res(url, 'mini'))
            if text == "!sauce-anime-raw":
                return sauce.reply(sauce.res(url, 'raw'))


def handle_sleep(t, sauce):
    time_t = threading.Thread(target=handle_sleeping, args=(t, sauce))
    time_t.start()


def handle_sleeping(t, sauce):
    global sleep_time
    global is_sleep
    is_sleep[sauce] = True
    temp = t
    sleep_time[sauce] = t
    for i in range(t, 0, -1):
        time.sleep(1)
        sleep_time[sauce] -= 1
    sleep_time[sauce] = temp
    is_sleep[sauce] = False


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

    if m.get('reply'):
        if m["source"] == 'trace':
            line_bot_api.reply_message(
                event.reply_token,
                [VideoSendMessage(original_content_url=m["url"],
                                  preview_image_url=base_url + versioning_dic.get(str(iid)) + '/' + iid),
                 TextSendMessage(text=m["comment"])])
            if m['limit'] < 9:
                handle_sleep(m["limit_ttl"], m['source'])
        if m["source"] == 'saucenao':
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text=m["reply"])])
        if m["source"] == 'hbot':
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=m["reply"]))

    elif is_sleep['trace'] or is_dead['trace']:
        line_bot_api.reply_message(
            event.reply_token,
            [ImageSendMessage(original_content_url=base_url + versioning_dic.get(str(iid)) + '/' + iid,
                              preview_image_url=base_url + versioning_dic.get(str(iid)) + '/' + iid),
             TextSendMessage(text=m['status'])])


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
    versioning_dic.update({str(iid): str(res['version'])})


app.run(host='0.0.0.0', port=port)
