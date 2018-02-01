"""Task queue using redis.

Redis client:
    LPUSH work "say Hello world!"
    LPUSH work "log This goes into syslog"
"""

import redis
from multiprocessing import Pool

QUEUE_NAME = 'work'
CMD = {}

def main():
    """Main loop. Dispatch messages"""

    conn = redis.Redis()

    pool = Pool()                             # Default pool size is cpu_count
    while True:
        func_msg = conn.blpop(QUEUE_NAME)[1]  # Blocking get from redis queue
        pool.apply_async(wrapper, [func_msg]) # Run task in sub process

def wrapper(cmd_msg):
    """Call function in try / catch. Runs in sub process.
    @param cmd_msg Format is <cmd> <arg1 arg2 ..>
    """
    cmd = CMD[cmd_msg.split()[0]]
    msg = cmd_msg[cmd_msg.index(' ') + 1:]
    try:
        cmd(msg)
    except Exception, err:
        print('Caught exception %s!' % err)

def task(func):
    """Decorator. Register this function as a task"""
    CMD[func.__name__] = func
    return func

#
# Example tasks.
#

@task
def say(msg):
    print(msg)

@task
def log(msg):
    import syslog
    syslog.syslog(msg)

@task
def sleep(msg):
    import time
    time.sleep(int(msg))

if __name__ == '__main__':
    main()