from datetime import datetime

# See https://gist.github.com/672279/
from inoi.util.random import sequential_id, monotonic_id

import httplib2
import json
import random
import time
import sys
import uuid

id_makers = {
    'random': lambda: uuid.uuid4().hex,
    'monotonic': monotonic_id,
    'sequential': sequential_id,
}

database = sys.argv[1]
make_id = id_makers[sys.argv[2]]
baseurl = 'http://localhost:5984/%s' % database

bulk_size = 2000
total_docs = 2000000

http = httplib2.Http()
def send_bulk(bulk):
    resp, content = http.request(
        baseurl + '/_bulk_docs',
        method='POST',
        body=json.dumps({'docs': bulk}),
    )

def make_bulk(size):
    return [
        {
            '_id': make_id(),
            'timestamp': datetime.now().isoformat(),
            'data': random.random() * 2000,
        }
        for i in xrange(size)
    ]

def main():
    max_bulk_rate = (-1, float('-inf'))
    min_bulk_rate = (-1, float('inf'))
    loop = 0

    def print_stats():
        end = time.time()
        total_rate = (loop * bulk_size) / (end - start)

        print '== loop %d ============================' % loop
        print 'peak min: in loop %d, %.2f docs/sec' % min_bulk_rate
        print 'peak max: in loop %d, %.2f docs/sec' % max_bulk_rate
        print 'current: %.2f docs/sec' % bulk_rate
        print 'total: %.2f docs/sec' % total_rate

    start = time.time()
    while True:
        loop += 1

        bulk_start = time.time()
        bulk = make_bulk(bulk_size)
        send_bulk(bulk)
        bulk_end = time.time()
        bulk_rate = bulk_size / (bulk_end - bulk_start)

        if bulk_rate > max_bulk_rate[1]:
            max_bulk_rate = (loop, bulk_rate)
        if bulk_rate < min_bulk_rate[1]:
            min_bulk_rate = (loop, bulk_rate)

        if loop % 20 == 0:
            print_stats()

        if loop * bulk_size >= total_docs:
            break

    print ''
    print 'FINISHED:'
    print_stats()

if __name__ == '__main__':
    main()

# python couchdb_test.py test_sequential_id sequential
#
# FINISHED:
# == loop 1000 ============================
# peak min: in loop 5, 3057.95 docs/sec
# peak max: in loop 8, 7904.39 docs/sec
# current: 7449.51 docs/sec
# total: 7294.78 docs/sec
#
# database size on disk: 648548454 bytes = 0.6 GB

# python couchdb_test.py test_monotonic_id monotonic
#
# FINISHED:
# == loop 1000 ============================
# peak min: in loop 195, 1911.73 docs/sec
# peak max: in loop 161, 7703.18 docs/sec
# current: 7511.34 docs/sec
# total: 7353.81 docs/sec
#
# database size on disk: 611405926 = 0.6 GB

# python couchdb_test.py test_random_id random
#
# FINISHED:
# == loop 1000 ============================
# peak min: in loop 889, 535.66 docs/sec
# peak max: in loop 1, 5473.21 docs/sec
# current: 1685.13 docs/sec
# total: 2133.34 docs/sec
#
# database size on disk: 4330426472 = 4.0 GB
