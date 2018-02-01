import mechanize,re,urllib2
from time import sleep
#Make a Browser (think of this as chrome or firefox etc)
br = mechanize.Browser()

#visit http://stockrt.github.com/p/emulating-a-browser-in-python-with-mechanize/
#for more ways to set up your br browser object e.g. so it look like mozilla
#and if you need to fill out forms with passwords.

br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

# Open your site
br.open('http://www.fia.com/championship/fia-formula-1-world-championship/2013/2013-brazilian-grand-prix-event-information')

f=open("source.html","w")
f.write(br.response().read()) #can be helpful for debugging maybe

filetypes=[".pdf"] #you will need to do some kind of pattern matching on your files
myfiles=[]

links=re.findall(r'\'http[^\']+', str(br.response().read())) #re.findall(r'http[s]?://[^\s<>"]+|www\.[^\s<>"]+', str(STRING))
f=open('test.txt','w')
for l in links:
	l=l.strip("'")
	for t in filetypes:
		if t in str(l):
			if l not in myfiles:
				myfiles.append(l)
f.write("\n".join(myfiles))				
f.close()
print myfiles

#then wget -i test.txt