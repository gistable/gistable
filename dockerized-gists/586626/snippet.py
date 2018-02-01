import logbook
import timeit

logger = logbook.Logger(__name__)

def log_noop():
    pass

def log_simple():
    logger.info("Testing")

def do_timing(func):
    t = timeit.Timer(func)
    elapsed = t.timeit(number=1000000)
    print("%-20s %5.2f microseconds" % (func.__name__, elapsed))

def main():
    handler = logbook.FileHandler('time_logbook.log', 'w', level='INFO')
    with handler.applicationbound():
        do_timing(log_noop)
        do_timing(log_simple)

if __name__ == "__main__":
    main()