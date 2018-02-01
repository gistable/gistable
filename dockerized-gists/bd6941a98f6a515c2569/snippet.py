import threading, os, logging
from math import sqrt


class threadsafe_iterator:
    def __init__(self, iterator):
        self.iterator = iterator
        self.lock = threading.Lock()

    def __iter__(self):
        return self

    def next(self):
        with self.lock:
            return self.iterator.next()


def threadsafe_generator(function):
    def inner(*args, **kwargs):
        return threadsafe_iterator(*args, **kwargs)

    return function


def process_logger():
    def _logger(function):
        def inner(*args, **kwargs):
            identifier = "%s:%s" % (str(os.getpid()), str(args[0]))
            logdir = os.path.join(os.getcwd(), 'logs')
            logfile = os.path.join(logdir, 'blah-' + identifier + '.log')
            logger = logging.getLogger(identifier)
            file_handle = logging.FileHandler(logfile)

            logger.addHandler(file_handle)
            return function(*args, **kwargs)
        return inner
    return _logger


@threadsafe_generator
def counter():
    i = 0

    while True:
        i += 1
        yield i


def gen_primes(count):
    """
    Generate n prime numbers
    """
    primes = [2]

    while len(primes) < count:
        num = primes[-1]

        while True:
            num += 1

            if num % 2:
                for n in range(3, int(sqrt(num)+1), 2):
                    if not num % n:
                        break
                else:
                    primes.append(num)
                    break

    return primes


@process_logger()
def worker(number):
    """
    Worker generates the n-thousandth prime number
    """
    pid = str(os.getpid())
    logger = logging.getLogger(pid)
    child_logger = logging.getLogger("%s:%s" % (pid, str(number)))
    primes = gen_primes(number * 1000)

    child_logger.info(primes)
    logger.info(primes[-1])


def start_workers(workers):
    """
    Spawn up to n workers until all work is complete
    """
    children = []
    number = counter()
    next_number = 0
    logdir = os.path.join(os.getcwd(), 'logs')
    logfile = "blah.log"

    if workers < 1:
        return

    if not os.path.exists(logdir):
        os.makedirs(logdir)

    logging.basicConfig(filename=os.path.join(logdir, logfile), level=logging.INFO)
    logger = logging.getLogger(__name__)

    while next_number < 100:
        while len(children) < workers:
            next_number = number.next()
            pid = os.fork()

            if not pid:
                worker(next_number)
                os._exit(0)
            else:
                children.append(pid)
                logger.info("Started: %d" % pid)

        child = os.wait()[0]

        children.remove(child)
        logger.info("Stopped: %d" % child)


if __name__ == '__main__':
    start_workers(10)