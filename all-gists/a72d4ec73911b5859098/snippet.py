import requests
from bs4 import BeautifulSoup


bugcrowdlist=requests.get('https://bugcrowd.com/list-of-bug-bounty-programs/')
soup=BeautifulSoup(bugcrowdlist.content)

#print soup
anchors=soup.findAll("a", { "class" : "tracked" })
fil=open('alldata.txt','w')
print "Please wait while I fetch the data..."
data=dict()
for tag in anchors:
    link = tag.get('href',None)
    if link.startswith('http'):
        fil.writelines(link+'\n')

fil.close()
print data

