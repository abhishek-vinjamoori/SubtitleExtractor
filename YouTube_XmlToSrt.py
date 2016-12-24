import sys
from bs4 import BeautifulSoup


def toSrt(xml_string):
    srt = ''
    texts = BeautifulSoup(xml_string, "lxml", from_encoding="utf8")
    listOfTranscripts = texts.findAll("text")

    captionNumber = 1
    for captions in listOfTranscripts:

        start = float(captions['start'])
        try:
            duration = float(captions['dur'])
        except:
            duration = float('2')

        end = start + duration

        start = "%02i:%02i:%02i,%03i" % (
            start / (60 * 60), start / 60 % 60, start % 60, start % 1 * 1000)
        end = "%02i:%02i:%02i,%03i" % (
            end / (60 * 60), end / 60 % 60, end % 60, end % 1 * 1000)

        caption = captions.string
        caption = caption.replace('&#39;', "'")
        caption = caption.replace('&quot;', '"')

        srt += str(captionNumber) + '\n'
        srt += start + ' --> ' + end + '\n'
        srt += caption + '\n\n'

        captionNumber += 1

    return srt


def formatTime(secTime):
    """Convert a time in seconds (google's transcript) to srt time format."""

    sec, micro = str(secTime).split('.')
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return [h, m, s, micro]


def main():
    f = open(sys.argv[1], "r")
    q = f.read()
    s = toSrt(q)
    print(s)


if __name__ == "__main__":
    main()
