import urllib2
from bs4 import BeautifulSoup
# http://segfault.in/2010/07/parsing-html-table-in-python-with-beautifulsoup/

f = open('cricket-data.txt','w')
linksFile = open("linksSource.txt")
lines = list(linksFile.readlines())
for i in lines[12:108]: #12:108
	url = "http://www.gunnercricket.com/"+str(i)
	try:
		page = urllib2.urlopen(url)
	except:
		continue
	soup = BeautifulSoup(page)
	title = soup.title
	date = title.string[:4]+',' #take first 4 characters from title
	
	try:
		table = soup.find('table')
		rows = table.findAll('tr')

		for tr in rows:
			cols = tr.findAll('td')
			text_data = []
			for td in cols:
				text = ''.join(td)
				utftext = str(text.encode('utf-8'))
				text_data.append(utftext) # EDIT
			text = date+','.join(text_data)
			f.write(text + '\n') 
	except:
		pass
f.close()
