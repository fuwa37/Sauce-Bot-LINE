import handlers.nHentaiTagBot.nhentai as nhentai
import handlers.nHentaiTagBot.ehentai as ehentai
import handlers.nHentaiTagBot.tsumino as tsumino
import handlers.nHentaiTagBot.hitomila as hitomila

API_URL_NHENTAI = 'https://nhentai.net/api/gallery/'
API_URL_TSUMINO = 'https://www.tsumino.com/Book/Info/'
API_URL_EHENTAI = "https://api.e-hentai.org/api.php"
LINK_URL_NHENTAI = "https://nhentai.net/g/"
LINK_URL_EHENTAI = "https://e-hentai.org/g/"

TIME_BETWEEN_PM_CHECKS = 60  # in seconds

nhentaiKey = 0
tsuminoKey = 1
ehentaiKey = 2
hitomilaKey = 3
redactedKey = 4


def subListToString(lst):
    string = f'{lst[0]}'
    for i in range(len(lst)):
        if i > 0:
            string += f'+{lst[i]}'
    return string


def addFooter():
    # Needs to use ASCII code to not break reddit formatting &#32; is space
    # &#40; is ( and &#41; is )
    return "[Source](https://github.com/TheVexedGerman/nHentai-Tag-Bot)"


def getNumbers(comment):
    numbersCombi = []
    numbersCombi = keyWordDetection(comment)
    if not numbersCombi:
        nhentaiNumbers = nhentai.getNumbers(comment)
        tsuminoNumbers = tsumino.getNumbers(comment)
        ehentaiNumbers = ehentai.getNumbers(comment)
        hitomilaNumbers = hitomila.getNumbers(comment)
        numbersCombi = [nhentaiNumbers, tsuminoNumbers,
                        ehentaiNumbers, hitomilaNumbers]
    return numbersCombi


def keyWordDetection(comment):
    foundNumbers = []
    if "!tags" in comment.lower():
        foundNumbers = scanForURL(comment)
    return foundNumbers


def scanForURL(comment):
    nhentaiNumbers = []
    tsuminoNumbers = []
    ehentaiNumbers = []
    hitomilaNumbers = []

    nhentaiNumbers = nhentai.scanURL(comment)
    tsuminoNumbers = tsumino.scanURL(comment)
    ehentaiNumbers = ehentai.scanURL(comment)
    hitomilaNumbers = hitomila.scanURL(comment)

    if nhentaiNumbers or tsuminoNumbers or ehentaiNumbers or hitomilaNumbers:
        print("true return")
        return [nhentaiNumbers, tsuminoNumbers,
                ehentaiNumbers, hitomilaNumbers]
    return []


def processComment(comment):
    replyString = ""
    logString = ""
    useError = True
    useLink = True
    censorshipLevel = 0
    numbersCombi = getNumbers(comment)
    # TODO make this more efficient
    combination = []
    i = 0
    if numbersCombi:
        for entry in numbersCombi:
            for subentry in entry:
                combination.append([subentry, i])
            i += 1
    if combination:
        if len(combination) > 5:
            replyString += "This bot does a maximum of 5 numbers at a time, your list has been shortened:\n\n"
            logString += "This bot does a maximum of 5 numbers at a time, your list has been shortened:\n\n"
        combination = combination[:5]
        for entry in combination:
            if replyString:
                replyString += "&#x200B;\n\n"
                logString += "&#x200B;\n\n"
            number = entry[0]
            key = entry[1]
            if key == nhentaiKey:
                processedData = nhentai.analyseNumber(number)
                replyString += nhentai.generateReplyString(
                    processedData, number, censorshipLevel, useError, useLink)
                logString += nhentai.generateReplyString(processedData, number)
            elif key == tsuminoKey:
                processedData = tsumino.analyseNumber(number)
                replyString += tsumino.generateReplyString(
                    processedData, number, censorshipLevel, useError, useLink)
                logString += tsumino.generateReplyString(processedData, number)
            elif key == ehentaiKey:
                processedData = ehentai.analyseNumber(number)
                replyString += ehentai.generateReplyString(
                    processedData, number, censorshipLevel, useError, useLink)
                logString += ehentai.generateReplyString(processedData, number)
            elif key == hitomilaKey:
                processedData = hitomila.analyseNumber(number)
                replyString += hitomila.generateReplyString(
                    processedData, number, censorshipLevel, useError, useLink)
                logString += hitomila.generateReplyString(
                    processedData, number)
    if replyString:
        # replyString += addFooter()
        return replyString
    else:
        return "NO SAUCE"

def generateLinkString(numbersCombi):
    # generate the string that will be replied
    linkString = ""
    if numbersCombi:
        if numbersCombi[nhentaiKey]:
            numbers = numbersCombi[nhentaiKey]
            for number in numbers:
                linkString += generateLinks(number, nhentaiKey) + "\n\n"
        if numbersCombi[tsuminoKey]:
            numbers = numbersCombi[tsuminoKey]
            for number in numbers:
                linkString += generateLinks(number, tsuminoKey) + "\n\n"
        if numbersCombi[ehentaiKey]:
            numbers = numbersCombi[ehentaiKey]
            for number in numbers:
                linkString += generateLinks(number, ehentaiKey) + "\n\n"
        if numbersCombi[hitomilaKey]:
            numbers = numbersCombi[hitomilaKey]
            for number in numbers:
                linkString += generateLinks(number, hitomilaKey) + "\n\n"
        if numbersCombi[redactedKey]:
            numbers = numbersCombi[redactedKey]
            for number in numbers:
                linkString += "This number has been redacted and therefore no link can be generated. \n\n"
    return linkString


def generateLinks(number, key):
    # make the link
    linkString = ""
    if key == nhentaiKey:
        linkString = LINK_URL_NHENTAI + str(number)
    elif key == tsuminoKey:
        # Since Tsumino is just being HTML parsed the API URL is fine
        linkString = API_URL_TSUMINO + str(number)
    elif key == ehentaiKey:
        linkString = LINK_URL_EHENTAI + str(number[0]) + "/" + number[1]
    elif key == hitomilaKey:
        linkString = hitomila.API_URL_HITOMILA + str(number) + ".html"
    return linkString

print(processComment('(177013)'))