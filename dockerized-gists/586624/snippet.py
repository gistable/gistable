import logging
import timeit

logger = logging.getLogger(__name__)

def log_noop():
    pass

def log_simple():
    logger.info("Testing")

def log_filtered():
    logger.debug("Testing")

def log_mitigated():
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Testing")

def log_disabled():
    logger.debug("Testing")

def do_timing(func):
    t = timeit.Timer(func)
    elapsed = t.timeit(number=1000000)
    print("%-20s %5.2f microseconds" % (func.__name__, elapsed))

def main():
    logging.basicConfig(level=logging.INFO, filename="time_logging.log", filemode="w")
    do_timing(log_noop)
    do_timing(log_simple)
    do_timing(log_filtered)
    do_timing(log_mitigated)
    logging.disable(logging.INFO)
    do_timing(log_disabled)
    logging.disable(0)
    sf, lt, lp = logging._srcfile, logging.logThreads, logging.logProcesses
    logging._srcfile = None
    logging.logThreads = 0
    logging.logProcesses = 0
    print("No caller, thread, process info...")
    do_timing(log_simple)
    do_timing(log_filtered)
    do_timing(log_mitigated)
    
if __name__ == "__main__":
    main()