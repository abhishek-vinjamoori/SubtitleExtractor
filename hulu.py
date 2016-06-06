import os
import re
import requests
from bs4 import BeautifulSoup


class huluExtractor(object):
	
	"""docstring for netflixExtractor"""
	
	def __init__(self,url):
		print("Detected Hulu\nProcessing....\n")
		self.loginRequired = False
		self.urlName = url
		pass

	def getSubtitles(self):
		pass