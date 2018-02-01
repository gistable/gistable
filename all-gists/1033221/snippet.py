'''
a simple script to pull some inspiring images 
test

kawandeep virdee
@kawantum
''' 

import xml.dom.minidom as XML
import urllib2 as URL

links = []


#pull links from FFFFOUND RSS feed
response = URL.urlopen('http://feeds.feedburner.com/ffffound/everyone')
html = response.read()
doc = XML.parseString(html)

for node in doc.getElementsByTagName("item"):
	link = node.getElementsByTagName("description")
	for node2 in link:
		linkName = ""
		for node3 in node2.childNodes:
			linkName+=node3.data
		#clean up string by only getting stuff in <a>..</a>
		start = linkName.find('<a')
		end = linkName.find('</a>')+4
		linkName = reduce(lambda x,y :x+y,[linkName[i] for i in xrange(start,end)])
		links.append('<div id=image>'+ linkName+ '</div>')


#write out 
file = open("found_links.html","w")
for i in links: file.write(i)
file.close()
	
