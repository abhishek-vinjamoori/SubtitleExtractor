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
		self.languageDict = {'sr': 'Serbian', 'th': 'Thai', 'gu': 'Gujarati', 'vi': 'Vietnamese', 'ps': 'Pashto', 'ha': 'Hausa', 'bg': 'Bulgarian', 'la': 'Latin', 'pl': 'Polish', 'ja': 'Japanese', 'km': 'Khmer', 'xh': 'Xhosa', 'ka': 'Georgian', 'gd': 'Scottish+Gaelic', 'hmn': 'Hmong', 'ceb': 'Cebuano', 'bn': 'Bengali', 'el': 'Greek', 'sq': 'Albanian', 'si': 'Sinhala', 'yi': 'Yiddish', 'cy': 'Welsh', 'ig': 'Igbo', 'uz': 'Uzbek', 'lb': 'Luxembourgish', 'su': 'Sundanese', 'hr': 'Croatian', 'ru': 'Russian', 'et': 'Estonian', 'ht': 'Haitian+Creole', 'no': 'Norwegian', 'hi': 'Hindi', 'tg': 'Tajik', 'mi': 'Maori', 'ga': 'Irish', 'ar': 'Arabic', 'haw': 'Hawaiian', 'bs': 'Bosnian', 'id': 'Indonesian', 'so': 'Somali', 'yo': 'Yoruba', 'st': 'Southern+Sotho', 'jv': 'Javanese', 'hu': 'Hungarian', 'pa': 'Punjabi', 'mt': 'Maltese', 'am': 'Amharic', 'fil': 'Filipino', 'uk': 'Ukrainian', 'fy': 'Western+Frisian', 'ky': 'Kyrgyz', 'my': 'Burmese', 'nl': 'Dutch', 'mk': 'Macedonian', 'da': 'Danish', 'sv': 'Swedish', 'ta': 'Tamil', 'co': 'Corsican', 'af': 'Afrikaans', 'lo': 'Lao', 'lv': 'Latvian', 'hy': 'Armenian', 'iw': 'Hebrew', 'eu': 'Basque', 'kn': 'Kannada', 'mr': 'Marathi', 'sw': 'Swahili', 'ny': 'Nyanja', 'az': 'Azerbaijani', 'es': 'Spanish', 'te': 'Telugu', 'zh': 'Chinese', 'it': 'Italian', 'be': 'Belarusian', 'sl': 'Slovenian', 'cs': 'Czech', 'lt': 'Lithuanian', 'ur': 'Urdu', 'ko': 'Korean', 'de': 'German', 'sd': 'Sindhi', 'fa': 'Persian', 'ms': 'Malay', 'sm': 'Samoan', 'fi': 'Finnish', 'kk': 'Kazakh', 'pt': 'Portuguese', 'ro': 'Romanian', 'tr': 'Turkish', 'en': 'English', 'gl': 'Galician', 'fr': 'French', 'zu': 'Zulu', 'ne': 'Nepali', 'mn': 'Mongolian', 'eo': 'Esperanto', 'sk': 'Slovak', 'ca': 'Catalan', 'ml': 'Malayalam', 'sn': 'Shona', 'ku': 'Kurdish', 'mg': 'Malagasy', 'is': 'Icelandic'}
		self.debug = False	
		pass

	def getSubtitles(self):

		"""
		The main function which uses helper functions to get the subtitles
		"""

		self.createSoupObject()
		
		self.getTitle()
		print(self.title)
		
		rawLink = self.getRawSubtitleLink()
		decodedLink = self.decodeLink(rawLink)
		if self.debug:
			print(decodedLink)
		
		stringToAppend = self.checkAvailableLanguages()
		FinalUrl = self.getFinalUrl(decodedLink,stringToAppend)
		
		print(FinalUrl)
		# if not smiLink:
		# 	print("Unable to fetch the subtitles. No subtitles present.")
		# 	self.deleteUnnecessaryfiles()
		# 	return 0

		self.downloadXMLTranscript(FinalUrl)
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
		self.uglyString = ""

		searchStringList = ["timed","TTS_URL","caption_tracks"]
		print()
		fh = open(self.requestsFileName,"r")

		for lines in fh:
			
			if searchStringList[0] in lines and searchStringList[1] in lines :
				lis  = lines.split('"')
				captionPosition = 0
				for i in range(len(lis)):
					if searchStringList[1] in lis[i]:
						captionPosition = i+1
						break
					
				rawLink = str(lis[captionPosition])

			elif searchStringList[0] in lines:
				lis = lines.split('"')
				position = 0
				#print(lis)
				for i in range(len(lis)):
					if searchStringList[2] in lis[i]:
						position = i+2
						break
				if position:
					self.uglyString = str(lis[position])

		fh.close()

		return rawLink
		
		pass

	def decodeLink(self,rawLink):

		rawLink = urllib.parse.unquote(rawLink)
		rawLink = rawLink.replace("\\u0026","&")
		decodedLink = rawLink.replace("\\","")
		
		return decodedLink
		pass


	def checkAvailableLanguages(self):
		
		print("<<<------ Choose the corressponding number for selecting the language ----->>>")
		
		self.uglyString = urllib.parse.unquote(str(self.uglyString))
		self.uglyString = self.uglyString.replace("\\u0026","&")
		self.uglyString = self.uglyString.replace("\\","")

	#	print(self.uglyString)
		lang = self.uglyString.split("&")
		availableLangList = []
		for info in lang:
			if info.startswith( 'lang' ):
				availableLangList.append(info)
		if self.debug:
			print(availableLangList)
		for languages in range(len(availableLangList)):
			
			langKey,equalKey,Language = availableLangList[languages].partition("=")
			#print(Language)
			LanguageKey,hyphenKey,randomVar = Language.partition("-")
			#print(LanguageKey)
			print("<%d> - "%(languages+1),end="")

#			[languageDict[k] for k in languageDict.keys() if 'zh' in k]
			if LanguageKey in self.languageDict.keys():
				print(self.languageDict[LanguageKey],end="  ")
			print("(%s)"%(Language))

		optionChoice = input()
		try:
			optionChoice = int(optionChoice)
		except:
			print("You have entered an invalid option. Application will download the first option available.")
			optionChoice = 1			

		if self.debug:
		 	print(availableLangList[optionChoice-1])
			
		return availableLangList[optionChoice-1] 
		# try:
		# 	smiLink = smiSoup.find(listOfLanguages[optionChoice-1].name).string
		
		# except:
		# 	print("You have entered an invalid option. Application will exit.")
		# 	exit()
		
		# return smiLink		

	def getFinalUrl(self, Link,subString):
	
		Link += "&"
		Link += subString
		return Link

		pass

	def downloadXMLTranscript(self,FinalUrl):

		"""
		This function fetches the captions and writes them into a file in VTT format
		"""

		requestObjectv = requests.get(FinalUrl)
		#print(requestObjectv.text)

		subsFileHandler = open(self.title + ".xml","w")
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
		try:
			titleString = self.soupObject.title.string
			self.title = titleString.replace(" - YouTube","")			
		except:
			pass

		pass

	def deleteUnnecessaryfiles(self):

		if not self.debug:
			try:
				os.remove(self.requestsFileName)
				os.remove(self.title+".vtt")
			except:
				pass