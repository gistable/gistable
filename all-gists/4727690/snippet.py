#!/usr/bin/env python

import json
import os
import time

import clouddns

USERNAME = ''
APIKEY   = ''
DIRECTORY = ''

dns = clouddns.connection.Connection(USERNAME, APIKEY)
domains = dns.get_domains()

DIRECTORY = os.path.expanduser(DIRECTORY)
if not os.path.exists(DIRECTORY):
    os.makedirs(DIRECTORY)

for domain in domains:
    finished = False
    response = json.loads(dns.make_request('GET', ["domains", domain.id, "export"]).read())
    try:
        status = response['callbackUrl'].split('/')[-2:]
    except KeyError as e:
        print response

    # Prevent rate-limiting
    time.sleep(5)

    while not finished:
        try:
            records = json.loads(dns.make_request('GET', status, parms = {'showDetails': "true"}).read())['response']['contents']
            filename = os.path.join(DIRECTORY, "%s.bind9" % domain.name)
            print "Creating %s" % filename
            with open(filename, 'w') as f:
                f.write(records)
        except KeyError as e:
            print "Request is still running for %s, retrying..." % domain.name
            time.sleep(5)
        else:
            finished = True