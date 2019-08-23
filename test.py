import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from typing import *
import enum
import json
import os
import io
from handlers.model import *
from handlers.firebase import *

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, VideoSendMessage, FollowEvent,
    LocationMessage, JoinEvent, VideoMessage, RichMenu, RichMenuArea, RichMenuBounds, RichMenuResponse, RichMenuSize,
    URIAction, MessageAction, CameraAction, CameraRollAction, LocationAction, DatetimePickerAction
)

# data = DataUser(user=User(123, Status.done), kucing=Kucing(["12312", "123123"], Loc(123, 123)))

ref = db.reference('dataUser')
# ref.child(str(data.user.id) + '/kucing/foto').child("asdasd").set(True)

config = json.loads(os.environ.get('line_config', None))

line_bot_api = LineBotApi(config['token'], timeout=15)
handler = WebhookHandler(config['secret'])


def create_mode():
    rich_menu_to_create = RichMenu(
        size=RichMenuSize(width=2500, height=843),
        selected=True,
        name="Mode",
        chat_bar_text="Mode",
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=0, width=1250, height=843),
                action=MessageAction(label="Sauce", text="!sauce-mode")),
            RichMenuArea(
                bounds=RichMenuBounds(x=1250, y=0, width=1250, height=843),
                action=MessageAction(label="Kucing", text="!kucing-mode")),
        ]
    )
    rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

    with open("assets/mode.png", 'rb') as f:
        line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', f)
    line_bot_api.set_default_rich_menu(rich_menu_id)


set_user("U42c8c14bf9f5bc869934ce753c7aef5f")
