"""
Creates a list of URLs to stdout based on repeating patterns found in the site, suitable for use with WGET or CURL.

"""

import datetime

scopes=[
	"aries",
	"taurus",
	"gemini",
	"cancer",
	"leo",
	"virgo",
	"libra",
	"scorpio",
	"sagittarius",
	"capricorn",
	"aquarius",
	"pisces"
]



daily_urlbases=[
	("overview","http://shine.yahoo.com/astrology/%s/daily-overview/%i/"),
	("extended","http://shine.yahoo.com/astrology/%s/daily-extended/%i/"),
	("daily-teen","http://shine.yahoo.com/astrology/%s/daily-teen/%i/"),
	("daily-love","http://shine.yahoo.com/astrology/%s/daily-love/%i/"),
	("daily-career","http://shine.yahoo.com/astrology/%s/daily-career/%i/"),
]

yearly_urlbases=[
	("yearly","http://shine.yahoo.com/astrology/%s/yearly-overview/"),
	("yearly-love","http://shine.yahoo.com/astrology/%s/yearly-love/"),
	("yearly-career","http://shine.yahoo.com/astrology/%s/yearly-career/")
]

weekly_urlbases=[
	("weekly","http://shine.yahoo.com/astrology/%s/weekly-overview/%i/"),
	("weekly-love","http://shine.yahoo.com/astrology/%s/weekly-love/%i/"),
	("weekly-career","http://shine.yahoo.com/astrology/%s/weekly-career/%i/")
]

monthly_urlbases=[
	("monthly","http://shine.yahoo.com/astrology/%s/monthly-overview/%i/"),
	("monthly-love","http://shine.yahoo.com/astrology/%s/monthly-love/%i/"),
	("monthly-career","http://shine.yahoo.com/astrology/%s/monthly-career/%i/")
	]

class dateincrement:
	def __init__(self,initialdate=datetime.datetime(2009,12,31),scale=datetime.timedelta(days=1)):
		self.thisdate=initialdate
		self.scale=scale
	def next(self):
		if self.thisdate + self.scale < datetime.datetime(2011,1,1):
			self.thisdate += self.scale
			return self.thisdate
		else:
			return False

class monthincrement:
	def __init__(self,initialmonth=0):
		self.month=initialmonth
	def next(self):
		if self.month < 12:
			self.month += 1
			return datetime.datetime(2010,self.month,1)
		else:
			return False

dayobj=None
weekobj=None
monthObj=None

def makeObjects():
	dayobj = dateincrement()
	weekobj = dateincrement(datetime.datetime(2009,12,28),datetime.timedelta(days=7))
	monthobj = monthincrement()

def testobj(obj):
	while True:
		result=obj.next()
		if result:
			print result
		else:
			break

def testallobjs():
	testobj(dayobj)
	testobj(weekobj)
	testobj(monthobj)

pad = lambda x: str(x).rjust(2,"0")

def generate_urls(thelist,theobj):
	results=[]
	while True:
		d=theobj.next()
		print d
		if d:
			for url in thelist:
				for month in scopes:
					datestr=int(str(d.year)+pad(d.month)+pad(d.day))
					print repr(month)
					print repr(datestr)
					aresult=url[1] % (month,datestr)
					print aresult
					results.append((url[0]+"_"+month,datestr,aresult))
		else:
			break
	return results

def generate_yearly_urls(thelist):
	results=[]
	for url in thelist:
		for month in scopes:
			print repr(month)
			aresult=url[1] % month
			print aresult
			results.append((url[0]+"_"+month,"2010",aresult))
	return results


import sys
from urllib import urlopen
#from BeautifulSoup import BeautifulSoup
from Queue import Queue, Empty
from threading import Thread

visited = set()
queue = Queue()

def get_parser():

	def parse():
		try:
			while True:
				url = queue.get_nowait()
				print "GRABBING: " + repr(url)
				try:
					content = urlopen(url[2]).read()
					f=open("output/"+url[0]+"_"+str(url[1])+".html",'w')
					f.write(content)
					f.close()
					if len(content) > 10000:
						url.task_done()
				except:
					print "PASS: " + repr(url)
					pass
		except Empty:
			pass
	
	return parse


if __name__ == "__main__":
	daily=generate_urls(daily_urlbases,dateincrement())
	weekly=generate_urls(weekly_urlbases,dateincrement(datetime.datetime(2009,12,28),datetime.timedelta(days=7)))
	monthly=generate_urls(monthly_urlbases,monthincrement())
	yearly=generate_yearly_urls(yearly_urlbases)
	combined = daily+weekly+monthly+yearly
	parser = get_parser()
	for x in combined:
		#queue.put(x)
		print x[2]
	workers=[]
#	for i in range(5):
		#worker = Thread(target=parser)
		#worker.start()
		#works.append(worker)
	#for worker in workers:
		#worker.join()
