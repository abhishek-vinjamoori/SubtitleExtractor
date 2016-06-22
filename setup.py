#! /usr/bin/env python3


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from configparser import SafeConfigParser




def amazonUpdate():

	#Initialising the parser
	parser = SafeConfigParser()
	parser.read('userconfig.ini')
	
	parsingDictionary = {"service":"AMAZON"}

	#Required variables for filling in config file
	baseurl  = parser.get(parsingDictionary['service'], 'url')
	username = parser.get(parsingDictionary['service'], 'username')
	password = parser.get(parsingDictionary['service'], 'password')

	parser.read('config.ini')
	customerUrl = parser.get(parsingDictionary['service'], 'customerUrl')

	xpaths = { 'usernameBox' : "//*[@id='ap_email']",
	           'passwordBox' : "//*[@id='ap_password']",
	           'submitButton' :   "//*[@id='signInSubmit']"
	         }

	amazonDriver = webdriver.Firefox()
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
	print(pageSource)
	amazonDriver.close()


def main():

	updateServices = {"amazon":amazonUpdate}

	for services in updateServices:
		updateServices[services]()
	pass
if __name__ == "__main__":
	main()