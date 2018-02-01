import time
import random
from multiprocessing import Process, Queue, JoinableQueue, cpu_count

""" Adjust time.sleep() values to see action of consumer """

def work(id, jobs, result):
    while True:
        task = jobs.get()
        if task is None:
            break
        time.sleep(0.0)
        print "%d task:" % id, task
        result.put("%s task r")
    #result.put(None)

def main():
    jobs = Queue()
    result = JoinableQueue()
    NUMBER_OF_PROCESSES = cpu_count()
    
    tasks = ["1","2","3","4","5"]
    
    for w in tasks:
        jobs.put(w)

    [Process(target=work, args=(i, jobs, result)).start()
            for i in xrange(NUMBER_OF_PROCESSES)]
    
    print 'starting workers'
    
    for t in xrange(len(tasks)):
        r = result.get()
        time.sleep(0.5)
        print r
        result.task_done()
    
    for w in xrange(NUMBER_OF_PROCESSES):
        jobs.put(None)

    result.join()
    jobs.close()
    result.close()

if __name__ == '__main__':
    main()