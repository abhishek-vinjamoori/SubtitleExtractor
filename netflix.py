import os
import requests

class netflixExtractor(object):
	
	"""docstring for netflixExtractor"""
	
	def __init__(self,url):
		print("Netflix processing")
		self.loginRequired = True
		self.urlName = url
		pass 

	def getSubtitles(self):
		requestObject = requests.get(self.urlName)
		
		self.fileHandler = open("requests.txt", "w")
		self.fileHandler.write(requestObject.text)
		self.fileHandler.close() 
		pass
