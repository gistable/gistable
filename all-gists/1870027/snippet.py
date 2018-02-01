import redis
import time
import sys

def producer():
    r = redis.Redis()

    i = 0
    while True:
        r.rpush('queue', 'Message %d' % i)
        i += 1
        time.sleep(1)

def consumer():
    r = redis.Redis()
    while True:
        val = r.blpop('queue')
        print 'Consuming: (%s, %s)' % val

if __name__ == '__main__':
    """
    Open up two terminals and run the two commands separately
    """
    if sys.argv[1] == 'consumer':
        print "Starting consumer: "
        consumer()
    else:
        print "Starting producer: "
        producer()