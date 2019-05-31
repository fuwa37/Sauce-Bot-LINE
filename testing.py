import sauce
import threading
import nHentaiTagBot.nHentaiTagBot as hBot
from hsauce.comment_builder import build_comment
from hsauce.get_source import get_source_data
import time

is_sleep = False
sleep_time = 20


def handle_command(text):
    m = hBot.processComment(text)
    if m:
        return ('hbot', m)
    url = 'https://i.ytimg.com/vi/pbhf0OOjc3s/maxresdefault.jpg'
    if text == "!sauce":
        return build_comment(get_source_data(url))
    if text == "!sauce-anime":
        return sauce.res(url)
    if text == "!sauce-anime-mini":
        return sauce.res(url, "mini")
    if text == "!sauce-anime-raw":
        return sauce.res(url, 'raw')

    m = handle_command('!sauce-anime')

    if m == 'sleep':
        is_sleep = True

    if m[1]:
        if m[0] == 'trace':
            print(m[1])
        if m[0] == 'saucenao':
            print(m[1])
        if m[0] == 'hbot':
            print(m[1])


def handle_sleep(t):
    global is_sleep
    is_sleep = True
    time_t = threading.Thread(target=handle_sleeping, args=(t,))
    time_t.start()


def handle_sleeping(t):
    global sleep_time
    global is_sleep
    temp = t
    for i in range(t, 0, -1):
        time.sleep(1)
        sleep_time -= 1
    sleep_time = temp
    is_sleep = False


handle_sleep(5)
