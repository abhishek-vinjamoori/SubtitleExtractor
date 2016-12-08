#! /usr/bin/env python3

import sys
from SubtitleExtractor import Subtitle
from HuluTest import HuluTestList
from BbcTest import BbcTestList
from FoxTest import FoxTestList
from AmazonTest import AmazonTestList


def main():

    testList = AmazonTestList
    Extractor = Subtitle()

    counter = 0
    failureList = []

    for entities in testList:

        url = entities[0]
        Extractor.getServiceName(url)
        Extractor.testMode = True
        # if len(entities) == 5:
        returnValue = Extractor.serviceProcess()

        if returnValue:
            print("File %d successful" % (counter + 1))
        else:
            print("Test Failed on File - %d" % (counter + 1))
            failureList.append([counter + 1, url])

        counter += 1

    print(
        "\n\n\n------------------------------------------------------------------------\n\n")

    if len(failureList):
        print("Test failed on files -")

        for i in failureList:
            print("<%d> - URL : %s" % (i[0], i[1]))


if __name__ == "__main__":
    main()
