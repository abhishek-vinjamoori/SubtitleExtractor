import os
import requests
from bs4 import BeautifulSoup
import json


class crackleExtractor(object):

    """docstring for CrackleExtractor"""

    def __init__(self, url, testMode):
        print("Crackle processing")
        self.loginRequired = False
        self.urlName = url
        self.requestsFileName = "iDoNotExistDefinitelyOnThisComputerFolder.html"
        self.debug = True
        self.testMode = testMode
        self.MediaBase = "https://web-api-us.crackle.com/Service.svc/details/media/"
        self.mediaStream = "/US?format=json"
        self.title = None
        self.SubtitleUrl = None
        self.soupObject = None
        self.requestObjectv = None

    def getSubtitles(self):
        """
        The main function which uses helper functions to get the subtitles
        """

        self.createSoupObject()

        episodeID = self.getEpisodeID()
        if self.debug:
            print("Episode ID - ", episodeID)

        MediaUrl = self.getMediaURL(episodeID)
        if self.debug:
            print("Media URL ", MediaUrl)

        self.title = "CrackleCaptions"
        self.SubtitleUrl = self.getSubtitleURL(MediaUrl)
        if self.debug:
            print("Subtitle URL - ", self.SubtitleUrl)

        returnValue = self.downloadXMLTranscript()

        return returnValue

    def createSoupObject(self):

        requestObject = requests.get(self.urlName)

        self.soupObject = BeautifulSoup(
            requestObject.text, "lxml", from_encoding="utf8")

        fh = open(self.requestsFileName, "w")
        fh.write(str(self.soupObject))
        fh.close()

    def getEpisodeID(self):
        """
        This function returns the Episode ID from the URL given.
        http://www.crackle.com/franklin-and-bash/2498587
        2498587 - EpisodeID
        """

        searchStringList = ["/"]

        juknkData, Slash, episodeID = self.urlName.rpartition(
            searchStringList[0])

        return episodeID

    def getMediaURL(self, episodeID):
        """
        This function makes the URL which contains the required PID
        """
        MediaUrl = self.MediaBase

        MediaUrl += episodeID
        MediaUrl += self.mediaStream

        return MediaUrl

    def getSubtitleURL(self, MediaUrl):
        """
        The json content looks like this -

        {"ClosedCaptionFiles":[{"Locale":"en-US","Path":"http:\/\/web-us-az.crackle.com\/1\/n\/wl\/t68wb_en-US_150506152834.xml","Default":false}]}
        """
        # If it is a movie, we use this methodology -
        try:
            IndexingParameters = ["ClosedCaptionFiles", 0, "Path"]

            subRequestObject = requests.get(MediaUrl)

            parsedJsonObject = json.loads(str(subRequestObject.text))
            SubsURL = parsedJsonObject[IndexingParameters[0]][
                IndexingParameters[1]][IndexingParameters[2]]

            return SubsURL

        except:
            pass

    def downloadXMLTranscript(self):
        """
        This function fetches the captions and writes them into a file in XML
        """

        try:
            self.requestObjectv = requests.get(self.SubtitleUrl)

            print("Creating ~  '%s.xml' ..." % (self.title))
            subsFileHandler = open(self.title + ".xml", "w")

            if not self.requestObjectv.text:
                return 0

            self.requestObjectv = BeautifulSoup(self.requestObjectv.text, "lxml", from_encoding="utf8")
            subsFileHandler.write(str(self.requestObjectv.prettify()))
            subsFileHandler.close()

            return 1

        except:
            return 0

    def getTitle(self):
        """
        This function returns the title of the video. This is also used for naming the file.

        <display_title>
        <title>NAME</title>
        <subtitle>OPTIONAL SUBTITLE</subtitle>
        </display_title>

        """
        try:
            titleString = self.soup.programme.display_title.title.string
            try:
                titleString += self.soup.programme.display_title.subtitle.string
            except:
                pass
            titleString = titleString.strip()
            self.title = titleString.replace("/", "")

        except:
            self.title = "BBC_subtitles"
            pass

    def deleteUnnecessaryfiles(self):

        if not self.debug:
            try:
                os.remove(self.requestsFileName)
            except:
                pass
