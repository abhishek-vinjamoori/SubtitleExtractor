from SubtitleExtractor import Subtitle
from HuluTest import testList

Extractor = Subtitle()

counter = 0
failureList = []

for entities in testList:
	
	url = entities[0]
	Extractor.getServiceName(url)
	Extractor.testMode = True
	# if len(entities) == 5:
	returnValue = Extractor.serviceProcess()

	if returnValue:
		print("File %d successful"%(counter+1))
	else:
		print("Test Failed on File - %d"%(counter+1))
		failureList.append(counter+1,url)

	counter += 1
