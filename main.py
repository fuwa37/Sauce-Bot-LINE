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

trace_commands = {'!sauce-anime',
                  '!sauce-anime-raw',
                  '!sauce-anime-ext',
                  '!sauce-anime-ext+',
                  '!sauce-anime-mini'}
sleep_time = {'trace': 0,
              'sauce': 0}
death_time = {'trace': 0,
              'sauce': 0}

sn_counter = 0

help_reply = "Steps:\n" \
             "1. Send image\n" \
             "2. Type command:\n" \
             "'!sauce' - general sauce\n" \
             "'!sauce-anime' - anime sauce\n" \
             "'!sauce-anime-mini' - minimal info\n" \
             "'!sauce-anime-ext' - extended info\n" \
             "'!sauce-anime-ext+' - extended+ info"

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

    if text[:1] == '!':
        m = hBot.processComment(text[1:])
        if m:
            return {'source': 'hbot',
                    'reply': m}
        if '!sauce' in text:
            url = base_url + versioning_dic.get(str(iid)) + '/' + iid

            if text == "!sauce":
                if is_sleep["sauce"]:
                    return {
                        'status': "(-_-) zzz\n!sauce Bot is exhausted\n\nPlease wait for " + str(
                            sleep_time['sauce']) + " seconds"}
                if is_dead["sauce"]:
                    return {'status': "(-_-) zzz\n!sauce Bot is dead\n\nPlease wait for resurrection in " + str(
                        death_time['sauce']) + " seconds"}

                return build_comment(get_source_data(url))

            if '!sauce-anime' in text:
                if is_sleep["trace"]:
                    return {
                        'status': "(-_-) zzz\n!sauce-anime Bot is exhausted\n\nPlease wait for " + str(
                            sleep_time['trace']) + " seconds"}
                if is_dead["trace"]:
                    return {'status': "(-_-) zzz\n!sauce-anime Bot is dead\n\nPlease wait for resurrection in " + str(
                        death_time['trace']) + " seconds"}
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
    else:
        return None


def handle_sleep(t, source):
    sleep_t = threading.Thread(target=handle_sleeping, args=(t, source))
    sleep_t.start()


def handle_sleeping(t, source):
    global sleep_time
    global is_sleep
    is_sleep[source] = True
    sleep_time[source] = t
    for i in range(t, 0, -1):
        time.sleep(1)
        sleep_time[source] -= 1
    sleep_time[source] = t
    is_sleep[source] = False


def handle_death(t, source):
    dead_t = threading.Thread(target=handle_dead, args=(t, source))
    dead_t.start()


def handle_dead(t, source):
    global death_time
    global is_dead
    global sn_counter

    is_dead[source] = True
    death_time[source] = t
    for i in range(t, 0, -1):
        time.sleep(1)
        death_time[source] -= 1
    death_time[source] = t
    if source == 'sauce':
        sn_counter = 0
    is_dead[source] = False


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
    global sn_counter
    stype = event.source.type
    iid = ''
    if stype == 'user':
        iid = event.source.user_id
    if stype == 'group':
        iid = event.source.group_id
    if stype == 'room':
        iid = event.source.room_id

    m = handle_command(event.message.text, iid)

    if m is not None:
        if event.message.text in trace_commands:
            if m.get('reply'):
                line_bot_api.reply_message(
                    event.reply_token,
                    [VideoSendMessage(original_content_url=m["url"],
                                      preview_image_url=base_url + versioning_dic.get(str(iid)) + '/' + iid),
                     TextSendMessage(text=m["comment"])])
                if m['limit'] < 9:
                    handle_sleep(m["limit_ttl"], 'trace')

            if is_sleep['trace'] or is_dead['trace']:
                line_bot_api.reply_message(
                    event.reply_token,
                    [ImageSendMessage(original_content_url=base_url + versioning_dic.get(str(iid)) + '/' + iid,
                                      preview_image_url=base_url + versioning_dic.get(str(iid)) + '/' + iid),
                     TextSendMessage(text=m['status'])])

        if event.message.text == '!sauce':
            if m == 429:
                sn_counter += 1
                handle_sleep(30, 'sauce')

            if sn_counter > 2:
                handle_dead(86400, 'sauce')

            if m.get('reply'):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=m["reply"]))

            if is_sleep['sauce'] or is_dead['sauce']:
                line_bot_api.reply_message(
                    event.reply_token,
                    [ImageSendMessage(original_content_url=base_url + versioning_dic.get(str(iid)) + '/' + iid,
                                      preview_image_url=base_url + versioning_dic.get(str(iid)) + '/' + iid),
                     TextSendMessage(text=m['status'])])

        if m["source"] == 'hbot':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=m["reply"]))


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
