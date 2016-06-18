import http.cookiejar
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse

amazon_username = "harshi@gmail.com"
amazon_password = "dsdfsdfsd96"

login_data = urllib.parse.urlencode({'action': 'sign-in',
                               'email': amazon_username,
                               'password': amazon_password,
                               })

cookie = http.cookiejar.CookieJar()    
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

response = opener.open('https://www.amazon.com/gp/sign-in.html')
print((response.getcode()))

response = opener.open('https://www.amazon.com/gp/flex/sign-in/select.html', login_data)
print((response.getcode()))

response = opener.open("https://www.amazon.com/") # it should show that you are logged in
print((response.getcode()))
