####DEPRECATED

# ABOUT:
# A script that grabs a list of the friends or followers of one or more folk on Google+,
# grabs a sample of their friends, and generates the resulting social graph

# USAGE:
# Requirements: networkx (see DEPENDENCIES)
# Configuration: see CONFIGURATION
# Output: files will be save to the reports directory
# To run the script:
# 1) Download this file to a directory somewhere as eg googPlusFrFo-preliminarySketch.py
# 2) cd to the directory
# 3) *The first time*, run the following from the command line: mkdir reports; mkdir cache
# 4) Call the script by running the following from the command line:
# python googPlusFrFo-preliminarySketch.py

# DEPENDENCIES
# The script makes use of the networkx library; you should only need to install it once.
# To install networkx, from the command line type: easy_install networkx
# If that doesn't work, follow the instructions on http://networkx.lanl.gov/install.html
# In short: a) download and unzip http://networkx.lanl.gov/download/networkx/networkx-1.5.zip
# b) cd to the networkx-1.5 directory, c) type: python setup.py install 
# END DEPENDENCIES

import networkx as nx

#--- the following should already be available
import urllib2,re
try: import simplejson as json
except ImportError: import json
import md5,urllib,os,tempfile,time
import random
import datetime

# CONFIGURATION

#gPlusIDS - a comma separated list of Google+ IDs. I'm just doing one below...
gPlusIDs=['100095426689697101649']

#name - is the slug in the filename the graph data will be saved to;
name='tonyHirst'

# cache time in seconds; if a file is cached and not older than cachetime, that data will be used
defCache=36000

# Some folk have a lot of friends. The Google Social API only seems to let you grab 15 names at a time
# so to limit API calls - and the time the script takes to run - I only grab sampleSize random
# friends or followers of the target accounts(s) to construct the graph
sampleSize=90

# Do we want to map the social connections between the friends of the friends ('fr') of the 
# target account(s) or the friends of the followers ('fo') of the target account(s) 
typ='fo'

# END CONFIGURATION

#----
# Do some checks...
def checkDir(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

checkDir('reports')
checkDir('cache')
#---

DG=nx.DiGraph()

#friends
#https://plus.google.com/u/0/_/socialgraph/lookup/visible/?o=%5Bnull%2Cnull%2C%22GOOGLEPLUSUSERID%22%5D&rt=j

#followers
#https://plus.google.com/u/0/_/socialgraph/lookup/incoming/?o=%5Bnull%2Cnull%2C%22GOOGLEPLUSUSERID%22%5D&n=1000&rt=j

#----------------------------------------------------------------
#Yield successive n-sized chunks from l
def chunks(l, n):   
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def report(m, verbose=False):
  if verbose is True:
    print m


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
                report("using "+filename+", cached copy of fetched url: "+url)
                return filepath
        report("fetching fresh copy of fetched url: "+url)
        # Retrieve over HTTP and cache, using rename to avoid collisions
        data = urllib.urlopen(url).read()
        fd, temppath = tempfile.mkstemp()
        fp = os.fdopen(fd, 'w')
        fp.write(data)
        fp.close()
        os.rename(temppath, filepath)
        return filepath

def getGenericCachedData(url, cachetime=36000):
  fetcher=DiskCacheFetcherfname('cache')
  fn=fetcher.fetch(url, cachetime)
  f=open(fn)
  data=f.read()
  f.close()
  #print 'data----',data
  #jdata=json.loads(data)
  return data #jdata
  
  
def getuserName(oid):
	#http://socialgraph.apis.google.com/lookup?q=https%3A%2F%2Fplus.google.com%2F104253436939071070140%2F&pretty=1&callback=
	url='http://socialgraph.apis.google.com/lookup?q=https%3A%2F%2Fplus.google.com%2F'+oid+'%2F&callback='
	xdata=getGenericCachedData(url)
	data=json.loads(xdata)
	#data=json.load(urllib2.urlopen(url))
	uid='http://profiles.google.com/'+str(oid)
	if uid in data['nodes']:
		name=data['nodes'][uid]['attributes']['fn']
	else: name=''
	return name
	
def getUserNames(oids,namelookup={}):
	oidlookup=[]
	for oid in oids:
		if oid not in namelookup and oid not in oidlookup: oidlookup.append(oid)
	oidblocks=chunks(oidlookup,15)
	for oidblock in oidblocks:
		encoids='%2Chttps%3A%2F%2Fplus.google.com%2F'.join(oidblock)
		#print encoids
		url='http://socialgraph.apis.google.com/lookup?q=https%3A%2F%2Fplus.google.com%2F'+encoids+'%2F&callback='
		#data=json.load(urllib2.urlopen(url))
		xdata=getGenericCachedData(url)
		try:
			data=json.loads(xdata)
		except:
			print '********SOME ERROR******'
			data={}
			data['nodes']=[]
		for oid in oidblock:
			uid='http://profiles.google.com/'+str(oid)
			if uid in data['nodes']:
				try:
					namelookup[oid]=data['nodes'][uid]['attributes']['fn']
				except:
					namelookup[oid]=''
			else: namelookup[oid]=''
	return namelookup
#---
#based on http://html5example.net/entry/tutorial/simple-python-google-plus-api
def getoids(oid,typ='fr'):
	oids = []
	if typ=='fr':
		url='https://plus.google.com/u/0/_/socialgraph/lookup/visible/?o=%5Bnull%2Cnull%2C%22'+oid+'%22%5D&rt=j'
	elif typ=='fo':
		url='https://plus.google.com/u/0/_/socialgraph/lookup/incoming/?o=%5Bnull%2Cnull%2C%22'+oid+'%22%5D&n=1000&rt=j'
	else:
		exit(-1)
	#req = urllib2.Request(url)
	#response = urllib2.urlopen(req)
	#data = response.read()
	print 'Fetching',url
	data=getGenericCachedData(url,defCache)
	#print data
	
	reobj = re.compile(r'[0-9]{21}')
	oids = reobj.findall(data)
	oids = list(set(oids))
	return oids
#---

def addDirectedEdges(DG,fromNode,toSet):
	for toNode in toSet:
		DG.add_edge(fromNode,toNode)
	nx.info(DG)
	return DG

def labelNodes(G,names):
	for nodeID in G.node:
		G.node[nodeID]['label']=names[nodeID]
	return G

oidNames={}

for id in gPlusIDs:
	print 'Top level run: getting',typ,id,getuserName(id)
	oidNames[id]=getuserName(id)
	oids=getoids(id, typ)
	#if len(oids)>sampleSize:
  	#	oidsSample=random.sample(oids, sampleSize)
	addDirectedEdges(DG, id, oids)
	oidNames=getUserNames(oids,oidNames)
	count=1
	fsize=len(oids)
	for oid in oids:
		print '\tSub-level run: getting fr',oid,oidNames[oid],count,'of',fsize
		foids=getoids(oid)
		todo=len(foids)
		if todo>sampleSize:
			print oidNames[oid],'has too many fr','so using a sample of',sampleSize,'instead'
			foids=random.sample(foids, sampleSize)
		addDirectedEdges(DG, oid, foids)
		oidNames=getUserNames(foids,oidNames)
		count=count+1

DG=labelNodes(DG,oidNames)
print nx.info(DG)

now = datetime.datetime.now()
ts = now.strftime("_%Y-%m-%d-%H-%M-%S")
  
nx.write_graphml(DG, '/'.join(['reports',name+'_google'+typ+'Friends_'+ts+".graphml"]))
nx.write_edgelist(DG, '/'.join(['reports',name+'_google'+typ+'Friends_'+ts+".txt"]),data=False)