'''
Search.py
Returns a built comment created from multiple databases when given a search
term.
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

import traceback

import handlers.Roboragi.Anilist as Anilist
import handlers.Roboragi.CommentBuilder as CommentBuilder
import handlers.Roboragi.Kitsu as Kitsu
import handlers.Roboragi.LNDB as LNDB
import handlers.Roboragi.NU as NU
from handlers.Roboragi.VNDB import VNDB


def buildMangaReply(searchText, isExpanded):
    """ Builds a manga reply from multiple sources """
    try:
        ani = {'search_function': Anilist.getMangaDetails,
               'title_function': Anilist.getTitles,
               'synonym_function': Anilist.getSynonyms,
               'checked_synonyms': [],
               'result': None}
        kit = {'search_function': Kitsu.search_manga,
               'synonym_function': Kitsu.get_synonyms,
               'title_function': Kitsu.get_titles,
               'checked_synonyms': [],
               'result': None}

        data_sources = [ani, kit]

        synonyms = set([searchText])
        titles = set()

        for x in range(len(data_sources)):
            for source in data_sources:
                if source['result']:
                    break
                else:
                    for title in titles:
                        if title in source['checked_synonyms']:
                            break

                        if source['result']:
                            break

                        source['result'] = source['search_function'](title)
                        source['checked_synonyms'].append(title)

                        if source['result']:
                            break

                    for synonym in synonyms:
                        if synonym in source['checked_synonyms']:
                            break

                        if source['result']:
                            break

                        search_function = source['search_function']
                        source['result'] = search_function(synonym)
                        source['checked_synonyms'].append(synonym)

                        if source['result']:
                            break

                if source['result']:
                    result = source['result']
                    synonym_function = source['synonym_function']
                    title_function = source['title_function']
                    synonyms.update(
                        [s.lower() for s in synonym_function(result)]
                    )
                    for t in title_function(result):
                        if t is not None:
                            titles.update(t.lower())

        if ani['result'] or kit['result']:
            return CommentBuilder.buildMangaComment(
                isExpanded=isExpanded,
                ani=ani['result'],
                kit=kit['result']
            )
        else:
            print('No result found for ' + searchText)
            return None

    except Exception:
        traceback.print_exc()
        return None


def buildAnimeReply(searchText, isExpanded, trace):
    """ Builds an anime reply from multiple sources """
    try:
        kit = {'search_function': Kitsu.search_anime,
               'synonym_function': Kitsu.get_synonyms,
               'title_function': Kitsu.get_titles,
               'checked_synonyms': [],
               'result': None}
        ani = {'search_function': Anilist.getAnimeDetails,
               'synonym_function': Anilist.getSynonyms,
               'title_function': Anilist.getTitles,
               'checked_synonyms': [],
               'result': None}

        data_sources = [ani, kit]

        synonyms = set([searchText])
        titles = set()

        for x in range(len(data_sources)):
            for source in data_sources:
                if source['result']:
                    break
                else:
                    for synonym in synonyms:
                        if synonym in source['checked_synonyms']:
                            continue

                        search_function = source['search_function']
                        source['result'] = search_function(synonym)
                        source['checked_synonyms'].append(synonym)

                        if source['result']:
                            break

                if source['result']:
                    result = source['result']
                    synonym_function = source['synonym_function']
                    title_function = source['title_function']
                    synonyms.update(
                        [s.lower() for s in synonym_function(result)]
                    )
                    for t in title_function(result):
                        if t is not None:
                            titles.update(t.lower())

        if ani['result'] or kit['result']:
            return CommentBuilder.buildAnimeComment(
                isExpanded=isExpanded,
                ani=ani['result'],
                kit=kit['result'],
                trace=trace
            )
        else:
            print('No result found for ' + searchText)
            return None

    except Exception:
        traceback.print_exc()
        return None


def buildLightNovelReply(searchText, isExpanded):
    """ Builds an LN reply from multiple sources """
    try:
        ani = {'search_function': Anilist.getLightNovelDetails,
               'synonym_function': Anilist.getSynonyms,
               'title_function': Anilist.getTitles,
               'checked_synonyms': [],
               'result': None}
        kit = {'search_function': Kitsu.search_light_novel,
               'synonym_function': Kitsu.get_synonyms,
               'title_function': Kitsu.get_titles,
               'checked_synonyms': [],
               'result': None}
        nu = {'search_function': NU.getLightNovelURL,
              'result': None}

        data_sources = [ani, kit]
        aux_sources = [nu]

        synonyms = set([searchText])
        titles = set()

        for x in range(len(data_sources)):
            for source in data_sources:
                if source['result']:
                    break
                else:
                    for synonym in synonyms:
                        if synonym in source['checked_synonyms']:
                            continue

                        search_function = source['search_function']
                        source['result'] = search_function(synonym)
                        source['checked_synonyms'].append(synonym)

                        if source['result']:
                            break

                if source['result']:
                    result = source['result']
                    synonym_function = source['synonym_function']
                    title_function = source['title_function']
                    synonyms.update(
                        [s.lower() for s in synonym_function(result)]
                    )
                    for t in title_function(result):
                        if t is not None:
                            titles.update(t.lower())

        for source in aux_sources:
            source['result'] = source['search_function'](synonym)

            if source['result']:
                break

            if not source['result']:
                for synonym in synonyms:
                    source['result'] = source['search_function'](synonym)

                    if source['result']:
                        break

        if ani['result'] or kit['result']:
            return CommentBuilder.buildLightNovelComment(
                isExpanded=isExpanded,
                ani=ani['result'],
                nu=nu['result'],
                kit=kit['result']
            )
        else:
            print('No result found for ' + searchText)
            return None

    except Exception:
        traceback.print_exc()
        return None


def buildVisualNovelReply(searchText, isExpanded):
    """ Builds an VN reply from VNDB """
    try:
        vndb = VNDB()

        result = vndb.getVisualNovelDetails(searchText)

        vndb.close()

        if result:
            return CommentBuilder.buildVisualNovelComment(isExpanded, result)
        else:
            print('No result found for ' + searchText)
            return None

    except Exception:
        traceback.print_exc()
        return None
