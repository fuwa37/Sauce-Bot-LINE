import time
import threading
import handlers.nHentaiTagBot.nHentaiTagBot as hBot
import handlers.Roboragi.AnimeBot as aBot
from handlers.strings import *
from handlers.sauce.comment_builder import build_comment
from handlers.sauce.get_source import get_source_data
from handlers.firebase import *

is_sleep = {'trace': False,
            'sauce': False}
is_dead = {'trace': False,
           'sauce': False}

sleep_time = {'trace': 0,
              'sauce': 0}
death_time = {'trace': 0,
              'sauce': 0}


def handle_command(text, iid):
    global sleep_time
    global is_sleep

    if text[:1] == '!':
        try:
            if iid["type"] == "group" or iid["type"] == "room":
                temp_text = text.split('@')
                url = get_user_glast_img(name=temp_text[1]) or get_group_last_img(iid["gid"])
            else:
                url = get_user_last_img(iid["uid"])
        except Exception as err:
            print(err)
            return {'reply': "NO SAUCE"}

        if text in sauce_commands:
            if is_sleep["sauce"] or is_sleep["trace"]:
                return {
                    'status': "(-_-) zzz\n!sauce Bot is exhausted\n\nPlease wait for " + str(
                        sleep_time['sauce']) + " seconds"}
            if is_dead["sauce"] or is_dead["trace"]:
                return {'status': "(✖╭╮✖)\n!sauce Bot is dead\n\nPlease wait for resurrection in " + str(
                    death_time['sauce']) + " seconds"}
            if text[-1] == '+':
                return build_comment(get_source_data(url, trace=True))
            else:
                return build_comment(get_source_data(url))  # else return empty dict

        if text[:2] in robo_commands:
            return aBot.process_comment(text[1:], is_expanded=True)  # else return empty dic

        if text[:2] in sukebei_commands:
            if is_sukebei(iid):
                m = hBot.processComment(text[1:])  # return string
                return {'source': 'hbot',
                        'reply': m}
            else:
                return {'source': 'hbot',
                        'reply': "Please turn on Sukebei mode\n !sukebei-switch"}


def handle_sleep(t, source):
    sleep_t = threading.Thread(target=handle_sleeping, args=(t, source))
    sleep_t.start()


def handle_sleeping(t, source):
    global sleep_time
    global is_sleep
    is_sleep[source] = True
    sleep_time[source] = t
    for i in range(t, 0, -1):
        time.sleep(1)
        sleep_time[source] -= 1
    sleep_time[source] = t
    is_sleep[source] = False


def handle_death(t, source):
    dead_t = threading.Thread(target=handle_dead, args=(t, source))
    dead_t.start()


def handle_dead(t, source):
    global death_time
    global is_dead
    global sn_counter

    is_dead[source] = True
    death_time[source] = t
    for i in range(t, 0, -1):
        time.sleep(1)
        death_time[source] -= 1
    death_time[source] = t
    if source == 'sauce':
        sn_counter = 0
    is_dead[source] = False


def is_sukebei(iid):
    if iid["type"] == "group" or iid["type"] == "room":
        return get_group_mode(iid["gid"])
    else:
        get_user_mode(iid["uid"])


def sukebei_on(iid):
    if iid["type"] == "group" or iid["type"] == "room":
        set_group_mode(iid["gid"], Mode.sukebei)
    else:
        set_user_mode(iid["uid"], Mode.sukebei)


def sukebei_off(iid):
    if iid["type"] == "group" or iid["type"] == "room":
        set_group_mode(iid["gid"], Mode.none)
    else:
        set_user_mode(iid["uid"], Mode.none)
