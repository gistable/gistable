import urllib2
import time
ticker = 'BAC'
string_match = 'rel="alternate"'
url = 'http://www.sec.gov/cgi-bin/browse-edgar?company=&match=&CIK=%s&owner=exclude&Find=Find+Companies&action=getcompany' % ticker
response = urllib2.urlopen(url)

for line in response:
    if string_match in line:
        for element in  line.split(';'):
            if 'CIK' in element:
                cik = element.replace('&amp','')
                print cik
