import urllib2
import json
import Queue
import threading

MAGIC_NUM = 543097027

def scrap(t_id, in_q, lst, exit_event, lock):
    while True:
        try:
            item = in_q.get(timeout=2e-2)
            in_q.task_done()
        except Queue.Empty:
            if exit_event.is_set():
                break
            continue

        try:
            opener = urllib2.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            raw = opener.open('http://api.gojek.co.id/gojek/booking/' + 
                              str(item))
            obj = json.loads(raw.read())
        except:
            continue

        lock.acquire()
        lst.append(obj)
        lock.release()

def main():
    for j in xrange(100):
        n = 80
        in_q = Queue.Queue()
        lst = []
        exit_event = threading.Event()
        lock = threading.Lock()

        workers = []
        for i in xrange(n):
            worker = threading.Thread(target=scrap, 
                                      args=(i, in_q, lst, exit_event, lock))
            worker.daemon = True
            workers.append(worker)

        for worker in workers:
            worker.start()

        for i in xrange(1000):
            in_q.put(MAGIC_NUM+i+j*1000)

        in_q.join()
        exit_event.set()
        
        for worker in workers:
            worker.join()
        
        with open('gojek' + '%02d' % j + '.txt', 'w') as f:
            json.dump(lst, f)
        
        print 'done with the %d to %d' % (MAGIC_NUM+j*1000, 
                                          MAGIC_NUM+(j+1)*1000-1)

if __name__ == '__main__':
    main()
