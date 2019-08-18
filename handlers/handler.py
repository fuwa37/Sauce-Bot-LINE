import time
import threading
import handlers.nHentaiTagBot.nHentaiTagBot as hBot
import handlers.Roboragi.AnimeBot as aBot
from handlers.strings import *
from handlers.sauce.comment_builder import build_comment
from handlers.sauce.get_source import get_source_data

versioning_dic = {}
sukebei_dic = {}

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
        print(text[:2])
        if text in sauce_commands:
            print("sauce")
            url = base_url + versioning_dic.get(str(iid)) + '/' + iid

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
            print("robo")
            return aBot.process_comment(text[2:-1], is_expanded=True)  # else return empty dic

        if text[:2] in sukebei_commands:
            print("h")
            if is_sukebei(str(iid)):
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
    if str(iid) not in sukebei_dic:
        sukebei_dic.update({str(iid): False})

    return sukebei_dic[str(iid)]


def handle_sukebei(iid):
    return sukebei_dic.update({str(iid): not is_sukebei(iid)})
