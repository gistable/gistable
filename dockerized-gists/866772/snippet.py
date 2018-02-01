#! /usr/bin/env python

"""
Script to copy all bookmarks from Read It Later to Instapaper.

See also http://readitlaterlist.com/api/docs/#get
and http://www.instapaper.com/api/simple
"""

import urllib, urllib2, json

RIL_ENDPOINT = 'https://readitlaterlist.com/v2'
IP_ENDPOINT = 'https://www.instapaper.com/api'

def main(ril_api_key, ril_usr, ril_pwd, ip_usr, ip_pwd):
  
  # fetch bookmarks from RIL as JSON
  ril_query = urllib.urlencode({'username':ril_usr, 'password':ril_pwd,'apikey':ril_api_key})
  ril_url = '%s/get?%s' %(RIL_ENDPOINT, ril_query)
  f = urllib2.urlopen(ril_url)
  bookmarks = json.loads(f.read())['list']

  # import bookmarks into Instapaper
  count = 0
  for bm in bookmarks.values():
    ip_query = urllib.urlencode({'url':bm['url'],'title':bm['title'].encode('utf-8'), 'username':ip_usr, 'password':ip_pwd})
    ip_url = '%s/add?%s' %(IP_ENDPOINT, ip_query)
    urllib2.urlopen(ip_url)
    count += 1
    print ''''%s' copied successfully''' %bm['title']
    
  print '%d bookmarks copied' %count

if __name__ == "__main__":
  import sys
  apply(main, sys.argv[1:])