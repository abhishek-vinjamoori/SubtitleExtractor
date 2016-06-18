import mechanize
import cookielib
import getpass
import sys
import urllib
import urllib2
import re

# Cookie Jar
useCookie = False
host = 'www.amazon.com'
url = "https://www.amazon.com/dp/B000I9WVAK?autoplay=1&t=26"
cj = cookielib.LWPCookieJar()
#if useCookie and os.path.isfile(COOKIEFILE):
#	cj.load(COOKIEFILE, ignore_discard=True, ignore_expires=True)
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)'),
                        ('Host', host)]
usock = opener.open(url)#,timeout=30)
response = usock.read()
usock.close()
# username = "asdadsi@gmail.com"
# password = "adadsasda"
# br.add_password('https://www.amazon.com/gp/sign-in.html', username, password)
# # browser.select_form(name="signIn")  
# # browser["email"] = username  #provide email
# # browser["password"] = password #provide passowrd
# # Browser
# url = br.open( "https://www.amazon.com/dp/B000I9WVAK?autoplay=1&t=26" ) 
# returnPage = url.read() 

fileHandler = open("req.txt", "w")
#soupObject = BeautifulSoup(returnPage)
fileHandler.write(response)
fileHandler.close()


s = re.compile("'flashVars', '(.*?)' \+ new Date\(\)\.getTime\(\)\+ '(.*?)'",re.DOTALL).findall(response)
# fileHandler = open("req.txt", "w")
# #soupObject = BeautifulSoup(returnPage)
# fileHandler.write(s)
# fileHandler.close()
