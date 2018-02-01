from redis import Redis
import simplejson

class Resque(object):
    """Dirt simple Resque client in Python. Can be used to create jobs."""
    redis_server = 'localhost:6379'

    def __init__(self):
        host, port = self.redis_server.split(':')
        self.redis = Redis(host=host, port=int(port))

    def push(self, queue, object):
        key = "resque:queue:%s" % queue
        self.redis.push(key, simplejson.dumps(object))

    def pop(self, queue):
        key = "resque:queue:%s" % queue
        return simplejson.loads(self.redis.pop(key))

queue = Resque()
queue.push('default', {'class':'ShellJob', 'args':['which', 'cat']})
