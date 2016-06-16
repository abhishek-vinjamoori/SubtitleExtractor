import os
import re
import requests
from bs4 import BeautifulSoup


class netflixExtractor(object):
	
	"""docstring for netflixExtractor"""
	
	def __init__(self,url):
		print("Netflix processing")
		self.loginRequired = False
		self.urlName = url
		self.requestsFileName = "iDoNotExistDefinitelyOnThisComputerFolder.html"
		pass 

	def getSubtitles(self):
		requestObject = requests.get(self.urlName)
		
		self.fileHandler = open(self.requestsFileName, "w")
		soupObject = BeautifulSoup(requestObject.text)
		self.fileHandler.write(str(soupObject))
		self.fileHandler.close() 
		return 0
		pass
