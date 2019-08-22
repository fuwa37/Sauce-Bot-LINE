import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from typing import *
import enum
import json
import os
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


class Status(enum.Enum):
    active = "active"
    waiting = "waiting"
    done = "done"


class Loc:
    def __init__(self, lat: float, lng: float):
        self.lat = lat
        self.lng = lng

    def todict(self):
        return {"lat": self.lat, "lng": self.lng}


class User:
    def __init__(self, user_id, status: Status):
        self.id = user_id
        self.status = status

    def todict(self):
        return {"id": self.id, "status": self.status.value}


class Kucing:
    def __init__(self, foto: List[str], loc: Loc):
        self.foto = foto
        self.loc = loc

    def todict(self):
        return {"foto": self.foto, "loc": self.loc.todict()}


class DataUser:
    def __init__(self, user: User, kucing: Kucing):
        self.user = user
        self.kucing = kucing

    def toDict(self):
        return {"user": self.user.todict(), "kucing": self.kucing.todict()}


try:
    config = json.loads(os.environ.get('firebase-admin', None))
    cred = credentials.Certificate(config)
except Exception as e:
    cred = credentials.Certificate("secret.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://portal-itb.firebaseio.com/'
})

data = DataUser(user=User(123, Status.done), kucing=Kucing(["12312", "123123"], Loc(123, 123)))

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


print(line_bot_api.get_group_member_profile('C38b8b57e92a7403fd6fb5cfd6395ce1e', 'U2e91a820fc12fa78c55ded8731cd3698'))
print(line_bot_api.get_profile('U42c8c14bf9f5bc869934ce753c7aef5f'))
