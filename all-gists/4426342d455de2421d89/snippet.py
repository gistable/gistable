from bs4 import BeautifulSoup
import urllib.request

#import url
url = 'http://jkt48.com/news/list?lang=id'

#init request
req = urllib.request.Request(url)
resp = urllib.request.urlopen(req)
respData = resp.read()

#new class soup
soup = BeautifulSoup(respData, 'html.parser')

#find div class=contentpink
contentpink = soup.find_all('div', 'contentpink')

#set parameter 10 latest news
i = 0

#find every post news
for posting in contentpink:
	#10 latest news
	if i<10:
		#find title
		title = posting.h2
		
		#find date posted
		posted = posting.find_all('div', 'metadata')
		
		#print
		print (title.string, '-', posted[0].string)
		
		# i+1 for parameter
		i += 1
