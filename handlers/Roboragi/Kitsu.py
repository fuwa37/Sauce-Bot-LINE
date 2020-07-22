# Copyright (C) 2018  Nihilate
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import difflib

import requests, traceback

AUTH_URL = 'https://kitsu.io/api/oauth/'
BASE_URL = 'https://kitsu.io/api/edge/'
ANIME_SEARCH_FILTER = 'anime?filter[text]='
MANGA_SEARCH_FILTER = 'manga?filter[text]='
ANIME_GET_FILTER = 'anime?filter[slug]='
MANGA_GET_FILTER = 'manga?filter[slug]='

ENGLISH_LANGUAGE_CODES = ['en', 'en_us']
ROMAJI_LANGUAGE_CODES = ['en_jp']
JAPANESE_LANGUAGE_CODES = ['ja_jp']
KOREAN_LANGUAGE_CODES = ['ko_kr']
ROMAJA__LANGUAGE_CODES = ['en_kr']
CHINESE_LANGUAGE_CODE = ['zh_cn']
PINYIN__LANGUAGE_CODES = ['en_cn']

session = requests.Session()
session.headers = {
    'Accept': 'application/vnd.api+json',
    'Content-Type': 'application/vnd.api+json'
}


def search(endpoint, search_term, parser, use_first_result=False):
    results = ''
    try:
        response = session.get(BASE_URL + endpoint + search_term, timeout=5)
        response.raise_for_status()

        results = parser(response.json()['data'])
    except Exception as e:
        print(e)

    try:
        if not results:
            return None

        if use_first_result:
            return results[0]
        else:
            closest_result = get_closest(results, search_term)
            return closest_result
    except Exception as e:
        print(traceback.format_exc())
        return None
    finally:
        session.close()


def get_closest(results, search_term):
    name_list = []
    closest_name_from_list = ''

    for result in results:
        title_and_synonyms = get_titles(result) | get_synonyms(result)
        synonyms = [synonym.lower() for synonym in title_and_synonyms]
        if synonyms:
            name_list.extend(synonyms)

    matches = difflib.get_close_matches(
        word=search_term.lower(),
        possibilities=name_list,
        n=1,
        cutoff=0.90
    )
    if matches:
        closest_name_from_list = matches[0].lower()

    for result in results:
        res_titles = result['titles']
        if res_titles['jp']['en']:
            if res_titles['jp']['en'].lower() == closest_name_from_list:
                return result
        if res_titles['kr']['en']:
            if res_titles['kr']['en'].lower() == closest_name_from_list:
                return result
        if res_titles['cn']['en']:
            if res_titles['cn']['en'].lower() == closest_name_from_list:
                return result
        if res_titles['en']:
            if res_titles['en'].lower() == closest_name_from_list:
                return result
        else:
            for synonym in result['synonyms']:
                if synonym.lower() == closest_name_from_list:
                    return result


def search_anime(search_term):
    return search(ANIME_SEARCH_FILTER, search_term, parse_anime)


def search_manga(search_term):
    return search(MANGA_SEARCH_FILTER, search_term, parse_manga)


def search_light_novel(search_term):
    return search(MANGA_SEARCH_FILTER, search_term, parse_light_novel)


def get_anime(search_term):
    try:
        return search(ANIME_GET_FILTER, search_term, parse_anime, True)
    except Exception:
        return None


def get_manga(search_term):
    try:
        return search(MANGA_GET_FILTER, search_term, parse_manga, True)
    except Exception:
        return None


def get_light_novel(search_term):
    try:
        return search(MANGA_GET_FILTER, search_term, parse_light_novel, True)
    except Exception:
        return None


def parse_anime(results):
    anime_list = []

    for entry in results:
        try:
            id_ = entry['id']
            slug = entry['attributes']['slug']
            url = f"https://kitsu.io/anime/{slug}"
            title_english = get_title_by_language_codes(
                titles=entry['attributes']['titles'],
                language_codes=ENGLISH_LANGUAGE_CODES
            )

            JP = {'en': get_title_by_language_codes(
                titles=entry['attributes']['titles'],
                language_codes=ROMAJI_LANGUAGE_CODES),
                'jp': get_title_by_language_codes(
                    titles=entry['attributes']['titles'],
                    language_codes=JAPANESE_LANGUAGE_CODES)}

            KR = {'en': get_title_by_language_codes(
                titles=entry['attributes']['titles'],
                language_codes=ROMAJA__LANGUAGE_CODES),
                'kr': get_title_by_language_codes(
                    titles=entry['attributes']['titles'],
                    language_codes=KOREAN_LANGUAGE_CODES)}

            CN = {'en': get_title_by_language_codes(
                titles=entry['attributes']['titles'],
                language_codes=PINYIN__LANGUAGE_CODES),
                'cn': get_title_by_language_codes(
                    titles=entry['attributes']['titles'],
                    language_codes=CHINESE_LANGUAGE_CODE)}

            if entry['attributes']['abbreviatedTitles']:
                synonyms = set(entry['attributes']['abbreviatedTitles'])
            else:
                synonyms = set()

            if entry['attributes']['episodeCount']:
                episode_count = int(entry['attributes']['episodeCount'])
            else:
                episode_count = None

            type_ = entry['attributes']['showType']
            description = entry['attributes']['synopsis']
            nsfw = entry['attributes']['nsfw']

            anime = dict(
                id=id_,
                url=url,
                titles={
                    'en': title_english,
                    'kr': KR,
                    'jp': JP,
                    'cn': CN
                },
                synonyms=synonyms,
                episode_count=episode_count,
                type=type_,
                description=description,
                nsfw=nsfw,
            )

            anime_list.append(anime)
        except AttributeError:
            pass

    return anime_list


def parse_manga(results):
    manga_list = []

    for entry in results:
        try:
            type_ = entry['attributes']['mangaType']
            # Avoid all the processsing below if the type is "novel".
            if type_.lower() == 'novel':
                continue

            id_ = entry['id']
            slug = entry['attributes']['slug']
            url = f"https://kitsu.io/manga/{slug}"
            title_english = get_title_by_language_codes(
                titles=entry['attributes']['titles'],
                language_codes=ENGLISH_LANGUAGE_CODES
            )

            JP = {'en': get_title_by_language_codes(
                titles=entry['attributes']['titles'],
                language_codes=ROMAJI_LANGUAGE_CODES),
                'jp': get_title_by_language_codes(
                    titles=entry['attributes']['titles'],
                    language_codes=JAPANESE_LANGUAGE_CODES)}

            KR = {'en': get_title_by_language_codes(
                titles=entry['attributes']['titles'],
                language_codes=ROMAJA__LANGUAGE_CODES),
                'kr': get_title_by_language_codes(
                    titles=entry['attributes']['titles'],
                    language_codes=KOREAN_LANGUAGE_CODES)}

            CN = {'en': get_title_by_language_codes(
                titles=entry['attributes']['titles'],
                language_codes=PINYIN__LANGUAGE_CODES),
                'cn': get_title_by_language_codes(
                    titles=entry['attributes']['titles'],
                    language_codes=CHINESE_LANGUAGE_CODE)}

            if entry['attributes']['abbreviatedTitles']:
                synonyms = set(entry['attributes']['abbreviatedTitles'])
            else:
                synonyms = set()

            if entry['attributes']['volumeCount']:
                volume_count = int(entry['attributes']['volumeCount'])
            else:
                volume_count = None

            if entry['attributes']['chapterCount']:
                chapter_count = int(entry['attributes']['chapterCount'])
            else:
                chapter_count = None

            description = entry['attributes']['synopsis']

            manga = dict(
                id=id_,
                url=url,
                titles={
                    'en': title_english,
                    'kr': KR,
                    'jp': JP,
                    'cn': CN
                },
                synonyms=synonyms,
                volume_count=volume_count,
                chapter_count=chapter_count,
                type=entry['attributes']['mangaType'],
                description=description,
            )

            manga_list.append(manga)
        except AttributeError:
            pass

    return manga_list


def parse_light_novel(results):
    ln_list = []

    for entry in results:
        try:
            type_ = entry['attributes']['mangaType']
            # Avoid all the processsing below if the type is not "novel".
            if type_.lower() != 'novel':
                continue

            id_ = entry['id']
            slug = entry['attributes']['slug']
            url = f"https://kitsu.io/manga/{slug}"
            title_english = get_title_by_language_codes(
                titles=entry['attributes']['titles'],
                language_codes=ENGLISH_LANGUAGE_CODES
            )

            JP = {'en': get_title_by_language_codes(
                titles=entry['attributes']['titles'],
                language_codes=ROMAJI_LANGUAGE_CODES),
                'jp': get_title_by_language_codes(
                    titles=entry['attributes']['titles'],
                    language_codes=JAPANESE_LANGUAGE_CODES)}

            KR = {'en': get_title_by_language_codes(
                titles=entry['attributes']['titles'],
                language_codes=ROMAJA__LANGUAGE_CODES),
                'kr': get_title_by_language_codes(
                    titles=entry['attributes']['titles'],
                    language_codes=KOREAN_LANGUAGE_CODES)}

            CN = {'en': get_title_by_language_codes(
                titles=entry['attributes']['titles'],
                language_codes=PINYIN__LANGUAGE_CODES),
                'cn': get_title_by_language_codes(
                    titles=entry['attributes']['titles'],
                    language_codes=CHINESE_LANGUAGE_CODE)}

            if entry['attributes']['abbreviatedTitles']:
                synonyms = set(entry['attributes']['abbreviatedTitles'])
            else:
                synonyms = set()

            if entry['attributes']['volumeCount']:
                volume_count = int(entry['attributes']['volumeCount'])
            else:
                volume_count = None

            if entry['attributes']['chapterCount']:
                chapter_count = int(entry['attributes']['chapterCount'])
            else:
                chapter_count = None

            description = entry['attributes']['synopsis']

            ln = dict(
                id=id_,
                url=url,
                titles={
                    'en': title_english,
                    'kr': KR,
                    'jp': JP,
                    'cn': CN
                },
                synonyms=synonyms,
                volume_count=volume_count,
                chapter_count=chapter_count,
                type=type_,
                description=description,
            )
            ln_list.append(ln)
        except AttributeError:
            pass

    return ln_list


def get_synonyms(result):
    synonyms = set()
    synonyms.update(result['synonyms'])
    return synonyms


def get_titles(result):
    titles = set()
    res_titles = result['titles']
    titles.add(res_titles['en']) if res_titles['en'] else None
    titles.add(res_titles['kr']['kr']) if res_titles['kr']['kr'] else None
    titles.add(res_titles['kr']['en']) if res_titles['kr']['en'] else None
    titles.add(res_titles['jp']['jp']) if res_titles['jp']['jp'] else None
    titles.add(res_titles['jp']['en']) if res_titles['jp']['en'] else None
    titles.add(res_titles['cn']['cn']) if res_titles['cn']['cn'] else None
    titles.add(res_titles['cn']['en']) if res_titles['cn']['en'] else None
    return titles


def get_title_by_language_codes(titles, language_codes):
    for language_code in language_codes:
        if language_code in titles:
            return titles[language_code]
    return None
