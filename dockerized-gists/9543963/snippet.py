#!/usr/bin/env python
# -*- coding: utf-8 -*-
# http://blog.ithomer.net

import time
import redis
import threading

class Listener(threading.Thread):
    def __init__(self, r, channels):
        threading.Thread.__init__(self)
        self.redis = r
        self.pubsub = self.redis.pubsub()   # 发布订阅对象
        self.pubsub.subscribe(channels)     # 订阅
        
    def work(self, item):
        print item['channel'], ":", item['data']
        
    def run(self):
        for item in self.pubsub.listen():
            print item
            if item['data'] == "KILL":
                print self, "unsubscribed and finished"
                self.pubsub.unsubscribe()   # 取消订阅
                break
            else:
                self.work(item)
                
            time.sleep(3)   # 暂停1秒
        
        
if __name__ == "__main__":
    r = redis.Redis()
    client = Listener(r, ['test', 'test2'])     # 仅订阅 'test', 'test2'， 'fail' 将被过滤掉
    client.start()
    
    r.publish('test', 'this will reach the listener')
    r.publish('test2', 'this will work')
    r.publish('fail', 'this will not')          # 被过滤掉了
    r.publish('test', 'KILL')