import os
import re
import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import json

class amazonExtractor(object):
	
	"""docstring for netflixExtractor"""
	
	def __init__(self,url):
		print("Detected Amazon\nProcessing....\n")
		self.loginRequired = False
		self.urlName = url
		self.debug = True
		self.requestsFileName = "iDoNotExistDefinitelyOnThisComputerFolder.html"
		
		#Parameters requireed for Obtaining the URL
		self.parametersDict = {
			"PreURL"                            : "https://atv-ps.amazon.com/cdp/catalog/GetPlaybackResources?",
			"asin"                              : "" ,
			"consumptionType"                   : "Streaming" ,
			"desiredResources"                  : "SubtitleUrls" ,
			"deviceID"                          : "b63345bc3fccf7275dcad0cf7f683a8f" ,
			"deviceTypeID"                      : "AOAGZA014O5RE" ,
			"firmware"                          : "1" ,
			"marketplaceID"                     : "ATVPDKIKX0DER" ,
			"resourceUsage"                     : "ImmediateConsumption" ,
			"videoMaterialType"                 : "Feature" ,
			"operatingSystemName"               : "Linux" ,
			"customerID"                        : "" ,
			"token"                             : "" ,
			"deviceDrmOverride"                 : "CENC" ,
			"deviceStreamingTechnologyOverride" : "DASH" ,
			"deviceProtocolOverride"            : "Https" ,
			"deviceBitrateAdaptationsOverride"  : "CVBR,CBR" ,
			"titleDecorationScheme"             : "primary-content"
		}
		pass 

	def getSubtitles(self):

		"""
		The main function which uses helper functions to get the subtitles
		"""

		self.createSoupObject()
		
		self.getTitle()
		if self.debug:
			print(self.title)
		
		self.getAsinID() #Method-1		
		if self.debug:
		 	print(self.parametersDict['asin'])

		self.getSubtitlesContainer()
		
		if self.debug:
			print(self.subtitleURLContainer)

		SubtitlesURL = self.getSubtitleURL()
		if self.debug:
		 	print(SubtitlesURL)

		if not SubtitlesURL:
			print("Unable to fetch the subtitles. No subtitles present.")
			self.deleteUnnecessaryfiles()
			return 0

		
		returnValue = self.downloadDfxpTranscript(SubtitlesURL)

		#self.convertDfxpToSrt()

		self.deleteUnnecessaryfiles()

		return returnValue

	def createSoupObject(self):
		
		#This is to tackle the Request Throttle error which occurs on Amazon frequently.
		numberOfTrials = 20
		errorNames = ["Service","Error"]

		while numberOfTrials:
			requestObject = requests.get(self.urlName)

			# fileHandler = open("requests.txt", "w")
			# fileHandler.write(requestObject.text)
			# fileHandler.close() 
			
			self.soupObject = BeautifulSoup(requestObject.text,from_encoding="utf8")
			#soupObject1 = BeautifulSoup(requestObject.text,"lxml")
			#print(self.soupObject.original_encoding)
			titleString = str(self.soupObject.title.string)
			if errorNames[0] in titleString and errorNames[1] in titleString:
				print("Request Throttle Error\n Trying Again....")
				numberOfTrials -= 1 
				continue
			else:
				print("Request successful")
				numberOfTrials = 0
			fh = open(self.requestsFileName, "w")
			fh.write(str(self.soupObject))
			fh.close()		

		pass


	def getAsinID(self):
		
		"""This is one of the methodologies to get the asin ID. 

		Obtaining the asin from here -

		<input name="asin" type="hidden" value="B000I9WVAK"/>
		The value contains the asin.

		"""

		try:
			s=self.soupObject.find("input",attrs={"name":"asin"})
			self.parametersDict['asin'] = str(s['value'])
			if not self.title:
				s = int("deliberateError")

		except:
			pass

	
	def getSubtitlesContainer(self):
		
		"""
		This function returns the final URL which contains the link to the Subtitles file.
		
		"""
		self.subtitleURLContainer = ""

		self.subtitleURLContainer += self.parametersDict['PreURL']

		for parameters in self.parametersDict:
			if parameters != "PreURL":
				self.subtitleURLContainer += "&"
				self.subtitleURLContainer += parameters
				self.subtitleURLContainer += "="
				self.subtitleURLContainer += self.parametersDict[parameters]
		pass


	def getSubtitleURL(self):

		"""
		The json content looks like this -	
	
		{"returnedTitleRendition":{""},"subtitleUrls":[{"url":"linkforsubtitle.dfxp"}]}

		"""
		IndexingParameters = ["subtitleUrls",0,"url"]

		subRequestObject = requests.get(self.subtitleURLContainer)
		
		parsedJsonObject = json.loads(str(subRequestObject.text))
		SubsURL = parsedJsonObject[IndexingParameters[0]][IndexingParameters[1]][IndexingParameters[2]]
		
		return SubsURL

		pass

	def downloadDfxpTranscript(self,SubsLink):

		"""
		This function fetches the captions and writes them into a file in VTT format
		"""
		try:
			subRequestObject = requests.get(SubsLink)
			#print(subRequestObject.text)

			subsFileHandler = open(self.title + ".dfxp","w")
			print("Creating ~  '%s.dfxp' ..."%(self.title))			
			subsFileHandler.write(subRequestObject.text)
			subsFileHandler.close()
			return 1
		
		except:
			return 0
		
		pass
	

	def getTitle(self):

		"""
		This function returns the title of the video. This is also used for naming the file.

		<meta name="twitter:title" content="Interstellar"/>   --> Extracting the value from here
		
		"""

		#print(self.soupObject.title.string)
		try:
			s = self.soupObject.find("meta",attrs={"name":"twitter:title"})
			self.title = str(s['content'])
			self.title = self.title.strip()
			if not self.title:
				s = int("deliberateError")

		except:
			self.title = "Amazonsubtitles"

		pass

	def deleteUnnecessaryfiles(self):

		if not self.debug:
			try:
				os.remove(self.requestsFileName)
			except:
				pass
