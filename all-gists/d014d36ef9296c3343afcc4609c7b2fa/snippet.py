import json
import datetime
import pytz
from random import randint
import logging
import time
import redis

main_prefix = "bqueues:"

class ClientRedisQueue():
    def __init__(self, qname, clientid, redis):
        self.client_id = clientid
        self.queue_name = main_prefix + qname + ":" + clientid
        logging.debug("created queue %s" % self.queue_name)
        self.redis = redis

    def send(self, msgs):
        jmsgs = [json.dumps({ "client_id" : self.client_id, "msg" : msg, "attempts" : 0}) for msg in msgs]
        self.redis.lpush(self.queue_name, *jmsgs)

    def exists(self):
        return self.redis.exists(self.queue_name)

    def length(self):
        return self.redis.llen(self.queue_name) 

    def delete(self):
        self.redis.delete(self.queue_name)

MAX_ATTEMPTS_COUNT = 4
class WorkerRedisQueue():
    def __init__(self, name, redis):
        self.queue_name = main_prefix + name
        self.processing_lname = main_prefix + "processing:" + name
        self.dead_sname = main_prefix + "dead:" + name
        self.refresh_period = datetime.timedelta(seconds=2)
        self.queue_pattern = self.queue_name + "*"
        self.redis = redis
        self.last_refresh_time = datetime.datetime.now(pytz.utc) - self.refresh_period - self.refresh_period
        self.list_names = []

    def proccessed(self, msg):
        self.redis.lrem(self.processing_lname, 0, json.dumps(msg))

    # start this from time to time
    def recover(self):
        recovered = 0
        proc_msgs = self.redis.lrange(self.processing_lname, -5,-1)
        for (msg, orig) in [(json.loads(msg),msg) for msg in proc_msgs if msg]:
            if msg["attempts"] > MAX_ATTEMPTS_COUNT:
                print "found dead letter"
                self.redis.sadd(self.dead_sname, orig)
            else:
                print "recovering"
                recovered = recovered + 1
                msg["attempts"] = msg["attempts"] + 1
                self.redis.lpush("%s:%s" % (self.queue_name, msg["client_id"]), json.dumps(msg))
            self.redis.lrem(self.processing_lname, 0, orig)

        return recovered

    def get_list_names(self):
        lists = []
        print "searching pattern", self.queue_pattern
        for l in self.redis.scan_iter(self.queue_pattern):
            print "found list", l
            lists.append(l)
        return lists

    def refresh(self, force = False):
        now = datetime.datetime.now(pytz.utc)
        time_to_refresh = now - self.last_refresh_time > self.refresh_period
        if force or time_to_refresh:
            self.list_names = self.get_list_names()
            self.last_refresh_time = now
        else:
            print "skip refresh"

    def receive(self, count):
        self.refresh()
        count = len(self.list_names)
        if count == 0:
            print "queues not found"
            return []
        p = self.redis.pipeline()
        for i in range(count):
            l = self.list_names[randint(0, count - 1)]
            p.rpoplpush(l,self.processing_lname)
        msgs = p.execute()
        return [json.loads(msg) for msg in msgs if msg]

    def length(self):
        self.refresh(True)
        res = 0
        for l in self.list_names:
            res = res + self.redis.llen(l)
        return res

if __name__ == "__main__":
    r = redis.StrictRedis("localhost", password="")
    cq = ClientRedisQueue("worker1", "client", r)

    cq2 = ClientRedisQueue("worker1", "client2", r)
    cq.send([1,2])
    cq2.send([3,4,0])
    wq = WorkerRedisQueue("worker1", r)
    while(True):
        time.sleep(1)
        msgs = wq.receive(2)
        if len(msgs) == 0:
            if randint(0, 10) == 0 and wq.length() == 0 and wq.recover() == 0:
                print "sleeping"
                time.sleep(1)
                
        for msg in msgs:
            print "received msg", msg
            try:
                a = 10/msg["msg"]
                wq.proccessed(msg)
            except Exception,e: 
                print "exception", str(e)
            
        

