import tweepy, simplejson, urllib, os,datetime,re
#----------------------------------------------------------------

def getBitlyKey():
  bu='USER'
  bkey='KEY'
  return bu,bkey
  
def getTwapperkeeperKey():
  key='KEY'
  return key

def getTwitterKeys():
  consumer_key='C_KEY'
  consumer_secret='C_SECRET'
  skey='S_KEY'
  ssecret='S_SECRET'  
  return consumer_key,consumer_secret,skey,ssecret


def expandBitlyURL(burl):
  bu,bkey=getBitlyKey()
  url='http://api.bit.ly/v3/expand?shortUrl='+urllib.quote(burl)+'&login='+bu+'&apiKey='+bkey+'&format=json'
  print 'url: '+url
  r=simplejson.load(urllib.urlopen(url))
  return r['data']['expand']
  # for j in r['data']['expand']:
  #   print 'long '+j['long_url']

def generateGoogleCSEDefinitionFile(cse,tag, tw,typ='flat'):
  report("Generating Google CSE definition file")
  fname='listhomepages_'+typ+'.xml'
  f=openTimestampedFile(tag,fname)
  f.write("<GoogleCustomizations>\n\t<Annotations>\n")
  for u in tw:
    un=tw[u]
    if  type(un) is tweepy.models.User:
      l=un.url
      if l:
       urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', l)
       for l in urls:
        #l=l.split(' ')[0]
        #if "http://bit.ly" in url:
        #  urls=expandBitlyURL(burl)
        #l=urls[0]
        #l=l.strip()
        lo=l
        l=l.replace("http://","")
        if not l.endswith('/') and '?' not in l:
          l=l+"/*"
        else:
          if l[-1]=="/":
            l=l+"*"
        report("- using "+lo+" as "+l)
        weight=1.0
        if typ is 'weighted':
          weight=un.status
        f.write("\t\t<Annotation about=\""+l+"\" score=\""+str(weight)+"\">\n")
        f.write("\t\t\t<Label name=\""+cse+"\"/>\n")
        f.write("\t\t</Annotation>\n")
  f.write("\t</Annotations>\n</GoogleCustomizations>")
  report("...Google CSE definition file DONE")
  f.close()


def googleCSEDefinitionFileWeighted(cse,tag, tw):
  generateGoogleCSEDefinitionFile(cse,tag, tw,'weighted')
  
def googleCSEDefinitionFile(cse,tag, tw):
  generateGoogleCSEDefinitionFile(cse,tag, tw,'flat')


#----------------------------------------------------------------
def getTwapperkeeperURL(tag,start,end,page=1):
  key=getTwapperkeeperKey()
  url='http://api.twapperkeeper.com/2/notebook/tweets/?apikey='+key+'&name='+tag+'&type=hashtag&since='+start+'&until='+end+'&rpp=1000&page='+str(page)
  return url
#----------------------------------------------------------------

#----------------------------------------------------------------  
def getTwapperkeeperPage(tag,start,end,page=1):
  report("Getting page "+str(page))
  url= getTwapperkeeperURL(tag,start,end,page)
  r=simplejson.load(urllib.urlopen(url))
  return r['response']
#----------------------------------------------------------------

#----------------------------------------------------------------
def parseTwapperkeeperResponse(tweeters,response,c):
  report("..parsing page")
  for i in response['tweets_returned']:
    c+=1
    u=i['from_user'].strip()
    if u in tweeters:
      tweeters[u]['count']+=1
    else:
      report("New user: "+u)
      tweeters[u]={}
      tweeters[u]['count']=1
  return tweeters,c
#----------------------------------------------------------------


#----------------------------------------------------------------  
def getTwapperkeeperArchiveTweeters(tweeters,tag,start,end):
  report("Getting Twapperkeeper archive tweeters")
  count=0
  num=0
  r=getTwapperkeeperPage(tag,start,end)
  tweeters,count=parseTwapperkeeperResponse(tweeters,r,count)
  #if there is only one page, does Twapperkeeper report the tweets_found_count?
  if r['tweets_found_count']:
   num=int(r['tweets_found_count'])

  page=2
  while count<num:
    r=getTwapperkeeperPage(tag,start,end,page)
    tweeters,count=parseTwapperkeeperResponse(tweeters,r,count)
    page+=1
  
  return tweeters
#----------------------------------------------------------------

#----------------------------------------------------------------
def getTwitterAPI():
  #----------------------------------------------------------------
  #API settings for Twitter
  consumer_key,consumer_secret,skey,ssecret=getTwitterKeys()
  #----------------------------------------------------------------

  #----------------------------------------------------------------
  #API initialisation for Twitter
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(skey, ssecret)
  api = tweepy.API(auth)
  #----------------------------------------------------------------
  return api
#----------------------------------------------------------------

#----------------------------------------------------------------
def report(m, verbose=True):
  if verbose is True:
    print m
#----------------------------------------------------------------

#----------------------------------------------------------------
def createListIfRequired(api, tag):
  lists=api.lists()
  listexists= False

  for l in lists:
    for l2 in l:
      if type(l2) is tweepy.models.List:
        if l2.slug==tag:
          listexists= True
          report("List appears to exist")
    
  if listexists is False:
    report("List doesn't appear to exist... creating it now")
    api.create_list(tag)

#----------------------------------------------------------------  

#----------------------------------------------------------------
def destroyListIfRequired(api,tag):
  lists=api.lists()
  listexists= False

  for l in lists:
    for l2 in l:
      if type(l2) is tweepy.models.List:
        if l2.slug==tag:
          listexists=True
          report("List appears to exist...destroying it now")
          api.destroy_list(l2.slug)

  if listexists is False:
    report("List did not appear to exist...")
#----------------------------------------------------------------

#----------------------------------------------------------------
def addManyToListByScreenName(api,o,tag,members):
  l=[]
  createListIfRequired(api, tag)
  for u in tweepy.Cursor(api.list_members,owner=o,slug=tag).items():
    if  type(u) is tweepy.models.User:
      l.append(u.screen_name)
  for u in members:
      if u in l:
        report(u+' in list')
      else:
        report('Adding '+u+' to '+tag+' list')
        try:
          api.add_list_member(tag, u)
        except:
          report("Hmm... didn't work for some reason")
#----------------------------------------------------------------

def mergeDicts(dicts,x=False):
  merger={}
  for d in dicts:
    for i in d:
      if x is True:
        if i in merger:
          for c in merger[i]['classVals']:
            d[i]['classVals'][c]+='::'+merger[i]['classVals'][c]
      merger[i]=d[i]
  return merger


def getTwitterUsersDetailsByScreenNames(api,users):
  twr={}
  twl=chunks(users,99)
  for f100 in twl:
    report("Hundred batch....")
    try:
      twd=api.lookup_users(screen_names=f100)
      for u in twd:
        if  type(u) is tweepy.models.User:
          twr[u.screen_name]=u
          #also works on  screen_names
    except:
      report("Failed lookup...")  
  return twr


def getTwitterFriendsDetailsByIDs(api,user):
  return getTwitterUserDetailsByIDs(api,user,"friends")

def getTwitterFollowersDetailsByIDs(api,user):
  return getTwitterUserDetailsByIDs(api,user,"followers")

def getTwitterUserDetailsByIDs(api,user,typ="friends"):
  twr={}
  if typ is 'friends':
    members=api.friends_ids(user)
  else:
    members=api.followers_ids(user)    
  twl=chunks(members,99)
  for f100 in twl:
    report("Hundred batch on "+typ+"....")
    try:
      twd=api.lookup_users(user_ids=f100)
      for u in twd:
        if  type(u) is tweepy.models.User:
          twr[u.screen_name]=u
          #also works on  screen_names
    except:
      report("Failed lookup...")  
  return twr

def gephiOutputNodeDef(f,members,extras=None):
  header=gephiCoreGDFNodeHeader()
  f.write(header+'\n')
  for u in members:
    u2=members[u]
    if u2.screen_name!='none':    
      f.write(gephiCoreGDFNodeDetails(u2)+'\n')
   
def gephiCoreGDFNodeHeader():
  header='nodedef> name VARCHAR,label VARCHAR, totFriends INT,totFollowers INT, location VARCHAR, description VARCHAR'
  return header
  
def gephiCoreGDFNodeDetails(u2):
  u2=tidyUserRecord(u2)
  details=str(u2.id)+','+u2.screen_name+','+str(u2.friends_count)+','+str(u2.followers_count)+',"'+u2.location+'","'+u2.description+'"'
  return details
  
def gephiOutputNodeDefExtended(f,members,extensions):
  header=gephiCoreGDFNodeHeader()
  for x in extensions:
    y=x.split(' ')
    header+=','+y[0]+' '+y[1]
  f.write(header+'\n')
  for u in members:
    u2=members[u]['user']
    if u2.screen_name!='none': 
      fout=gephiCoreGDFNodeDetails(u2)
      for x in extensions:
        y=x.split(' ')
        if y[1]=='INT':
          fout+=','+str(members[u]['classVals'][y[0]])
        else:
          fout+=',"'+str(members[u]['classVals'][y[0]])+'"'
      f.write(fout+'\n')
   
def tidyUserRecord(u2):
  if u2.location is not None:
    u2.location=u2.location.replace('\r',' ')
    u2.location=u2.location.replace('\n','  ')
    u2.location=u2.location.encode('ascii','ignore')
  else:
    u2.location=''
  if u2.description is not None:
    u2.description=u2.description.replace('\r',' ')
    u2.description=u2.description.replace('\n',' ')
    u2.description=u2.description.encode('ascii','ignore')
  else:
    u2.description=''
  return u2

def gephiOutputEdgeDefInner(api,f,members,typ='friends'):
  f.write('edgedef> user VARCHAR,friend VARCHAR\n')
  i=0
  membersid=[]
  for id in members:
    membersid.append(members[id].id)
  M=len(members)
  for id in members:
    friend=members[id]
    report("- finding "+typ+" of whatever (friends? followers?) was passed in of "+friend.screen_name)
    try:
      if typ is 'friends':
        foafs=api.friends_ids(friend.id)
      else:
        foafs=api.followers_ids(friend.id)
      cofriends=intersect(membersid,foafs)
      #being naughty - changing .status to record no. of foafs/no. in community
      members[id].status=0.7+0.3*len(cofriends)/M
      report("...weight: "+str(members[id].status))
      for foaf in cofriends:
        f.write(str(friend.id)+','+str(foaf)+'\n')
    except tweepy.error.TweepError,e:
      report(e)


def gephiOutputFile(api,dirname, members,typ="innerfriends",fname='Net.gdf'):
  report("Generating Gephi file using: "+typ)
  f=openTimestampedFile(dirname,typ+fname)
  gephiOutputNodeDef(f,members)
  if typ is 'innerfriends':
    gephiOutputEdgeDefInner(api,f,members,'friends')
  elif typ is 'innerfollowers':
    gephiOutputEdgeDefInner(api,f,members,'followers')

  f.close()
  report("...Gephi "+typ+" file generated")
  
def extendUserList(tw,extensions):
  ttx={}
  for t in tw:
    ttx[t]={}
    ttx[t]['user']=tw[t]
    ttx[t]['classVals']={}
    for x in extensions:
      y=x.split(' ')
      ttx[t]['classVals'][y[0]]=y[1]
  return ttx

def deExtendUserList(membersX):
  members={}
  for m in membersX:
    members[m]=membersX[m]['user']
  return members
  
def gephiOutputFileExtended(api,dirname, membersX,extensions,typ="innerfriends",fname='friendsNet.gdf'):
  report("Generating extended Gephi file using: "+typ)
  fname='X'+fname
  f=openTimestampedFile(dirname,fname)
  gephiOutputNodeDefExtended(f,membersX,extensions)
  members=deExtendUserList(membersX)
  if typ is 'innerfriends':
    gephiOutputEdgeDefInnerFriends(api,f,members)
  f.close()
  report("...extended Gephi "+typ+" file generated")

def openTimestampedFile(fpath,fname):
  fpath='reports/'+fpath
  now = datetime.datetime.now()
  ts = now.strftime("_%Y-%m-%d-%H-%M-%S")
  checkDir(fpath)
  fpart=fname.split('.')
  f=open(fpath+'/'+fpart[0]+'%s.'%ts+fpart[1],'w')
  return f
  
def checkDir(dirpath):
  if not os.path.exists(dirpath):
    os.makedirs(dirpath)

#----------------------------------------------------------------
#return common members of two lists
def intersect(a, b):
     return list(set(a) & set(b))
#----------------------------------------------------------------

#----------------------------------------------------------------
#Yield successive n-sized chunks from l
def chunks(l, n):   
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

    
#----------------------------------------------------------------
def listDetailsByID(tw,l,o,t):
  report("Fetching list details for "+t+"...")
  for u in tweepy.Cursor(l,owner=o,slug=t).items():
    if  type(u) is tweepy.models.User:
      tw[int(u.id)]=u
  return tw
#----------------------------------------------------------------

#----------------------------------------------------------------
def listDetailsByScreenName(tw,l,o,t):
  report("Fetching list details for "+t+"...")
  for u in tweepy.Cursor(l,owner=o,slug=t).items():
    if  type(u) is tweepy.models.User:
      tw[u.screen_name]=u
  return tw
#----------------------------------------------------------------