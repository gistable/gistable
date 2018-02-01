#!/usr/bin/python

import redis
import pickle
import argparse


class RedisMigrate():

	def __init__(self, host, port, db):
		self._redis = redis.StrictRedis(host=host, port=port, db=db)
		print "Connecting to redis %s:%d db=%d" % (host, port, db)

	def download(self, fileName):
		keys = self._redis.keys("*")
		data = {}
		i = 0
		keysIHave = len(keys)
		print "Got %d keys from the db" % keysIHave
		onePercent = keysIHave/100

		for key in keys:
			data[key] = self._redis.dump(key)
			i += 1
			if i % onePercent == 0:
				print "Dumped (%d/%d) keys " % (i, keysIHave)

		print "Starting dump to file %s" % fileName

		pickle.dump(data, open(fileName, "wb"))
		print "Done"

	def upload(self, fileName, ttl):
		print "Loading data from %s" % fileName
		data = pickle.load(open(fileName))

		i = 0
		keysIHave = len(data)
		print "Got %d keys in %s" % (keysIHave, fileName)
		onePercent = keysIHave/100

		for key in data:
			try:
				self._redis.restore(key, ttl*1000, data[key])
			except Exception as e:
				print "Failed on %s due to %s" % (key, str(e))
			i += 1
			if i % onePercent == 0:
				print "Loaded (%d/%d) keys to redis " % (i, keysIHave)

		print "Done"


if __name__ == "__main__":
	load = False
	parser = argparse.ArgumentParser(description='Redis migration utility')
	parser.add_argument("--host", help="redis host", default="localhost")
	parser.add_argument("-p", "--port", type=int, help="redis port", default=6379)
	parser.add_argument("--db", type=int, help="redis db number", default=0)
	parser.add_argument("-t", "--ttl", type=int, help="time to live for the keys in seconds", default=604800)
	parser.add_argument("-f", "--filename", help="filename to read from / write to ", default="data.pickle")
	
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-d', "--download", help="download data from redis to file", action="store_true")
	group.add_argument('-u', "--upload", help="upload serialized data from file to redis ", action="store_true")
	args = parser.parse_args()
	
	rm = RedisMigrate(args.host, args.port, args.db)
	if args.upload:
		rm.upload(args.filename, args.ttl)
	else:
		rm.download(args.filename)

	print "Done"
