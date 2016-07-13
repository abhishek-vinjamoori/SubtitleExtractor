import os
import re
import requests
from bs4 import BeautifulSoup
import json

class foxExtractor(object):
	
	"""docstring for foxExtractor"""
	
	def __init__(self,url):

		print("Detected FOX NOW\nProcessing....\n")
		self.loginRequired    = False
		self.urlName          = url
		self.debug            = True
		self.requestsFileName = "iDoNotExistDefinitelyOnThisComputerFolder.html"
		self.showId           = ""
		self.showName         = ""
		self.videoGuid        = ""

		self.subtitleServer   = "http://static-media.fox.com/cc/"
		self.fileExtension    = [".srt",".dfxp"]
		pass
		

	def getSubtitles(self):

		"""
		The main function which uses helper functions to get the subtitles
		"""

		self.createSoupObject()
		
		self.getTitle()
		if self.debug:
			print(self.title)

		self.contentID = self.getContentID1(self.urlName) #Method-1
		
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

		jsonString = self.getShowJson()
		if self.debug:
			print(jsonString)
		self.standardCheck(jsonString)

		self.getShowDetails(jsonString)
		if self.debug:
			print(self.showId)
			print(self.showName)
			print(self.videoGuid)

		self.standardCheck(self.showId, self.showName, self.videoGuid)

		CaptionList = self.getSubtitleUrl()
		if self.debug:
			print(CaptionList)


		for link in CaptionList:
			returnValue = self.downloadDfxpTranscript(link)
			if returnValue:
				break
		
		self.deleteUnnecessaryfiles()

		return returnValue

	def createSoupObject(self):
		
		requestObject = requests.get(self.urlName)

		# fileHandler = open("requests.txt", "w")
		# fileHandler.write(requestObject.text)
		# fileHandler.close() 
		
		self.soupObject = BeautifulSoup(requestObject.text,from_encoding="utf8")
		#soupObject1 = BeautifulSoup(requestObject.text,"lxml")
		#print(self.soupObject.original_encoding)

		fh = open(self.requestsFileName, "w")
		fh.write(str(self.soupObject))
		fh.close()		

		pass


	def getContentID1(self,url):
		
		"""This is one of the methodologies to get the content ID. If this fails the alternative method will be called
		
		The URL follows a specific standard throughout.
		
		http://www.fox.com/watch/684171331973/7684520448
		
		We need to split and return "684171331973"

		"""
		
		contentId = ''

		try:
			searchStringList = ["watch/"]
			juknkData,episodeName,IDContainer = url.partition(searchStringList[0])
			contentId,Slash,Junk = IDContainer.partition("/")

		except:
			pass

		return contentId		


	def getContentID2(self):

		"""
		This is the alternative method to obtain the contentID. 

		<meta content="http://www.fox.com/watch/681382467805/7683748608" property="og:url"/>
		Obtained from the SOUP.
		"""
		contentId = ''

		try:
			UrlObj = self.soupObject.find("meta",attrs={"property":"og:url"})
			Url = UrlObj['content']
			contentId = self.getContentID1(Url)

		except:
			pass
		
		return contentId
		
		pass


	def getShowJson(self):
		
		"""		
		The required script content  looks like this-

		jQuery.extend(Drupal.settings, {"":...............}); 
		
		1) We add everything to a new string after encountering the first "{".
		2) Remove the last parantheses and the semi-colon to create a valid JSON. ---- ');' 

		"""
		scripts = self.soupObject.findAll("script")
		rawScript = ""

		for strs in scripts:
			if strs.string is not None:
				if "showid" in strs.string:
					rawScript = strs.string

		addState = False
		jsonString = ''
		
		for i in rawScript:
			if i == "{" and addState is False:
				addState = True
			if addState is True:
				jsonString += i
		
		jsonString = jsonString.replace(");","")

		return jsonString

		pass


	def getShowDetails(self,jsonString):

		"""
		The json content looks like this -	
	
		{"foxProfileContinueWatching":{"showid":"empire","showname":"Empire"},..............
		 "foxAdobePassProvider": {......,"videoGUID":"2AYB18"}}

		"""

		try:
			IndexingParameters = [
				["foxProfileContinueWatching","showid","showname"],
				["foxAdobePassProvider","videoGUID"],
			]
			
			parsedJsonObject = json.loads(jsonString)

			self.showId    = parsedJsonObject[IndexingParameters[0][0]][IndexingParameters[0][1]]
			self.showName  = parsedJsonObject[IndexingParameters[0][0]][IndexingParameters[0][2]]
			self.videoGuid = parsedJsonObject[IndexingParameters[1][0]][IndexingParameters[1][1]]

		except:
			print("Unable to parse Json. Please report.")
			pass

		pass


	def getSubtitleUrl(self):

		"""
		Sample Subtitle Link -
		http://static-media.fox.com/cc/sleepy-hollow/SleepyHollow_3AWL18_660599363942.srt
		http://static-media.fox.com/cc/sleepy-hollow/SleepyHollow_3AWL18_660599363942.dfxp

		The standard followed is -
		http://static-media.fox.com/cc/[showid]/showname_videoGUID_contentID.srt
		OR
		http://static-media.fox.com/cc/[showid]/showname_videoGUID_contentID.dfxp


		Some Subtitle URL's follow this standard -
		http://static-media.fox.com/cc/[showid]/showname_videoGUID.dfxp
		http://static-media.fox.com/cc/[showid]/showname_videoGUID.srt

		So we store both URL's and check both

		"""
		SubsUrl = self.subtitleServer
		SecondarySubsUrl = ''

		self.showName = self.processShowName(self.showName)

		SubsUrl          += str(self.showId)
		SubsUrl          += "/"

		SubsUrl          += str(self.showName)
		SubsUrl          += "_"

		SubsUrl          += str(self.videoGuid)
		SecondarySubsUrl  = SubsUrl
		SubsUrl          += "_"

		SubsUrl          += str(self.contentID)
		SubsUrl          += self.fileExtension[0]

		SecondarySubsUrl += self.fileExtension[0]

		return [SubsUrl,SecondarySubsUrl]


	def processShowName(self,name):

		"""
		
		Removes white spaces
		
		"""
		name = name.replace(" ","")
		return name


	def downloadDfxpTranscript(self,SubsLink):

		"""
		This function fetches the captions and writes them into a file in VTT format
		"""
		try:
			subRequestObject = requests.get(SubsLink)
			#print(subRequestObject.text)

			if subRequestObject.status_code >=400:
				#Deliberate error to exit.
				s = int("deliberateError")

			subsFileHandler = open(self.title + self.fileExtension[0],"w")
			print("Creating ~  '%s%s' ..."%(self.title, self.fileExtension[0]))		
			subsFileHandler.write(subRequestObject.text)
			subsFileHandler.close()
			return 1
		
		except:
			return 0
		
		pass

	def getTitle(self):

		"""
		This function returns the title of the video. This is also used for naming the file.

		<title>Watch New Girl Online: Episode 21, Season 5 on FOX</title>   --> Extracting the value from here
		
		"""

		#print(self.soupObject.title.string)
		try:

			self.title = self.soupObject.title.string.strip()
			if not self.title:
				s = int("deliberateError")

		except:
			self.title = "DownloadedFOXNowSubtitles"

		pass

	def deleteUnnecessaryfiles(self):

		if not self.debug:
			try:
				os.remove(self.requestsFileName)
			except:
				pass


	def standardCheck(self,*variablesToCheck):

		for variables in variablesToCheck:
			if not variables:
				print("Unable to fetch the subtitles.")
				self.deleteUnnecessaryfiles()
				exit()