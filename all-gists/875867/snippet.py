from BeautifulSoup import BeautifulSoup

import urllib2
import re
import time
import sys
import os

user_agent = 'Mozilla/5 (Solaris 10) Gecko'
headers = { 'User-Agent' : user_agent }

request = urllib2.Request("http://www.lfgss.com/search.php?do=process&prefixchoice[]=ForSale&excludeclosed=1&nocache=1",None,headers)
page=urllib2.urlopen(request)
soup = BeautifulSoup(page)

known = [ ]

#print soup.prettify()

print "Right, to crunch"

for thread in soup("a", id=re.compile("thread_title")):
    print thread
    known.append(thread['id'])

print "Seeded dictionary with: "

for know in known:
    print know

while(1):
    time.sleep(60)
    print ".",  #scrolling info on grabs
    sys.stdout.flush()  #flush buffer so it actually displays :^)
    page = urllib2.urlopen(request)
    soup = BeautifulSoup(page)
    for thread in soup("a", id=re.compile("thread_title")):
        if thread['id'] not in known:
            print thread
            cmd="google-chrome \"http://www.lfgss.com/"+thread['href']+"\""
            os.system(cmd)
            known.append(thread['id'])
