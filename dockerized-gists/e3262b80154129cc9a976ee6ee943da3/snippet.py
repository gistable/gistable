import requests
from bs4 import BeautifulSoup

url = "http://www.azlyrics.com/lyrics/onyx/bacdafucup.html"

print "Default request (it will fail)..."

# make the default request
try:
    r = requests.get(url)
except requests.exceptions.RequestException as e:
    print e

print "User-Agent request (it will pass)..."

# act like a mac
headers = {'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.112 Safari/534.30"}

# make a request for the data
r = requests.get(url, headers=headers)

# convert the response text to soup
soup = BeautifulSoup(r.text, "lxml")

# get the goods
for goods in soup.find_all("div", {"class":None}):
    if len(goods.text) == 0: pass
    print goods.text