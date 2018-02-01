from twython import Twython
import urllib2
import sys

reload(sys)
sys.setdefaultencoding('utf8')

# get the keys on https://apps.twitter.com/
C_key = ""
C_secret = ""
A_token = ""
A_secret = ""

myTweet = Twython(C_key,C_secret,A_token,A_secret)
hashtag = " #ESP8266 #RaspberryPi"

while True:
    url = 'https://en.wikipedia.org/w/api.php?&action=query&format=xml&prop=extracts&generator=search&exsentences=1&exintro=1&generator=random&exlimit=10&explaintext&grnnamespace=0'
    response = urllib2.urlopen(url)
    html = response.read()
    html = html.encode('utf-8')
    html = html.split("preserve",1)[1]
    html = html[2:-39].replace("&quot;", "'")

    if html.find("refers to:") == -1 and html.find("This is a list of") == -1 and html.endswith('.') and len(html) <= 258:
        break

html = html + hashtag
myTweet.update_status(status=html)
