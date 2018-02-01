import threading
import urllib2
import time, random

class GrabUrl(threading.Thread):
    def __init__(self, arg0):
        threading.Thread.__init__(self)
        self.host=arg0
    def run(self):
        k=random.randint(10,20)
        print "Processing " + self.host + " waiting for : " + str(k)
        time.sleep(k)
        print "exiting " + self.host
        pool.release()

class Handler(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        for i in hosts:
            pool.acquire()
            graburl=GrabUrl(i)
            graburl.setDaemon(True)
            graburl.start()

maxconn=2
pool=threading.BoundedSemaphore(value=maxconn)
hosts=["http://yahoo.com", "http://google.com", "http://amazon.com", "http://ibm.com", "http://apple.com"]
print str(len(hosts))
handler=Handler()
handler.start()
handler.join()
print "exiting main"
