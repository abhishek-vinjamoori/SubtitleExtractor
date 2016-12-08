import http.cookiejar
import urllib.request
import urllib.parse
import urllib.error
import urllib.request
import urllib.error
import urllib.parse

amazon_username = "i@gmail.com"
amazon_password = "32refdvfdgre"

login_data = urllib.parse.urlencode({'action': 'sign-in',
                                     'email': amazon_username,
                                     'password': amazon_password,
                                     })

binary_data = login_data.encode("utf-8")
cookie = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cookie))
opener.addheaders = [
    ('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')]

response = opener.open('https://www.amazon.com/gp/sign-in.html')
# print((response.getcode()))

response = opener.open(
    'https://www.amazon.com/gp/flex/sign-in/select.html', binary_data)
# print((response.getcode()))

response = opener.open("https://www.amazon.com/")
                       # it should show that you are logged in
print((response.read().decode("utf8")))
