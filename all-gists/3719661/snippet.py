from HTMLParser import HTMLParser
import urllib2

class WAVersionParser(HTMLParser):
	def __init__ (self):
		HTMLParser.__init__(self)
		self.flag=0
		self.data="Symbian-"		
	def handle_starttag(self, tag, attrs):
		if(tag == "p" and attrs[0][0] == "class" and attrs[0][1] == "version"):
			self.flag=1
	def handle_data(self, data):
		if(self.flag==1):
			self.data += data[4:]
	def handle_endtag(self, tag):
		self.flag=0

p=WAVersionParser()
p.feed(urllib2.urlopen('http://www.whatsapp.com/nokia').read())
print p.data
