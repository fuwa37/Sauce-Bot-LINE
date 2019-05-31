import base64
import requests
import json
import urllib.request
import datetime
import urllib.parse as urlparse
import time

sauceurl = "https://saucenao.com/search.php?output_type=2&db=9998&url="
traceurl = "https://trace.moe/api/search"


def chop_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)


def urltofile(url):
    with urllib.request.urlopen(url) as url:
        temp = url.read()
    return temp


def tob64(file):
    b64 = base64.b64encode(file)
    return b64.decode('utf-8')


def saucetrace(url):
    header = {'Content-Type': 'application/json'}
    body = json.dumps({'image': tob64(urltofile(url))})

    r = requests.post(traceurl, headers=header, data=body)

    return json.loads(r.text)


def res(url, mode=None):
    r = saucetrace(url)
    if r['docs'][0]['similarity'] < 0.85:
        return reply(None)
    url_prev = 'https://media.trace.moe/video/' + str(r['docs'][0]['anilist_id']) + '/' + urlparse.quote(
        r['docs'][0]['filename']) + '?t=' + str(r['docs'][0]['at'] - 30) + '&token=' + r['docs'][0]['tokenthumb']
    url_prev2 = 'https://trace.moe/preview.php?anilist_id=' + str(
        r['docs'][0]['anilist_id']) + '&file=' + urlparse.quote(r['docs'][0]['filename']) + '&t=' + str(
        r['docs'][0]['at']) + '&token=' + r['docs'][0]['tokenthumb']
    if mode is None:
        return ('trace', reply({'Title': r['docs'][0]['title_native'],
                                'Romaji': r['docs'][0]['title_romaji'],
                                'English': r['docs'][0]['title_english'],
                                'Season': str(r['docs'][0]['season']),
                                'Episode': str(r['docs'][0]['episode']),
                                'Time': str(
                                    chop_microseconds(datetime.timedelta(seconds=r['docs'][0]['at']))),
                                }), url_prev2, r['limit'])

    if mode == 'mini':
        return ('trace', reply({'Title': r['docs'][0]['title_native'],
                                'Romaji': r['docs'][0]['title_romaji'],
                                'English': r['docs'][0]['title_english'],
                                }), url_prev2, r['limit'])
    if mode == 'raw':
        return ('trace', r['docs'][0], url_prev, r['limit'])


def reply(res):
    if res is None:
        return "Not Found"
    rs = ""
    for i in res:
        rs += "\n" + i + "  :" + res[i] + "\n"
    return rs
