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


def res(url, force, proxy=None):
    dic = {}
    minimum_similarity = 0.90
    if force is True:
        minimum_similarity = 0
    r = saucetrace(url, proxy)
    top_similarity = r['docs'][0]['similarity']
    if top_similarity < minimum_similarity:
        return {}
    url_prev = 'https://trace.moe/thumbnail.php?anilist_id=' + str(
        r['docs'][0]['anilist_id']) + '&file=' + urlparse.quote(r['docs'][0]['filename']) + '&t=' + str(
        r['docs'][0]['at']) + '&token=' + r['docs'][0]['tokenthumb']
    url_prev2 = 'https://trace.moe/preview.php?anilist_id=' + str(
        r['docs'][0]['anilist_id']) + '&file=' + urlparse.quote(r['docs'][0]['filename']) + '&t=' + str(
        r['docs'][0]['at']) + '&token=' + r['docs'][0]['tokenthumb']

    dic.update({'Title': r['docs'][0]['title_native'],
                'Romaji': r['docs'][0]['title_romaji'],
                'English': r['docs'][0]['title_english'],
                'Season': str(r['docs'][0]['season']),
                'Episode': str(r['docs'][0]['episode']),
                'Time': str(chop_microseconds(datetime.timedelta(seconds=r['docs'][0]['at']))) + '\n',
                'Similarity': "{:.2%}".format(top_similarity),
                'Info': aBot.process_comment('{' + r['docs'][0]['title_romaji'] + '}', is_expanded=True,
                                             trace=True)['reply']})

    return {'url': url_prev2,
            'image_url': url_prev,
            'limit': r['limit'],
            'limit_ttl': r['limit_ttl'],
            'quota': r['quota'],
            'quota_ttl': r['quota_ttl'],
            'reply': dic}
