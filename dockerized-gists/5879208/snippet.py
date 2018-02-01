import urllib2
import urllib
from cookielib import CookieJar
from xml.dom.minidom import parseString

cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

response = opener.open("http://192.168.1.100/astmanager/asterisk/mxml?action=login&username=user&secret=senha")
var = response.read()
print var

action = opener.open('http://192.168.1.100/astmanager/asterisk/mxml?action=queuestatus')
var = action.read()
dom = parseString(var)
print dom

xmlTag = dom.getElementsByTagName('response')[0].toxml()
print xmlTag