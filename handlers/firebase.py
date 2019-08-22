import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from handlers.model import *
import json
import os

try:
    config = json.loads(os.environ.get('firebase_admin', None))
    cred = credentials.Certificate(config)
except Exception as e:
    print(e)
    cred = credentials.Certificate("secret.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ.get('firebase_url', None)
})

user_ref = db.reference('user')
group_ref = db.reference('group')


def set_group(group: Group):
    group_ref.child(group.id).set(group.todict())


def set_group_mode(group_id, mode: Mode):
    group_ref.child(group_id).child("mode").set(mode.value)


def set_group_user(group_id, user_id):
    group_ref.child(group_id).child("user").child(user_id).set(True)


def set_group_last_img(group_id, last_img):
    group_ref.child(group_id).child("last_img").set(last_img)


def set_user(user: User):
    user_ref.child(user.id).set(user.todict())


def set_user_mode(user_id, mode: Mode):
    user_ref.child(user_id).child("mode").set(mode.value)


def set_user_last_img(user_id, last_img):
    user_ref.child(user_id).child("last_img").set(last_img)


print(group_ref.child("124").get())
