from bs4 import BeautifulSoup
import requests
import os

def createSoupObject(url, fileName):

    requestObject = requests.get(url)

    soupObject = BeautifulSoup(requestObject.text, "lxml", from_encoding="utf8")

    fh = open(fileName, "w")
    fh.write(str(soupObject))
    fh.close()


def deleteUnnecessaryfiles(debug, fileName, title, extension):

    if not debug:
        try:
            os.remove(fileName)
            os.remove(title + extension)
        except:
            pass
