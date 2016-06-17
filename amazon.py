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
			"deviceID"                          : "" ,
			"deviceTypeID"                      : "" ,
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
		return 0

		# if not smiLink:
		# 	print("Unable to fetch the subtitles. No subtitles present.")
		# 	self.deleteUnnecessaryfiles()
		# 	return

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



	def getContentID2(self):

		"""
		This is the alternative method to obtain the contentID. 
		Sample line 1) - <link href="http://ib3.huluim.com/video/60585710?region=US&amp;size=220x124"
		Sample line 2) - <link href="http://ib3.huluim.com/movie/60535322?region=US&amp;size=220x318"
		Required content ID's are 60585710 & 60535322 respectively.

		Partition technique is used to obtain the content ID.
		"""
		fh = open(self.requestsFileName, "r")		
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
				os.remove(self.title+".vtt")
			except:
				pass
