#!/usr/local/bin/python

import requests
import json

def call_rabbitmq_api(host, port, user, passwd):
  url = 'http://%s:%s/api/queues' % (host, port)
  r = requests.get(url, auth=(user,passwd))
  return r

def get_queue_name(json_list):
  res = []
  for json in json_list:
    res.append(json["name"])
  return res

if __name__ == '__main__':
  host = 'rabbitmq_host'
  port = 55672
  user = 'basic_auth_user'
  passwd = 'basic_auth_password'
  res = call_rabbitmq_api(host, port, user, passwd)
  print "--- dump json ---"
  print json.dumps(res.json(), indent=4)
  print "--- get queue name ---"
  q_name = get_queue_name(res.json())
  print q_name

  
