import multiprocessing
import time
import signal
import sys

# based on http://stackoverflow.com/a/6191991/1711188 
# but instead of calling Pool.join(), we just close and manually poll for processes exiting
# also it assumes we have a finite number of jobs we want to run; if they complete
# it terminates in the normal way

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def worker(jobid):
    time.sleep(1.1234)
    print "Working on job...", jobid

def main():
    pool = multiprocessing.Pool(3, init_worker)
    try:
        results = []
        for i in range(23):
            results.append(pool.apply_async(worker, (i,)))

        pool.close()
        while True:
            if all(r.ready() for r in results):
                print "All processes completed"
                return
            time.sleep(1)

    except KeyboardInterrupt:
        print "Caught KeyboardInterrupt, terminating workers"
        pool.terminate()
        pool.join()


if __name__ == "__main__":
    main()