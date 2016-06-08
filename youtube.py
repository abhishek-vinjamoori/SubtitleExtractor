import os

class youtubeExtractor(object):
	
	"""docstring for YouTubeExtractor"""
	
	def __init__(self):
		print("YouTubes processing")
		self.loginRequired = False
		self.urlName = url
		pass

	def getSubtitles(self):
		requestObject = requests.get(self.urlName)

		self.fileHandler = open("requests.txt", "w")
		self.fileHandler.write(requestObject.text)
		print(requestObject.headers)
		self.fileHandler.close() 
		
		pass
