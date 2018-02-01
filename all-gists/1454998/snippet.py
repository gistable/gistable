#!/usr/bin/env python

import sys, os, urllib, json

user = sys.argv[1]
u = urllib.urlopen('http://gist.github.com/api/v1/json/gists/' + user)
bytes = u.read()
u.close()

gistdir = user + '-gists'
if os.path.exists(gistdir): 
   print >> sys.stderr, 'Error: Already exists: ' + gistdir
   sys.exit(1)

os.mkdir(gistdir)
os.chdir(gistdir)

for gist in json.loads(bytes)[u'gists']: 
   repo = gist[u'repo']
   for name in gist[u'files']: 
      u = urllib.urlopen('http://gist.github.com/raw/%s/%s' % (repo, name))
      bytes = u.read()
      u.close()
      with open('%s.%s' % (repo, name), 'wb') as w: 
         w.write(bytes)
      print 'Got %s.%s' % (repo, name)
