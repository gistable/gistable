"""Example to cancel a set of asyncio coroutines (futures),
using one coroutine to signal the event loop to stop.
"""

import asyncio
import logging
from datetime import datetime
from concurrent.futures import CancelledError


logging.basicConfig(level=logging.DEBUG)


@asyncio.coroutine
def poll(incr=1):
    """A continuous coroutine."""
    i = 0
    while True:
        print("Polling at {} seconds.".format(i))
        i += incr
        yield from asyncio.sleep(incr)
    

@asyncio.coroutine
def stop(duration):
    """The coroutine to listen for signal to stop the event loop."""
    # In practice, a signal of sorts (e.g., through a TCP socket) may
    # be send here to indicate a full stop
    yield from asyncio.sleep(duration)
    # Alternatively, one can raise an Exception and use
    # `return_when=asyncio.FIRST_EXCEPTION` in `asyncio.wait`.


def main():
    loop = asyncio.get_event_loop()
    # For Python 3.4.4, use `ensure_future` instead of `async` below
    tasks = [asyncio.async(poll(2)),
             asyncio.async(poll(1.4)),
             asyncio.async(stop(5))]
    finished, pending = loop.run_until_complete(
        asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED))
    logging.debug(">> Finished: {}", finished)
    logging.debug(">> Pending: {}", pending)
    # Cancel the remaining tasks
    for task in pending:
        logging.info("Cancelling %s: %s", task, task.cancel())
    try:
        loop.run_until_complete(asyncio.gather(*pending))
    except CancelledError: # Any other exception would be bad
        for task in pending:
            logging.debug("Cancelled %s: %s", task, task.cancelled())
    # Stop and clean up
    loop.stop()
    loop.close()
    
                        
if __name__ == "__main__":
    main()
