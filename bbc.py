import os
import re
import requests
from bs4 import BeautifulSoup
from configparser import SafeConfigParser
from BBC_XmlToSrt import toSrt


class bbcExtractor(object):

    """docstring for bbcExtractor"""

    def __init__(self, url, testMode):
        print("BBC processing")
        self.loginRequired = False
        self.urlName = url
        self.requestsFileName = "iDoNotExistDefinitelyOnThisComputerFolder.html"
        self.debug = True
        self.testMode = testMode

        pass

    def getSubtitles(self):
        """
        The main function which uses helper functions to get the subtitles
        """

        self.createSoupObject()

        episodeID = self.getEpisodeID()
        if self.debug:
            print("Episode ID - ", episodeID)

        PIDLink = self.getPIDurl(episodeID)
        if self.debug:
            print("PIDLINK", PIDLink)

        availablePIDs = self.getPID(PIDLink)
        if self.debug:
            print("Available PIDs ", availablePIDs)

        self.getTitle()
        if self.debug:
            print("Title - ", self.title)

        self.getSubtitleURL(availablePIDs)
        if self.debug:
            print("Subtitle URL - ", self.SubtitleUrl)

        medianCheck = self.downloadXMLTranscript()

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

    def getEpisodeID(self):
        """
        This function returns the Episode ID from the URL given.
        """

        searchStringList = ["episode/"]
        juknkData, episodeName, IDContainer = self.urlName.partition(
            searchStringList[0])
        episodeID, Slash, Junk = IDContainer.partition("/")
        return episodeID

        pass

    def getPIDurl(self, episodeID):
        """
        This function makes the URL which contains the required PID
        """

        parser = SafeConfigParser()
        parser.read('config.ini')
        programmeUrl = parser.get('BBC', 'programmeurl')

        programmeUrl += episodeID
        programmeUrl += ".xml"

        return programmeUrl

        pass

    def getSubtitleURL(self, availablePIDs):
        """
        This function fetches the subtitl URL based on the PIDs
        """

        self.SubtitleUrl = ""
        parser = SafeConfigParser()
        parser.read('config.ini')

        for pid in availablePIDs:

            MediaUrl = parser.get('BBC', 'mediastream')
            MediaUrl += pid

            if self.debug:
                print(MediaUrl)

            try:
                requestObject = requests.get(MediaUrl)
                soup = BeautifulSoup(
                    requestObject.text, "lxml", from_encoding="utf8")
                temp = soup.find("media", attrs={"kind": "captions"})
                self.SubtitleUrl = temp.connection['href']
                break

            except:
                pass

        pass

    def getPID(self, Link):
        """
        This function returns the PID of the episode.
        """
        requestObject = requests.get(Link)

        # fileHandler = open("requests.txt", "w")
        # fileHandler.write(requestObject.text)
        # fileHandler.close()
        pidList = []
        self.soup = BeautifulSoup(
            requestObject.text, "lxml", from_encoding="utf8")
        try:
            versionList = self.soup.programme.versions.findAll("version")
        except:
            print("Unable to get requested page.")
            return []

        for versions in versionList:
            pidList.append(versions.pid.string)

        return pidList

        pass

    def downloadXMLTranscript(self):
        """
        This function fetches the captions and writes them into a file in XML
        """

        try:
            self.requestObjectv = requests.get(self.SubtitleUrl)
            self.requestObjectv.encoding = 'utf-8'
            print("Creating ~  '%s.xml' ..." % (self.title))
            subsFileHandler = open(self.title + ".xml", "w")

            if not self.requestObjectv.text:
                return 0

            self.requestObjectv = BeautifulSoup(self.requestObjectv.text)
            subsFileHandler.write(str(self.requestObjectv))
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

        pass

    def deleteUnnecessaryfiles(self):

        if not self.debug:
            try:
                os.remove(self.requestsFileName)
            except:
                pass
