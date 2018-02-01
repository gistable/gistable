import simplejson,urllib2
import md5, tempfile, time
import argparse,os
import networkx as nx

parser = argparse.ArgumentParser(description='Mine Twitter account contributions')
parser.add_argument('-contributeto',nargs='*', help="A space separated list of account names (without the @) for whom you want to find the contributors.")
parser.add_argument('-contributeby',nargs='*', help="A space separated list of account names (without the @) whom you believe contributes to other accounts.")
parser.add_argument('-depth',default=3,type=int,metavar='N',help='Snowball search depth.')

args=parser.parse_args()

DG=nx.DiGraph()

def checkDir(dirpath):
  if not os.path.exists(dirpath):
    os.makedirs(dirpath)

def getContributors(user,userlist):
    net=[]
    print 'Getting contributors to',user
    try:
        data= simplejson.load(urllib2.urlopen('https://api.twitter.com/1/users/contributors.json?screen_name='+user))
        print data
        for d in data:
            net.append(d['screen_name'])
            if d['screen_name'] not in userlist: userlist.append(d['screen_name'])
    except:
        print 'oops'
    return net,userlist

def getContributees(user,accountlist):
    print 'Getting contributions of',user
    net=[]
    try:
        data= simplejson.load(urllib2.urlopen('https://api.twitter.com/1/users/contributees.json?screen_name='+user))
        for d in data:
            net.append(d['screen_name'])
            if d['screen_name'] not in accountlist: accountlist.append(d['screen_name'])
    except:
        pass
    return net,accountlist

#accountlist=['twitterapi']
accountlist=args.contributeto
userlist=args.contributeby
	
contributors={}
contributees={}

depth=args.depth

if args.contributeto and len(args.contributeto):
	print "finding contributors to..."
	fpath='/'.join(['reports','contributors','_'.join(args.contributeto)])
	typ='contributors'
	data={'accountlist':args.contributeto,'userlist':[],'contributors':{},'contributees':{},'graph':DG}
elif args.contributeby and len(args.contributeby):
	print "finding contributions by..."
	fpath='/'.join(['reports','contributees','_'.join(args.contributeby)])	
	typ='contributees'
	data={'accountlist':[],'userlist':args.contributeby,'contributors':{},'contributees':{},'graph':DG}
else:
	exit(-1)

checkDir(fpath)


#==
#tweak of http://developer.yahoo.com/python/python-caching.html
class DiskCacheFetcherfname:
	def __init__(self, cache_dir=None):
		# If no cache directory specified, use system temp directory
		if cache_dir is None:
			cache_dir = tempfile.gettempdir()
		self.cache_dir = cache_dir
	def fetch(self, url, max_age=0):
		# Use MD5 hash of the URL as the filename
		filename = md5.new(url).hexdigest()
		filepath = os.path.join(self.cache_dir, filename)
		if os.path.exists(filepath):
			if int(time.time()) - os.path.getmtime(filepath) < max_age:
				#return open(filepath).read()
				print "using cached copy of fetched url: ",url
				return filepath
		print "fetching fresh copy of fetched url: ",url
		# Retrieve over HTTP and cache, using rename to avoid collisions
		tempdata = urllib2.urlopen(url).read()
		fd, temppath = tempfile.mkstemp()
		fp = os.fdopen(fd, 'w')
		fp.write(tempdata)
		fp.close()
		os.rename(temppath, filepath)
		return filepath
        
def getTwCachedData(url, cachetime=144000):
	fetcher=DiskCacheFetcherfname('cache')
	fn=fetcher.fetch(url, cachetime)
	f=open(fn)
	data=f.read()
	f.close()
	#print 'data----',data
	jdata=simplejson.loads(data)
	if 'error' in jdata:
		if jdata['error'].startswith('Rate limit exceeded'):
			os.remove(fn)
	return jdata


def rgetContributors(user,bigdata):
	net=[]
	print 'Getting contributors to',user
	bigdata['graph'].add_node(user.lower(),label=user)
	try:
		url='https://api.twitter.com/1/users/contributors.json?screen_name='+user
		print 'trying',url
		#data= simplejson.load(urllib2.urlopen(url))
		data=getTwCachedData(url)
		#print data
		for d in data:
			if 'screen_name' in d:
				dsname=d['screen_name']
				net.append(dsname)
				if dsname not in bigdata['userlist']:
					bigdata['userlist'].append(dsname)
					bigdata['graph'].add_node(dsname.lower(),label=dsname)
					bigdata['graph'].add_edge(dsname.lower(),user.lower())
	except:
		print 'oops'
	bigdata['contributors'][user]=net
	return bigdata

def rgetContributees(user,bigdata):
	print 'Getting contributions of',user
	bigdata['graph'].add_node(user.lower(),label=user)
	net=[]
	try:
		url='https://api.twitter.com/1/users/contributees.json?screen_name='+user
		print 'trying',url
		#data= simplejson.load(urllib2.urlopen(url))
		data=getTwCachedData(url)
		for d in data:
			if 'screen_name' in d:
				dsname=d['screen_name']
				net.append(dsname)
				if dsname not in bigdata['accountlist']:
					bigdata['accountlist'].append(dsname)
					bigdata['graph'].add_node(dsname.lower(),label=dsname)
					bigdata['graph'].add_edge(user.lower(),dsname.lower())
	except:
		print 'oops2'
	bigdata['contributees'][user]=net
	return bigdata

#via mhawksey - googole: site:twitter.com "via web by"
#twitterapi, starbucks, HuffingtonPost,sportscenter,todayshow,reelseo,qualcomm,DefJamRecords,HornitosTequila,googletalks,salesforce,noh8campaign,chevron,mtv,jangomail,ESPNCFB,noh8campaign,playstation,mail


#Originally inspired by http://www.drewconway.com/zia/?p=345
def snowball_build(bigdata,rounds,typ='contributors'):
	print 'Starting...'
	if typ=='contributors':
		offset=0
	else:
		offset=1
	for r in range(0,rounds):
		print "STARTING PASS",str(r)
		if (r+offset) % 2:
			print "Finding contributees...",str(r)
			for user in bigdata['userlist']:
				if user not in bigdata['contributees']:
					bigdata=rgetContributees(user,bigdata)
	else:
		# THis includes first pass
		print "Finding contributors...",str(r)
		for account in bigdata['accountlist']:
			if account not in bigdata['contributors']:
				bigdata=rgetContributors(account,bigdata)
	return bigdata

data=snowball_build(data,depth,typ)

print data
print 'contributors',data['contributors']
print 'contributees',data['contributees']
print 'accountlist',data['accountlist']
print 'userlist',data['userlist']


nx.write_graphml(data['graph'], fpath+"/graph.graphml")
nx.write_edgelist(data['graph'], fpath+"/graph.txt",data=False)
