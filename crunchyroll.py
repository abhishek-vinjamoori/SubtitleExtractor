import os
import re
import requests
from bs4 import BeautifulSoup
import base64
import zlib

from hashlib import sha1


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

		self.standardCheck(self.ssidList)

		captionsLink = self.getSubtitleLink()
		if self.debug:
			print(captionsLink)
		
		self.standardCheck(captionsLink)		
		
		self.createEncryptedSubtitleFile(captionsLink)
		
		#s=self.decryptSubtitleData()
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


	def getSubtitleLink(self):
		
		"""
		This function returns the SMI subtitle link based on the contentID.
		Currently, the link resides in the xmlLinkTemplate variable
		
		The XML Link for any subtitle video is - "http://www.hulu.com/captions.xml?content_id=CONTENTID"
		Where, CONTENTID is the unique content_ID of the video.
		
		"""
		print("<<<------ Choose the corressponding number for selecting the language ----->>>")
			
		for languages in range(len(self.ssidList)):
			print("<%d> - %s"%(languages+1,self.ssidList[languages][1]))

		optionChoice = input()
		
		try:
			optionChoice = int(optionChoice)
		
		except:
			print("You have entered an invalid option. The first available option will be downloaded.")
			optionChoice = 1
		
		try:
			xmlLink = self.subtitleSource + str(self.ssidList[optionChoice-1][0])
		
		except:
			print("You have entered an invalid option. The first available option will be downloaded.")
			optionChoice = 1
		

		xmlLink = self.subtitleSource + str(self.ssidList[optionChoice-1][0])
		return xmlLink

		
		pass


	def createEncryptedSubtitleFile(self,Link):

		"""
		This function fetches the encrypted captions and writes them into a file.
		"""

		requestObjectv = requests.get(Link)
		#print(requestObjectv.text)

		subsFileHandler = open(self.title + ".txt","w")
		
		soupData = BeautifulSoup(requestObjectv.text,from_encoding="utf8")
		self.encryptedData = soupData.data.string
		subsFileHandler.write(self.encryptedData)
		subsFileHandler.close()

		#Required parameters for decrypting the subtitles
		self.subtitleId = soupData.subtitle['id']
		self.subtitleIV = soupData.iv.string

		if self.debug:
			print(self.subtitleId)
			print(self.subtitleIV)
		pass
	


	# def decryptSubtitleData(self):
		
	# 	self.encryptedData = bytes_to_intlist(base64.b64decode(self.encryptedData.encode('utf-8')))
	# 	self.subtitleIV = bytes_to_intlist(base64.b64decode(self.subtitleIV.encode('utf-8')))
	# 	self.subtitleId = int(self.subtitleId)

	# 	def obfuscate_key_aux(count, modulo, start):
	# 		output = list(start)
	# 		for _ in range(count):
	# 			output.append(output[-1] + output[-2])
	# 		# cut off start values
	# 		output = output[2:]
	# 		output = list(map(lambda x: x % modulo + 33, output))
	# 		return output

	# 	def obfuscate_key(key):
	# 		num1 = int(floor(pow(2, 25) * sqrt(6.9)))
	# 		num2 = (num1 ^ key) << 5
	# 		num3 = key ^ num1
	# 		num4 = num3 ^ (num3 >> 3) ^ num2
	# 		prefix = intlist_to_bytes(obfuscate_key_aux(20, 97, (1, 2)))
	# 		shaHash = bytes_to_intlist(sha1(prefix + str(num4).encode('ascii')).digest())
	# 		# Extend 160 Bit hash to 256 Bit
	# 		return shaHash + [0] * 12

	# 	key = obfuscate_key(self.subtitleId)

	# 	decrypted_data = intlist_to_bytes(aes_cbc_decrypt(key))
	# 	return zlib.decompress(decrypted_data)


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

	def deleteUnnecessaryfiles(self):

		if not self.debug:
			try:
				os.remove(self.requestsFileName)
			except:
				pass


	def standardCheck(self,variableToCheck):

		if not variableToCheck:
			print("Unable to fetch the subtitles.")
			self.deleteUnnecessaryfiles()
			exit()


	# def aes_cbc_decrypt(self,key):
 #    """
 #    Decrypt with aes in CBC mode

 #    @param {int[]} data        cipher
 #    @param {int[]} key         16/24/32-Byte cipher key
 #    @param {int[]} iv          16-Byte IV
 #    @returns {int[]}           decrypted data
 #    """
	# 	expanded_key = key_expansion(key)
	# 	block_count = int(ceil(float(len(data)) / BLOCK_SIZE_BYTES))

	# 	decrypted_data = []
	# 	previous_cipher_block = self.subtitleIV
	# 	for i in range(block_count):
	# 		block = data[i * BLOCK_SIZE_BYTES: (i + 1) * BLOCK_SIZE_BYTES]
	# 		block += [0] * (BLOCK_SIZE_BYTES - len(block))

	# 		decrypted_block = aes_decrypt(block, expanded_key)
	# 		decrypted_data += xor(decrypted_block, previous_cipher_block)
	# 		previous_cipher_block = block
	# 	decrypted_data = decrypted_data[:len(data)]

	# 	return decrypted_data