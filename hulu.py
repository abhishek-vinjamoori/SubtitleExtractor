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
		

	def getSubtitles(self):

		"""
		The main function which uses helper functions to get the subtitles
		"""

		requestObject = requests.get(self.urlName)

		# fileHandler = open("requests.txt", "w")
		# fileHandler.write(requestObject.text)
		# fileHandler.close() 
		
		self.soupObject = BeautifulSoup(requestObject.text,from_encoding="utf8")
		#soupObject1 = BeautifulSoup(requestObject.text,"lxml")
		#print(self.soupObject.original_encoding)

		fh = open("iDoNotExistDefinitelyOnThisComputerFolder.txt", "w")
		fh.write(str(self.soupObject))
		fh.close()
		
		self.getTitle()

		self.contentID = self.getContentID1() #Method-1
		
		try:
			self.contentID = int(self.contentID)
		except:
			print("Trying an alternative method to fetch Content ID")
			self.contentID = self.getContentID2()  #Method-2

		try:
			self.contentID = int(self.contentID)
		except:
			print("Unable to fetch the contentID.")
			self.deleteUnnecessaryfiles()
			return 0

		if self.debug:
			print(self.contentID)

		smiLink = self.getSmiSubtitlesLink()

		if not smiLink:
			print("Unable to fetch the subtitles. No subtitles present.")
			self.deleteUnnecessaryfiles()
			return 0

		if self.debug:
			print(smiLink)
		
		vttLink = self.transformToVtt(smiLink)
		if self.debug:
			print(vttLink)
		
		self.createVttSubtitleFile(vttLink)
		self.convertVttToSrt()

		self.deleteUnnecessaryfiles()

		return 1

	def getContentID1(self):
		
		"""This is one of the methodologies to get the content ID. If this fails the alternative method will be called
		
		In the Beautiful soup text it can be found that every video has this paramter.
		\"content_id\": \"60535322\"
		
		So we first use '"'(quotes) as the delimetter and split the text. Then access the content ID from the returned list.

		"""

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

		Partition technique is used to obtain the content ID.
		"""
		fh = open("iDoNotExistDefinitelyOnThisComputerFolder.txt", "r")		
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
		
		The XML Link for any subtitle video is - "http://www.hulu.com/captions.xml?content_id=CONTENTID"
		Where, CONTENTID is the unique content_ID of the video.
		
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
		Source - http://stream-recorder.com/forum/hulu-subtitles-t20120.html
		
		http://assets.huluim.com/"captions"/380/60601380_US_en_en."smi"  -----> 
		http://assets.huluim.com/"captions_webvtt"/380/60601380_US_en_en."vtt"
		
		captions --> captions_webvtt
		smi      --> vtt

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

		subsFileHandler = open(self.title + ".vtt","w")
		subsFileHandler.write(requestObjectv.text)
		subsFileHandler.close()

		pass
	
	def convertVttToSrt(self):

		"""
		This function converts the VTT subtitle file into SRT format.
		Credits - http://goo.gl/XRllyy for the conversion method.
		"""

		f =  open(self.title + ".vtt","r")
		fh = open(self.title + ".srt","w")
		print("Creating %s.srt ..."%(self.title))
		
		count = 1

		#Removing WEBVTT Header line.
		for line in f.readlines():
			if line[:6] == 'WEBVTT':
				continue

			#Substituting '.' with ',' in the time-stamps
			line = re.sub(r'(:\d+)\.(\d+)', r'\1,\2', line)

			#Printing the header number in each line. This is required for the SRT format.
			if line == '\n':	
				fh.write("\n" + str(count)+"\n")
				count += 1
			else:
				fh.write(line.strip()+"\n")

		f.close()
		fh.close()

	def getTitle(self):

		"""
		This function returns the title of the video. This is also used for naming the file.

		<meta name="twitter:title" value="Interstellar"/>   --> Extracting the value from here
		
		"""

		#print(self.soupObject.title.string)
		s=self.soupObject.find("meta",attrs={"name":"twitter:title"})
		self.title = s['value']

		pass

	def deleteUnnecessaryfiles(self):

		try:
			os.remove("iDoNotExistDefinitelyOnThisComputerFolder.txt")
			os.remove(self.title+".vtt")
		except:
			pass