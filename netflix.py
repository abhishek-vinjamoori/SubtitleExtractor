import os
import re
import requests
from bs4 import BeautifulSoup
import json
from configparser import ConfigParser
from selenium import webdriver
import time
import codecs
import math
import Netflix_XmlToSrt


class netflixExtractor(object):

    """docstring for netflixExtractor"""

    def __init__(self, url, testMode):

        print("Detected Netflix\nProcessing....\n")
        self.loginRequired = False
        self.urlName = url
        self.debug = True
        self.testMode = testMode
        self.requestsFileName = "iDoNotExistDefinitelyOnThisComputerFolder.html"

        # Parameters requireed for Obtaining the URL
        pass

    def getSubtitles(self):
        """
        The main function which uses helper functions to get the subtitles
        """

        # self.createSoupObject()

        check = self.loginNetflix()
        self.title = "NetflixCaptions"
        # self.getTitle()
        # if self.debug:
        # 	print(self.title)
        if self.debug:
            print("Resource List -\n", self.resourceList)

        if not check:
            self.deleteUnnecessaryfiles()
            return 0

        returnValue = self.standardFunctionCalls()
        return returnValue

    def createSoupObject(self, source):

        # requestObject = requests.get(self.urlName)

        # fileHandler = open("requests.txt", "w")
        # fileHandler.write(requestObject.text)
        # fileHandler.close()

        self.soupObject = BeautifulSoup(source, "lxml", from_encoding="utf8")
        # soupObject1 = BeautifulSoup(requestObject.text,"lxml")
        # print(self.soupObject.original_encoding)

        fh = open(self.requestsFileName, "w")
        fh.write(str(self.soupObject))
        fh.close()

        pass

    def getSubtitleURL(self):
        """
        The json content looks like this -

        https://ipv4_1-lagg0-c018.1.sea001.ix.nflxvideo.net/?o=AQFtvJqRtkpGGH0jaYbAeHDGEm3tLGTZN8tCWrNrzICT9fS14rFqdUC3QcK4ubNZ9F3wIYkfEFWsRfSUnJjwk5xe1gzkZvg52clcbA_tI5ZRZRKeT8tIMgImep2skGqb8C8laZdAkTrGFDFSIJKP&v=3&e=1467941170&t=nKoR2V91TssNcDr5AGDUUPJ_AmA

        """

        # If it is a movie, we use this methodology -
        try:
            SubsURL = ""

            for names in self.resourceList:
                if 'name' in names.keys():
                    if "/?o" in names['name']:
                        SubsURL = names['name']

            return SubsURL

        except:
            print(
                "Failed to fetch subtitles resource. Please ensure that subtitles are switched on by default for your account")
            pass

        pass

    def downloadDfxpTranscript(self, SubsLink):
        """
        This function fetches the captions and writes them into a file in VTT format
        """
        try:
            subRequestObject = requests.get(SubsLink)
            # print(subRequestObject.text)

            subsFileHandler = open(self.title + ".xml", "w")
            print("Creating ~  '%s.xml' ..." % (self.title))
            subsFileHandler.write(subRequestObject.text)
            subsFileHandler.close()
            return 1

        except:
            return 0

        pass

    def getTitle(self):
        """
        This function returns the title of the video. This is also used for naming the file.

        <meta name="twitter:title" content="Interstellar"/>   --> Extracting the value from here

        """

        # print(self.soupObject.title.string)
        try:
            s = self.soupObject.find("meta", attrs={"name": "twitter:title"})
            self.title = str(s['content'])
            self.title = self.title.strip()
            if not self.title:
                s = int("deliberateError")

        except:
            self.title = "Netflixsubtitles"

        pass

    def deleteUnnecessaryfiles(self):

        if not self.debug:
            try:
                os.remove(self.requestsFileName)
                os.remove(self.title + ".xml")
            except:
                pass

    def standardFunctionCalls(self):

        SubtitlesURL = self.getSubtitleURL()
        if self.debug:
            print("Subtitle URL - ", SubtitlesURL)

        self.standardCheck(SubtitlesURL)

        returnValue = self.downloadDfxpTranscript(SubtitlesURL)

        self.standardCheck(returnValue)

        self.convertXMLToSrt()

        self.deleteUnnecessaryfiles()

        return returnValue
        pass

    def standardCheck(self, variableToCheck):

        if not variableToCheck:
            print("Unable to fetch the subtitles.")
            self.deleteUnnecessaryfiles()
            exit()

    def loginNetflix(self):

        # Initialising the parser
        userParser = ConfigParser()
        userParser.read('userconfig.ini')
        userParser.optionxform = str
        parsingDictionary = {"service": "NETFLIX"}

        # Required variables for filling in config file
        baseurl = userParser.get(parsingDictionary['service'], 'url')
        username = userParser.get(parsingDictionary['service'], 'username')
        password = userParser.get(parsingDictionary['service'], 'password')

        parser = ConfigParser()
        parser.read('config.ini')
        parser.optionxform = str

        paths = {'usernameBox': "email",
                 'passwordBox': "password",
                 'submitButton':   "login-button"
                 }

        # firefox_profile = webdriver.FirefoxProfile()
        # firefox_profile.set_preference('permissions.default.stylesheet', 2)
        # firefox_profile.set_preference('permissions.default.image', 2)
        # firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so',
        # 'false')

        # netflixDriver = webdriver.Firefox(firefox_profile=firefox_profile)
        netflixDriver = webdriver.PhantomJS()
        netflixDriver.userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:36.0) Gecko/20100101 Firefox/36.0 WebKit'
        netflixDriver.cookiesEnabled = True
        netflixDriver.javascriptEnabled = True
        netflixDriver.get(baseurl)
        mutliPageLogin = False
        # Clearing Username TextBox
        netflixDriver.find_element_by_name(paths['usernameBox']).clear()

        # Typing in the username as obtained from config file
        netflixDriver.find_element_by_name(
            paths['usernameBox']).send_keys(username)

        # Clearing password field

        try:
            netflixDriver.find_element_by_name(paths['passwordBox']).clear()

        # It is a double page login. So we first need to click on "Next" and
        # then send the password
        except:
            netflixDriver.find_element_by_class_name(
                paths['submitButton']).click()
            mutliPageLogin = True

        time.sleep(1)

        if mutliPageLogin:
            netflixDriver.find_element_by_name(paths['passwordBox']).clear()

        # Typing in the password
        netflixDriver.find_element_by_name(
            paths['passwordBox']).send_keys(password)

        # Clicking on Submit button
        netflixDriver.find_element_by_class_name(paths['submitButton']).click()

        # temp = input()

        netflixDriver.get(self.urlName)
        pageSource = netflixDriver.page_source

        self.createSoupObject(pageSource)

        returnStatus = self.getResources(netflixDriver)

        netflixDriver.close()

        return returnStatus

    def getResources(self, driver):

        self.resourceList = []
        print("Searching for subtitle source")
        Found = False
        Counter = 0
        while not Found:

            self.resourceList = driver.execute_script(
                "return window.performance.getEntries();")
            time.sleep(1)
            print(".", end="")
            for i in self.resourceList:
                if 'name' in i.keys():
                    if "/?o" in i['name']:
                        Found = True
                        break

            if len(self.resourceList) >= 60 or Counter >= 100:
                print("Timed out. Trying anyway")
                break
                # return 0

            Counter += 1

        pass
        return 1

    def convertXMLToSrt(self):
        """

        Taken from - https://github.com/isaacbernat/netflix-to-srt

        """

        filename = self.title + ".xml"
        outputFile = self.title + ".srt"
        if self.debug:
            print("Creating ~  '%s.srt' ..." % (self.title))
        with codecs.open(filename, 'rb', "utf-8") as f:
            text = f.read()

        with codecs.open(outputFile, 'wb', "utf-8") as f:
            f.write(Netflix_XmlToSrt.to_srt(text))
