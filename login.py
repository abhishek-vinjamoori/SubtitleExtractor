import cookielib
import urllib2
import re

# Cookie Jar
useCookie = False
host = 'www.amazon.com'
url = "https://www.amazon.com/dp/B000I9WVAK?autoplay=1&t=26"
cj = cookielib.LWPCookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [(
    'User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)'),
    ('Host', host)]
usock = opener.open(url)
response = usock.read()
usock.close()

fileHandler = open("req.txt", "w")
fileHandler.write(response)
fileHandler.close()


s = re.compile(
    "'flashVars', '(.*?)' \+ new Date\(\)\.getTime\(\)\+ '(.*?)'", re.DOTALL).findall(response)
