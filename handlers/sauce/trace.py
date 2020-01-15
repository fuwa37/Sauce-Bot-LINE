import base64
import requests
import json
import datetime
import urllib.parse as urlparse
import handlers.Roboragi.AnimeBot as aBot
import imagehash
from PIL import Image
from io import BytesIO

traceurl = "https://trace.moe/api/search"


def chop_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)


def saucetrace(url):
    header = {'Content-Type': 'application/json'}
    data = requests.get(url, stream=True)
    buffered = BytesIO()
    image = Image.open(data.raw)
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())

    body = json.dumps({'image': img_str.decode('utf-8')})
    r = requests.post(traceurl, headers=header, data=body)

    return image, json.loads(r.text)


def forceres(img, r):
    cutoff = 100
    temp = {}
    for i in r['docs'][:3]:
        data = requests.get('https://trace.moe/thumbnail.php?anilist_id=' + str(
            i['anilist_id']) + '&file=' + urlparse.quote(i['filename']) + '&t=' + str(
            i['at']) + '&token=' + i['tokenthumb'], stream=True)
        img_thumb = Image.open(data.raw)

        thumb_hash = imagehash.dhash(img_thumb)
        img_hash = imagehash.dhash(img)

        diff = thumb_hash - img_hash
        if diff == 0:
            return i
        elif diff < cutoff:
            cutoff = diff
            temp = i

    return temp


def res(url, force):
    dic = {}
    minimum_similarity = 0.90
    img, r = saucetrace(url)
    if force is True:
        data = forceres(img, r)
        similarity = data['similarity']
    else:
        data = r['docs'][0]
        similarity = data['similarity']
        if similarity < minimum_similarity:
            return {}
    url_prev = 'https://trace.moe/thumbnail.php?anilist_id=' + str(
        data['anilist_id']) + '&file=' + urlparse.quote(data['filename']) + '&t=' + str(
        data['at']) + '&token=' + data['tokenthumb']
    url_prev2 = 'https://trace.moe/preview.php?anilist_id=' + str(
        data['anilist_id']) + '&file=' + urlparse.quote(data['filename']) + '&t=' + str(
        data['at']) + '&token=' + data['tokenthumb']

    dic.update({'Title': data['title_native'],
                'Romaji': data['title_romaji'],
                'English': data['title_english'],
                'Season': str(data['season']),
                'Episode': str(data['episode']),
                'Time': str(chop_microseconds(datetime.timedelta(seconds=data['at']))) + '\n',
                'Similarity': "{:.2%}".format(similarity),
                'Info': aBot.process_comment('{' + data['title_romaji'] + '}', is_expanded=True,
                                             trace=True)['reply']})

    return {'url': url_prev2,
            'image_url': url_prev,
            'limit': r['limit'],
            'limit_ttl': r['limit_ttl'],
            'quota': r['quota'],
            'quota_ttl': r['quota_ttl'],
            'reply': dic}
