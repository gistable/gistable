import sys
import time
import json

import requests

endpoint = sys.argv[1]

while True:
    r = requests.get(endpoint, stream=True, timeout=600)
    for line in r.iter_lines(chunk_size=1):
        if line:
            blob = json.loads(line)

            print '--------', int(time.time()), '->'
            print json.dumps(blob, sort_keys=True, indent=2)
            print ''
            print ''

    print 'sleeping before reconnect'
    time.sleep(1)