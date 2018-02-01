#!/usr/bin/env python
#
# Simple script showing how to read a mitmproxy dump file
#

### UPD: this feature is now avaiable in mitmproxy: https://github.com/mitmproxy/mitmproxy/pull/619

from libmproxy import flow
import json, sys

with open("mitmproxy_dump.txt", "rb") as logfile:
    freader = flow.FlowReader(logfile)
    try:
        for f in freader.stream():
            request = f.request
            print(request)
            curl = 'curl -X ' + request.method + ' -d \'' + request.content + '\' ' + ' '.join(['-H ' + '"' + header[0] + ': ' + header[1] + '"' for header in request.headers])
            curl += " https://" + request.host + request.path
            print(curl)
            print("--")

    except flow.FlowReadError as v:
        print("Flow file corrupted. Stopped loading.")
