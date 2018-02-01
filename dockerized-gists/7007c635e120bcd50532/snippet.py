#!/usr/bin/python

from __future__ import print_function
import requests
import sys
import json

def get_response(idval, sessid):
  headers = {'Session': sessid[0]}
  req = 'http://challenge.shopcurbside.com/'
  if not idval:
    req += 'start'
  else:
    req += idval
  print ('.',end="")
  sys.stdout.flush()
  response = requests.get(req, headers=headers)
  if not response:
    if response.text:
      data = json.loads(response.text)
      if "error" in data:
        if data["error"] == "Invalid session id, a token is valid for 10 requests.":
          nextsess = get_session()
          sessid[0] = nextsess
          return get_response(idval, sessid)
      else:
        print ("Got unknown error")
        sys.exit(1)
    else:
      print ("Got a -ve response for req:%s with no text"%req)
      sys.exit(1)
  data = json.loads(response.text)
  offending_keys = []
  for keys in data:
    if keys.lower() != keys:
      offending_keys.append(keys)
  for i in offending_keys:
    data[i.lower()] = data[i]
  if 'next' in data:
    return ('N', data['next'])
  elif 'secret' in data:
    return ('S', data['secret'])
  else:
    print ("unrecognized data for req:%s"%req)
    sys.exit(1)

def get_session():
  print ('+',end="")
  sys.stdout.flush()
  response = requests.get('http://challenge.shopcurbside.com/get-session')
  if not response:
    print ("Got a -ve response for get-session")
    sys.exit(1)
  return response.text

def get_values(next_depth, collection, sess, secret):
  if next_depth not in collection:
    return
  if not collection[next_depth]:
    return
  while collection[next_depth]:
    ida = collection[next_depth].pop(0)
    result = get_response(ida, sess)
    if result[0] == 'N':
      if not next_depth+1 in collection:
        collection[next_depth+1] = []
      if isinstance(result[1],list):
        collection[next_depth+1].extend(result[1])
      else:
        collection[next_depth+1].append(result[1])
      get_values(next_depth+1, collection, sess, secret)
    elif result[0] == 'S':
      secret.append(result[1])

if __name__ == '__main__':
  sess = get_session()
  collection = {}
  a=get_response(None,[sess])
  if a[0] != 'N':
    print("first depth should be N")
    sys.exit(1)
  collection[1] = []
  collection[1].extend(a[1])
  secret = []
  get_values(1, collection, [sess], secret)
  print ('\n'+''.join(secret))

