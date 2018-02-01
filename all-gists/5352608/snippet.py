from apscheduler.scheduler import Scheduler
import datetime as dt

sched = Scheduler()
sched.start()

def timeout(job_fn, *fn_args, **delta_args):
    """Like setTimeout in javascript; returns a job object
    
    First argument is the function to be called.
    
    Positional arguments will be passed to the function when it's called.
    
    Keyword arguemnts will be passed to datetime.timedelta
    
    Usage:
        # calls `fn()` after 3 seconds
        timeout(fn, seconds=3)
        
        # calls `fn(foo, bar)` after 10 seconds
        timeout(fn, foor, bar, seconds=10)
    """
    time = dt.datetime.now() + dt.timedelta(**delta_args)
    return sched.add_date_job(job_fn, time, fn_args)


# Example usage:

def hello_spam(name): 
    print "Hello {0}".format(name)
    timeout(hello_spam, name, seconds=1)

hello_spam("Dude")

import time
time.sleep(15)