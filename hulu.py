import os
import re
import requests
from bs4 import BeautifulSoup


class huluExtractor(object):
	
	"""docstring for netflixExtractor"""
	
	def __init__(self,url):
		print("Detected Hulu\nProcessing....\n")
		self.loginRequired = False
		self.urlName = url
		self.debug = False
		pass
		#http://stream-recorder.com/forum/hulu-subtitles-t20120.html

	def getSubtitles(self):
		requestObject = requests.get(self.urlName)

		self.fileHandler = open("requests.txt", "w")
		self.fileHandler.write(requestObject.text)
		if self.debug:
			print(requestObject.headers)
		self.fileHandler.close() 
		soupText = BeautifulSoup(requestObject.text,from_encoding="utf8")
		print(requestObject.encoding)
		#soupText1 = BeautifulSoup(requestObject.text,"lxml")
		print(soupText.original_encoding)
		#print(soupText.encode("utf8"))

		fh = open("soup.txt", "w")
		fh.write(str(soupText))
		fh.close()
		listedSoup = str(soupText).split('"')
		contentCounter = 0
		for counter in range(len(listedSoup)):
			if "content_id" in listedSoup[counter]:
				contentCounter = counter+2
				break
		print(listedSoup[contentCounter])

		#print(soupText.encode("utf8"))
		# fh = open("soup1.txt", "w")
		# fh.write(soupText.contents)
		# fh.close()		
		# fh = open("soup2.txt", "w")
		# fh.write(str(soupText2))
		# fh.close()		
		pass