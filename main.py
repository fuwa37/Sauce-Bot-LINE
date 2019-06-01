import nHentaiTagBot.nHentaiTagBot as hBot
import os, json
from flask import Flask, request, abort
import cloudinary.uploader
import cloudinary.api
from hsauce.comment_builder import build_comment
from hsauce.get_source import get_source_data
import trace
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
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, VideoSendMessage, FollowEvent, JoinEvent
)

config = json.loads(os.environ.get('cloudinary_config', None))

cloudinary.config(
    cloud_name=config['name'],
    api_key=config['key'],
    api_secret=config['secret']
)

versioning_dic = {}
sukebei_dic = {}

is_sleep = {'trace': False,
            'sauce': False}
is_dead = {'trace': False,
           'sauce': False}

trace_commands = {'!sauce-anime',
                  '!sauce-anime-raw',
                  '!sauce-anime-ext',
                  '!sauce-anime-ext+',
                  '!sauce-anime-mini'}
hbot_commands = {'!(',
                 '!)',
                 '!}',
                 '!!', }

sleep_time = {'trace': 0,
              'sauce': 0}
death_time = {'trace': 0,
              'sauce': 0}

sn_counter = 0

help_reply = "1. Send image\n" \
             "2. Type command:\n" \
             "'- !sauce' - general sauce\n" \
             "'- !sauce-anime' - anime sauce\n" \
             "'- !sauce-anime-mini' - minimal info\n" \
             "'- !sauce-anime-ext' - extended info\n" \
             "'- !sauce-anime-ext+' - extended+ info"

help_sukebei = "Sukebei Commands:\n" \
               "- !(<numbers>) - nHentai\n" \
               "example: !(123456) or !(00001)\n\n" \
               "- !)<numbers>( - Tsumino\n" \
               "example: !)12345( or !)00002("

hel_sukebei_ext = "For nHentai galleries you need to put the gallery number in parentheses, " \
                  "while padding it with leading zeroes to have at least 5 digits. For example: (123456) or (00001)\n" \
                  "For Tsumino galleries you need to put the gallery number in inverted parentheses, " \
                  "while padding it with leading zeroes to have at least 5 digits. For example: )12345( or )00002("

base_url = "https://res.cloudinary.com/fuwa/image/upload/v"

app = Flask(__name__)
port = int(os.environ.get('PORT', 33507))

config = json.loads(os.environ.get('line_config', None))

line_bot_api = LineBotApi(config['token'])
handler = WebhookHandler(config['secret'])


def handle_command(text, iid):
    global sleep_time
    global is_sleep

    if text[:1] == '!':
        if '!sauce' in text:
            url = base_url + versioning_dic.get(str(iid)) + '/' + iid

            if text == "!sauce":
                if is_sleep["sauce"]:
                    return {
                        'status': "(-_-) zzz\n!sauce Bot is exhausted\n\nPlease wait for " + str(
                            sleep_time['sauce']) + " seconds"}
                if is_dead["sauce"]:
                    return {'status': "(✖╭╮✖)\n!sauce Bot is dead\n\nPlease wait for resurrection in " + str(
                        death_time['sauce']) + " seconds"}

                return build_comment(get_source_data(url))

            if '!sauce-anime' in text:
                if is_sleep["trace"]:
                    return {
                        'status': "(-_-) zzz\n!sauce-anime Bot is exhausted\n\nPlease wait for " + str(
                            sleep_time['trace']) + " seconds"}
                if is_dead["trace"]:
                    return {'status': "(✖╭╮✖)\n!sauce-anime Bot is dead\n\nPlease wait for resurrection in " + str(
                        death_time['trace']) + " seconds"}
                if text == "!sauce-anime":
                    return trace.reply(trace.res(url))
                if text == "!sauce-anime-ext":
                    return trace.reply(trace.res(url, 'ext'))
                if text == "!sauce-anime-ext+":
                    return trace.reply(trace.res(url, 'ext+'))
                if text == "!sauce-anime-mini":
                    return trace.reply(trace.res(url, 'mini'))
                if text == "!sauce-anime-raw":
                    return trace.reply(trace.res(url, 'raw'))

        if is_sukebei(str(iid)):
            # print(text[1:])
            m = hBot.processComment(text[1:])
            if m:
                return {'source': 'hbot',
                        'reply': m}
        else:
            return {'source': 'hbot',
                    'reply': "Please turn on Sukebei mode\n !sukebei-switch"}
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


def is_sukebei(iid):
    if str(iid) not in sukebei_dic:
        sukebei_dic.update({str(iid): False})

    return sukebei_dic[str(iid)]


def handle_sukebei(iid):
    return sukebei_dic.update({str(iid): not is_sukebei(iid)})


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

    if event.message.text == '!help':
        reply = help_reply
        if is_sukebei(str(iid)):
            reply += '\n\n' + help_sukebei
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    if event.message.text == '!sukebei-switch':
        handle_sukebei(str(iid))
        if is_sukebei(str(iid)):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Sukebei mode ON\n\n" + help_sukebei))
            return
        if not is_sukebei(str(iid)):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Sukebei mode OFF"))
            return

    m = handle_command(event.message.text, iid)

    if m is not None:
        if event.message.text in trace_commands:
            if is_sleep['trace'] or is_dead['trace']:
                line_bot_api.reply_message(
                    event.reply_token,
                    [ImageSendMessage(original_content_url=base_url + versioning_dic.get(str(iid)) + '/' + iid,
                                      preview_image_url=base_url + versioning_dic.get(str(iid)) + '/' + iid),
                     TextSendMessage(text=m['status'])])
                return

            if m.get('reply'):
                line_bot_api.reply_message(
                    event.reply_token,
                    [VideoSendMessage(original_content_url=m["url"],
                                      preview_image_url=base_url + versioning_dic.get(str(iid)) + '/' + iid),
                     TextSendMessage(text=m["comment"])])

            if m['quota'] < 1:
                handle_death(m["quota_ttl"], 'trace')
                return

            if m['limit'] < 1:
                handle_sleep(m["limit_ttl"], 'trace')
                return

        if event.message.text == '!sauce':
            if is_sleep['sauce'] or is_dead['sauce']:
                line_bot_api.reply_message(
                    event.reply_token,
                    [ImageSendMessage(original_content_url=base_url + versioning_dic.get(str(iid)) + '/' + iid,
                                      preview_image_url=base_url + versioning_dic.get(str(iid)) + '/' + iid),
                     TextSendMessage(text=m['status'])])
                return
            if m == 429:
                sn_counter += 1
                if sn_counter > 2:
                    handle_death(86400, 'sauce')
                    return
                handle_sleep(30, 'sauce')
                return

            if m.get('reply'):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=m["reply"]))
                return

        if event.message.text[:2] in hbot_commands:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=m["reply"]))
            return


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


@handler.add(FollowEvent)
def handle_follow(event):
    iid = ''
    stype = event.source.type
    if stype == 'user':
        iid = event.source.user_id
    if stype == 'group':
        iid = event.source.group_id
    if stype == 'room':
        iid = event.source.room_id

    sukebei_dic.update({str(iid): False})


@handler.add(JoinEvent)
def handle_join(event):
    iid = ''
    stype = event.source.type
    if stype == 'user':
        iid = event.source.user_id
    if stype == 'group':
        iid = event.source.group_id
    if stype == 'room':
        iid = event.source.room_id

    sukebei_dic.update({str(iid): False})


app.run(host='0.0.0.0', port=port)
