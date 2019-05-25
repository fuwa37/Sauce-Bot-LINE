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
    def minires(res):
        return {'Title': res['docs'][0]['title_native'],
                'Romaji': res['docs'][0]['title_romaji'],
                'English': res['docs'][0]['title_english'],
                }

    @staticmethod
    def extres(res):
        return {'Title': res['docs'][0]['title_native'],
                'Romaji': res['docs'][0]['title_romaji'],
                'English': res['docs'][0]['title_english'],
                'Season': res['docs'][0]['season'],
                'Episode': res['docs'][0]['episode'],
                'Time': str(chop_microseconds(datetime.timedelta(seconds=res['docs'][0]['at']))),
                "Similarity": "{:.0%}".format(res['docs'][0]['similarity']),
                }


class SauceNow:
    @staticmethod
    def sauce(url):
        r = requests.get(sauceurl + url)
        return json.loads(r.text)

    @staticmethod
    def result(res):
        results = []
        for i in res['results']:
            if float(i['header']['similarity']) > 65:
                results.append(i)
        return results

    @staticmethod
    def extres(res):
        r = SauceNow.result(res)
        return {'Title': r[0]['data']['source'],
                'Episode': r[0]['data']['part'],
                'Time': r[0]['data']['est_time'],
                'Similarity': r[0]['header']['similarity'],
                }

    @staticmethod
    def minires(res):
        r = SauceNow.result(res)
        return {'Title': r[0]['data']['source'],
                }
