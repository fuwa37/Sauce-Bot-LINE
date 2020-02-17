from tinydb import TinyDB, Query
import handlers.model as model
from datetime import datetime
from string import capwords

line_db = TinyDB('db/line_db.db')
user_ref = line_db.table('users')
group_ref = line_db.table('groups')

hentai_db = TinyDB('db/hentai.db')

ani_db = TinyDB('db/ani.db')

Search = Query()


class LineProfile:
    @staticmethod
    def set_user(user_id, group_id=None):
        from handlers.lineHandler import get_profile
        temp = get_profile(user_id, group_id)
        user = model.User(user_id=temp.user_id, name=temp.display_name)
        user_ref.insert(user.to_dict())

    @staticmethod
    def set_user_name(user_id, group_id=None):
        from handlers.lineHandler import get_profile
        temp = get_profile(user_id, group_id)
        user_ref.update({'name': temp.display_name}, Search.user_id == temp.user_id)

    @staticmethod
    def set_group(group_id, user_id=None):
        if user_id is not None and not user_ref.contains(Search.user_id == user_id):
            LineProfile.set_user(user_id, group_id)
        group = model.Group(group_id=group_id)
        group_ref.insert(group.to_dict())

    @staticmethod
    def set_group_user(group_id, user_id):
        temp = LineProfile.get_group_users(group_id)
        if user_id in temp:
            return
        else:
            temp.append(user_id)
            group_ref.update({'users': temp}, Search.group_id == group_id)

    @staticmethod
    def set_user_mode(user_id, mode: model.Mode):
        if not LineProfile.get_user(user_id):
            LineProfile.set_user(user_id)
        user_ref.update({'mode': mode.value}, Search.user_id == user_id)

    @staticmethod
    def set_group_mode(group_id, mode: model.Mode):
        if not LineProfile.get_group(group_id):
            LineProfile.set_group(group_id)
        group_ref.update({'mode': mode.value}, Search.group_id == group_id)

    @staticmethod
    def set_user_last_img(user_id, img):
        if not LineProfile.get_user(user_id):
            LineProfile.set_user(user_id)
        user_ref.update({'last_img': img}, Search.user_id == user_id)

    @staticmethod
    def set_user_glast_img(user_id, group_id, img):
        if not LineProfile.get_user(user_id):
            LineProfile.set_user(user_id, group_id)
        user_ref.update({'glast_img': img}, Search.user_id == user_id)

    @staticmethod
    def set_group_last_img(user_id, group_id, img):
        LineProfile.set_user_glast_img(user_id, group_id, img)
        if not LineProfile.get_group(group_id):
            LineProfile.set_group(group_id, user_id)
        group_ref.update({'last_img': img}, Search.group_id == group_id)

    @staticmethod
    def get_user(user_id):
        return user_ref.get(Search.user_id == user_id)

    @staticmethod
    def get_user_by_name(name):
        return user_ref.get(Search.name == name)

    @staticmethod
    def get_group(group_id):
        return group_ref.get(Search.group_id == group_id)

    @staticmethod
    def get_user_mode(user_id):
        temp = LineProfile.get_user(user_id)
        return temp['mode'] if temp else False

    @staticmethod
    def get_group_mode(group_id):
        temp = LineProfile.get_group(group_id)
        return temp['mode'] if temp else False

    @staticmethod
    def get_user_last_img(user_id):
        temp = LineProfile.get_user(user_id)
        return temp['last_img'] if temp else None

    @staticmethod
    def get_user_glast_img(name):
        temp = LineProfile.get_user_by_name(name)
        return temp['glast_img'] if temp else None

    @staticmethod
    def get_group_last_img(group_id):
        temp = LineProfile.get_group(group_id)
        return temp['last_img'] if temp else None

    @staticmethod
    def get_group_users(group_id):
        temp = LineProfile.get_group(group_id)
        return temp['users'] if temp else []


class HentaiCache:
    def __init__(self, table: str):
        self.table = table

    @staticmethod
    def date_to_string(date):
        return date.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def string_to_date(date):
        return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    def set(self, number, info, token=None):
        temp = model.Hentai(number, info, token, HentaiCache.date_to_string(datetime.now()))
        hentai_db.table(self.table).upsert(temp.to_dict(), Search.number == number)

    def get(self, number, token=None):
        if token is not None:
            return hentai_db.table(self.table).get(Search.number == number and Search.token == token)
        return hentai_db.table(self.table).get(Search.number == number)


class AniDB:
    def __init__(self, table: str):
        self.table = table

    @staticmethod
    def date_to_string(date):
        return date.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def string_to_date(date):
        return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    def append_synonyms(self, first_list, second_list):
        in_first = set(first_list)
        in_second = set(second_list)

        in_second_but_not_in_first = in_second - in_first

        result = first_list + list(in_second_but_not_in_first)

        return result

    def set(self, synonyms, info):
        temp = model.Ani(synonyms, info, AniDB.date_to_string(datetime.now()))
        entry = self.get(info['title'])
        if entry:
            try:
                temp = self.append_synonyms(entry['synonyms'], synonyms)
            except Exception as e:
                temp = entry['synonyms']
                temp.extend(synonyms)
            ani_db.table(self.table).update({'synonyms': temp}, Search.info.title == info['title'])
        else:
            ani_db.table(self.table).insert(temp.to_dict())

    def get(self, synonym):
        return ani_db.table(self.table).get(
            (Search.info.title == capwords(synonym)) | (Search.synonyms.any(synonym.lower())))
