import urllib
import urllib2
import bs4

startreg = 11161667
endreg = 11170000

for i in range(startreg, endreg):
    istr = str(i)
    soup = bs4.BeautifulSoup(urllib2.urlopen(urllib2.Request('http://www.annauniv.edu/cgi-bin/786786786/cet1.pl',urllib.urlencode ({'regno' : i, 'dob' : '14-09-1991' }))).read())
    if(soup.find('span') != None):
       print 'found it ' + istr
       doc = open('matches.txt','a')
       doc.write("\n"+ istr)
       doc.close()      
    else: print 'not ' + istr