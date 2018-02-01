import feedparser, csv, os
import argparse, urllib, StringIO
from lxml import etree

parser = argparse.ArgumentParser(description='Rescue Twapperkeeper archive')

group = parser.add_mutually_exclusive_group()
group.add_argument('-user',help='Name of a user whose archives you want to rescue.')
group.add_argument('-tag',help='Name of a hashtag archive you want to rescue.')
group.add_argument('-tags',nargs='*',help='A space separated list of a hashtag archives you want to rescue.')
group.add_argument('-userarchives',help='Show the archives associated with a particular user')


parser.add_argument('-l',default=500,type=int,metavar='N',help='The number of tweets grabbed on each page call. Max 10000 seems to be a sensible maximum.')
parser.add_argument('-bigmax',default=1500,type=int,metavar='N',help='The maximum number of tweets to download from the archive. Default is deliberately small.')
parser.add_argument('-reportdir',default='reports',help='The directory path you want to store reports in.')
parser.add_argument('-excl',nargs='*', help="A space separated list of archives (without the #), you don't want to be saved from a given user. Note that this is currently case sensitive.")
#-excl should really require presence of -user to work?

args=parser.parse_args()

#You will probably need to install feedparser first.
#If you have easy_install, this should do the job:
##From the command line: easy_install feedparser

#USAGE: from the command line:
## python twapperkeeperRescue.py -h

#call the script from the commandline with:
# python twapperkeeperRescue.py -tag MYTAG
#to grab a single hashtag archive

#call the script from the commandline with:
# python twapperkeeperRescue.py -user USERNAME
#to grab all the hastag archives associated with a particular individual

#you also need to set the maximum number of tweets to download (-bigmax) and the number of tweets per download page (-l)
# python twapperkeeperRescue.py -tag MYTAG -l 1500 -bigmax 1000000
#would download up to a million tweets from an archive 1500 tweets at a time



#Only set up for hashtag exports atm
tag=args.tag
tags=args.tags
#We can also grab all the hashtag archives from a given user
user=args.user
excl=args.excl
if excl==None: excl=[]
#l is the number of tweets we try to export at a time; I find 50000 is too big
l=args.l
#bigmax is a fudge; I really should look to see how many tweets are in an archive and pull that many..
#As it is, I grab another page if the current page is size l;
#bigmax stops the programme running forever, and kills things when bigmax number of tweets have been pulled
bigmax=args.bigmax
#Specify a directory for the saved files
userdir=args.reportdir

#if the specified directory doesn't exist, create it
def checkDir(dirpath):
  if not os.path.exists(dirpath):
    os.makedirs(dirpath)
checkDir(userdir)


def writeNextPage(archive,writer,tag,l,ey='',em='',ed='',ehh='',emm=''):
	print tag,l,ey,em,ed,ehh,emm
	#if len(archive)>=int(bigmax):
	#	print 'bailing out...'
	#	return archive
	#We'd need to tweak this URL if we want to export archives other than hashtag archives
	url='http://twapperkeeper.com/rss.php?type=hashtag&name='+tag+'&l='+str(l)
	url=url+'&em='+str(em)+'&ed='+str(ed)+'&ey='+str(ey)+'&ehh='+str(ehh)+'&emm='+str(emm)
	d = feedparser.parse(url)
	de = d['entries']
	for i in de:
		writer.writerow([i['title'].encode('utf-8')])
	archive.extend(de)
	if len(de)==l and len(archive)<bigmax:
		ey=de[-1]['updated_parsed'][0]
		em=de[-1]['updated_parsed'][1]
		ed=de[-1]['updated_parsed'][2]
		ehh=de[-1]['updated_parsed'][3]
		emm=de[-1]['updated_parsed'][4]
		writeNextPage(archive,writer,tag,l,ey,em,ed,ehh,emm)
	return archive
	
def saveArchive(tag,l):
	#we're going to save the output to a file in the specified directory using a standard filename
	fn='/'.join([userdir,'twArchive_'+tag+'.txt'])
	f=open(fn,'wb+')
	writer = csv.writer(f)
	archive=writeNextPage([],writer,tag,l)
	f.close()
	return archive

def getUserArchiveNames(user,l):
	#scraper cribs from http://www.techchorus.net/web-scraping-lxml
	url='http://twapperkeeper.com/allnotebooks.php?type=hashtag&name=&description=&tag=&created_by='+user
	print url
	result = urllib.urlopen(url)
	html = result.read()
	parser = etree.HTMLParser()
	tree   = etree.parse(StringIO.StringIO(html), parser)
	userarchives=tree.xpath('//table[1]/tr[position()>1]/td[position()=2]/a/child::text()')
	#NEED TO WORK THIS IN - ARCHIVE SIZES: td[position()=5]
	print userarchives
	return userarchives

def saveUserArchives(userarchives,l):
	for userarchive in userarchives:
		tag=userarchive.lstrip('#')
		if tag not in excl:
			archive=saveArchive(tag,l)


if args.user!=None:
	userarchives=getUserArchiveNames(user,l)
	saveUserArchives(userarchives,l)
elif args.tag!=None:
	archive=saveArchive(tag,l)
elif args.tags!=None:
	for tag in tags:
		archive=saveArchive(tag,l)
elif args.userarchives!=None:
	#Really need to also grab the size of each archive?
	userarchives=getUserArchiveNames(args.userarchives,l)