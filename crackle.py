import os
import re
import requests
from bs4 import BeautifulSoup
from configparser import SafeConfigParser
import json

class crackleExtractor(object):
	
	"""docstring for CrackleExtractor"""
	
	def __init__(self,url,testMode):
		print("Crackle processing")
		self.loginRequired    = False
		self.urlName          = url
		self.requestsFileName = "iDoNotExistDefinitelyOnThisComputerFolder.html"
		self.debug            = True
		self.testMode         = testMode
		self.MediaBase        = "https://web-api-us.crackle.com/Service.svc/details/media/"
		self.mediaStream      = "/US?format=json" 

		pass 


	def getSubtitles(self):

		"""	
		The main function which uses helper functions to get the subtitles
		"""

		self.createSoupObject()
		

		episodeID = self.getEpisodeID()
		if self.debug:
		 	print("Episode ID - ",episodeID)

		

		MediaUrl = self.getMediaURL(episodeID)
		if self.debug:
		  	print("Media URL ", MediaUrl)


		# self.getTitle()
		# if self.debug:
		# 	print("Title - ",self.title)

		self.title = "CrackleCaptions"
		self.SubtitleUrl = self.getSubtitleURL(MediaUrl)
		if self.debug:
		  	print("Subtitle URL - ",self.SubtitleUrl)

		returnValue = self.downloadXMLTranscript()

		# # #srtText = self.convertXMLToSrt(str(self.requestObjectv.text))
		# # #srtText = self._parseXml(str(self.requestObjectv.text))
		# # #print(srtText)
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

	def getEpisodeID(self):
		
		"""
		This function returns the Episode ID from the URL given.
		http://www.crackle.com/franklin-and-bash/2498587
		2498587 - EpisodeID


		"""

		searchStringList = ["/"]
		
		juknkData,Slash,episodeID = self.urlName.rpartition(searchStringList[0])
		
		return episodeID

		
		pass

	def getMediaURL(self,episodeID):

		"""
		This function makes the URL which contains the required PID
		"""
		MediaUrl      = self.MediaBase
		
		MediaUrl     += episodeID
		MediaUrl     += self.mediaStream
		
		return MediaUrl
		
		pass


	def getSubtitleURL(self,MediaUrl):

		"""
		The json content looks like this -	
	
		{"ClosedCaptionFiles":[{"Locale":"en-US","Path":"http:\/\/web-us-az.crackle.com\/1\/n\/wl\/t68wb_en-US_150506152834.xml","Default":false}]}

		"""

		#If it is a movie, we use this methodology -
		try:
			IndexingParameters = ["ClosedCaptionFiles",0,"Path"]

			subRequestObject = requests.get(MediaUrl)
			
			parsedJsonObject = json.loads(str(subRequestObject.text))
			SubsURL = parsedJsonObject[IndexingParameters[0]][IndexingParameters[1]][IndexingParameters[2]]
			
			return SubsURL

		except:
			pass
		pass
		

	def downloadXMLTranscript(self):

		"""
		This function fetches the captions and writes them into a file in XML
		"""

		try:
			self.requestObjectv = requests.get(self.SubtitleUrl)
			
			print("Creating ~  '%s.xml' ..."%(self.title))
			subsFileHandler = open(self.title + ".xml","w")
			

			if not self.requestObjectv.text:
				return 0

			self.requestObjectv = BeautifulSoup(self.requestObjectv.text)
			subsFileHandler.write(str(self.requestObjectv.prettify()))
			subsFileHandler.close()

			return 1

		except:
			return 0
		pass

	# def convertXMLToSrt(self,xml_string):
	# 	pass
	# 	#TODO
	# # def _parseXml(self,cc):
	# # 	""" INPUT: XML file with captions
	# # 	OUTPUT: parsed object like:
	# # 	[{'texlines': [u"So, I'm going to rewrite this", 'in a more concise form as'],
	# # 	'time': {'hours':'1', 'min':'2','sec':44,'msec':232} }]
	# # 	"""
	# # 	#htmlpar = HTMLParser.HTMLParser()
	# # 	cc = cc.split("</text>") # ['<text start="2997.929">So, it will\nhas time', '<text start="3000.929">blah', ..]
	# # 	captions = []
	# # 	for line in cc:
	# # 		if re.search('text', line):
	# # 			time = re.search(r'start="(\d+)(?:\.(\d+)){0,1}', line).groups() # ('2997','929')
	# # 			time = ( int(time[0]), int(0 if not time[1] else time[1]) )
	# # 			    #convert seconds and millisec to int
	# # 			text = re.search(r'">(.*)', line, re.DOTALL).group(1) # extract text i.e. 'So, it will\nhas time'
	# # 			textlines = text.split('\n')
	# # 			print(textlines)
	# # 			    #unscape chars like &amp; or &#39;
	# # 			ntime = {'hours':time[0]/3600,"min":time[0]%3600/60,"sec":time[0]%3600%60,"msec":time[1]}
	# # 			captions.append({'time':ntime,'textlines':textlines})
	# # 	return captions

	# # def _generateSrt(self,captions):
	# #     """ INPUT: array with captions, i.e.
	# #             [{'texlines': [u"So, I'm going to rewrite this", 'in a more concise form as'],
	# #             'time': {'hours':'1', 'min':'2','sec':44,'msec':232} }]
	# #         OUTPUT: srtformated string
	# #     """
	# #     caption_number = 0
	# #     srt_output = []
	# #     for caption in captions:
	# #         caption_number += 1
	# #         #CAPTION NUMBER
	# #         srt_output.append(str(caption_number))
	# #         #TIME
	# #         time_from = ( caption['time']['hours'], caption['time']['min'], caption['time']['sec'], caption['time']['msec'] ) 
	# #         if len(captions)>caption_number:
	# #             #display caption until next one
	# #             next_caption_time = captions[caption_number]['time']
	# #             time_to = ( next_caption_time['hours'], next_caption_time['min'], next_caption_time['sec'], next_caption_time['msec'] )
	# #         else:
	# #             #display caption for 2 seconds
	# #             time_to = (time_from[0],time_from[1]+2,time_from[2],time_from[3]) 
	# #         srt_output.append( (":").join([str(i) for i in time_from[0:-1]])+","+str(time_from[-1])+" --> "+(":").join([str(i) for i in time_to[0:-1]])+","+str(time_to[-1]))
	# #         #CAPTIONS
	# #         for caption_line in caption['textlines']:
	# #             srt_output.append(caption_line)
	# #         #Add two empty lines to serarate every caption showed
	# #         srt_output.append("")
	# #         srt_output.append("")
	# #     return srt_output

	def getTitle(self):

		"""
		This function returns the title of the video. This is also used for naming the file.

		<display_title>
		<title>NAME</title>
		<subtitle>OPTIONAL SUBTITLE</subtitle>
		</display_title>
		
		"""
		try:
			titleString = self.soup.programme.display_title.title.string
			try:
				titleString += self.soup.programme.display_title.subtitle.string
			except:
				pass
			titleString = titleString.strip()
			self.title  = titleString.replace("/","")

		except:
			self.title = "BBC_subtitles"
			pass

		pass

	def deleteUnnecessaryfiles(self):

		if not self.debug:
			try:
				os.remove(self.requestsFileName)
			except:
				pass
