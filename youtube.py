import os
import re
import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse

class youtubeExtractor(object):
	
	"""docstring for YouTubeExtractor"""
	
	def __init__(self,url):

		print("YouTubes processing")
		self.loginRequired = False
		self.urlName = url
		self.requestsFileName = "iDoNotExistDefinitelyOnThisComputerFolder.html"

		pass

	def getSubtitles(self):

		"""
		The main function which uses helper functions to get the subtitles
		"""

		self.createSoupObject()
		
		self.getTitle()

		rawLink = self.getRawSubtitleLink()
		rawLink = urllib.parse.unquote(rawLink)
		rawLink = rawLink.replace("\\u0026","&")
		decodedLink = rawLink.replace("\\","")
		print(decodedLink)
		return 0
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

	def getRawSubtitleLink(self):
		
		"""
		This function returns the SMI subtitle link based on the contentID.
		Currently, the link resides in the xmlLinkTemplate variable
		
		The XML Link for any subtitle video is - "http://www.hulu.com/captions.xml?content_id=CONTENTID"
		Where, CONTENTID is the unique content_ID of the video.
		
		"""

		rawLink = ""
		
		self.soupObject.findAll("scripts")
		print()
		fh = open(self.requestsFileName,"r")

		for lines in fh:
			
			if "timed" in lines:
				lis  = lines.split('"')
				captionPosition = 0
				for i in range(len(lis)):
					if "TTS_URL" in lis[i]:
						captionPosition = i+1
						break
				rawLink = str(lis[captionPosition])

		fh.close()
		
		return rawLink
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

		<meta name="twitter:title" value="Interstellar"/>   --> Extracting the value from here
		
		"""

		#print(self.soupObject.title.string)
		self.title = "YouTube_subtitles"

		pass

	def deleteUnnecessaryfiles(self):

		if not self.debug:
			try:
				os.remove(self.requestsFileName)
				os.remove(self.title+".vtt")
			except:
				pass