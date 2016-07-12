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

		
		self.getShowDetails(jsonString)
		if self.debug:
			print(self.showId)
			print(self.showName)
			print(self.videoGuid)

		# smiLink = self.getSmiSubtitlesLink()

		# if not smiLink:
		# 	print("Unable to fetch the subtitles. No subtitles present.")
		# 	self.deleteUnnecessaryfiles()
		# 	return 0

		# if self.debug:
		# 	print(smiLink)
		
		# vttLink = self.transformToVtt(smiLink)
		# if self.debug:
		# 	print(vttLink)
		
		# self.createVttSubtitleFile(vttLink)
		# self.convertVttToSrt()

		# self.deleteUnnecessaryfiles()

		return 1

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
		
		searchStringList = ["watch/"]
		juknkData,episodeName,IDContainer = url.partition(searchStringList[0])
		contentId,Slash,Junk = IDContainer.partition("/")

		return contentId		


	def getContentID2(self):

		"""
		This is the alternative method to obtain the contentID. 

		<meta content="http://www.fox.com/watch/681382467805/7683748608" property="og:url"/>
		Obtained from the SOUP.
		"""

		UrlObj = self.soupObject.find("meta",attrs={"property":"og:url"})
		Url = UrlObj['content']
		contentId = self.getContentID1(Url)
		
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



	def transformToVtt(self,smiLink):
		
		"""
		This function takes an smiLink and returns the corressponding subtitles in VTT format(a link)

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
		print("Creating ~  '%s.srt' ..."%(self.title))
		
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
				os.remove(self.title+".vtt")
			except:
				pass