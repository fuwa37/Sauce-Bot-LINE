import sauce
import threading
import nHentaiTagBot.nHentaiTagBot as hBot
from hsauce.comment_builder import build_comment
from hsauce.get_source import get_source_data
import time

is_sleep = True
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


if not is_sleep:
    print('b')
else:
    print('c')
