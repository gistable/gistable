import redis
import logging

class RedisLogHandler:
    """Log handler for logging logs in some redis list
    """
    def __init__(self, host = None, port = None, db = 0, log_key = 'log_key'):
	self._formatter = logging.Formatter()
	self._redis = redis.Redis(host = host or 'localhost', port = port or 6379, db = db)
	self._redis_list_key = log_key
	self._level = logging.DEBUG
		
    def handle(self, record):
	try:
	    self._redis.lpush(self._redis_list_key, self._formatter.format(record)) 
	except:
	    #can't do much here--probably redis have stopped responding...
	    pass

    def setFormatter(self, formatter):
	self._formatter = formatter

    @property
    def level(self):
	return self._level 

    def setLevel(self, val):
	self._level = val
