import base64
import requests
import json
import urllib.request
import datetime
import urllib.parse as urlparse
import handlers.Roboragi.AnimeBot as aBot

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


def saucetrace(url, proxy):
    header = {'Content-Type': 'application/json'}
    body = json.dumps({'image': tob64(urltofile(url))})
    proxies = {}
    if proxy:
        proxies.update({
            'http': 'http://' + proxy,
            'https': 'http://' + proxy,
        })
    r = requests.post(traceurl, headers=header, data=body, proxies=proxies)

    return json.loads(r.text)


def res(url, proxy=None):
    dic = {}
    r = saucetrace(url, proxy)
    if r['docs'][0]['similarity'] < 0.90:
        return dic
    url_prev2 = 'https://trace.moe/preview.php?anilist_id=' + str(
        r['docs'][0]['anilist_id']) + '&file=' + urlparse.quote(r['docs'][0]['filename']) + '&t=' + str(
        r['docs'][0]['at']) + '&token=' + r['docs'][0]['tokenthumb']

    dic.update({'Title': r['docs'][0]['title_native'],
                'Romaji': r['docs'][0]['title_romaji'],
                'English': r['docs'][0]['title_english'],
                'Season': str(r['docs'][0]['season']),
                'Episode': str(r['docs'][0]['episode']),
                'Time': str(chop_microseconds(datetime.timedelta(seconds=r['docs'][0]['at']))) + '\n',
                'Info': aBot.process_comment('{' + r['docs'][0]['title_romaji'] + '}', is_expanded=True,
                                             trace=True)['reply']})

    return {'source': 'trace',
            'url': url_prev2,
            'limit': r['limit'],
            'limit_ttl': r['limit_ttl'],
            'quota': r['quota'],
            'quota_ttl': r['quota_ttl'],
            'reply': dic}
