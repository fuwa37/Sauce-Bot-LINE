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


def saucetrace(picture):
    header = {'Content-Type': 'application/json'}
    buffered = BytesIO()

    if type(picture) is str and picture.startswith('http'):
        data = requests.get(picture, stream=True)
        image = Image.open(data.raw)
    else:
        image = Image.open(picture.stream)
    try:
        image.save(buffered, format='JPEG')
    except Exception as x:
        print("Error: " + str(x))
        image.save(buffered, format='PNG')
    img_str = base64.b64encode(buffered.getvalue())

    body = json.dumps({'image': img_str.decode('utf-8')})
    r = requests.post(url=traceurl, headers=header, data=body)
    try:
        temp = json.loads(r.text)
    except Exception as e:
        print(e)
        temp = None

    return image, temp


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
    minimum_similarity = 0.88
    img, r = saucetrace(url)
    if r is None:
        return {}

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

    print(data)

    dic.update({'Title': data['title_native'],
                'Romaji': data['title_romaji'],
                'English': data['title_english'],
                'Season': str(data['season']),
                'Episode': str(data['episode']),
                'Time': str(chop_microseconds(datetime.timedelta(seconds=data['at']))) + '\n',
                'Similarity': float("%.2f" % (similarity*100)),
                'Info': aBot.process_comment('{' + data['title_romaji'] + '}', is_expanded=True,
                                             trace=True).get('reply')})

    return {'url': url_prev2,
            'image_url': url_prev,
            'limit': r['limit'],
            'limit_ttl': r['limit_ttl'],
            'quota': r['quota'],
            'quota_ttl': r['quota_ttl'],
            'reply': dic}
