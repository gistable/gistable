#!/usr/bin/env python
__author__ = 'Kevin Warrick'
__email__  = 'kwarrick@uga.edu'

import cPickle
from functools import wraps

def redis_lru(capacity=5000, slice=slice(None)):
	"""
	Simple Redis-based LRU cache decorator *.
	*conn* 	    Redis connection
	*capacity*  maximum number of entries in LRU cache
	*slice*    slice object for restricting prototype args
	
	Usage is as simple as prepending the decorator to a function, 
	passing a Redis connection object, and the desired capacity 
	of your cache. 
	
	@redis_lru(capacity=10000)
	def func(foo, bar):
		# some expensive operation
		return baz
		
	func.init(redis.StrictRedis())
	
	Uses 4 Redis keys, all suffixed with the function name:
		lru:keys: - sorted set, stores hash keys
		lru:vals: - hash, stores function output values
		lru:hits: - string, stores hit counter
		lru:miss: - string, stores miss counter
	
	* Functions prototypes must be serializable equivalent!
	"""
	def decorator(func):
		cache_keys = "lru:keys:%s" % (func.__name__,)
		cache_vals = "lru:vals:%s" % (func.__name__,)
		cache_hits = "lru:hits:%s" % (func.__name__,)
		cache_miss = "lru:miss:%s" % (func.__name__,)
		
		lvars = [None]		# closure mutable 
		
		def add(key, value):
			eject()
			conn = lvars[0]
			conn.incr(cache_miss)
			conn.hset(cache_vals, key, cPickle.dumps(value))
			conn.zadd(cache_keys, 0, key)
			return value
			
		def get(key):
			conn = lvars[0]
			value = conn.hget(cache_vals, key)
			if value:
				conn.incr(cache_hits)
				conn.zincrby(cache_keys, key, 1.0)
				value = cPickle.loads(value)
			return value
			
		def eject():
			conn = lvars[0]
			count = min((capacity / 10) or 1, 1000)
			if conn.zcard(cache_keys) >= capacity:
				eject = conn.zrange(cache_keys, 0, count)				
				conn.zremrangebyrank(cache_keys, 0, count)
				conn.hdel(cache_vals, *eject)
						
		@wraps(func)
		def wrapper(*args, **kwargs):
			conn = lvars[0]
			if conn:
				items = args + tuple(sorted(kwargs.items()))
				key = cPickle.dumps(items[slice])
				return get(key) or add(key, func(*args, **kwargs))
			else:
				return func(*args, **kwargs)
		
		def info():
			conn = lvars[0]
			size = int(conn.zcard(cache_keys) or 0)
			hits, misses = int(conn.get(cache_hits) or 0), int(conn.get(cache_miss) or 0)
			return hits, misses, capacity, size
		
		def clear():
			conn = lvars[0]
			conn.delete(cache_keys, cache_vals)
			conn.delete(cache_hits, cache_miss)
		
		def init(conn):
			lvars[0] = conn
		
		wrapper.init = init
		wrapper.info = info
		wrapper.clear = clear
		return wrapper
	return decorator

if __name__ == "__main__":
	import redis

	conn = redis.StrictRedis()

	@redis_lru(capacity=10)
	def test(foo, bar, baz=None):
		print 'called test.'
		return True

	conn = redis.StrictRedis()
	test.init(conn)

	test.clear()
	test(1, 2, baz='A')
	test(3, 4, baz='B')
	test(1, 2, baz='A')
	print "hits %d, misses %d, capacity %d, size %d" % test.info()
	
	test(1, 2, baz='A')
	test(3, 4, baz='B')
	test(1, 2, baz='A')

	print "hits %d, misses %d, capacity %d, size %d" % test.info()
