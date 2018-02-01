"""

Example of using the old BeautifulSoup API to extract content from downloaded html files into CSV... if you're doing this sort of thing today, I recommend using the newer lxml interface directly, but lxml also has a BeautifulSoup compatibility layer.

"""


import os


from BeautifulSoup import BeautifulSoup as bs

def get_horo(source):
	g=bs(source)
	mainblock=g.find('div',{'class':'content'})
	return mainblock

import os

filelist=[]


for dirname, dirnames, filenames in os.walk('./cleaned/'):
    for filename in filenames:
        filelist.append(os.path.join(dirname, filename))

bses=[]
for f in filelist:
	source=open(f).read()
	bses.append((f,source,bs(source)))

noneones=[]
for f in bses:
	if f[1]=='None':
		noneones.append(f)

sourcecomp=[]
for f in noneones:
	sourcecomp.append((f[0],open(f[0].replace('./cleaned/','./output/')).read()))


urls=[x[0].replace('./cleaned/','').replace('-','/') for x in sourcecomp]

open('html_urls.txt','w').writelines([u + '\n' for u in urls])

newurls=[]
for u in urls:
	a=u.split('/')
	newurls.append(a[0] +'//' + a[2] + '/' + a[3] + '/' + a[4] + '/' + a[5] + '-' + a[6] + '/' + a[7] + '/')

open('html_urls.txt','w').writelines([u + '\n' for u in newurls])

newbses=[]
noneurls=[x[0] for x in noneones]
for b in range(len(bses)):
	if not bses[b][0] in noneurls:
		newbses.append(bses[b])




b=newbses

parsed=[]
for u in b:
	record=[]
	h3s=u[2].findAll('h3')
	section_count=0
	if len(h3s) == 2:
		record=[h3s[0],h3s[0].next.next.next,h3s[1],h3s[1].next.next.next]
		record=[x.contents[0].strip() for x in record]
		section_count=2
	if len(h3s) == 0:
		record=[u[2].contents[0].next.next]
		record=[x.contents[0].strip() for x in record]
		section_count=0
	if len(h3s) == 1:
		record=[h3s[0],h3s[0].next.next]
		record=[x.contents[0].strip() for x in record]
		section_count=1
	if len(h3s) == 3:
		record=[h3s[0],h3s[0].next.next.next,h3s[1],h3s[1].next.next.next,h3s[2],h3s[2].next.next.next]
		record=[x.contents[0].strip() for x in record]
		section_count=3
	record.reverse()
	record.append(section_count)
	record.reverse()
	parsed.append((u[0].split('-')[3:-1],u[1],u[2],record))

noneones=[x for x in parsed if len(x[3])==0]

import pickle
parsed=pickle.load(open('parsed','b'))

newparsed=[x[0]+x[3] for x in parsed]

import csv
w=csv.writer(open('horoscopes.csv','wb'),delimiter=',',quoting=csv.QUOTE_NONNUMERIC)
for x in newparsed:
	w.writerow(x[1:])
