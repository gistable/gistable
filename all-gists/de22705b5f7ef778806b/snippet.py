#-*- coding: big5 -*-
#-*- coding: cp950 -*-
import time
from concurrent import futures

# pip install futures
# More information:
# https://docs.python.org/3/library/concurrent.futures.html
def process(x):
    time.sleep(2)
    print x, 'finished'

if __name__ == "__main__":
    executor = futures.ThreadPoolExecutor(max_workers=2)

    for x in xrange(1,10):
        executor.submit(process, x)
