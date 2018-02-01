import time
import json
import urllib2
import threading

# Settings
MINIMUM  = 2000
MAXIMUM  = 100000
PARALLEL = 100
STORE_ID = 10231

# Containers
coupons = []
threads = {}

def make_thread(target, args=()):
    '''Return a threading.Thread given target and args.'''
    new_thread = threading.Thread(target=target, args=args)
    return new_thread

def save_code(json_str):
    with open('dominos.log', 'a') as fh:
        fh.write('%s\n' % json_str)

def check_code(i):
    # Check code online.
    try:
        url_hnd = urllib2.urlopen(
            'http://express.dominos.ca/power/store/%d/coupon/%d' % \
            (STORE_ID, i))
        print (' *%04d*' % i),
        json_str = url_hnd.read()
        save_code(json_str)
        coupons.append(json.loads(json_str))
    except urllib2.HTTPError:
        print (' %04d' % i),
    # Remove from threads.
    del threads[i]

for code in range(MINIMUM, MAXIMUM):
    while len(threads) > PARALLEL:
        time.sleep(1)
    threads[code] = make_thread(check_code, (code,)).start()
