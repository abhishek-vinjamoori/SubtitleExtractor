def createSoupObject(url,fileName):
	
	requestObject = requests.get(url)

	# fileHandler = open("requests.txt", "w")
	# fileHandler.write(requestObject.text)
	# fileHandler.close() 
	
	soupObject = BeautifulSoup(requestObject.text,from_encoding="utf8")
	#soupObject1 = BeautifulSoup(requestObject.text,"lxml")
	#print(self.soupObject.original_encoding)

	fh = open(fileName, "w")
	fh.write(str(soupObject))
	fh.close()		

	pass

def deleteUnnecessaryfiles(debug,fileName,title,extension):

	if not debug:
		try:
			os.remove(self.fileName)
			os.remove(self.title+".vtt")
		except:
			pass
