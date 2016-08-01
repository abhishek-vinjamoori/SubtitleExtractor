import re
import sys
from bs4 import BeautifulSoup


def toSrt(xml_string):
	srt = ''
	texts = BeautifulSoup(xml_string)
	listOfTranscripts = texts.findAll("text")

	# TODO parse xml instead of regex
	
	captionNumber = 1
	for captions in listOfTranscripts:
		

		start = float(captions['start'])
		try:
			duration = float(captions['dur'])
		except:
			duration = float('2')

		end = start + duration
		
		

		# startSec, startMicro = str(start).split('.')
		# endSec, endMicro = str(end).split('.')
		
		#startTime = formatTime(start)
		#endTime   = formatTime(end)
		start = "%02i:%02i:%02i,%03i" %(start/(60*60), start/60%60, start%60, start%1*1000)
		end = "%02i:%02i:%02i,%03i" %(end/(60*60), end/60%60, end%60, end%1*1000)

		# start = "%02d:%02d:%02d,%" % (startTime[0], startTime[1], startTime[2], startTime[3])
		# end   = "%02d:%02d:%02d,%s" % (endTime[0], endTime[1], endTime[2], endTime[3])


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
	return [h,m,s,micro]

def main():
	f = open(sys.argv[1],"r")
	q = f.read()
	s = toSrt(q)
	print(s)


if __name__ == "__main__":
	main()