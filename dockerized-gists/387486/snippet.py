#
#  redis-geo-test.py
#  Redis proof-of-concept for geo searching
#
#  Created by Berry Groenendijk on 2010-04-30.
#  Copyright 2010 - personal project. All rights reserved.
#
import redis
from random import Random

c = redis.Redis(host='localhost', port=6379, db=9)

LEN = 1000

def gps_distance(gpsLon1, gpsLat1, gpsLon2, gpsLat2):
	'''Distance using spherical law of cosines
	
	Returns: distance in meters
	'''
	import math
	gpsLon1 = math.radians(float(gpsLon1))
	gpsLat1 = math.radians(float(gpsLat1))
	gpsLon2 = math.radians(float(gpsLon2))
	gpsLat2 = math.radians(float(gpsLat2))
	R = float(6371000) #earth's mean radius in meters
	a = math.sin(gpsLat1)*math.sin(gpsLat2) + math.cos(gpsLat1)*math.cos(gpsLat2)*math.cos(gpsLon2-gpsLon1)
	# See function EarthDistance on http://svn.berlios.de/svnroot/repos/gpsd/trunk/gps.py
	# See also http://gpsd.berlios.de/CHANGES, on 10 Febr 2005.
	# a should be in [1, -1] but can sometimes fall outside it by
	# a very small amount due to rounding errors in the preceding
	# calculations (this is prone to happen when the argument points
	# are very close together).	 Thus we constrain it here.
	if abs(a) > 1: a = 1
	elif a < -1: a = -1
	d = math.acos(a) * R;
	return d

def rem_all_geo_keys():
	keys = c.keys("geo:*")
	for k in keys:
		c.delete(k)

def create_geo_items():
	for i in range(LEN):
		lat = 5 + Random().randrange(1, 10)/10.0
		lon = 50 + Random().randrange(1, 10)/10.0
		d = {
			'id': i,
			'lat': lat,
			'lon': lon,
		}
		key = 'geo:%s' % i
		c.hmset(key, d)
		c.zadd('geo:lat', key, lat)
		c.zadd('geo:lon', key, lon)

def show_items():
	for i in range(LEN):
		key = 'geo:%s' % i
		print key, c.hgetall(key)
	print 'geo:lat', c.zrange('geo:lat', 0, -1)
	print 'geo:lon', c.zrange('geo:lon', 0, -1)

def items_by_lat_lon_square(
	zset_range_lat,
	zset_range_lon, 
	current_location=(0.0, 0.0), 
	limit=None, 
	distance_name='distance', 
	lat_name='lat', 
	lon_name='lon',
	):
	"""
	parameters:
	zset_range_lat: tuple(zset_name, lat1, lat2) - latitude range
	zset_range_lon: tuple(zset_name, lon1, lon2) - longitude range
	current_location: (latitude, longitude) - current location
	limit: amount of items returned
	distance_name: name of the attribute added to items returned
		holding the value of the distance between each item and the given
		current location.
	lat_name: attribute name of the objects holding the value of latitude
	lon_name: attribute name of the objects holding the value of longitude
	"""
	def _add_distance(dict, current_location):
		lat, lon = current_location
		dict[distance_name] = gps_distance(lon, lat, dict[lon_name], dict[lat_name])
		return dict
	
	# select items in lat and lon sets
	pipe = c.pipeline()
	pipe.zrangebyscore(*zset_range_lat)
	pipe.zrangebyscore(*zset_range_lon)
	response = pipe.execute()
	# intersection of lat_range and lon_range results in keys in given square
	isect = set(response[0]).intersection(set(response[1]))
	# get list of hashes from all keys in isect
	pipe = c.pipeline()
	for i in isect:
		pipe.hgetall(i)
	found_hashes = pipe.execute()
	# add distance to found hash objects
	found_hashes = [_add_distance(fh, current_location) for fh in found_hashes]
	# sort on distance
	found_hashes.sort(cmp = lambda x, y: cmp(x[distance_name], y[distance_name]))
	if limit:
		return found_hashes[:limit]
	else:
		return found_hashes

if __name__ == "__main__":
	#rem_all_geo_keys()
	#create_geo_items()
	#show_items()
	
	import time
	ITERATIONS = 100
	t0 = time.time()
	for i in range(ITERATIONS):
		found = items_by_lat_lon_square(
			("geo:lat", 5.4, 5.5),
			("geo:lon", 50.4, 50.5),
			current_location = (5.1, 50.43),
			limit=None,
			)
	elapsed = time.time() - t0
	print "Total time: %.2f seconds, iterations: %s, time per iteration: %.2f msec, speed: %.2f req/sec." % (elapsed, ITERATIONS, (elapsed/ITERATIONS) * 1000, 1/(elapsed/ITERATIONS))
	print found, "number of items found: %s" % len(found)

	# >>> python -m cProfile redis-geo-test.py 
	# Total time: 1.96 seconds, iterations: 100, time per iteration: 19.63 msec, speed: 50.94 req/sec.
	#    Ordered by: standard name
	# 
	#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
	#         1    0.000    0.000    0.000    0.000 <string>:1(<module>)
	#         1    0.000    0.000    0.000    0.000 <string>:1(connect)
	#       201    0.021    0.000    0.021    0.000 <string>:1(sendall)
	#         1    0.000    0.000    0.000    0.000 <string>:1(setsockopt)
	#         1    0.000    0.000    0.000    0.000 <string>:1(settimeout)
	#         1    0.001    0.001    0.015    0.015 __init__.py:2(<module>)
	#         1    0.005    0.005    0.014    0.014 client.py:1(<module>)
	#      5600    0.007    0.000    0.084    0.000 client.py:1029(hgetall)
	#         1    0.000    0.000    0.000    0.000 client.py:11(ConnectionPool)
	#         1    0.000    0.000    0.000    0.000 client.py:1126(Pipeline)
	#       200    0.001    0.000    0.001    0.000 client.py:1144(__init__)
	#       400    0.000    0.000    0.000    0.000 client.py:1152(reset)
	#      5801    0.008    0.000    0.010    0.000 client.py:1155(_execute_command)
	#       200    0.030    0.000    1.729    0.009 client.py:1178(_execute_transaction)
	#       200    0.002    0.000    1.731    0.009 client.py:1215(execute)
	#         1    0.000    0.000    0.000    0.000 client.py:13(__init__)
	#         7    0.000    0.000    0.000    0.000 client.py:138(string_keys_to_dict)
	#         1    0.000    0.000    0.000    0.000 client.py:141(dict_merge)
	#         1    0.000    0.000    0.000    0.000 client.py:16(make_connection_key)
	#      5600    0.022    0.000    0.030    0.000 client.py:168(pairs_to_dict)
	#       200    0.000    0.000    0.000    0.000 client.py:172(zset_score_pairs)
	#         1    0.000    0.000    0.000    0.000 client.py:181(Redis)
	#         1    0.000    0.000    0.000    0.000 client.py:20(get_connection)
	#         1    0.000    0.000    0.000    0.000 client.py:212(<lambda>)
	#      5600    0.004    0.000    0.034    0.000 client.py:222(<lambda>)
	#         1    0.000    0.000    0.000    0.000 client.py:234(__init__)
	#       200    0.002    0.000    0.003    0.000 client.py:258(pipeline)
	#         1    0.000    0.000    0.000    0.000 client.py:275(_execute_command)
	#      5801    0.055    0.000    0.084    0.000 client.py:292(execute_command)
	# 89201/6201    0.535    0.000    1.627    0.000 client.py:305(_parse_response) !!
	#         1    0.000    0.000    0.000    0.000 client.py:33(Connection)
	#         1    0.000    0.000    0.000    0.000 client.py:35(__init__)
	#      6201    0.009    0.000    1.637    0.000 client.py:360(parse_response)
	#     12002    0.009    0.000    0.012    0.000 client.py:367(encode)
	#         1    0.000    0.000    0.000    0.000 client.py:377(get_connection)
	#         1    0.000    0.000    0.000    0.000 client.py:387(_setup_connection)
	#         1    0.000    0.000    0.000    0.000 client.py:398(select)
	#   201/200    0.000    0.000    0.001    0.000 client.py:45(connect)
	#   201/200    0.001    0.000    0.022    0.000 client.py:79(send)
	#    243601    0.312    0.000    1.069    0.000 client.py:90(read)
	#       200    0.001    0.000    0.009    0.000 client.py:926(zrangebyscore)
	#         1    0.000    0.000    0.000    0.000 exceptions.py:1(<module>)
	#         1    0.000    0.000    0.000    0.000 exceptions.py:12(ResponseError)
	#         1    0.000    0.000    0.000    0.000 exceptions.py:15(InvalidResponse)
	#         1    0.000    0.000    0.000    0.000 exceptions.py:18(InvalidData)
	#         1    0.000    0.000    0.000    0.000 exceptions.py:3(RedisError)
	#         1    0.000    0.000    0.000    0.000 exceptions.py:6(AuthenticationError)
	#         1    0.000    0.000    0.000    0.000 exceptions.py:9(ConnectionError)
	#         2    0.000    0.000    0.000    0.000 os.py:35(_get_exports_list)
	#         1    0.000    0.000    0.000    0.000 os.py:724(urandom)
	#         1    0.003    0.003    0.003    0.003 random.py:39(<module>)
	#         1    0.000    0.000    0.000    0.000 random.py:609(WichmannHill)
	#         1    0.000    0.000    0.000    0.000 random.py:69(Random)
	#         1    0.000    0.000    0.000    0.000 random.py:759(SystemRandom)
	#         1    0.000    0.000    0.000    0.000 random.py:88(__init__)
	#         1    0.000    0.000    0.000    0.000 random.py:97(seed)
	#     24300    0.014    0.000    0.020    0.000 redis-geo-test.py:105(<lambda>)
	#      5600    0.058    0.000    0.075    0.000 redis-geo-test.py:15(gps_distance)
	#       100    0.029    0.000    1.960    0.020 redis-geo-test.py:64(items_by_lat_lon_square)
	#         1    0.008    0.008    1.986    1.986 redis-geo-test.py:8(<module>)
	#      5600    0.008    0.000    0.083    0.000 redis-geo-test.py:85(_add_distance)
	#         1    0.000    0.000    0.000    0.000 socket.py:138(_closedsocket)
	#         1    0.001    0.001    0.001    0.001 socket.py:146(_socketobject)
	#         1    0.000    0.000    0.000    0.000 socket.py:152(__init__)
	#         1    0.000    0.000    0.000    0.000 socket.py:177(makefile)
	#         1    0.000    0.000    0.000    0.000 socket.py:196(_fileobject)
	#         1    0.000    0.000    0.000    0.000 socket.py:207(__init__)
	#    154400    0.254    0.000    0.281    0.000 socket.py:278(read)
	#     89201    0.203    0.000    0.476    0.000 socket.py:321(readline)
	#         1    0.004    0.004    0.005    0.005 socket.py:43(<module>)
	#         1    0.004    0.004    0.004    0.004 threading.py:1(<module>)
	#         1    0.000    0.000    0.000    0.000 threading.py:152(Condition)
	#         1    0.000    0.000    0.000    0.000 threading.py:155(_Condition)
	#         1    0.000    0.000    0.000    0.000 threading.py:157(__init__)
	#         1    0.000    0.000    0.000    0.000 threading.py:271(_Semaphore)
	#         1    0.000    0.000    0.000    0.000 threading.py:318(_BoundedSemaphore)
	#         1    0.000    0.000    0.000    0.000 threading.py:333(_Event)
	#         1    0.000    0.000    0.000    0.000 threading.py:37(_Verbose)
	#         1    0.000    0.000    0.000    0.000 threading.py:383(Thread)
	#         2    0.000    0.000    0.000    0.000 threading.py:39(__init__)
	#         1    0.000    0.000    0.000    0.000 threading.py:392(__init__)
	#         1    0.000    0.000    0.000    0.000 threading.py:602(_Timer)
	#         1    0.000    0.000    0.000    0.000 threading.py:631(_MainThread)
	#         1    0.000    0.000    0.000    0.000 threading.py:633(__init__)
	#         1    0.000    0.000    0.000    0.000 threading.py:640(_set_daemon)
	#         1    0.000    0.000    0.000    0.000 threading.py:671(_DummyThread)
	#         1    0.000    0.000    0.000    0.000 threading.py:79(_RLock)
	#         1    0.000    0.000    0.000    0.000 traceback.py:1(<module>)
	#      5600    0.001    0.000    0.001    0.000 {abs}
	#         1    0.000    0.000    0.000    0.000 {binascii.hexlify}
	#         1    0.000    0.000    0.000    0.000 {built-in method acquire}
	#         1    0.000    0.000    0.000    0.000 {built-in method release}
	#     24300    0.006    0.000    0.006    0.000 {cmp}
	#         2    0.000    0.000    0.000    0.000 {dir}
	#         1    0.002    0.002    1.988    1.988 {execfile}
	#         1    0.000    0.000    0.000    0.000 {function seed at 0x4223b0}
	#         6    0.000    0.000    0.000    0.000 {getattr}
	#     18203    0.006    0.000    0.006    0.000 {isinstance}
	#    172990    0.027    0.000    0.027    0.000 {len}
	#      5600    0.002    0.000    0.002    0.000 {math.acos}
	#     16800    0.005    0.000    0.005    0.000 {math.cos}
	#         1    0.000    0.000    0.000    0.000 {math.exp}
	#         2    0.000    0.000    0.000    0.000 {math.log}
	#     22400    0.006    0.000    0.006    0.000 {math.radians}
	#     11200    0.003    0.000    0.003    0.000 {math.sin}
	#         1    0.000    0.000    0.000    0.000 {math.sqrt}
	#       183    0.000    0.000    0.000    0.000 {max}
	#    106986    0.024    0.000    0.024    0.000 {method 'append' of 'list' objects}
	#         1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
	#         2    0.000    0.000    0.000    0.000 {method 'extend' of 'list' objects}
	#     89402    0.039    0.000    0.039    0.000 {method 'find' of 'str' objects}
	#       100    0.002    0.000    0.002    0.000 {method 'intersection' of 'set' objects}
	#      6385    0.003    0.000    0.003    0.000 {method 'join' of 'str' objects}
	#         1    0.000    0.000    0.000    0.000 {method 'lower' of 'str' objects}
	#       384    0.237    0.001    0.237    0.001 {method 'recv' of '_socket.socket' objects}
	#         7    0.000    0.000    0.000    0.000 {method 'split' of 'str' objects}
	#         1    0.000    0.000    0.000    0.000 {method 'startswith' of 'str' objects}
	#         8    0.000    0.000    0.000    0.000 {method 'update' of 'dict' objects}
	#         1    0.000    0.000    0.000    0.000 {posix.close}
	#         1    0.000    0.000    0.000    0.000 {posix.open}
	#         1    0.000    0.000    0.000    0.000 {posix.read}
	#      6201    0.005    0.000    0.005    0.000 {range}
	#         6    0.000    0.000    0.000    0.000 {setattr}
	#         2    0.000    0.000    0.000    0.000 {thread.allocate_lock}
	#         1    0.000    0.000    0.000    0.000 {thread.get_ident}
	#         2    0.000    0.000    0.000    0.000 {time.time}
	#      5800    0.009    0.000    0.009    0.000 {zip}
	
	