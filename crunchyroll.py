import os
import re
import requests
from bs4 import BeautifulSoup


class crunchyrollExtractor(object):
	
	"""docstring for crunchyrollExtractor"""
	
	def __init__(self,url):

		print("Detected crunchyroll\nProcessing....\n")
		self.loginRequired = False
		self.urlName = url
		self.debug = True
		self.requestsFileName = "iDoNotExistDefinitelyOnThisComputerFolder.html"
		self.subtitleSource = "http://www.crunchyroll.com/xml/?req=RpcApiSubtitle_GetXml&subtitle_script_id="
		pass
		

	def getSubtitles(self):

		"""
		The main function which uses helper functions to get the subtitles
		"""

		self.createSoupObject()
		
		self.getTitle()
		if self.debug:
			print(self.title)

		self.ssidList = self.getSsid() #Method-1
		if self.debug:
			print(self.ssidList)

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

		return 0

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


	def getSsid(self):
		
		"""This is one of the methodologies to get the subtitles ID.		
		In the Beautiful soup text it can be found that every video has this parameter.
		<div>Subtitles: 
		  <span class="showmedia-subtitle-text">
		    <img src="http://static.ak.crunchyroll.com/i/country_flags/us.gif"/> 
		    <a href="/naruto-shippuden/episode-464-ninshu-the-ninja-creed-696237?ssid=206027" title="English (US)">English (US)</a>,
		    <img src="http://static.ak.crunchyroll.com/i/country_flags/sa.gif"/> 
		    <a href="/naruto-shippuden/episode-464-ninshu-the-ninja-creed-696237?ssid=206015" title="العربية">العربية</a>,
		    <img src="http://static.ak.crunchyroll.com/i/country_flags/it.gif"/> 
		    <a href="/naruto-shippuden/episode-464-ninshu-the-ninja-creed-696237?ssid=206733" title="Italiano">Italiano</a>, 
		    <img src="http://static.ak.crunchyroll.com/i/country_flags/de.gif"/>
		    <a href="/naruto-shippuden/episode-464-ninshu-the-ninja-creed-696237?ssid=206033" title="Deutsch">Deutsch</a>
		  </span>
		</div>
		
		We need to obtain all the SSID's.

		We return all the id's as a list along with the respective Language title attached.

		For the above HTML we should have this -

		[['206027', 'English (US)'], ['206015', 'العربية'], ['206733', 'Italiano'], ['206033', 'Deutsch']]


		"""

		try:
			ssid = []
			container = self.soupObject.find("span",attrs={"class":"showmedia-subtitle-text"})
			links = container.findAll("a")
			
			for i in links:

				#Processing the link to get the Subtitle ID's.
				rawLink = i['href']
				junk, partition, requiredID = rawLink.partition("ssid=")
				ssid.append([requiredID,i['title']])
		

		except:
			pass
		
		return ssid		


	# def getContentID2(self):

	# 	"""
	# 	This is the alternative method to obtain the contentID. 
	# 	Sample line 1) - <link href="http://ib3.huluim.com/video/60585710?region=US&amp;size=220x124"
	# 	Sample line 2) - <link href="http://ib3.huluim.com/movie/60535322?region=US&amp;size=220x318"
	# 	Required content ID's are 60585710 & 60535322 respectively.

	# 	Partition technique is used to obtain the content ID.
	# 	"""
	# 	fh = open(self.requestsFileName, "r")		
	# 	listOfOptions = ["video/","movie/"]
	# 	foundContent = False
	# 	contentId = ""
	# 	for line in fh:
			
	# 		for option in listOfOptions:
	# 			junkText, separator, contentIdContainer = line.partition(option)
	# 			#The Content Id has been found.
	# 			if contentIdContainer:
	# 				foundContent = True
	# 				break
			
	# 		#The Content ID has been found. No need to read the file anymore.
	# 		#Get the Content ID from the container 			
	# 		if foundContent:    
	# 			contentId,separator, junkText = contentIdContainer.partition("?")
	# 			if separator:
	# 				break
	# 			else:
	# 				foundContent = False		
		
	# 	return contentId
		
	# 	pass


	# def getSmiSubtitlesLink(self):
		
	# 	"""
	# 	This function returns the SMI subtitle link based on the contentID.
	# 	Currently, the link resides in the xmlLinkTemplate variable
		
	# 	The XML Link for any subtitle video is - "http://www.hulu.com/captions.xml?content_id=CONTENTID"
	# 	Where, CONTENTID is the unique content_ID of the video.
		
	# 	"""

	# 	smiLink = ""
	# 	xmlLinkTemplate = "http://www.hulu.com/captions.xml?content_id="
	# 	xmlLink = xmlLinkTemplate + str(self.contentID)
	# 	xmlRequest = requests.get(xmlLink)
	# 	if self.debug:
	# 		print(xmlRequest.text)
	# 	smiSoup = BeautifulSoup(xmlRequest.text)
		
	# 	li = smiSoup.find("transcripts")
	# 	listOfLanguages = li.findChildren()
		
	# 	if self.debug:
	# 		print(listOfLanguages)
		
		
	# 	#If more than one language subtitles are present, the user can choose the desired language.
	# 	if len(listOfLanguages)>1:

	# 		print("<<<------ Choose the corressponding number for selecting the language ----->>>")
			
	# 		for languages in range(len(listOfLanguages)):
	# 			print("<%d> - %s"%(languages+1,listOfLanguages[languages].name))

	# 		optionChoice = input()
	# 		try:
	# 			optionChoice = int(optionChoice)
	# 		except:
	# 			print("You have entered an invalid option. Application will exit.")
	# 			exit()

	# 		if self.debug:
	# 			print(smiSoup.find(listOfLanguages[optionChoice-1].name).string)
			
	# 		try:
	# 			smiLink = smiSoup.find(listOfLanguages[optionChoice-1].name).string
			
	# 		except:
	# 			print("You have entered an invalid option. Application will exit.")
	# 			exit()
		
	# 	else:
			
	# 		if smiSoup.en:
	# 			smiLink = smiSoup.en.string
		
	# 	return smiLink
		
	# 	pass

	# def transformToVtt(self,smiLink):
		
	# 	"""
	# 	This function takes an smiLink and returns the corressponding subtitles in VTT format(a link)
	# 	Source - http://stream-recorder.com/forum/hulu-subtitles-t20120.html
		
	# 	http://assets.huluim.com/"captions"/380/60601380_US_en_en."smi"  -----> 
	# 	http://assets.huluim.com/"captions_webvtt"/380/60601380_US_en_en."vtt"
		
	# 	captions --> captions_webvtt
	# 	smi      --> vtt

	# 	"""
	# 	#print(smiLink)
	# 	vttLink = ""
	# 	replaceDict = {"captions":"captions_webvtt", "smi":"vtt"}

	# 	for keys in replaceDict:
	# 		smiLink = smiLink.replace(keys,replaceDict[keys])

	# 	vttLink = smiLink
	# 	#print(vttLink)

	# 	return vttLink	

	# 	pass

	# def createVttSubtitleFile(self,vttLink):

	# 	"""
	# 	This function fetches the captions and writes them into a file in VTT format
	# 	"""

	# 	requestObjectv = requests.get(vttLink)
	# 	#print(requestObjectv.text)

	# 	subsFileHandler = open(self.title + ".vtt","w")
	# 	subsFileHandler.write(requestObjectv.text)
	# 	subsFileHandler.close()

	# 	pass
	
	# def convertVttToSrt(self):

	# 	"""
	# 	This function converts the VTT subtitle file into SRT format.
	# 	Credits - http://goo.gl/XRllyy for the conversion method.
	# 	"""

	# 	f =  open(self.title + ".vtt","r")
	# 	fh = open(self.title + ".srt","w")
	# 	print("Creating ~  '%s.srt' ..."%(self.title))
		
	# 	count = 1

	# 	#Removing WEBVTT Header line.
	# 	for line in f.readlines():
	# 		if line[:6] == 'WEBVTT':
	# 			continue

	# 		#Substituting '.' with ',' in the time-stamps
	# 		line = re.sub(r'(:\d+)\.(\d+)', r'\1,\2', line)

	# 		#Printing the header number in each line. This is required for the SRT format.
	# 		if line == '\n':	
	# 			fh.write("\n" + str(count)+"\n")
	# 			count += 1
	# 		else:
	# 			fh.write(line.strip()+"\n")

	# 	f.close()
	# 	fh.close()

	def getTitle(self):

		"""
		This function returns the title of the video. This is also used for naming the file.

		<title>Crunchyroll - Watch Naruto Shippuden: Season 17 Episode 464 - Ninshu: The Ninja Creed</title>
		
		"""

		
		try:
			self.title = self.soupObject.title.string.strip()

		except:
			self.title = "CrunchyRollSubtitles"

		pass

	# def deleteUnnecessaryfiles(self):

	# 	if not self.debug:
	# 		try:
	# 			os.remove(self.requestsFileName)
	# 			os.remove(self.title+".vtt")
	# 		except:
	# 			pass