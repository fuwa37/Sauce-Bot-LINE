import base64
import requests
import json
import urllib.request
import datetime

sauceurl = "https://saucenao.com/search.php?output_type=2&db=9998&url="
traceurl = "https://trace.moe/api/search"


def chop_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)


def urltofile(url):
    with urllib.request.urlopen(url) as url:
        with open('temp', 'wb') as f:
            f.write(url.read())
    return "temp"


class Trace:
    @staticmethod
    def tob64(file):
        with open(file, "rb") as image_file:
            b64 = base64.b64encode(image_file.read())
            return b64.decode('utf-8')

    @staticmethod
    def saucetrace(url):
        header = {'Content-Type': 'application/json'}
        body = json.dumps({'image': Trace.tob64(urltofile(url))})

        r = requests.post(traceurl, headers=header, data=body)

        return json.loads(r.text)

    @staticmethod
    def res(url, mode=None):
        if url == '':
            return None
        r = Trace.saucetrace(url)
        if r['docs'][0]['similarity'] < 0.65:
            return None
        if mode is None:
            return ReplyBuilder.reply({'Title': r['docs'][0]['title_native'],
                                       'Romaji': r['docs'][0]['title_romaji'],
                                       'English': r['docs'][0]['title_english'],
                                       })
        if mode == 'ext':
            return ReplyBuilder.reply({'Title': r['docs'][0]['title_native'],
                                       'Romaji': r['docs'][0]['title_romaji'],
                                       'English': r['docs'][0]['title_english'],
                                       'Season': str(r['docs'][0]['season']),
                                       'Episode': str(r['docs'][0]['episode']),
                                       'Time': str(chop_microseconds(datetime.timedelta(seconds=r['docs'][0]['at']))),
                                       })


class SauceNow:
    @staticmethod
    def sauce(url):
        r = requests.get(sauceurl + url)
        return json.loads(r.text)

    @staticmethod
    def result(url, c=65):
        r = SauceNow.sauce(url)
        results = []
        for i in r['results']:
            if float(i['header']['similarity']) > c:
                results.append(i)
        return results

    @staticmethod
    def res(url, mode=None):
        r = SauceNow.result(url)
        if mode is None:
            return ReplyBuilder.reply({'Title': r[0]['data']['source'],
                                       'Episode': r[0]['data']['part'],
                                       'Time': r[0]['data']['est_time'],
                                       'Similarity': r[0]['header']['similarity'] + "%",
                                       })
        if mode == 'ext':
            er = []
            for i in r:
                er.append({'Title': i['data']['source'],
                           'Episode': i['data']['part'],
                           'Time': i['data']['est_time'],
                           'Similarity': i['header']['similarity'] + "%",
                           })
            return ReplyBuilder.reply2(er)
        if mode == 'mini':
            return ReplyBuilder.reply({'Title': r[0]['data']['source'],
                                       })


class ReplyBuilder:
    @staticmethod
    def reply(res):
        if res is None:
            return "Not Found"
        rs = ""
        for i in res:
            rs += "\n" + i + "  :" + res[i] + "\n"
        return rs

    @staticmethod
    def reply2(res):
        rs = ""
        for i in res:
            for j in i:
                rs += "\n" + j + "  :" + i[j] + "\n"
        return rs

