#!/usr/bin/env python
import urllib2
import datetime

offset = 33039 #initial id
first = datetime.datetime(1990,1,1) #initial date
today = datetime.datetime.today()
for i in xrange(offset, offset+(today-first).days):
  _dirs = [0]
  for j in range(9,1,-1):
    p = 10**j
    _dirs.append(i/p*p-sum(_dirs))
  _dirs.pop(0)
  _dirs.append(i)
  url = "http://www.dilbert.com/dyn/str_strip/"
  for k,e in enumerate(_dirs):
    if k:
      url+="".join(["%0",str(10-k),"d/"]) % e
  url+="%d.strip.gif" % i
  filename=(first+datetime.timedelta(i-offset)).strftime('%Y-%m-%d.gif');
  c = urllib2.urlopen(url)
  if c.headers['content-type'] == 'image/gif':
    file(filename, "wb").write(c.read())
