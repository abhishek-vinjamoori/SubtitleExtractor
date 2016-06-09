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
		self.soupText = BeautifulSoup(requestObject.text,from_encoding="utf8")
		#soupText1 = BeautifulSoup(requestObject.text,"lxml")
		print(self.soupText.original_encoding)
		#print(soupText.encode("utf8"))

		fh = open("soup.txt", "w")
		fh.write(str(self.soupText))
		fh.close()
		self.contentID = self.getContentID1()
		try:
			self.contentID = int(self.contentID)+"123"
		except:
			print("Trying an alternative method to fetch Content ID")
			self.contentID = self.getContentID2()

		try:
			self.contentID = int(self.contentID)
		except:
			print("Unable to fetch the contentID.")

		print(self.contentID)


	def getContentID1(self):
		
		"""This is one of the methodologies to get the content ID. If this fails the alternative method will be called"""

		listedSoup = str(self.soupText).split('"')
		contentCounter = 0
		for counter in range(len(listedSoup)):
			if "content_id" in listedSoup[counter]:
				contentCounter = counter+2
				break
		#print(listedSoup[contentCounter])
		contentId = ""
		
		for i in listedSoup[contentCounter]:
			if i.isdigit():
				contentId+=i
		return contentId		


	def getContentID2(self):

		"""
		This is the alternative method to obtain the contentID. 
		Sample line 1) - <link href="http://ib3.huluim.com/video/60585710?region=US&amp;size=220x124"
		Sample line 2) - <link href="http://ib3.huluim.com/movie/60535322?region=US&amp;size=220x318"
		Required content ID's are 60585710 & 60535322 respectively.
		"""
		fh = open("soup.txt", "r")		
		listOfOptions = ["video/","movie/"]
		foundContent = False
		contentId = ""
		for line in fh:
			
			for option in listOfOptions:
				junkText, separator, contentIdContainer = line.partition(option)
				#The Content Id has been found.
				if contentIdContainer:
					foundContent = True
					break
			
			#The Content ID has been found. No need to read the file anymore.
			#Get the Content ID from the container 			
			if foundContent:    
				contentId,separator, junkText = contentIdContainer.partition("?")
				if separator:
					break
				else:
					foundContent = False		
		
		return contentId
		
		pass