import urllib2
import sys

def cleanupString(string):
    string = urllib2.unquote(string).decode('utf8')
    return HTMLParser.HTMLParser().unescape(string).encode(sys.getfilesystemencoding())