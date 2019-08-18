import os
import json
import base64
from handlers.handler import *
from flask import request, abort, Blueprint, current_app
import cloudinary.uploader
import cloudinary.api
import moviepy.editor as mpe
from PIL import Image
from io import BytesIO

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, VideoSendMessage, FollowEvent,
    JoinEvent, VideoMessage
)

config = json.loads(os.environ.get('cloudinary_config', None))

cloudinary.config(
    cloud_name=config['name'],
    api_key=config['key'],
    api_secret=config['secret']
)

line = Blueprint('line', __name__)

config = json.loads(os.environ.get('line_config', None))

line_bot_api = LineBotApi(config['token'], timeout=15)
handler = WebhookHandler(config['secret'])

sn_counter = 0


@line.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    current_app.logger.info("Request body: " + body)

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
        if event.message.text == '!kikku':
            line_bot_api.leave_group(str(iid))
            return
    if stype == 'room':
        iid = event.source.room_id
        if event.message.text == '!kikku':
            line_bot_api.leave_group(str(iid))
            return

    if event.message.text == '!help':
        reply = help_sauce + '\n\n' + help_robo
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
        if m.get('status'):
            reply = [ImageSendMessage(original_content_url=base_url + versioning_dic.get(str(iid)) + '/' + iid,
                                      preview_image_url=base_url + versioning_dic.get(str(iid)) + '/' + iid),
                     TextSendMessage(text=m['status'])]
        else:
            try:
                if m["source"] == 'trace':
                    if m['info']['quota'] < 1:
                        handle_death(m["quota_ttl"], 'trace')
                        reply = TextSendMessage(
                            text="(✖╭╮✖)\n!sauce Bot is dead\n\nPlease wait for resurrection in " + str(
                                death_time['trace']) + " seconds")

                    elif m['info']['limit'] < 1:
                        handle_sleep(m["limit_ttl"], 'trace')
                        reply = TextSendMessage(text="(-_-) zzz\n!sauce Bot is exhausted\n\nPlease wait for " + str(
                            sleep_time['trace']) + " seconds")
                    else:
                        reply = [VideoSendMessage(original_content_url=m["vid_url"],
                                                  preview_image_url=base_url + versioning_dic.get(str(iid)) + '/' + iid),
                                 TextSendMessage(text=m["reply"])]
                elif m['source'] == 'sauce':
                    if m == 429:
                        sn_counter += 1
                        handle_sleep(30, 'sauce')
                        reply = TextSendMessage(text="(-_-) zzz\n!sauce Bot is exhausted\n\nPlease wait for " + str(
                            sleep_time['sauce']) + " seconds")
                        if sn_counter > 2:
                            handle_death(86400, 'sauce')
                            reply = TextSendMessage(
                                text="(✖╭╮✖)\n!sauce Bot is dead\n\nPlease wait for resurrection in " + str(
                                    death_time['sauce']) + " seconds")
                    else:
                        reply = [
                            ImageSendMessage(original_content_url=base_url + versioning_dic.get(str(iid)) + '/' + iid,
                                             preview_image_url=base_url + versioning_dic.get(str(iid)) + '/' + iid),
                            TextSendMessage(text=m["reply"])]
                else:
                    reply = TextSendMessage(text=m["reply"])
            except Exception as e:
                print(e)
                reply = TextSendMessage(text="NO SAUCE")

        line_bot_api.reply_message(event.reply_token, reply)


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


@handler.add(MessageEvent, message=VideoMessage)
def handle_video(event):
    iid = ''
    stype = event.source.type
    if stype == 'user':
        iid = event.source.user_id
    if stype == 'group':
        iid = event.source.group_id
    if stype == 'room':
        iid = event.source.room_id
    message_content = line_bot_api.get_message_content(event.message.id)
    with open(iid, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    video = mpe.VideoFileClip(iid)
    frame = video.get_frame(5 * 1 / video.fps)

    pil_img = Image.fromarray(frame)
    buff = BytesIO()
    pil_img.save(buff, format="JPEG")
    b64file = base64.b64encode(buff.getvalue()).decode("utf-8")
    res = cloudinary.uploader.upload('data:image/jpg;base64,' + b64file, public_id=iid, tags="TEMP")
    versioning_dic.update({str(iid): str(res['version'])})
    os.remove(iid)


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

    line_bot_api.reply_message(
        event.reply_token,
        [ImageSendMessage(original_content_url="https://res.cloudinary.com/fuwa/image/upload/v1559414185/sauce.jpg",
                          preview_image_url="https://res.cloudinary.com/fuwa/image/upload/v1559414185/sauce.jpg"),
         TextSendMessage(text="[Sauce Bot]\n\nRead bot's TIMELINE\nor\nType '!help' for help")])

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

    line_bot_api.reply_message(
        event.reply_token,
        [ImageSendMessage(original_content_url="https://res.cloudinary.com/fuwa/image/upload/v1559414185/sauce.jpg",
                          preview_image_url="https://res.cloudinary.com/fuwa/image/upload/v1559414185/sauce.jpg"),
         TextSendMessage(text="[Sauce Bot]\n\nRead bot's TIMELINE\nor\nType '!help' for help")])

    sukebei_dic.update({str(iid): False})
