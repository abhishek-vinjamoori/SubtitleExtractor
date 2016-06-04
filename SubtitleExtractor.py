import os
from netflix import netflixExtractor
from hulu import huluExtractor
from youtube import youtubeExtractor
#import amazon
#import bbc
#import hbo
#import crackle
#import vudu
#import epix
#import syfy
#import sky
#import shomi
#import fox

print("Downloading Subtitles")

class Subtitle(object):
	
	"""This is the main class which holds all the information for the main module"""
	
	def __init__(self):
		self.urlName = ""
		self.serviceType = ""
		self.supportedServices = {"netflix":netflixExtractor,"hulu":huluExtractor,"youtube":youtubeExtractor}
		#,"amazon","bbc","hbo","crackle","vudu","epix","syfy","sky","shomi","fox"]


	def getServiceName(self):
		self.urlName = input("Paste the link here : ")
		for names in self.supportedServices:
			if names in self.urlName:
				self.serviceType = names
				break


	def serviceProcess(self):
		if self.serviceType:
			self.serviceClass = self.supportedServices[self.serviceType]()
		else:
			print("Service Not Supported")




def main():

	#try:
	Extractor = Subtitle()
	Extractor.getServiceName()
	if Extractor.serviceType:
		print(Extractor.serviceType)

	Extractor.serviceProcess()


	# except:
	# 	print("An error occurred")
	# 	pass

if __name__ == "__main__":
	main()