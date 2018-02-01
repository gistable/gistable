#!/usr/bin/env python3

import concurrent.futures.thread
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def remove_file(path):
    print('Removing file %s' % path)
    time.sleep(10)  # Pretending that I'm removing the file...
    print('%s is removed' % path)


not_graceful = sys.argv[1:] and sys.argv[1] == '--not-graceful'
if not_graceful:
    print('I will _not_ be shut down gracefully...')
else:
    print('I will be shut down gracefully... (default behavior)')


with ThreadPoolExecutor(1) as executor:
    futures = [executor.submit(remove_file, path) for path in 'abcd']
    try:
        for future in as_completed(futures):
            future.result()
    except KeyboardInterrupt:
        if not_graceful:
            executor._threads.clear()
            concurrent.futures.thread._threads_queues.clear()
        raise