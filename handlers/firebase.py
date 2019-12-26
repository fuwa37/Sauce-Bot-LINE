import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from handlers.model import *
import json
import os

try:
    config = json.loads(os.environ.get('firebase_admin', None))
except Exception as e:
    print(e)
    config = "firebase_admin.json"
cred = credentials.Certificate(config)

firebase_url = os.environ.get('firebase_url', None)
if firebase_url is None:
    firebase_url = open("firebase_url.txt", "r").read()

firebase_admin.initialize_app(cred, {
    'databaseURL': firebase_url
})

user_ref = db.reference('users')
group_ref = db.reference('groups')


def set_group_mode(group_id, mode: Mode):
    group_ref.child(group_id).child("mode").set(mode.value)


def get_group_mode(group_id):
    return group_ref.child(group_id).child("mode").get()


def set_group_user(group_id, user_id=None):
    if user_id is None:
        return
    if user_ref.child(user_id).get() is None:
        set_user(user_id)
    if user_ref.child(user_id).child("name").get() is None:
        from handlers.lineHandler import get_profile
        temp = get_profile(user_id)
        user_ref.child(user_id).child("name").set(temp.display_name)
    group_ref.child(group_id).child("user").child(user_id).set(True)


def set_group_last_img(group_id, last_img):
    group_ref.child(group_id).child("last_img").set(last_img)


def get_group_last_img(group_id):
    return group_ref.child(group_id).child("last_img").get()


def set_user(id):
    from handlers.lineHandler import get_profile
    temp = get_profile(id)
    user = User(user_id=temp.user_id, name=temp.display_name)
    user_ref.child(id).set(user.to_dict())


def get_user_by_id(user_id):
    return user_ref.child(user_id).get()


def get_user_by_name(name):
    temp = user_ref.order_by_child("name").equal_to(name).get().items()

    if temp:
        return list(temp)[0][1]


def get_user_glast_img(user_id=None, name=None):
    temp = {}
    if user_id:
        temp = get_user_by_id(user_id)
    elif name:
        temp = get_user_by_name(name)

    if temp:
        return temp["glast_img"]


def set_user_mode(user_id, mode: Mode):
    user_ref.child(user_id).child("mode").set(mode.value)


def get_user_mode(user_id):
    return user_ref.child(user_id).child("mode").get()


def get_user_last_img(user_id):
    return user_ref.child(user_id).child("last_img").get()


def set_user_last_img(user_id, last_img):
    user_ref.child(user_id).child("last_img").set(last_img)


def set_user_glast_img(user_id, glast_img):
    user_ref.child(user_id).child("glast_img").set(glast_img)
