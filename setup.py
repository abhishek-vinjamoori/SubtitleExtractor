#! /usr/bin/env python3


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from configparser import SafeConfigParser
import os,sys
from bs4 import BeautifulSoup
import json

filename = "temporaryFile.html"

def amazonUpdate():

	#Initialising the parser
	userParser = SafeConfigParser()
	userParser.read('userconfig.ini')
	userParser.optionxform = str
	parsingDictionary = {"service":"AMAZON"}

	#Required variables for filling in config file
	baseurl  = userParser.get(parsingDictionary['service'], 'url')
	username = userParser.get(parsingDictionary['service'], 'username')
	password = userParser.get(parsingDictionary['service'], 'password')

	parser = SafeConfigParser()
	parser.read('config.ini')
	parser.optionxform = str
	customerUrl = parser.get(parsingDictionary['service'], 'customerurl')
	tokenUrl = parser.get(parsingDictionary['service'], 'tokenurl')
	
	xpaths = { 'usernameBox' : "//*[@id='ap_email']",
	           'passwordBox' : "//*[@id='ap_password']",
	           'submitButton' :   "//*[@id='signInSubmit']"
	         }
	
	firefox_profile = webdriver.FirefoxProfile()
	firefox_profile.set_preference('permissions.default.stylesheet', 2)
	firefox_profile.set_preference('permissions.default.image', 2)
	firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')


	amazonDriver = webdriver.Chrome()
	amazonDriver.userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:36.0) Gecko/20100101 Firefox/36.0 WebKit'
	amazonDriver.cookiesEnabled = True
	amazonDriver.javascriptEnabled = True
	amazonDriver.get(baseurl)
	#Clearing Username TextBox 
	amazonDriver.find_element_by_xpath(xpaths['usernameBox']).clear()

	#Typing in the username as obtained from config file
	amazonDriver.find_element_by_xpath(xpaths['usernameBox']).send_keys(username)

	#Clearing password field 
	amazonDriver.find_element_by_xpath(xpaths['passwordBox']).clear()

	#Typing in the password
	amazonDriver.find_element_by_xpath(xpaths['passwordBox']).send_keys(password)
	
	#Clicking on Submit button
	amazonDriver.find_element_by_xpath(xpaths['submitButton']).click()
	amazonDriver.get(customerUrl)
	pageSource = amazonDriver.page_source
	pageSource = BeautifulSoup(pageSource).pre.text
	#print(pageSource)

	#Removing escaped characters like \n \t and literal double quotes
	pageSource = pageSource.replace('\\"',"").replace('\\n',"").replace('\\t',"")
	
	obtainFrom = ["customerInfo","customerID"]
	try:
		parsedSource = json.loads(pageSource)
		customerID = parsedSource[obtainFrom[0]][obtainFrom[1]]
		#print(customerID)
		parser.set(parsingDictionary['service'], 'customerid', customerID)
		amazonDriver.get(tokenUrl)
		pageSource = amazonDriver.page_source
		token = BeautifulSoup(pageSource).pre.text
		tokenId = token.replace("onWebToken_fccab172c7f94fe78ff8dc7d985dd3e4","").replace('(',"").replace(")","").replace(';',"")
		token = json.loads(tokenId)
		token = token['token']
		parser.set(parsingDictionary['service'], 'token', token)
		fileHandler = open('config.ini',"w") 
		parser.write(fileHandler)
		fileHandler.close()

	except ZeroDivisionError:
		print("An error ocurred. Please report the issue.")
		pass
	amazonDriver.close()


def main():

	updateServices = {"amazon":amazonUpdate}

	for services in updateServices:
		updateServices[services]()
	
	# try:
	# 	os.remove(filename)
	# except:
	# 	pass

	pass
if __name__ == "__main__":
	main()
