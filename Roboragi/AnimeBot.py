'''
AnimeBot.py
Acts as the "main" file and ties all the other functionality together.
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

import re
import traceback

import Roboragi.Search as Search
from Roboragi.patterns import find_requests


def process_comment(comment, is_edit=True, is_expanded=False):
    """ process dat comment """
    # Anime/Manga requests that are found go into separate arrays
    animeArray = []
    mangaArray = []
    lnArray = []
    vnArray = []

    # ignores all "code" markup (i.e. anything between backticks)
    comment = re.sub(r"\`[{<\[]+(.*?)[}>\]]+\`", "", comment)

    num_so_far = 0

    numOfRequest = 0
    numOfExpandedRequest = 0

    # The basic algorithm here is:
    # If it's an expanded request, build a reply using the data in the
    # braces, clear the arrays, add the reply to the relevant array and
    # ignore everything else. If it's a normal request, build a reply using
    # the data in the braces, add the reply to the relevant array.

    # Counts the number of expanded results vs total results. If it's not
    # just a single expanded result, they all get turned into normal
    # requests.

    forceNormal = False

    for match in find_requests('all', comment, expanded=True):
        numOfRequest += 1
        numOfExpandedRequest += 1

    for match in find_requests('all', comment):
        numOfRequest += 1

    if (numOfExpandedRequest >= 1) and (numOfRequest > 1):
        forceNormal = True

    # Determine whether we'll build an expanded reply just once.

    isExpanded = False if forceNormal else is_expanded

    # The final comment reply. We add stuff to this progressively.
    commentReply = ''

    # Anime
    for match in find_requests('anime', comment):
        if num_so_far < 30:
            reply = Search.buildAnimeReply(match, isExpanded)

            if (reply is not None):
                num_so_far = num_so_far + 1
                animeArray.append(reply)

    # Manga
    for match in find_requests('manga', comment):
        if num_so_far < 30:
            reply = Search.buildMangaReply(match, is_expanded)

            if (reply is not None):
                num_so_far = num_so_far + 1
                mangaArray.append(reply)

    # LN
    for match in find_requests('light_novel', comment):
        if num_so_far < 30:
            reply = Search.buildLightNovelReply(match, is_expanded)

            if (reply is not None):
                num_so_far = num_so_far + 1
                lnArray.append(reply)

    # Normal VN
    for match in find_requests('visual_novel', comment):
        if num_so_far < 30:
            reply = Search.buildVisualNovelReply(match, is_expanded)

            if (reply is not None):
                num_so_far = num_so_far + 1
                vnArray.append(reply)

    # Here is where we create the final reply to be posted

    # Basically just to keep track of people posting the same title
    # multiple times (e.g. {Nisekoi}{Nisekoi}{Nisekoi})
    postedAnimeTitles = []
    postedMangaTitles = []
    postedLNTitles = []
    postedVNTitles = []

    # Adding all the anime to the final comment. If there's manga too we
    # split up all the paragraphs and indent them in Reddit markup by
    # adding a '>', then recombine them
    for i, animeReply in enumerate(animeArray):
        if not (i is 0):
            commentReply += '\n\n'

        if not (animeReply['title'] in postedAnimeTitles):
            postedAnimeTitles.append(animeReply['title'])
            commentReply += animeReply['comment']

    # Adding all the manga to the final comment
    for i, mangaReply in enumerate(mangaArray):
        if not (i is 0):
            commentReply += '\n\n'

        if not (mangaReply['title'] in postedMangaTitles):
            postedMangaTitles.append(mangaReply['title'])
            commentReply += mangaReply['comment']

    # Adding all the light novels to the final comment
    for i, lnReply in enumerate(lnArray):
        if not (i is 0):
            commentReply += '\n\n'

        if not (lnReply['title'] in postedLNTitles):
            postedLNTitles.append(lnReply['title'])
            commentReply += lnReply['comment']

    # Adding all the visual novels to the final comment
    for i, vnReply in enumerate(vnArray):
        if not (i is 0):
            commentReply += '\n\n'

        if not (vnReply['title'] in postedVNTitles):
            postedVNTitles.append(vnReply['title'])
            commentReply += vnReply['comment']

    # If there are more than 10 requests, shorten them all
    lenRequests = sum(map(len, (animeArray, mangaArray, lnArray, vnArray)))
    if not (commentReply is '') and (lenRequests >= 10):
        commentReply = re.sub(r"\^\((.*?)\)", "", commentReply, flags=re.M)

    # If there was actually something found, add the signature and post the
    # comment to Reddit. Then, add the comment to the "already seen" database.
    if commentReply is not '':

        if num_so_far >= 30:
            commentReply += ("\n\nI'm limited to 30 requests at once and have "
                             "had to cut off some, sorry for the "
                             "inconvenience!\n\n")

        total_expected = int(numOfRequest)
        total_found = sum(map(len, (animeArray, mangaArray, lnArray, vnArray)))

        if total_found != total_expected:
            commentReply += '&#32;|&#32;({0}/{1})'.format(total_found,
                                                          total_expected)

        if is_edit:
            return commentReply
    else:
        try:
            if is_edit:
                return None
        except Exception as e:
            traceback.print_exc()
            print(e)
