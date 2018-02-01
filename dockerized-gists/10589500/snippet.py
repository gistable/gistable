import urlparse
import argparse
import redis
import sys
from multiprocessing import Pool
import signal

def parse_redis_url(s):
    url = urlparse.urlparse(s)
    if not url.scheme:
        s = 'redis://' + s
        url = urlparse.urlparse(s)
    if url.scheme != 'redis':
        print 'Invalid scheme %s for %s'%(url.scheme,s)
        return None
    try:
        db = int(url.path)
    except ValueError:
        db = 0        
    return (url.hostname, url.port or 6379, url.password, db)
    
def compare_string(src, dst, key):
    if src.get(key) != dst.get(key):
        return False
    return True        

def compare_hash(src, dst, key):
    h1 = src.hgetall(key)
    h2 = dst.hgetall(key)
    if set(h1) != set(h2):
        return False
        
    for k,v in h1.iteritems():
        if h2[k] != v:
            return False
    return True            

def compare_list(src, dst, key):
    if src.lrange(key, 0, -1) != dst.lrange(key, 0, -1):
        return False
    return True            

def compare_set(src, dst, key):
    if src.smembers(key) != dst.smembers(key):
        return False
    return True            

def compare_zset(src, dst, key):
    if src.zrange(key, 0, -1, withscores = True) != dst.zrange(key, 0, -1, withscores = True):
        return False
    return True
    
def compare(key):
    try:
        res = cmp_funcs[src.type(key)](src, dst, key)
        if not res:
            print "key '%s' differs"%key
        return res
    except redis.ResponseError as e:
        print "Error '%s' when comparing key: '%s', skipping"%(e, key)
        return True

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    
if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Redis diff tool.')
    argparser.add_argument('--src', required='True')
    argparser.add_argument('--dst', required='True')
    
    args = argparser.parse_args()
    
    host,port,password,db = parse_redis_url(args.src)
    src = redis.Redis(host = host, port = port, password = password, db = db)
    host,port,password,db = parse_redis_url(args.dst)
    dst = redis.Redis(host = host, port = port, password = password, db = db)
    
    src_key_count = src.dbsize()
    dst_key_count = dst.dbsize()
    if dst_key_count != src_key_count:
        print "Source and destination key counts differ (%d : %d)"%(src_key_count, dst_key_count)
        
    cmp_funcs = {}
    for t in ['string', 'hash', 'list', 'set', 'zset']:
        cmp_funcs[t] = globals().get("compare_" + t)
        
    pool = Pool(50, init_worker)
    
    it = 0
    scanned = 0
    diffs = 0
    try:
        while True:
            it, keys = src.execute_command('scan', int(it), 'count', 1000)
            if int(it) == 0:
                break

            # Use multiprocess pool to compare lots of keys simultaneously
            res = pool.map(compare, keys)
            diffs += len([x for x in res if x == False])

# Straight forward non-parallel approach, slower
#            for key in keys:
#                try:
#                    if not compare(key):
#                        print "key '%s' differs"%key
#                        diffs += 1
#                except redis.ResponseError as e:
#                    print "Error '%s' when comparing key: '%s'"%(e, key)
                    
            scanned += len(keys)
            sys.stdout.write("\rprogress: {:3.2f}".format(100.0*float(scanned)/src_key_count))
            sys.stdout.flush()
    
        print 'Done. Found %d diffs'%diffs                

    except KeyboardInterrupt:
        print "Caught KeyboardInterrupt, terminating workers"
        pool.terminate()
        pool.join()        
