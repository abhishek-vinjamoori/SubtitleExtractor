import os
import re
import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import json
from configparser import SafeConfigParser
from selenium import webdriver


class amazonExtractor(object):
	
	"""docstring for amazonExtractor"""
	
	def __init__(self,url):
		print("Detected Amazon\nProcessing....\n")
		self.loginRequired = False
		self.urlName = url
		self.debug = True
		self.requestsFileName = "iDoNotExistDefinitelyOnThisComputerFolder.html"
		self.videoType = ""

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
		
		self.getcustomerID()
		self.getToken()
		self.getTitle()
		if self.debug:
			print(self.title)

		self.getVideoType()
		if self.debug:
			print(self.videoType)

		if self.videoType == "movie":
			
			self.getAsinID1() #Method-1		
			if self.debug:
				print(self.parametersDict['asin'])

			returnValue = self.standardFunctionCalls()

		else:

			self.getAsinID2()
			if self.debug:
				print(self.asinList)
			
			folderPath = "./"			
			directoryName = folderPath + self.title
			try:
				os.mkdir(directoryName)
			except:
				print("Directory exists")
				pass

			self.title = directoryName + "/" + self.title
			episodeNum = 1
			for asins in self.asinList:
				self.parametersDict['asin'] = asins 			
				currentTitle = self.title

				self.title += str(episodeNum) 
				try:
					returnValue = self.standardFunctionCalls()
				except:
					pass
				self.title = currentTitle
				episodeNum+=1
			#returnValue = 0
		# self.getSubtitlesContainer()
		# if self.debug:
		# 	print(self.subtitleURLContainer)


		# SubtitlesURL = self.getSubtitleURL()
		# if self.debug:
		#  	print(SubtitlesURL)


		# if not SubtitlesURL:
		# 	print("Unable to fetch the subtitles. No subtitles present.")
		# 	self.deleteUnnecessaryfiles()
		# 	return 0

		
		# returnValue = self.downloadDfxpTranscript(SubtitlesURL)

		# #self.convertDfxpToSrt()

		# self.deleteUnnecessaryfiles()

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

	def getcustomerID(self):

		parser = SafeConfigParser()
		parser.read('config.ini')
		self.parametersDict['customerID'] = parser.get('AMAZON', 'customerid')
		pass

	def getToken(self):

		parser = SafeConfigParser()
		parser.read('config.ini')
		self.parametersDict['token'] = parser.get('AMAZON', 'token')
		pass


	def getVideoType(self):

		"""

		<script data-a-state='{"key":"dv-dp-state"}' type="a-state">{"pageType":"tv","pageAsin":null}</script>

		"""
		parsingParams = {"tagname":"script","tagAttrs":["type","a-state"], "jsonparam":"pagetype"}

		try:
			scriptTags = self.soupObject.findAll(parsingParams['tagname'],attrs={parsingParams['tagAttrs'][0]:parsingParams['tagAttrs'][1]})
			for allTags in scriptTags: 
				try:
					jsonString = allTags.string.lower()
					jsonparser = json.loads(jsonString)
					self.videoType = jsonparser[parsingParams['jsonparam']]
					break
				except:
					continue
			#print(s)

		except:
			pass		

		#Unable to get the type. Using movie as the default case.

		if self.videoType == "":
			self.videoType = "movie"

		pass

	def getAsinID1(self):
		
		"""
		This is one of the methodologies to get the asin ID. 
		If it is a movie, we use this methodology.
		Obtaining the asin from here -

		<input name="asin" type="hidden" value="B000I9WVAK"/>
		The value contains the asin.

		"""

		try:
			asinObject = self.soupObject.find("input",attrs={"name" : re.compile("^asin$", re.I)})
			self.parametersDict['asin'] = str(asinObject['value'])
			#print(s)

		except:
			pass

	def getAsinID2(self):
		
		"""
		This is one of the methodologies to get the asin ID. 
		If it is a TV Series, we use this methodology.
		Obtaining the asin from here -

		<div class="a-section dv-episode-container aok-clearfix" data-aliases="B000I9WVAK" id="dv-el-id-2">
		The value contains the asin.

		"""

		self.loginAmazon()

		try:
			self.asinList = [i['data-aliases'] for i in self.soupObject.find_all('div',attrs={'data-aliases' : True})]
			
			#There maybe multiple ASIN's present which are separated by comma. So we just take one of it.

			for i in range(len(self.asinList)):
				tempList = self.asinList[i].split(",")
				for ids in tempList:
					if ids != "":
						self.asinList[i] = ids
						break

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

		#If it is a movie, we use this methodology -
		try:
			IndexingParameters = ["subtitleUrls",0,"url"]

			subRequestObject = requests.get(self.subtitleURLContainer)
			
			parsedJsonObject = json.loads(str(subRequestObject.text))
			SubsURL = parsedJsonObject[IndexingParameters[0]][IndexingParameters[1]][IndexingParameters[2]]
			
			return SubsURL

		except:
			pass
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

	def standardFunctionCalls(self):
		
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
		pass


	def loginAmazon(self):

		#Initialising the parser
		userParser = SafeConfigParser()
		userParser.read('userconfig.ini')
		userParser.optionxform = str
		parsingDictionary = {"service":"AMAZON"}

		#Required variables for filling in config file
		baseurl  = userParser.get(parsingDictionary['service'], 'url')
		username = userParser.get(parsingDictionary['service'], 'username')
		password = userParser.get(parsingDictionary['service'], 'password')

		parser = SafeConfigParser()
		parser.read('config.ini')
		parser.optionxform = str

		xpaths = { 'usernameBox' : "//*[@id='ap_email']",
		           'passwordBox' : "//*[@id='ap_password']",
		           'submitButton' :   "//*[@id='signInSubmit']"
		         }

		firefox_profile = webdriver.FirefoxProfile()
		firefox_profile.set_preference('permissions.default.stylesheet', 2)
		firefox_profile.set_preference('permissions.default.image', 2)
		firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')


		#amazonDriver = webdriver.Firefox(firefox_profile=firefox_profile)
		amazonDriver = webdriver.Chrome()
		amazonDriver.userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:36.0) Gecko/20100101 Firefox/36.0 WebKit'
		amazonDriver.cookiesEnabled = True
		amazonDriver.javascriptEnabled = True
		amazonDriver.get(baseurl)
		#Clearing Username TextBox 
		amazonDriver.find_element_by_xpath(xpaths['usernameBox']).clear()

		#Typing in the username as obtained from config file
		amazonDriver.find_element_by_xpath(xpaths['usernameBox']).send_keys(username)

		#Clearing password field 
		amazonDriver.find_element_by_xpath(xpaths['passwordBox']).clear()

		#Typing in the password
		amazonDriver.find_element_by_xpath(xpaths['passwordBox']).send_keys(password)
		
		#Clicking on Submit button
		amazonDriver.find_element_by_xpath(xpaths['submitButton']).click()
		temp = input()
		amazonDriver.get(self.urlName)
		pageSource = amazonDriver.page_source
		self.soupObject = BeautifulSoup(pageSource,from_encoding="utf8")
		#print(pageSource)
		fh = open(self.requestsFileName, "w")
		fh.write(str(self.soupObject))
		fh.close()
		
		pass
		amazonDriver.close()