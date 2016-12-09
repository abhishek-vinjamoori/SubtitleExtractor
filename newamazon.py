import os
import re
import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import json
from configparser import SafeConfigParser
from selenium import webdriver
from Amazon_XmlToSrt import toSrt


class amazonExtractor(object):

    """docstring for amazonExtractor"""

    def __init__(self, url, testMode):

        print("Detected Amazon\nProcessing....\n")
        self.loginRequired = False
        self.urlName = url
        self.debug = True
        self.testMode = testMode
        self.requestsFileName = "iDoNotExistDefinitelyOnThisComputerFolder.html"
        self.videoType = ""

        # Parameters requireed for Obtaining the URL
        self.parametersDict = {
            "PreURL": "https://atv-ps.amazon.com/cdp/catalog/GetPlaybackResources?",
                "asin": "",
                "consumptionType": "Streaming",
                "desiredResources": "AudioVideoUrls,CatalogMetadata,SubtitlePresets,SubtitleUrls",
                "deviceID": "b63345bc3fccf7275dcad0cf7f683a8f",
                "deviceTypeID": "AOAGZA014O5RE",
                "firmware": "1",
                "marketplaceID": "ATVPDKIKX0DER",
                "resourceUsage": "ImmediateConsumption",
                "videoMaterialType": "Feature",
                "operatingSystemName": "Linux",
                "customerID": "",
                "token": "",
                "deviceDrmOverride": "CENC",
                "deviceStreamingTechnologyOverride": "DASH",
                "deviceProtocolOverride": "Https",
                "deviceBitrateAdaptationsOverride": "CVBR,CBR",
                "titleDecorationScheme": "primary-content"
        }
        pass

    def getSubtitles(self):
        """
        The main function which uses helper functions to get the subtitles
        """

        self.createSoupObject()
        self.getcustomerID()
        self.getToken()
        self.getTitle()

        if self.debug:
            print(self.title)

        self.getVideoType()
        if self.debug:
            print(self.videoType)

        if self.videoType == "movie":

            self.getAsinID1()  # Method-1
            if self.debug:
                print(self.parametersDict['asin'])

            returnValue = self.standardFunctionCalls()
            if returnValue != 1:
                self.videoType = "tv"

        if self.videoType != "movie":

            self.getAsinID2()
            if self.debug:
                print(self.asinList)

            self.parametersDict['asin'] = self.asinList
            currentTitle = self.title

            try:
                returnValue = self.standardFunctionCalls()
            except:
                pass
            self.title = currentTitle

        return returnValue

    def createSoupObject(self):

        # This is to tackle the Request Throttle error which occurs on Amazon
        # frequently.
        numberOfTrials = 20
        errorNames = ["Error", "Robot"]

        successful = False

        while numberOfTrials:

            requestObject = requests.get(self.urlName)
            # fileHandler = open("requests.txt", "w")
            # fileHandler.write(requestObject.text)
            # fileHandler.close()

            self.soupObject = BeautifulSoup(
                requestObject.text, "lxml", from_encoding="utf8")
            # soupObject1 = BeautifulSoup(requestObject.text,"lxml")
            # print(self.soupObject.original_encoding)
            titleString = str(self.soupObject.title.string)

            if self.debug:
                print("Status Code", requestObject.status_code)

            fh = open(self.requestsFileName, "w")
            fh.write(str(self.soupObject))
            fh.close()

            fail = 0

            if requestObject.status_code >= 400:
                print("Request Throttle Error\n Trying Again....")
                numberOfTrials -= 1
                fail = 1
                continue

            # if fail:
            # 	continue

            print("Request successful")
            successful = True
            numberOfTrials = 0

            fh = open(self.requestsFileName, "w")
            fh.write(str(self.soupObject))
            fh.close()

        pass

    def getcustomerID(self):

        parser = SafeConfigParser()
        parser.read('config.ini')
        self.parametersDict['customerID'] = parser.get('AMAZON', 'customerid')
        pass

    def getToken(self):

        parser = SafeConfigParser()
        parser.read('config.ini')
        self.parametersDict['token'] = parser.get('AMAZON', 'token')
        pass

    def getVideoType(self):
        """

        <script data-a-state='{"key":"dv-dp-state"}' type="a-state">{"pageType":"tv","pageAsin":null}</script>

        """
        parsingParams = {"tagname": "script", "tagAttrs": [
            "type", "a-state"], "jsonparam": "pagetype"}

        try:
            scriptTags = self.soupObject.findAll(parsingParams['tagname'], attrs={
                                                 parsingParams['tagAttrs'][0]: parsingParams['tagAttrs'][1]})
            for allTags in scriptTags:
                try:
                    jsonString = allTags.string.lower()
                    jsonparser = json.loads(jsonString)
                    self.videoType = jsonparser[parsingParams['jsonparam']]
                    break
                except:
                    continue
            # print(s)

        except:
            pass

        # Unable to get the type. Using movie as the default case.

        if self.videoType == "":
            self.videoType = "movie"

        pass

    def getAsinID1(self):
        """
        This is one of the methodologies to get the asin ID.
        If it is a movie, we use this methodology.
        Obtaining the asin from here -

        <input name="asin" type="hidden" value="B000I9WVAK"/>
        The value contains the asin.

        """

        try:
            asinObject = self.soupObject.find(
                "input", attrs={"name": re.compile("^asin$", re.I)})
            self.parametersDict['asin'] = str(asinObject['value'])
            # print(s)

        except:
            pass

    def getAsinID2(self):
        """
        This is one of the methodologies to get the asin ID.
        If it is a TV Series, we use this methodology.
        Obtaining the asin from here -

        <div class="a-section dv-episode-container aok-clearfix" data-aliases="B000I9WVAK" id="dv-el-id-2">
        The value contains the asin.

        """

        # self.loginAmazon()

        try:
            # https://www.amazon.com/dp/B0157MP078/?autoplay=1
            # https://www.amazon.com/dp/B017UGX5M6?autoplay=1&t=24
            a, b, idContainer = self.urlName.partition("dp/")
            asinID, x, y = idContainer.partition("/")
            asinID, x, y = asinID.partition("?")
            self.asinList = asinID

            # There maybe multiple ASIN's present which are separated by comma.
            # So we just take one of it.

            # for i in range(len(self.asinList)):
            # 	tempList = self.asinList[i].split(",")
            # 	for ids in tempList:
            # 		if ids != "":
            # 			self.asinList[i] = ids
            # 			break

        except:
            pass

    def getSubtitlesContainer(self):
        """
        This function returns the final URL which contains the link to the Subtitles file.

        """
        self.subtitleURLContainer = ""

        self.subtitleURLContainer += self.parametersDict['PreURL']

        for parameters in self.parametersDict:
            if parameters != "PreURL":
                self.subtitleURLContainer += "&"
                self.subtitleURLContainer += parameters
                self.subtitleURLContainer += "="
                self.subtitleURLContainer += self.parametersDict[parameters]
        pass

    def getSubtitleURL(self):
        """
        The json content looks like this -

        {"returnedTitleRendition":{""},"subtitleUrls":[{"url":"linkforsubtitle.dfxp"}]}

        """

        # If it is a movie, we use this methodology -
        try:
            IndexingParameters = ["subtitleUrls", 0, "url"]
            TitleParamters = [
                "catalogMetadata", "catalog", "title", "episodeNumber"]
            subRequestObject = requests.get(self.subtitleURLContainer)

            parsedJsonObject = json.loads(str(subRequestObject.text))
            SubsURL = parsedJsonObject[IndexingParameters[0]][
                IndexingParameters[1]][IndexingParameters[2]]
            if self.title == "Amazonsubtitles":
                try:
                    self.title = parsedJsonObject[TitleParamters[0]][TitleParamters[1]][TitleParamters[2]] + "_" + str(
                        parsedJsonObject[TitleParamters[0]][TitleParamters[1]][TitleParamters[3]])
                except:
                    pass

            return SubsURL

        except:
            pass
        pass

    def downloadDfxpTranscript(self, SubsLink):
        """
        This function fetches the captions and writes them into a file in VTT format
        """
        try:
            subRequestObject = requests.get(SubsLink)
            # print(subRequestObject.text)
            subRequestObject.encoding = 'utf-8'

            subsFileHandler = open(self.title + ".dfxp", "w")
            print("Creating ~  '%s.dfxp' ..." % (self.title))
            subsFileHandler.write(subRequestObject.text)
            subsFileHandler.close()
            return 1

        except:
            return 0

        pass

    def convertDfxpToSrt(self):

        try:
            subsFileHandler = open(self.title + ".dfxp", "r")
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

        <meta name="twitter:title" content=" Watch Defiance Season 1 Episode  - Amazon Video"/>   --> Extracting the value from here
        
        OR
        
        <meta property="og:title" content="Watch Defiance Season 1 Episode  - Amazon Video"/>  --> Extracting the value from here

        """

        # print(self.soupObject.title.string)
        try:
            s = self.soupObject.find("meta", attrs={"name": "twitter:title"})
            self.title = str(s['content'])
            self.title = self.title.replace("/", "")
            self.title = self.title[6:]     #slicing "Watch "
            self.title = self.title[:-16]   #slicing "  - Amazon Video"
            self.title = self.title.strip()
            if not self.title:
                s = int("deliberateError")

        # except
        except:
            
            try:
            s = self.soupObject.find("meta", attrs={"property": "og:title"})
            self.title = str(s['content'])
            self.title = self.title.replace("/", "")
            self.title = self.title[6:]     #slicing "Watch "
            self.title = self.title[:-16]   #slicing "  - Amazon Video"
            self.title = self.title.strip()
            if not self.title:
                s = int("deliberateError")
                
            except:
                self.title = "Amazonsubtitles"

        pass

    def deleteUnnecessaryfiles(self):

        if not self.debug:
            try:
                os.remove(self.requestsFileName)
            except:
                pass

    def standardFunctionCalls(self):

        self.getSubtitlesContainer()
        if self.debug:
            print(self.subtitleURLContainer)

        SubtitlesURL = self.getSubtitleURL()
        if self.debug:
            print(SubtitlesURL)

        if not SubtitlesURL:
            print("Unable to fetch the subtitles. No subtitles present.")
            self.deleteUnnecessaryfiles()
            return 0

        medianCheck = self.downloadDfxpTranscript(SubtitlesURL)

        if medianCheck:
            returnValue = self.convertDfxpToSrt()

        else:
            returnValue = 0

        self.deleteUnnecessaryfiles()

        return returnValue
        pass
