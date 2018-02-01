# ABOUT:
# A script that grabs a list of the friends or followers of a user on Google+,
# grabs a sample of their friends, and generates the resulting social graph

# USAGE:
# Requirements: networkx (see DEPENDENCIES)
# Configuration: see CONFIGURATION
# Output: files will be save to the reports directory
# To run the script:
# 1) Download this file to a new directory somewhere as eg gplusESPnet.py
# 2) cd to the directory
# 3) *The first time*, create to new subdirectories (reports and cache); for example, run the following from the command line: mkdir reports; mkdir cache
# 4) Call the script by running the following from the command line:
# python gplusESPnet.py

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
import md5,urllib,os,tempfile,time
import random
import datetime

import StringIO


#USER SETTINGS
#rootID is the Google+ ID of the person whos ESP net you want to map
rootID='100095426689697101649'
#You also need to provide the name of this user
name='Tony Hirst'


#----
# Do some checks...
def checkDir(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

checkDir('reports')
checkDir('cache')
#---

oidRootNamePairs={rootID:name}

defCache=360000
typ='fo'
typ2='fr'
DG=nx.DiGraph()


reobj = re.compile(r'.*([0-9]{21}).*')
reobj2 = re.compile(r',\["([^"]*)".*')
reobj3=re.compile(r'.*[0-9]{21}"\]\n,\[\]\n,\["[^"]*')
#oids = reobj3.findall(data)
#for oid in oids:
#,[[,,"112696985248193005986"]\n,[]\n,["Dawn Wicks-Sutton
reobj4=re.compile(r',\[+,,"([0-9]{21})"]\n,\[\]\n,\["(.*)$')
#ascii(reobj4.match(oid).group(2)) is name, tho check not '' if so 'U N Owen", reobj4.match(oid).group(1) is ID 
def ascii(s): return "".join(i for i in s if ord(i)<128)

def getoidName(i,currIDs,oidNames):
	l=i.next()
	#print l
	oid = reobj.match(l)
	if oid==None:
		print 'at the end???'
		return i,currIDs,oidNames,-1
	else: oid=oid.group(1)
	#if we don't get an ID, then return oidNames, i, -1
	if oid not in currIDs:
		#print 'toploop'
		i.next()
		n=i.next()
		n=ascii(reobj2.match(n).group(1))
		if oid not in oidNames:
			oidNames[oid]=n
		currIDs.append(oid)
		#print oid,n
		next=''
		while next!=',[]\n':
			next=i.next()
			#print '...'+next+',,,,'
		next=''
		while next!=']\n':
			next=i.next()
	else:
		print 'bottomloop'
		next=''
		while next!=']\n':
			next=i.next()
	return i,currIDs,oidNames,1

def getoidNames(oidNames,oid='',typ='fr'):
	#oidNames = {}
	if oid=='': return oidNames,[]
	currIDs=[]
	#???I suspect this only does one page of up to 1000(?) users? Need to check?
	if typ=='fr':
		url='https://plus.google.com/u/0/_/socialgraph/lookup/visible/?o=%5Bnull%2Cnull%2C%22'+oid+'%22%5D&rt=j'
	elif typ=='fo':
		url='https://plus.google.com/u/0/_/socialgraph/lookup/incoming/?o=%5Bnull%2Cnull%2C%22'+oid+'%22%5D&n=1000&rt=j'
	else:
		exit(-1)
	print url
	#data = urllib.urlopen(url).read()
	data=getGenericCachedData(url)
	i=StringIO.StringIO(data)
	i.next()
	i.next()
	i.next()
	#if flag returns <0, we're done
	flag=1
	while flag>0:
		i,currIDs,oidNames,flag=getoidName(i,currIDs,oidNames)
	#print currIDs,oidNames
	return oidNames,currIDs
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

def getGenericCachedData(url, cachetime=defCache):
  fetcher=DiskCacheFetcherfname('cache')
  fn=fetcher.fetch(url, cachetime)
  f=open(fn)
  data=f.read()
  f.close()

  return data
  

def addDirectedEdges(DG,fromNode,toSet,flip=False):
	for toNode in toSet:
		if flip==True:
			DG.add_edge(toNode,fromNode)
		else:
			DG.add_edge(fromNode,toNode)
	#print nx.info(DG)
	return DG

def labelNodes(G,names):
	for nodeID in G.node:
		G.node[nodeID]['label']=names[nodeID]
	return G



oidNamePairs={}
for id in oidRootNamePairs:
	oidNamePairs,currIDs=getoidNames(oidNamePairs,id,typ)
	print currIDs
	flip=(typ=='fr')
	DG=addDirectedEdges(DG, id, currIDs,flip=flip)
	n=len(currIDs)
	print str(n)
	c=1
	for cid in currIDs:
		print '\tSub-level run: getting ',typ2,str(c),'of',str(n),typ,cid
		oidNamePairs,ccurrIDs=getoidNames(oidNamePairs,cid,typ2)
		DG=addDirectedEdges(DG, cid, ccurrIDs)
		c=c+1
for id in oidRootNamePairs:
	if id not in oidNamePairs:
		oidNamePairs[id]=oidRootNamePairs[id]
DG=labelNodes(DG,oidNamePairs)
print nx.info(DG)

now = datetime.datetime.now()
ts = now.strftime("_%Y-%m-%d-%H-%M-%S")

fname=name.replace(' ','_')
nx.write_graphml(DG, '/'.join(['reports',fname+'_google'+typ+'Friends_'+ts+".graphml"]))
nx.write_edgelist(DG, '/'.join(['reports',fname+'_google'+typ+'Friends_'+ts+".txt"]),data=False)

def filterNet(DG,mindegree,indegree,outdegree,outdegreemax,typ,typ2,addUserFriendships,user,indegreemax):
	#need to tweak this to allow filtering by in and out degree?
	if addUserFriendships==1:
		DG=addFocus(DG,user,typ)
	#handle min,in,out degree
	filter=[]
	#filter=[n for n in DG if DG.degree(n)>=mindegree]
	for n in DG:
		if outdegreemax==None or DG.out_degree(n)<=outdegreemax:
			if mindegree!=None:
				if DG.degree(n)>=mindegree:
					filter.append(n)
			else:
				if indegree!=None:
					if DG.in_degree(n)>=indegree:
						filter.append(n)
				if outdegree!=None:
					if DG.out_degree(n)>=outdegree:
						filter.append(n)
	#the filter represents the intersect of the *degreesets
	#indegree and outdegree values are ignored if mindegree is set
	filter=set(filter)
	H=DG.subgraph(filter)
	#Superstitiously, perhaps, make sure we only grab nodes that project edges...
	filter= [n for n in H if H.degree(n)>0]
	L=H.subgraph(filter)
	#print "Filter set:",filter
	print L.order(),L.size()
	#L=labelGraph(L,filter)
	
	if mindegree==None: tm='X'
	else: tm=str(mindegree)
	if indegree==None: ti='X'
	else: ti=str(indegree)
	if outdegree==None: to='X'
	else: to=str(outdegree)
	if outdegreemax==None: tom='X'
	else: tom=str(outdegreemax)
	st='/'.join([projname,name+'_google'+typ+typ2+'degree_'+tm+'_'+ti+'_'+to+'_'+tom+"_esp"])
	print nx.info(L)
	nx.write_graphml(L, st+".graphml")
	nx.write_edgelist(L, st+".txt",data=False)


mindegree=None
indegree=20
outdegree=25
outdegreemax=None
addUserFriendships=0
user=''
indegreemax=None
projname='reports/'
filterNet(DG,mindegree,indegree,outdegree,outdegreemax,typ,typ2,addUserFriendships,user,indegreemax)