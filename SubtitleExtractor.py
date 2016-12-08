#! /usr/bin/env python3

import os
import getpass
from netflix import netflixExtractor
from hulu import huluExtractor
from youtube import youtubeExtractor
from newamazon import amazonExtractor
from bbc import bbcExtractor
from crunchyroll import crunchyrollExtractor
from fox import foxExtractor
from crackle import crackleExtractor
from comedycentral import comedycentralExtractor
# import vudu
# import epix
# import syfy
# import sky
# import shomi


print("Downloading Subtitles")


class Subtitle(object):

    """This is the main class which holds all the information for the main module"""

    def __init__(self):

        self.urlName = ""
        self.serviceType = ""
        self.supportedServices = {
            "hulu": huluExtractor, "netflix": netflixExtractor, "youtube": youtubeExtractor,
            "amazon": amazonExtractor, "bbc": bbcExtractor, "crunchyroll": crunchyrollExtractor, "fox": foxExtractor,
            "crackle": crackleExtractor, "comedyCentral": comedycentralExtractor}
        #"hbo","vudu","epix","syfy","sky","shomi"]

        # Dictionary of all the supported services with the respective class
        # name as the value.
        self.testMode = False

    def getServiceName(self, url):

        self.urlName = url

        for names in self.supportedServices:
            if names in self.urlName:  # Parsing URL input
                self.serviceType = names
                break

    def serviceProcess(self):
        if self.serviceType:
            self.serviceClass = self.supportedServices[self.serviceType](
                self.urlName, self.testMode)  # Creating instance of the sub-class
            try:
                # if self.serviceClass.loginRequired is True:
                # 	print("Login is required. Your details are safe and secure\n")
                # 	self.serviceClass.username = input("Username : ")
                # 	self.serviceClass.password = getpass.getpass("Password : ")
                # 	print(self.serviceClass.password)
                returnValue = self.serviceClass.getSubtitles()

                if not returnValue:
                    print(
                        "Please report the issue and make sure that the video contains subtitles.")
                    return 0

                return 1

            except ValueError:
                print(
                    "Unable to get the subtitles. Please try again and open an issue to request for support for this video.")
                return 0
        else:
            print(
                "Service Not Supported. Please open an issue to request for support.")
            return 0

    def getServiceinfo(self):
        pass


def main():

    try:
        Extractor = Subtitle()
        url = input("Paste the link here : ")
                    #Parse the URL and find out which Internet service it is
        Extractor.getServiceName(url)

        if Extractor.serviceType:
            print(Extractor.serviceType)

        finalStatus = Extractor.serviceProcess()
                                               # Proces the corresponding
                                               # sub-module

        if finalStatus:
            print("Subtitles downloaded successfully !")
        else:
            print("Subtitles not downloaded.")

    except IndexError:
        print("An unknown error occurred")
        pass

if __name__ == "__main__":
    main()
