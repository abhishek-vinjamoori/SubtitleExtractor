import re
import sys
from bs4 import BeautifulSoup


def toSrt(xml_string):
    srt = ''
    xml_string = xml_string.replace("<tt:br/>", "\n")
    texts = BeautifulSoup(xml_string)
    listOfTranscripts = texts.findAll("tt:p")

    # TODO parse xml instead of regex

    captionNumber = 1
    for captions in listOfTranscripts:

        start = captions['begin']
        end = captions['end']

        start = formatTime(start)
        end = formatTime(end)
        caption = captions.string

        srt += str(captionNumber) + '\n'
        srt += start + ' --> ' + end + '\n'
        srt += caption + '\n\n'

        captionNumber += 1

    return srt


def formatTime(time):

    formatted = time.replace(".", ",")

    return formatted


def main():
    f = open(sys.argv[1], "r")
    q = f.read()
    s = toSrt(q)
    print(s)


if __name__ == "__main__":
    main()
