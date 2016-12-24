import sys
from bs4 import BeautifulSoup


def toSrt(xml_string):
    srt = ''
    xml_string = xml_string.replace("<br/>", "\n")
    texts = BeautifulSoup(xml_string, "lxml", from_encoding="utf8")
    listOfTranscripts = texts.findAll("p")

    colorDict = {}

    colorInfo = texts.findAll("style")
    for i in colorInfo:
        try:
            colorDict[i['id']] = i['tts:color']
        except:
            pass

    captionNumber = 1
    for captions in listOfTranscripts:

        spanList = captions.findAll("span")
        for i in spanList:
            newtag = texts.new_tag("font", color=i['tts:color'])
            newtag.string = i.string
            i.replace_with(newtag)

        start = captions['begin']
        end = captions['end']

        start = formatTime(start)
        end = formatTime(end)
        captionContent = captions.contents

        caption = ""

        personalStyle = False
        # The default font for this caption must be changed from the color
        # dictionary
        if captions.has_attr('style'):
            personalStyle = True

        if personalStyle:
            colorName = colorDict[captions['style']]
            tagName = '<font color="%s">' % colorName
            caption += tagName

        for content in captionContent:
            caption += str(content)

        if personalStyle:
            caption += '</font>'

        srt += str(captionNumber) + '\n'
        srt += start + ' --> ' + end + '\n'
        srt += caption + '\n\n'

        captionNumber += 1

    return srt


def formatTime(time):

    try:
        pieces = time.split(".")
        pieces[1] = (pieces[1] + "0" * 3)[0:3]
        formatted = "%s,%s" % (pieces[0], pieces[1])
    except:
        pieces = ("0" * 3)[0:3]
        formatted = "%s,%s" % (time, pieces)

    return formatted


def main():
    f = open(sys.argv[1], "r")
    q = f.read()
    s = toSrt(q)
    print(s)


if __name__ == "__main__":
    main()
