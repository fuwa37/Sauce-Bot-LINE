import time
import threading
import handlers.trace as trace
import handlers.nHentaiTagBot.nHentaiTagBot as hBot
from handlers.strings import *
from handlers.hsauce.comment_builder import build_comment
from handlers.hsauce.get_source import get_source_data

versioning_dic = {}
sukebei_dic = {}

is_sleep = {'trace': False,
            'sauce': False}
is_dead = {'trace': False,
           'sauce': False}

trace_commands = {'!sauce-anime',
                  '!sauce-anime-raw',
                  '!sauce-anime-ext',
                  '!sauce-anime-ext+',
                  '!sauce-anime-mini'}
hbot_commands = {'!(',
                 '!)',
                 '!}',
                 '!!', }

sleep_time = {'trace': 0,
              'sauce': 0}
death_time = {'trace': 0,
              'sauce': 0}


def handle_command(text, iid):
    global sleep_time
    global is_sleep

    if text[:1] == '!':
        if '!sauce' in text:
            url = base_url + versioning_dic.get(str(iid)) + '/' + iid

            if text == "!sauce":
                if is_sleep["sauce"]:
                    return {
                        'status': "(-_-) zzz\n!sauce Bot is exhausted\n\nPlease wait for " + str(
                            sleep_time['sauce']) + " seconds"}
                if is_dead["sauce"]:
                    return {'status': "(✖╭╮✖)\n!sauce Bot is dead\n\nPlease wait for resurrection in " + str(
                        death_time['sauce']) + " seconds"}

                return build_comment(get_source_data(url))

            if '!sauce-anime' in text:
                if is_sleep["trace"]:
                    return {
                        'status': "(-_-) zzz\n!sauce-anime Bot is exhausted\n\nPlease wait for " + str(
                            sleep_time['trace']) + " seconds"}
                if is_dead["trace"]:
                    return {'status': "(✖╭╮✖)\n!sauce-anime Bot is dead\n\nPlease wait for resurrection in " + str(
                        death_time['trace']) + " seconds"}
                if text == "!sauce-anime":
                    return trace.reply(trace.res(url))
                if text == "!sauce-anime-ext":
                    return trace.reply(trace.res(url, 'ext'))
                if text == "!sauce-anime-ext+":
                    return trace.reply(trace.res(url, 'ext+'))
                if text == "!sauce-anime-mini":
                    return trace.reply(trace.res(url, 'mini'))
                if text == "!sauce-anime-raw":
                    return trace.reply(trace.res(url, 'raw'))

        if is_sukebei(str(iid)):
            # print(text[1:])
            m = hBot.processComment(text[1:])
            if m:
                return {'source': 'hbot',
                        'reply': m}
        else:
            return {'source': 'hbot',
                    'reply': "Please turn on Sukebei mode\n !sukebei-switch"}
    else:
        return None


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
