#!/usr/bin/env python3.4

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from binascii import unhexlify
from gmlan import parse_frame
from datetime import datetime

import socket
import threading
from queue import Queue
import sys
import time

# Check we got an arg
if len(sys.argv) != 2:
  print('Provide CAN device name (can0, slcan0 etc.)')
  sys.exit(1)

# lock for output
lock = threading.Lock()

# Do the write to ES
def write(es, items):
  with lock:
    actions = []
    for item in items:
      action = {
        "_index": "gmlan",
        "_type": "packet",
        "_source": item
      }
      actions.append(action)
    helpers.bulk(es, actions, chunk_size=128)
    print("Wrote " + str(len(actions)) + " items to Elastic Search")

# Worker to write items to elastic search
def poll_queue():
  es = Elasticsearch(['vega.host64.net'])
  while True:
    items = q.get()
    write(es, items)
    q.task_done()

# Create a thread to poll the queue and write
# the items to elastic search
t = threading.Thread(target=poll_queue)
t.daemon = True
t.start()

# Initialise a queue to hold all the items
q = Queue()

# List to bundle up packets into to use bulk writes
items = []

# create a raw socket and bind it to the given CAN interface
s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
s.bind((sys.argv[1],))

try:
  while True:
    cf, addr = s.recvfrom(16)
    # Parse parts from data ad put it in the queue
    arbid, priority, station, dlc, data = parse_frame(cf)
    item = {
      'arbid': arbid,
      'priority': priority,
      'station': station,
      'dlc': dlc,
      'msgtime': datetime.now(),
      'data': []
    }
    if dlc > 0:
      for i in range(0, dlc):
        byte = "b"+str(i)
        item[byte] = hex(data[i])
        item['data'].append(hex(data[i]))
    items.append(item)

    # When we have 1024 items push them to the queue to be written out
    if len(items) >= 1024:
      q.put(items)
      items = []

except KeyboardInterrupt:
  print ("Interrupted, writing any left over messages before exit")
  # Get any stragglers placed on the queue
  if len(items) > 0:
    q.put(items)
  q.join() # block until the writers are done
  print ("Writers competed, items written to ES")