from multiprocessing import Pool as MPool
from time import sleep
import datetime
import multiprocessing
import random

def time_request():
    from gevent import monkey; monkey.patch_socket
    from jsonrequester import JsonRequester

    base_url = 'http://example.com'
    relative_url = '/blah'
    now = datetime.datetime.utcnow()
    requester = JsonRequester(base_url)
    result = requester.get(relative_url)
    return (datetime.datetime.utcnow() - now, result)

def gevent_req(num_req):
    from gevent.pool import Pool as GPool
    import gevent
    pool = GPool(num_req/2)
    glets = []
    for x in range(0, num_req):
        with gevent.Timeout(10, False):
            g = pool.spawn(time_request)
            glets.append(g)
        pool.join()
    return [g.value for g in glets]

if __name__ == "__main__":
    num_reqs = 10000
    num_procs = multiprocessing.cpu_count()*4
    num_greqs = int(num_reqs/num_procs)
    num_reqs = num_greqs * num_procs

    pool = MPool(processes=num_procs)
    results = []
    now = datetime.datetime.utcnow()
    for i in range(0, num_procs):
        result = pool.apply_async(gevent_req, (num_greqs,))
        results.append(result)
    pool.close()
    pool.join()

    print len(results)

    total_time = datetime.timedelta(0)
    for result in results:
        while not result.ready():
            sleep(5)
        res = result.get(timeout=1)
        

    print datetime.datetime.utcnow() - now
    print total_time