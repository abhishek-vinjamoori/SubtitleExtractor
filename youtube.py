import os
import re
import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
from YouTube_XmlToSrt import toSrt


class youtubeExtractor(object):

    """docstring for YouTubeExtractor"""

    def __init__(self, url, testMode):

        print("Detected YouTube\nProcessing....\n")
        self.loginRequired = False
        self.urlName = url
        self.requestsFileName = "iDoNotExistDefinitelyOnThisComputerFolder.html"
        self.languageDict = {
            'sr': 'Serbian', 'th': 'Thai', 'gu': 'Gujarati', 'vi': 'Vietnamese', 'ps': 'Pashto', 'ha': 'Hausa', 'bg': 'Bulgarian', 'la': 'Latin', 'pl': 'Polish', 'ja': 'Japanese', 'km': 'Khmer', 'xh': 'Xhosa', 'ka': 'Georgian', 'gd': 'Scottish+Gaelic', 'hmn': 'Hmong', 'ceb': 'Cebuano', 'bn': 'Bengali', 'el': 'Greek', 'sq': 'Albanian', 'si': 'Sinhala', 'yi': 'Yiddish', 'cy': 'Welsh', 'ig': 'Igbo', 'uz': 'Uzbek', 'lb': 'Luxembourgish', 'su': 'Sundanese', 'hr': 'Croatian', 'ru': 'Russian', 'et': 'Estonian', 'ht': 'Haitian+Creole', 'no': 'Norwegian', 'hi': 'Hindi', 'tg': 'Tajik', 'mi': 'Maori', 'ga': 'Irish', 'ar': 'Arabic', 'haw': 'Hawaiian', 'bs': 'Bosnian', 'id': 'Indonesian', 'so': 'Somali', 'yo': 'Yoruba', 'st': 'Southern+Sotho', 'jv': 'Javanese', 'hu': 'Hungarian', 'pa': 'Punjabi', 'mt': 'Maltese', 'am': 'Amharic', 'fil': 'Filipino', 'uk': 'Ukrainian', 'fy': 'Western+Frisian',
            'ky': 'Kyrgyz', 'my': 'Burmese', 'nl': 'Dutch', 'mk': 'Macedonian', 'da': 'Danish', 'sv': 'Swedish', 'ta': 'Tamil', 'co': 'Corsican', 'af': 'Afrikaans', 'lo': 'Lao', 'lv': 'Latvian', 'hy': 'Armenian', 'iw': 'Hebrew', 'eu': 'Basque', 'kn': 'Kannada', 'mr': 'Marathi', 'sw': 'Swahili', 'ny': 'Nyanja', 'az': 'Azerbaijani', 'es': 'Spanish', 'te': 'Telugu', 'zh': 'Chinese', 'it': 'Italian', 'be': 'Belarusian', 'sl': 'Slovenian', 'cs': 'Czech', 'lt': 'Lithuanian', 'ur': 'Urdu', 'ko': 'Korean', 'de': 'German', 'sd': 'Sindhi', 'fa': 'Persian', 'ms': 'Malay', 'sm': 'Samoan', 'fi': 'Finnish', 'kk': 'Kazakh', 'pt': 'Portuguese', 'ro': 'Romanian', 'tr': 'Turkish', 'en': 'English', 'gl': 'Galician', 'fr': 'French', 'zu': 'Zulu', 'ne': 'Nepali', 'mn': 'Mongolian', 'eo': 'Esperanto', 'sk': 'Slovak', 'ca': 'Catalan', 'ml': 'Malayalam', 'sn': 'Shona', 'ku': 'Kurdish', 'mg': 'Malagasy', 'is': 'Icelandic'}
        self.debug = False
        self.testMode = testMode
        pass

    def getSubtitles(self):
        """
        The main function which uses helper functions to get the subtitles
        """

        self.createSoupObject()

        self.getTitle()
        print("Title - ", self.title)

        rawLink = self.getRawSubtitleLink()
        if self.debug:
            print("Raw Link -", rawLink)
        self.standardCheck(rawLink)

        decodedLink = self.decodeLink(rawLink)
        if self.debug:
            print("Decoded Link -", decodedLink)
        self.standardCheck(decodedLink)

        stringToAppend = self.checkAvailableLanguages()
        self.standardCheck(stringToAppend)

        FinalUrl = self.getFinalUrl(decodedLink, stringToAppend)

        if self.debug:
            print("Final URL -", FinalUrl)
        self.standardCheck(FinalUrl)

        medianCheck = self.downloadXMLTranscript(FinalUrl)

        if medianCheck:
            returnValue = self.convertXMLToSrt()

        else:
            returnValue = 0

        self.deleteUnnecessaryfiles()

        return returnValue

    def createSoupObject(self):

        requestObject = requests.get(self.urlName)

        # fileHandler = open("requests.txt", "w")
        # fileHandler.write(requestObject.text)
        # fileHandler.close()

        self.soupObject = BeautifulSoup(
            requestObject.text, from_encoding="utf8")
        # soupObject1 = BeautifulSoup(requestObject.text,"lxml")
        # print(self.soupObject.original_encoding)

        fh = open(self.requestsFileName, "w")
        fh.write(str(self.soupObject))
        fh.close()

        pass

    def getRawSubtitleLink(self):
        """
        This function returns the Raw Link which is in encoded format.
        Note - This is still an incomplete URL.
        The variable UglyString contains the complete URL.

        """

        rawLink = ""
        self.uglyString = ""

        searchStringList = ["timed", "TTS_URL", "caption_tracks"]
        print()
        fh = open(self.requestsFileName, "r")

        for lines in fh:

            if searchStringList[0] in lines and searchStringList[1] in lines:
                lis = lines.split('"')
                captionPosition = 0
                for i in range(len(lis)):
                    if searchStringList[1] in lis[i]:
                        captionPosition = i + 1
                        break

                rawLink = str(lis[captionPosition])

            elif searchStringList[0] in lines:
                lis = lines.split('"')
                position = 0
                # print(lis)
                for i in range(len(lis)):
                    if searchStringList[2] in lis[i]:
                        position = i + 2
                        break
                if position:
                    self.uglyString = str(lis[position])

        fh.close()

        return rawLink

        pass

    def decodeLink(self, rawLink):
        """
        This function decodes the requested URL
        """

        rawLink = urllib.parse.unquote(rawLink)
        rawLink = rawLink.replace("\\u0026", "&")
        decodedLink = rawLink.replace("\\", "")

        return decodedLink
        pass

    def checkAvailableLanguages(self):
        """
        This function checks for the available subtitle languages and prmopts the user to select the language
        """

        print(
            "<<<------ Choose the corressponding number for selecting the language ----->>>")

        self.uglyString = urllib.parse.unquote(str(self.uglyString))
        self.uglyString = self.uglyString.replace("\\u0026", "&")
        self.uglyString = self.uglyString.replace("\\", "")

    #	print(self.uglyString)
        lang = self.uglyString.split("&")
        availableLangList = []
        for info in lang:
            if info.startswith('lang'):
                availableLangList.append(info)
        if self.debug:
            print(availableLangList)
        for languages in range(len(availableLangList)):

            langKey, equalKey, Language = availableLangList[
                languages].partition("=")
            if self.debug:
                print(Language)
            LanguageKey, hyphenKey, randomVar = Language.partition("-")
            if self.debug:
                print(LanguageKey)
            print("<%d> - " % (languages + 1), end="")

#			[languageDict[k] for k in languageDict.keys() if 'zh' in k]
            if LanguageKey in self.languageDict.keys():
                print(self.languageDict[LanguageKey], end="  ")
            print("(%s)" % (Language))

        optionChoice = input()

        try:
            optionChoice = int(optionChoice)
        except:
            print(
                "You have entered an invalid option. Application will download the first option available.")
            optionChoice = 1

        if self.debug:
            print(availableLangList[optionChoice - 1])

        return availableLangList[optionChoice - 1]

    def getFinalUrl(self, Link, subString):
        """
        This function returns the final URL which contains the transcripts
        """

        Link += "&"
        Link += subString
        return Link

        pass

    def downloadXMLTranscript(self, FinalUrl):
        """
        This function fetches the captions and writes them into a file in XML
        """

        autoGeneratedUrl = "&kind=asr"
        try:
            self.requestObjectv = requests.get(FinalUrl)
            self.requestObjectv.encoding = 'utf-8'
            self.title = self.title.replace("/", "")
            if self.debug:
                print("Creating ~  '%s.xml' ..." % (self.title))
            subsFileHandler = open(self.title + ".xml", "w")

            # It probably could be auto-generated subtitles. Lets try even that here.
            # Auto-generated subtitles need - "&kind=asr" to be appended to the
            # FinalUrl

            if not self.requestObjectv.text:
                FinalUrl += autoGeneratedUrl
                self.requestObjectv = requests.get(FinalUrl)
            # self.requestObjectv = BeautifulSoup(self.requestObjectv.text)
            subsFileHandler.write(str(self.requestObjectv.text))
            subsFileHandler.close()

            return 1

        except:
            return 0
        pass

    def convertXMLToSrt(self):

        try:
            subsFileHandler = open(self.title + ".xml", "r")
            xmlString = subsFileHandler.read()
            subsFileHandler.close()

            srtText = toSrt(xmlString)

            subsFileHandler = open(self.title + ".srt", "w")
            print("Creating ~  '%s.srt' ..." % (self.title))
            subsFileHandler.write(srtText)
            subsFileHandler.close()

            return 1

        except:
            print("Couldn't convert to SRT")
            return 0

        pass

    def getTitle(self):
        """
        This function returns the title of the video. This is also used for naming the file.

        <title>VIDEO NAME - YouTube</title>

        """
        try:
            titleString = self.soupObject.title.string
            self.title = titleString.replace(" - YouTube", "")
            self.title = self.title.strip()
        except:
            self.title = "YouTube_subtitles"
            pass

        pass

    def standardCheck(self, variableToCheck):

        if not variableToCheck:
            print(
                "Unable to fetch the subtitles. Ensure that the video contains subtitles")
            self.deleteUnnecessaryfiles()
            exit()

    def deleteUnnecessaryfiles(self):

        if not self.debug:
            try:
                os.remove(self.requestsFileName)
                os.remove(self.title + ".xml")
            except:
                pass
