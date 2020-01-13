import base64
from handlers.handler import *
from flask import request, abort, Blueprint, current_app
import cloudinary.uploader
import cloudinary.api
import cv2

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
    source_type = event.source.type
    if source_type == 'user':
        return {"uid": event.source.user_id, "type": "user"}
    if source_type == 'group':
        return {"uid": event.source.user_id, "type": "group", "gid": event.source.group_id}
    if source_type == 'room':
        return {"uid": event.source.user_id, "type": "room", "gid": event.source.room_id}


def proc_message(iid, event):
    if event.message.text == '!help':
        reply = help_sauce + '\n\n' + help_robo
        if is_sukebei(iid):
            reply += '\n\n' + help_sukebei
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    elif event.message.text == '!sukebei-switch':
        if not is_sukebei(iid):
            sukebei_on(iid)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Sukebei mode ON\n\n" + help_sukebei))
            return
        else:
            sukebei_off(iid)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Sukebei mode OFF"))
            return

    elif iid["type"] == "group" or iid["type"] == "room":
        if event.message.text == '!kikku':
            line_bot_api.leave_group(iid["gid"])
            return

    else:
        return handle_command(event.message.text, iid)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    iid = lid(event)

    m = proc_message(iid, event)

    if m is not None:
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
                    sn_inc()
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


def image_uploader_group(iid, img):
    res = cloudinary.uploader.upload('data:image/jpg;base64,' + img, public_id=iid["gid"] + "_" + iid["uid"],
                                     tags="TEMP")
    set_group_user(iid["gid"], iid["uid"])
    set_group_last_img(iid["uid"], iid["gid"], res["url"])


def image_uploader_user(iid, img):
    res = cloudinary.uploader.upload('data:image/jpg;base64,' + img, public_id=iid["uid"],
                                     tags="TEMP")
    set_user_img(iid["uid"], last_img=res["url"])


def proc_image(event):
    r = b''
    message_content = line_bot_api.get_message_content(event.message.id)
    for chunk in message_content.iter_content():
        r += chunk
    img = base64.b64encode(r).decode('utf-8')

    return img


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    iid = lid(event)
    if iid["type"] == "group" or iid["type"] == "room":
        image_uploader_group(iid, proc_image(event))
    else:
        image_uploader_user(iid, proc_image(event))


def proc_video(iid, event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with open(iid["uid"], 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    cap = cv2.VideoCapture(iid["uid"])
    success, frame = cap.read()
    success, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
    image = base64.b64encode(buffer)
    os.remove(iid["uid"])

    return image.decode('utf-8')


@handler.add(MessageEvent, message=VideoMessage)
def handle_video(event):
    iid = lid(event)
    if iid["type"] == "group" or iid["type"] == "room":
        image_uploader_group(iid, proc_video(iid, event))
    else:
        image_uploader_user(iid, proc_video(iid, event))


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

    set_group_user(iid["gid"])
