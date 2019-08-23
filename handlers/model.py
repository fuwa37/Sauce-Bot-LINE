from typing import *
from enum import Enum


class Mode(Enum):
    sukebei = True
    none = False


class User:
    def __init__(self, user_id, name, last_img="", glast_img="", mode: Mode = Mode.none):
        self.id = user_id
        self.name = name
        self.last_img = last_img
        self.glast_img = glast_img
        self.mode = mode

    def to_dict(self):
        return {"name": self.name, "last_img": self.last_img, "glast_img": self.last_img, "mode": self.mode.value}


class Group:
    def __init__(self, group_id, users: List[str], last_img="", mode: Mode = Mode.none):
        self.id = group_id
        self.users = users
        self.last_img = last_img
        self.mode = mode

    def user_list(self):
        temp = {}
        for i in self.users:
            temp.update({i: True})
        return temp

    def to_dict(self):
        return {"users": self.user_list(), "last_img": self.last_img, "mode": self.mode.value}
