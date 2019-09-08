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
    VideoMessage, JoinEvent, QuickReply, QuickReplyButton, MessageAction
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

quick_reply_sauce = QuickReply(
    items=[
        QuickReplyButton(action=MessageAction(label="!sauce")),
        QuickReplyButton(action=MessageAction(label="!sauce+"))]
)


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


def get_profile(id):
    return line_bot_api.get_profile(id)


def lid(event):
    stype = event.source.type
    iid = ''
    if stype == 'user':
        iid = {"uid": event.source.user_id, "type": "user"}
    if stype == 'group':
        iid = {"uid": event.source.user_id, "type": "group", "gid": event.source.group_id}
    if stype == 'room':
        iid = {"uid": event.source.user_id, "type": "room", "gid": event.source.room_id}

    return iid


def handle_user_message(iid, event):
    if event.message.text == '!help':
        reply = help_sauce + '\n\n' + help_robo
        if is_sukebei(iid):
            reply += '\n\n' + help_sukebei
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    if event.message.text == '!sukebei-switch':
        if not is_sukebei(iid):
            sukebei_on(iid)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Sukebei mode ON\n\n" + help_sukebei))
            return
        else:
            sukebei_off(iid)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Sukebei mode OFF"))
            return

    m = handle_command(event.message.text, iid)

    return m


def handle_group_message(iid, event):
    if event.message.text == '!help':
        reply = help_sauce + '\n\n' + help_robo
        if is_sukebei(iid):
            reply += '\n\n' + help_sukebei
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    if event.message.text == '!sukebei-switch':
        if not is_sukebei(iid):
            sukebei_on(iid)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Sukebei mode ON\n\n" + help_sukebei))
            return
        else:
            sukebei_off(iid)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Sukebei mode OFF"))
            return

    if event.message.text == '!kikku':
        line_bot_api.leave_group(iid["gid"])
        return
    m = handle_command(event.message.text, iid)

    return m


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global sn_counter
    iid = lid(event)

    if event.message.text == '!sauce-mode':
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text="Sauce Mode On", quick_reply=quick_reply_sauce))
        return

    if iid["type"] == "group" or iid["type"] == "room":
        m = handle_group_message(iid, event)
    else:
        m = handle_user_message(iid, event)

    if type(m) is dict:
        if "status" in m:
            reply = TextSendMessage(text=m['status'])
        else:
            try:
                if m["source"] == 'trace':
                    if m['info']['quota'] < 1:
                        handle_death(m["quota_ttl"], 'trace')

                    elif m['info']['limit'] < 1:
                        handle_sleep(m["limit_ttl"], 'trace')

                    reply = [VideoSendMessage(original_content_url=m["vid_url"],
                                              preview_image_url=m["image_url"]),
                             TextSendMessage(text=m["reply"])]
                elif m.get("code"):
                    sn_counter += 1
                    handle_sleep(30, 'sauce')
                    reply = TextSendMessage(text="(-_-) zzz\n!sauce Bot is exhausted\n\nPlease wait for " + str(
                        sleep_time['sauce']) + " seconds")
                    if sn_counter > 2:
                        handle_death(86400, 'sauce')
                        reply = TextSendMessage(
                            text="(✖╭╮✖)\n!sauce Bot is dead\n\nPlease wait for resurrection in " + str(
                                death_time['sauce']) + " seconds")

                elif m['source'] == 'sauce':
                    reply = [
                        ImageSendMessage(original_content_url=m["image_url"],
                                         preview_image_url=m["image_url"]),
                        TextSendMessage(text=m["reply"])]
                else:
                    reply = TextSendMessage(text=m["reply"])
            except Exception as err:
                print(err)
                reply = TextSendMessage(text="NO SAUCE")

        line_bot_api.reply_message(event.reply_token, reply)


def handle_group_image(iid, event):
    r = b''
    message_content = line_bot_api.get_message_content(event.message.id)
    for chunk in message_content.iter_content():
        r += chunk
    img = base64.b64encode(r).decode('utf-8')
    res = cloudinary.uploader.upload('data:image/jpg;base64,' + img, public_id=iid["gid"] + "_" + iid["uid"],
                                     tags="TEMP")
    set_group_user(iid["gid"], iid["uid"])
    set_user_glast_img(iid["uid"], res["url"])
    set_group_last_img(iid["gid"], res["url"])


def handle_user_image(iid, event):
    r = b''
    message_content = line_bot_api.get_message_content(event.message.id)
    for chunk in message_content.iter_content():
        r += chunk
    img = base64.b64encode(r).decode('utf-8')
    res = cloudinary.uploader.upload('data:image/jpg;base64,' + img, public_id=iid["uid"],
                                     tags="TEMP")
    set_user_last_img(iid["uid"], res["url"])


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    iid = lid(event)
    if iid["type"] == "group" or iid["type"] == "room":
        handle_group_image(iid, event)
    else:
        handle_user_image(iid, event)


def handle_group_video(iid, event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with open(iid, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    video = mpe.VideoFileClip(iid)
    frame = video.get_frame(5 * 1 / video.fps)

    pil_img = Image.fromarray(frame)
    buff = BytesIO()
    pil_img.save(buff, format="JPEG")
    img = base64.b64encode(buff.getvalue()).decode("utf-8")
    os.remove(iid)
    res = cloudinary.uploader.upload('data:image/jpg;base64,' + img, public_id=iid["gid"] + "_" + iid["uid"],
                                     tags="TEMP")
    set_group_user(iid["gid"], iid["uid"])
    set_user_glast_img(iid["uid"], res["url"])
    set_group_last_img(iid["gid"], res["url"])


def handle_user_video(iid, event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with open(iid, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    video = mpe.VideoFileClip(iid)
    frame = video.get_frame(5 * 1 / video.fps)

    pil_img = Image.fromarray(frame)
    buff = BytesIO()
    pil_img.save(buff, format="JPEG")
    img = base64.b64encode(buff.getvalue()).decode("utf-8")
    os.remove(iid)
    res = cloudinary.uploader.upload('data:image/jpg;base64,' + img, public_id=iid["uid"],
                                     tags="TEMP")
    set_user_last_img(iid["uid"], res["url"])


@handler.add(MessageEvent, message=VideoMessage)
def handle_video(event):
    iid = lid(event)
    if iid["type"] == "group" or iid["type"] == "room":
        handle_group_video(iid, event)
    else:
        handle_user_video(iid, event)


@handler.add(FollowEvent)
def handle_follow(event):
    iid = lid(event)

    line_bot_api.reply_message(
        event.reply_token,
        [ImageSendMessage(original_content_url="https://res.cloudinary.com/fuwa/image/upload/v1559414185/sauce.jpg",
                          preview_image_url="https://res.cloudinary.com/fuwa/image/upload/v1559414185/sauce.jpg"),
         TextSendMessage(text="[Sauce Bot]\n\nRead bot's TIMELINE\nor\nType '!help' for help")])

    set_user(iid["uid"])


@handler.add(JoinEvent)
def handle_join(event):
    iid = lid(event)

    line_bot_api.reply_message(
        event.reply_token,
        [ImageSendMessage(original_content_url="https://res.cloudinary.com/fuwa/image/upload/v1559414185/sauce.jpg",
                          preview_image_url="https://res.cloudinary.com/fuwa/image/upload/v1559414185/sauce.jpg"),
         TextSendMessage(text="[Sauce Bot]\n\nRead bot's TIMELINE\nor\nType '!help' for help")])

    set_group_user(iid["gid"], iid["uid"])
