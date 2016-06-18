#ScriptName : Login.py
#---------------------
from selenium import webdriver

#Following are optional required
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

baseurl = "https://www.amazon.com/gp/sign-in.html"
username = "asdasdasdas@gmail.com"
password = "dasdasd"



xpaths = { 'usernameTxtBox' : "//*[@id='ap_email']",
           'passwordTxtBox' : "//*[@id='ap_password']",
           'submitButton' :   "//*[@id='signInSubmit']"
         }

mydriver = webdriver.PhantomJS()
mydriver.get(baseurl)
mydriver.maximize_window()
	#Clear Username TextBox if already allowed "Remember Me" 
mydriver.find_element_by_xpath(xpaths['usernameTxtBox']).clear()

#Write Username in Username TextBox
mydriver.find_element_by_xpath(xpaths['usernameTxtBox']).send_keys(username)

#Clear Password TextBox if already allowed "Remember Me" 
mydriver.find_element_by_xpath(xpaths['passwordTxtBox']).clear()

#Write Password in password TextBox
mydriver.find_element_by_xpath(xpaths['passwordTxtBox']).send_keys(password)

#Click Login button
mydriver.find_element_by_xpath(xpaths['submitButton']).click()
