'''
Copyright (c) 2012, Joseph W. Dougherty
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the organization nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL Joseph W. Dougherty BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import urllib, urllib2, cookielib
from BeautifulSoup import BeautifulSoup

RIN = '660123456'
PIN = '012345'
SIS = "sis.rpi.edu"
SCHEME = "https://"

cj = cookielib.CookieJar()

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

login_data = urllib.urlencode({'sid' : RIN, 'PIN' : PIN})

resp = opener.open(SCHEME + SIS +'/rss/twbkwbis.P_ValLogin', login_data)
resp = opener.open(SCHEME + SIS +'/rss/twbkwbis.P_ValLogin', login_data)

resp = opener.open(SCHEME + SIS +'/rss/bwskogrd.P_ViewTermGrde')
content = resp.read()
soup = BeautifulSoup(content)
semester = soup.find('select',attrs={"name":"term_in"})
semester = semester.findAll('option',attrs={"selected":"SELECTED"})
print "Fetching grades for semester " + semester[0].text

semester = semester[0]['value'].encode("utf8")

term_data = urllib.urlencode({'term_in' : semester})
resp = opener.open(SCHEME + SIS +'/rss/bwskogrd.P_ViewGrde',term_data)
content = resp.read()
soup = BeautifulSoup(content)
gradetables = soup.findAll('table',attrs={"class":"datadisplaytable"})
for table in gradetables:
    if("Course work" in table.find('caption').text):
        rows = table.findAll('tr')
        rows=rows[1:]
        for row in rows:
            cells = row.findAll('td')
            print cells[1].text + "-" + cells[2].text + ": " + cells[4].text + " = " + cells[6].text

