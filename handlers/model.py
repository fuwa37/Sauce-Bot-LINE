from typing import *
from enum import Enum


class Mode(Enum):
    kucing = "kucing"
    sauce = "sauce"
    none = None


class Loc:
    def __init__(self, lat: float, lng: float):
        self.lat = lat
        self.lng = lng

    def todict(self):
        return {"lat": self.lat, "lng": self.lng}


class User:
    def __init__(self, user_id, last_img="", glast_img="", mode: Mode = Mode.none):
        self.id = user_id
        self.last_img = last_img
        self.glast_img = glast_img
        self.mode = mode

    def todict(self):
        return {"last_img": self.last_img, "glast_img": self.last_img, "mode": self.mode.value}


class Group:
    def __init__(self, group_id, user: List[str], last_img="", mode: Mode = Mode.none):
        self.id = group_id
        self.user = user
        self.last_img = last_img
        self.mode = mode

    def userlist(self):
        temp = {}
        for i in self.user:
            temp.update({i: True})
        return temp

    def todict(self):
        return {"user": self.userlist(), "last_img": self.last_img, "mode": self.mode.value}


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
