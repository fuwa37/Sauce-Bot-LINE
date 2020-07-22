from bs4 import BeautifulSoup
import re
import handlers.sauce.trace as trace2
from PIL import Image
from io import BytesIO
import requests

def create_link_dictionary(soup, force):
    MINIMUM_SIMILARITY_PERCENTAGE = 65
    MAX_DELTA = 20
    dic = {}
    first = True
    top_similarity_percentage = 0.0
    if force is True:
        MINIMUM_SIMILARITY_PERCENTAGE = 0
    # Creator - boorus; Material - boorus; Author - DeviantArt; Member - Pixiv

    # Filters to only show relevant results.
    results = soup.find_all('div', class_='result')

    if not results:
        return {}

    for result in results:
        # Skip "hidden results" result
        if result.get('id') is not None:
            continue

        if first:
            top_similarity_percentage = float(result.find(class_='resultsimilarityinfo').text[:-1])
            first = False
        # Skip all further results if they are low quality matches
        similarity_percentage = float(result.find(class_='resultsimilarityinfo').text[:-1])
        if similarity_percentage < MINIMUM_SIMILARITY_PERCENTAGE or top_similarity_percentage - MAX_DELTA > similarity_percentage:
            break

        # Make assumption about content based on preview image url /frames/ = anidb, /dA/ = deviantart,
        # /res/pixiv/ = pixiv, /booru/ = danbooru/gelbooru, /res/nhentai = nhentai, /res/fakku = FAKKU,
        # /res/mangadex = mangadex
        image_url = result.table.tr.td.div.a.img.get('src')

        if re.search(r'/res/nhentai/', image_url):
            # nHentai Block
            if not dic.get('type'):
                dic.update(({'similarity': similarity_percentage}))
                dic.update(({'image_url': image_url}))
                dic.update({'type': 'nhentai'})
            gallery_number = re.search(r'(?<=\/nhentai\/)\d+', image_url)
            if gallery_number and not dic.get('gallery_number'):
                dic.update({'gallery_number': gallery_number.group(0)})
            page_number = re.search(r'(?<=\/)\d+(?=\.jpg)', image_url)
            if page_number and not dic.get('page_number'):
                dic.update({'page_number': page_number.group(0)})
            title = result.find('div', class_='resulttitle').strong.text
            if title and not dic.get('title'):
                dic.update({'title': title})
            creator = results[0].table.tr.find('div', class_='resultcontentcolumn')
            creator = re.search(r'(?<=Creator\(s\): <\/strong>).*?(?=<br\/>)', str(creator))
            if creator and not dic.get('creator'):
                dic.update({'creator': creator.group(0)})
            continue

        if re.search(r'/frames/', image_url):
            # aniDB block
            if not dic.get('type'):
                dic.update(({'similarity': similarity_percentage}))
                dic.update(({'image_url': image_url}))
                dic.update({'type': 'anidb'})
            title_candidate = result.find('div', class_='resulttitle')
            title = title_candidate.strong.text
            if title and not dic.get('title'):
                dic.update({'title': title})
            supplemental_info = re.sub(r'\<strong\>.*?\<\/strong\>', '',
                                       title_candidate.text.replace('<small>', '').replace('</small>', ''))
            if supplemental_info and not dic.get('supplemental_info'):
                dic.update({'supplemental_info': supplemental_info})
            japanese_title = re.search(r'(?<=<strong>Title: </strong>).*?(?=<)', str(result))
            if japanese_title and not dic.get('japanese_title'):
                dic.update({'japanese_title': japanese_title.group(0)})
            time_code = re.search(r'(?<=<strong>Est Time: </strong>).*?(?=<)', str(result))
            if time_code and not dic.get('time_code'):
                dic.update({'time_code': time_code.group(0)})
            episode = re.search(r'(?<=<strong>Name: </strong>).*?(?=<)', str(result))
            if episode and not dic.get('episode'):
                dic.update({'episode': episode.group(0)})
            anidb_link = result.find('div', class_='resultmiscinfo').a.get('href')
            if anidb_link and not dic.get('anidb_link'):
                dic.update({'anidb_link': anidb_link})
            continue

        if re.search(r'/res/dA/', image_url):
            # DeviantArt block
            if not dic.get('type'):
                dic.update(({'similarity': similarity_percentage}))
                dic.update(({'image_url': image_url}))
                dic.update({'type': 'da'})
            title = result.find('div', class_='resulttitle')
            if title and not dic.get('title'):
                dic.update({'title': title.strong.text})
            resultcontentcolumn = result.find('div', class_='resultcontentcolumn').find_all('a')
            if len(resultcontentcolumn) == 2:
                if not dic.get('da_link'):
                    dic.update({'da_link': resultcontentcolumn[0].get('href')})
                if not dic.get('da_id'):
                    dic.update({'da_id': resultcontentcolumn[0].text})
                if not dic.get('author_link'):
                    dic.update({'author_link': resultcontentcolumn[1].get('href')})
                if not dic.get('author'):
                    dic.update({'author': resultcontentcolumn[1].text})
            continue
        if re.search(r'/booru/', image_url):
            # 'Booru block
            if not dic.get('type'):
                dic.update(({'similarity': similarity_percentage}))
                dic.update(({'image_url': image_url}))
                dic.update({'type': 'booru'})
            creator = result.find('div', class_='resulttitle')
            if creator:
                creator = re.search(r'(?<=Creator: <\/strong>).*?(?=<)', str(creator))
                if creator and not dic.get('creator'):
                    dic.update({'creator': creator.group(0)})
            # print(creator)
            res = result.find_all('div', class_='resultcontentcolumn')
            material = res[0]
            chars = res[1]

            if material:
                material1 = re.search(r'(?<=Material: <\/strong>).*?(?=<br/><)', str(material))
                if material1 is not None:
                    mat = material1.group(0)
                    if mat.find("<br/>"):
                        mat = mat.replace("<br/>", " | ")
                    if material1 and not dic.get('material'):
                        dic.update({'material': mat})
                    material = re.search(r'(?<=Source: </strong>).*?(?=<)', str(material))
                    if material and not dic.get('material'):
                        dic.update({'material': material.group(0)})

            if chars:
                char1 = re.search(r'(?<=Characters: <\/strong><br/>).*?(?=<br/><)', str(chars))
                if char1 is not None:
                    char = char1.group(0)
                    if char.find("<br/>"):
                        char = char.replace("<br/>", " | ")
                    if char1 and not dic.get('character'):
                        dic.update({'character': char})

            for link in result.find('div', class_='resultmiscinfo').find_all('a'):
                link = link.get('href')
                # print(link)
                if link[8:17] == 'danbooru.':
                    if not dic.get('danbooru_link'):
                        dic.update({'danbooru_link': link})
                        continue
                if link[8:17] == 'gelbooru.':
                    if not dic.get('gelbooru_link'):
                        dic.update({'gelbooru_link': link})
                        continue
                if link[8:28] == 'chan.sankakucomplex.':
                    if not dic.get('sankaku_link'):
                        dic.update({'sankaku_link': link})
                        continue
                if link[8:16] == 'yande.re':
                    if not dic.get('yandere_link'):
                        dic.update({'yandere_link': link})
                        continue
            if similarity_percentage > 90:
                dic.update(({'similarity': similarity_percentage}))
                dic.update(({'image_url': image_url}))
                dic.update({'type': 'booru'})
            continue

        if re.search(r'/res/pixiv/', image_url):
            # Pixiv block
            if not dic.get('type'):
                dic.update(({'similarity': similarity_percentage}))
                dic.update(({'image_url': image_url}))
                dic.update({'type': 'pixiv'})
            title = result.find('div', class_='resulttitle')
            if title and not dic.get('title'):
                dic.update({'title': title.strong.text})
            resultcontentcolumn = result.find('div', class_='resultcontentcolumn').find_all('a')
            if len(resultcontentcolumn) == 4:
                if not dic.get('pixiv_link'):
                    dic.update({'pixiv_link': resultcontentcolumn[0].get('href')})
                if not dic.get('pixiv_id'):
                    dic.update({'pixiv_id': resultcontentcolumn[0].text})
                if not dic.get('member_link'):
                    dic.update({'member_link': resultcontentcolumn[2].get('href')})
                if not dic.get('member'):
                    dic.update({'member': resultcontentcolumn[2].text})
            continue

        if re.search(r'/res/fakku', image_url):
            # FAKKU block
            if not dic.get('type'):
                dic.update(({'similarity': similarity_percentage}))
                dic.update(({'image_url': image_url}))
                dic.update({'type': 'fakku'})
            result_content = result.find('div', class_='resultcontent')
            title = result_content.find('div', class_='resulttitle')
            if title:
                if not dic.get('title'):
                    dic.update({'title': title.a.strong.text})
                if not dic.get('fakku_link'):
                    dic.update({'fakku_link': title.a.get('href')})
            artist = result_content.find('div', class_='resultcontentcolumn')
            if artist:
                if not dic.get('artist'):
                    dic.update({'artist': artist.a.strong.text})
                if not dic.get('artist_link'):
                    dic.update({'artist_link': artist.a.get('href')})
            continue

        if re.search(r'/res/mangadex', image_url):
            # Mangadex block
            if not dic.get('type'):
                dic.update(({'similarity': similarity_percentage}))
                dic.update(({'image_url': image_url}))
                dic.update({'type': 'mangadex'})

            page_number = re.search(r'\d+(?=\.jpg)', image_url)
            if page_number and not dic.get('mangadex_page_number'):
                dic.update({'mangadex_page_number': page_number.group(0)})

            resultcontentcolumn = result.find('div', class_='resultcontentcolumn')
            if resultcontentcolumn:
                artist = re.search(r'(?<=Artist: <\/strong>).*?(?=<)', str(resultcontentcolumn))
                author = re.search(r'(?<=Author: <\/strong>).*?(?=<)', str(resultcontentcolumn))
                if artist and not dic.get('artist'):
                    dic.update({'artist': artist.group(0)})
                if author and not dic.get('author'):
                    dic.update({'author': author.group(0)})

            title = result.find('div', class_='resulttitle')
            if title and not dic.get('title'):
                text = ''
                for entry in title.contents:
                    text += f'{entry}'
                dic.update({'title': text.replace('<strong>', '').replace('</strong>', '').replace('<br/>', ' ')})

            for link in result.find('div', class_='resultmiscinfo').find_all('a'):
                link = link.get('href')
                if link[8:20] == 'mangadex.org':
                    if not dic.get('mangadex_link'):
                        dic.update({'mangadex_link': link})
                        continue
                if link[8:24] == 'www.mangaupdates':
                    if not dic.get('mangaupdates_link'):
                        dic.update({'mangaupdates_link': link})
                        continue
                if link[8:30] == 'myanimelist.net/manga/':
                    if not dic.get('mal_manga_link'):
                        dic.update({'mal_manga_link': link})
                        continue
            continue
    return dic


def get_source_data(picture, force = False, trace=False):
    dic = {}
    try:
        resp = ''
        if type(picture) is str and picture.startswith('http'):
            resp = requests.get('https://saucenao.com/search.php?db=999&url=' + picture)
            if resp.status_code == 429:
                raise Exception('Code 429')
        else:
            image = Image.open(picture.stream)
            buffered = BytesIO()
            try:
                image.save(buffered, format='JPEG')
                files = {'file': ("image.jpg", buffered.getvalue())}
            except Exception as x:
                print("Error: " + str(x))
                image.save(buffered, format='PNG')
                files = {'file': ("image.png", buffered.getvalue())}
            resp = requests.post('https://saucenao.com/search.php?output_type=0', data=files)
        soup = BeautifulSoup(resp.content, features='lxml')
        dic.update(create_link_dictionary(soup, force))
    except Exception as x:
        temp = {}
        print("Error: " + str(x))
        if trace:
            temp.update(trace2.res(picture, force))
            if temp:
                dic.update(temp)
            return dic
        else:
            return dic.update({'code': 429})
    finally:
        if trace:
            if dic.get('type') == 'anidb' or not dic:
                dic.update(trace2.res(picture, force))
        return dic
