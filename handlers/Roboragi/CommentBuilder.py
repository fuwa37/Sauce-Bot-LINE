'''
CommentBuilder.py
Takes the data given to it by search and formats it into a comment
'''

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

import datetime
import re
import traceback
from os import linesep


# Removes the (Source: MAL) or (Written by X) bits from the decriptions in the databases
def cleanupDescription(desc):
    for match in re.finditer("([\[\<\(](.*?)[\]\>\)])", desc, re.S):
        if 'Source' in match.group(1).lower():
            desc = desc.replace(match.group(1), '')
        if 'MAL' in match.group(1):
            desc = desc.replace(match.group(1), '')
        if '[From' in match.group(1):
            desc = desc.replace(match.group(1), '')
        if 'taken from' in match.group(1):
            desc = desc.replace(match.group(1), '')

    for match in re.finditer("([\<](.*?)[\>])", desc, re.S):
        if 'br' in match.group(1).lower():
            desc = desc.replace(match.group(1), '')
        if 'i' == match.group(1).lower():
            desc = desc.replace(match.group(1), '')
        if 'b' == match.group(1).lower():
            desc = desc.replace(match.group(1), '')

    reply = ''
    for i, line in enumerate(linesep.join([s for s in desc.splitlines() if s]).splitlines()):
        if i is not 0:
            reply += '\n'
        reply += line + '\n'
    return reply


# Builds an anime comment from the various data sources
def buildAnimeComment(isExpanded, ani, kit, trace):
    try:
        comment = ''

        title = None
        jTitle = None

        cType = None

        malURL = None
        aniURL = None

        status = None
        episodes = None
        genres = []

        countdown = None
        nextEpisode = None
        curEpisode = None

        desc = None

        release_year = None

        if ani:
            aniURL = 'http://anilist.co/anime/' + str(ani['id'])
            malURL = 'http://myanimelist.net/anime/' + str(ani['id_mal']) if ani['id_mal'] else None

            title = ani['title_romaji'] if 'title_romaji' in ani else ani['title_english']
            desc = ani['description'] if 'description' in ani else None
            status = ani['airing_status'].title() if 'airing_status' in ani else None
            cType = ani['type'] if 'type' in ani else None

            jTitle = ani['title_japanese'] if 'title_japanese' in ani else None
            genres = ani['genres'] if 'genres' in ani else None

            try:
                year_str = str(ani['start_date_fuzzy']) if 'start_date_fuzzy' in ani else None
                if year_str:
                    release_year = year_str[:4]
            except:
                pass

            episodes = ani['total_episodes'] if 'total_episodes' in ani else None
            if episodes == 0:
                episodes = None

            if ani['airing']:
                countdown = ani['airing']['countdown']
                nextEpisode = ani['airing']['next_episode']
                if nextEpisode is not None:
                    curEpisode = ani['airing']['next_episode'] - 1
                else:
                    curEpisode = None
        # print(curEpisode)

        if kit:
            kitURL = kit['url']

            res_titles = kit["titles"]
            if not title:
                title = res_titles['en'] if res_titles['en'] else None
                kTitle = res_titles['kr']['kr'] if res_titles['kr']['kr'] else None
                kenTitle = res_titles['kr']['en'] if res_titles['kr']['en'] else None
                jTitle = res_titles['jp']['jp'] if res_titles['jp']['jp'] else None
                jenTitle = res_titles['jp']['en'] if res_titles['jp']['en'] else None
                cTitle = res_titles['cn']['cn'] if res_titles['cn']['cn'] else None
                cenTitle = res_titles['cn']['en'] if res_titles['cn']['en'] else None
            if not desc:
                desc = kit['description'] if 'description' in kit else None
            if not cType:
                cType = kit['type'].title() if 'type' in kit else None

            try:
                year_str = str(kit['startDate']) if 'startDate' in kit else None
                if year_str:
                    release_year = year_str[:4]
            except:
                pass

            if not episodes:
                episodes = kit['episode_count'] if 'episode_count' in kit else None
                if episodes == 0:
                    episodes = None

        # ---------- BUILDING THE COMMENT ----------#

        if not trace:
            # ----- TITLE -----#
            comment += title.strip() + '\n'

            # ----- JAPANESE TITLE -----#
            if (isExpanded):
                if jTitle is not None:
                    splitJTitle = jTitle.split()
                    for i, word in enumerate(splitJTitle):
                        if not (i == 0):
                            comment += ' '
                        comment += word + '\n'

        # ----- INFO LINE -----#
        if (isExpanded):
            comment += '\n('

            if cType:
                comment += cType + ' | '

            if release_year:
                comment += release_year

            if status:
                comment += ' | Status: ' + status

            # ----- Current Episodes -----#
            if curEpisode is not None:
                comment += ', Current episode: ' + str(curEpisode)

            if cType != 'Movie' and episodes:
                comment += ' | Episodes: ' + str(episodes)
        else:
            comment += '\n('

            if cType:
                comment += cType

            if status:
                comment += ' | Status: ' + status

            # ----- Current Episodes -----#
            if curEpisode is not None:
                comment += ', Current episode: ' + str(curEpisode)

            if cType != 'Movie' and episodes:
                comment += ' | Episodes: ' + str(episodes)

        if genres:
            if (isExpanded):
                comment += ' | Genres: '
            else:
                comment += ' | Genres: '

            for i, genre in enumerate(genres):
                if i is not 0:
                    comment += ', '
                comment += genre

        comment += ')'

        '''
        # ----- EPISODE COUNTDOWN -----#
        if (countdown is not None) and (nextEpisode is not None):
            current_utc_time = datetime.datetime.utcnow()
            air_time_in_utc = current_utc_time + datetime.timedelta(0, countdown)
            formatted_time = air_time_in_utc.strftime('%Y%m%dT%H%M')

            # countdown is given to us in seconds
            days, countdown = divmod(countdown, 24 * 60 * 60)
            hours, countdown = divmod(countdown, 60 * 60)
            minutes, countdown = divmod(countdown, 60)

            comment += '\n\n[Episode&#32;' + str(nextEpisode) + '&#32;airs&#32;in&#32;' + str(
                days) + '&#32;days,&#32;' + str(hours) + '&#32;hours,&#32;' + str(
                minutes) + '&#32;minutes](https://www.timeanddate.com/worldclock/fixedtime.html?iso=' + formatted_time + ')'
        '''

        # ----- DESCRIPTION -----#
        if (isExpanded):
            comment += '\n\n' + cleanupDescription(desc) + '\n'

        # ----- LINKS -----#
        urlComments = []

        if ani is not None:
            urlComments.append('[AL](' + sanitise_url_for_markdown(aniURL) + ')')
        if kit is not None:
            urlComments.append('[KIT](' + sanitise_url_for_markdown(kitURL) + ')')
        if malURL:
            urlComments.append('[MAL](' + sanitise_url_for_markdown(malURL) + ')')

        for i, link in enumerate(urlComments):
            if i is not 0:
                comment += '\n'
            comment += link

        # ----- END -----#
        receipt = '(A) Request successful: ' + title + ' - '
        if malURL is not None:
            receipt += 'MAL '
        if ani is not None:
            receipt += 'AL '
        if kit is not None:
            receipt += 'KIT '
        print(receipt)

        # We return the title/comment separately so we can track if multiples of the same comment have been requests (e.g. {Nisekoi}{Nisekoi}{Nisekoi})
        dictToReturn = {}
        dictToReturn['title'] = title
        dictToReturn['comment'] = comment

        return dictToReturn
    except:
        traceback.print_exc()
        return None


# Builds a manga comment from MAL/Anilist/MangaUpdates data
def buildMangaComment(isExpanded, ani, kit):
    try:
        comment = ''

        title = None
        jTitle = None

        cType = None

        malURL = None
        aniURL = None
        kitURL = None

        status = None
        chapters = None
        volumes = None
        genres = []

        desc = None

        if ani:
            aniURL = 'http://anilist.co/manga/' + str(ani['id'])
            malURL = 'http://myanimelist.net/manga/' + str(ani['id_mal']) if ani['id_mal'] else None

            title = ani['title_romaji'] if 'title_romaji' in ani else ani['title_english']
            desc = ani['description'] if 'description' in ani else None
            status = ani['publishing_status'].title() if 'publishing_status' in ani else None
            cType = ani['type'] if 'type' in ani else None

            jTitle = ani['title_japanese'] if 'title_japanese' in ani else None
            genres = ani['genres'] if 'genres' in ani else None

            chapters = ani['total_chapters'] if 'total_chapters' in ani else None
            if chapters == 0:
                chapters = None
            volumes = ani['total_volumes'] if 'total_volumes' in ani else None
            if volumes == 0:
                volumes = None

        if kit:
            kitURL = kit['url']

            res_titles = kit["titles"]
            if not title:
                title = res_titles['en'] if res_titles['en'] else None
                kTitle = res_titles['kr']['kr'] if res_titles['kr']['kr'] else None
                kenTitle = res_titles['kr']['en'] if res_titles['kr']['en'] else None
                jTitle = res_titles['jp']['jp'] if res_titles['jp']['jp'] else None
                jenTitle = res_titles['jp']['en'] if res_titles['jp']['en'] else None
                cTitle = res_titles['cn']['cn'] if res_titles['cn']['cn'] else None
                cenTitle = res_titles['cn']['en'] if res_titles['cn']['en'] else None
            if not desc:
                desc = kit['description'] if 'description' in kit else None
            if not cType:
                cType = kit['type'].title() if 'type' in kit else None

            if not chapters:
                chapters = kit['chapter_count'] if 'chapter_count' in kit else None
                if chapters == 0:
                    chapters = None
            if not volumes:
                volumes = kit['volume_count'] if 'volume_count' in kit else None
                if volumes == 0:
                    volumes = None

        # ---------- BUILDING THE COMMENT ----------#

        # ----- TITLE -----#
        comment += title.strip() + '\n'

        # ----- JAPANESE TITLE -----#
        if (isExpanded):
            if jTitle is not None:
                splitJTitle = jTitle.split()
                for i, word in enumerate(splitJTitle):
                    if not (i == 0):
                        comment += ' '
                    comment += word

        # ----- INFO LINE -----#

        if (isExpanded):
            comment += '\n('

            if cType:
                if cType == 'Novel':
                    cType = 'Light Novel'

                comment += '' + cType + ''

            if status:
                comment += ' | Status: ' + status

            if (cType != 'Light Novel'):
                if volumes and str(volumes) is not 'Unknown':
                    comment += ' | Volumes: ' + str(volumes)
                if chapters and str(chapters) is not 'Unknown':
                    comment += ' | Chapters: ' + str(chapters)
            else:
                if volumes and str(volumes) is not 'Unknown':
                    comment += ' | Volumes: ' + str(volumes)
        else:
            comment += '\n('

            if cType:
                if cType == 'Novel':
                    cType = 'Light Novel'

                comment += cType

            if status:
                comment += ' | Status: ' + status

            if (cType != 'Light Novel'):
                if volumes and str(volumes) is not 'Unknown':
                    comment += ' | Volumes: ' + str(volumes)
                if chapters and str(chapters) is not 'Unknown':
                    comment += ' | Chapters: ' + str(chapters)
            else:
                if volumes and str(volumes) is not 'Unknown':
                    comment += ' | Volumes: ' + str(volumes)

        if genres:
            if (isExpanded):
                comment += ' | Genres: '
            else:
                comment += ' | Genres: '

            for i, genre in enumerate(genres):
                if i is not 0:
                    comment += ', '
                comment += genre

        comment += ')'

        # ----- DESCRIPTION -----#
        if (isExpanded):
            comment += '\n\n' + cleanupDescription(desc)

        # ----- LINKS -----#
        urlComments = []

        if aniURL is not None:
            urlComments.append('[AL](' + sanitise_url_for_markdown(aniURL) + ')')
        if kitURL is not None:
            urlComments.append('[KIT](' + sanitise_url_for_markdown(kitURL) + ')')
        if malURL:
            urlComments.append('[MAL](' + sanitise_url_for_markdown(malURL) + ')')

        for i, link in enumerate(urlComments):
            if i is not 0:
                comment += '\n'
            comment += link

        comment += ')'

        # ----- END -----#
        receipt = '(M) Request successful: ' + title + ' - '
        if malURL is not None:
            receipt += 'MAL '
        if ani is not None:
            receipt += 'AL '
        if kit is not None:
            receipt += 'KIT '
        print(receipt)

        dictToReturn = {}
        dictToReturn['title'] = title
        dictToReturn['comment'] = comment

        return dictToReturn
    except:
        # traceback.print_exc()
        return None


# Builds a manga comment from MAL/Anilist/MangaUpdates data
def buildLightNovelComment(isExpanded, ani, nu, kit):
    try:
        comment = ''

        title = None
        jTitle = None

        cType = None

        malURL = None
        aniURL = None
        nuURL = nu
        kitURL = None

        status = None
        chapters = None
        volumes = None
        genres = []

        desc = None

        if ani:
            aniURL = 'http://anilist.co/manga/' + str(ani['id'])
            malURL = 'http://myanimelist.net/manga/' + str(ani['id_mal']) if ani['id_mal'] else None

            title = ani['title_romaji'] if 'title_romaji' in ani else ani['title_english']
            desc = ani['description'] if 'description' in ani else None
            status = ani['publishing_status'].title() if 'publishing_status' in ani and ani[
                'publishing_status'] else None
            cType = ani['type'] if 'type' in ani else None

            jTitle = ani['title_japanese'] if 'title_japanese' in ani else None
            genres = ani['genres'] if 'genres' in ani else None

            chapters = ani['total_chapters'] if 'total_chapters' in ani else None
            if chapters == 0:
                chapters = None
            volumes = ani['total_volumes'] if 'total_volumes' in ani else None
            if volumes == 0:
                volumes = None

        if kit:
            kitURL = kit['url']
            res_titles = kit["titles"]
            if not title:
                title = res_titles['en'] if res_titles['en'] else None
                kTitle = res_titles['kr']['kr'] if res_titles['kr']['kr'] else None
                kenTitle = res_titles['kr']['en'] if res_titles['kr']['en'] else None
                jTitle = res_titles['jp']['jp'] if res_titles['jp']['jp'] else None
                jenTitle = res_titles['jp']['en'] if res_titles['jp']['en'] else None
                cTitle = res_titles['cn']['cn'] if res_titles['cn']['cn'] else None
                cenTitle = res_titles['cn']['en'] if res_titles['cn']['en'] else None

            if not desc:
                desc = kit['description'] if 'description' in kit else None
            if not cType:
                cType = kit['type'].title() if 'type' in kit else None

            if not chapters:
                chapters = kit['chapter_count'] if 'chapter_count' in kit else None
                if chapters == 0:
                    chapters = None
            if not volumes:
                volumes = kit['volume_count'] if 'volume_count' in kit else None
                if volumes == 0:
                    volumes = None

        # ---------- BUILDING THE COMMENT ----------#

        # ----- TITLE -----#
        comment += title.strip() + '\n'

        # ----- JAPANESE TITLE -----#
        if (isExpanded):
            if jTitle is not None:
                splitJTitle = jTitle.split()
                for i, word in enumerate(splitJTitle):
                    if not (i == 0):
                        comment += ' '
                    comment += word

        # ----- INFO LINE -----#

        if (isExpanded):
            comment += '\n('

            if cType:
                if cType == 'Novel':
                    cType = 'Light Novel'

                comment += '' + cType + ''

            if status:
                comment += ' | Status: ' + status

            if (cType != 'Light Novel'):
                if volumes and str(volumes) is not 'Unknown':
                    comment += ' | Volumes: ' + str(volumes)
                if chapters and str(chapters) is not 'Unknown':
                    comment += ' | Chapters: ' + str(chapters)
            else:
                if volumes and str(volumes) is not 'Unknown':
                    comment += ' | Volumes: ' + str(volumes)
        else:
            comment += '\n('

            if cType:
                if cType == 'Novel':
                    cType = 'Light Novel'

                comment += cType

            if status:
                comment += ' | Status: ' + status

            if (cType != 'Light Novel'):
                if volumes and str(volumes) is not 'Unknown':
                    comment += ' | Volumes: ' + str(volumes)
                if chapters and str(chapters) is not 'Unknown':
                    comment += ' | Chapters: ' + str(chapters)
            else:
                if volumes and str(volumes) is not 'Unknown':
                    comment += ' | Volumes: ' + str(volumes)

        if genres:
            if (isExpanded):
                comment += ' | Genres: '
            else:
                comment += ' | Genres: '

            for i, genre in enumerate(genres):
                if i is not 0:
                    comment += ', '
                comment += genre

        comment += ')'

        # ----- DESCRIPTION -----#
        if (isExpanded):
            comment += '\n\n' + cleanupDescription(desc)

        # ----- LINKS -----#
        urlComments = []

        if aniURL is not None:
            urlComments.append('[AL](' + sanitise_url_for_markdown(aniURL) + ')')
        if kitURL is not None:
            urlComments.append('[KIT](' + sanitise_url_for_markdown(kitURL) + ')')
        if nuURL is not None:
            urlComments.append('[NU](' + sanitise_url_for_markdown(nuURL) + ')')
        if malURL:
            urlComments.append('[MAL](' + sanitise_url_for_markdown(malURL) + ')')

        for i, link in enumerate(urlComments):
            if i is not 0:
                comment += '\n'
            comment += link

        comment += ')'


        # ----- END -----#
        receipt = '(LN) Request successful: ' + title + ' - '
        if malURL is not None:
            receipt += 'MAL '
        if ani is not None:
            receipt += 'AL '
        if kit is not None:
            receipt += 'KIT '
        if nuURL is not None:
            receipt += 'MU '
        print(receipt)

        dictToReturn = {}
        dictToReturn['title'] = title
        dictToReturn['comment'] = comment

        return dictToReturn
    except:
        traceback.print_exc()
        return None


def sanitise_url_for_markdown(url):
    return url.replace('(', '\(').replace(')', '\)')


# Builds an anime comment from MAL/HB/Anilist data
def buildVisualNovelComment(isExpanded, vndb):
    try:
        comment = ''

        urls = []
        if vndb['url']:
            urls.append('[VNDB]({0})'.format(vndb['url']))
        if vndb['wikipedia_url']:
            if vndb['wikipedia_url'].endswith(')'):
                formatted_wiki_url = vndb['wikipedia_url'][:-1] + '\)'
            else:
                formatted_wiki_url = vndb['wikipedia_url']
            urls.append('[Wiki]({0})'.format(formatted_wiki_url))

        formatted_links = ''
        for i, link in enumerate(urls):
            if i is not 0:
                formatted_links += '\n'
            formatted_links += link

        if not isExpanded:
            template = '{title} - {links}\n\n({type}{released}{length})'
            formatted = template.format(title=vndb['title'],
                                        links='({})'.format(formatted_links),
                                        type='VN',
                                        released=' | Released: ' + vndb['release_year'] if vndb['release_year'] else '',
                                        length=' | Length: ' + vndb['length'] if vndb['length'] else '')

            comment = formatted
        else:
            template = '{title} - {links}\n\n({type}{released}{length})\n\n{desc}'
            formatted = template.format(title=vndb['title'],
                                        links='({})'.format(formatted_links),
                                        type='VN',
                                        released=' | Released: ' + vndb['release_year'] if vndb[
                                            'release_year'] else '',
                                        length=' | Length: ' + vndb['length'] if vndb['length'] else '',
                                        desc=cleanupDescription(vndb['description']))

            comment = formatted

        # ----- END -----#
        receipt = '(VN) Request successful: ' + vndb['title'] + ' - '
        if vndb:
            receipt += 'VNDB'
        print(receipt)

        # We return the title/comment separately so we can track if multiples of the same comment have been requests (e.g. {Nisekoi}{Nisekoi}{Nisekoi})
        dictToReturn = {}
        dictToReturn['title'] = vndb['title']
        dictToReturn['comment'] = comment

        return dictToReturn
    except:
        traceback.print_exc()
        return None
