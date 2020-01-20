from enum import Enum
from typing import List


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
        return {"user_id": self.id, "name": self.name, "last_img": self.last_img, "glast_img": self.last_img,
                "mode": self.mode.value}


class Group:
    def __init__(self, group_id, last_img="", mode: Mode = Mode.none):
        self.id = group_id
        self.last_img = last_img
        self.mode = mode

    def to_dict(self):
        return {"group_id": self.id, "users": [], "last_img": self.last_img, "mode": self.mode.value}


class Hentai:
    def __init__(self, number, info, token, last_update):
        self.number = number
        self.info = info
        self.token = token
        self.last_update = last_update

    def to_dict(self):
        return {'number': self.number, 'info': self.info, 'token': self.token, 'last_update': self.last_update}


class Ani:
    def __init__(self, synonyms: List[str], info, last_update):
        self.synonyms = synonyms
        self.info = info
        self.last_update = last_update

    def to_dict(self):
        return {'synonyms': self.synonyms, 'info': self.info, 'last_update': self.last_update}
