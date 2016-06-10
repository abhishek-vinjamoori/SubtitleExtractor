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
		self.debug = True
		pass
		#http://stream-recorder.com/forum/hulu-subtitles-t20120.html

	def getSubtitles(self):
		requestObject = requests.get(self.urlName)

		fileHandler = open("requests.txt", "w")
		fileHandler.write(requestObject.text)
		fileHandler.close() 
		
		self.soupObject = BeautifulSoup(requestObject.text,from_encoding="utf8")
		#soupObject1 = BeautifulSoup(requestObject.text,"lxml")
		#print(self.soupObject.original_encoding)

		fh = open("soup.txt", "w")
		fh.write(str(self.soupObject))
		fh.close()
		
		self.contentID = self.getContentID1()
		
		try:
			self.contentID = int(self.contentID)
		except:
			print("Trying an alternative method to fetch Content ID")
			self.contentID = self.getContentID2()

		try:
			self.contentID = int(self.contentID)
		except:
			print("Unable to fetch the contentID.")
			return 0
		if self.debug:
			print(self.contentID)

		smiLink = self.getSmiSubtitlesLink()

		if not smiLink:
			print("Unable to fetch the subtitles. No subtitles present")
			return 0			
		if self.debug:
			print(smiLink)
		
		vttLink = self.transformToVtt(smiLink)
		if self.debug:
			print(vttLink)
		
		self.createVttSubtitleFile(vttLink)
		self.convertVttToSrt()

		return 1

	def getContentID1(self):
		
		"""This is one of the methodologies to get the content ID. If this fails the alternative method will be called"""

		listedSoup = str(self.soupObject).split('"')
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


	def getSmiSubtitlesLink(self):
		
		"""
		This function returns the SMI subtitle link based on the contentID.
		Currently, the link resides in the xmlLinkTemplate variable
		"""

		smiLink = ""
		xmlLinkTemplate = "http://www.hulu.com/captions.xml?content_id="
		xmlLink = xmlLinkTemplate + str(self.contentID)
		xmlRequest = requests.get(xmlLink)
		if self.debug:
			print(xmlRequest.text)
		smiSoup = BeautifulSoup(xmlRequest.text)
		
		if smiSoup.en:
			#print(smiSoup.en.string)
			smiLink = smiSoup.en.string
		
		return smiLink
		
		pass

	def transformToVtt(self,smiLink):
		
		"""
		This function takes an smiLink and returns the corressponding subtitles in VTT format(a link)
		"""
		#print(smiLink)
		vttLink = ""
		replaceDict = {"captions":"captions_webvtt", "smi":"vtt"}

		for keys in replaceDict:
			smiLink = smiLink.replace(keys,replaceDict[keys])

		vttLink = smiLink
		#print(vttLink)

		return vttLink	

		pass

	def createVttSubtitleFile(self,vttLink):

		"""
		This function fetches the captions and writes them into a file in VTT format
		"""

		requestObjectv = requests.get(vttLink)
		#print(requestObjectv.text)

		subsFileHandler = open("subtitles.vtt","w")
		subsFileHandler.write(requestObjectv.text)
		subsFileHandler.close()

		pass
	
	def convertVttToSrt(self):

		"""
		This function converts the VTT subtitle file into SRT format.
		"""

		f =  open("subtitles.vtt","r")
		fh = open("finalSubtitle.srt","w")
		
		count = 1
		for line in f.readlines():
			if line[:6] == 'WEBVTT':
				continue

			line = re.sub(r'(:\d+)\.(\d+)', r'\1,\2', line)

			if line == '\n':	
				fh.write("\n" + str(count)+"\n")
				count += 1
			else:
				fh.write(line.strip()+"\n")

		f.close()
		fh.close()