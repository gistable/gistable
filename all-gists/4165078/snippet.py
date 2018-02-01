from multiprocessing.process import Process
import time
import redis

def pub(myredis):
    for n in range(10):
        myredis.publish('channel','blah %d' % n)
        time.sleep(5)

def sub(myredis, name):
    pubsub = myredis.pubsub()
    pubsub.subscribe(['channel'])
    for item in pubsub.listen():
        print '%s : %s' % (name, item['data'])

if __name__ == '__main__':
    myredis = redis.Redis()
    Process(target=pub, args=(myredis,)).start()
    Process(target=sub, args=(myredis,'reader1')).start()
    Process(target=sub, args=(myredis,'reader2')).start()