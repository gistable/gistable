from random import randrange

from twisted.internet.defer import DeferredQueue
from twisted.internet.task import deferLater, cooperate
from twisted.internet import reactor


def async(n):
    print 'Starting job', n
    d = deferLater(reactor, n, lambda: None)
    def cbFinished(ignored):
        print 'Finishing job', n
    d.addCallback(cbFinished)
    return d


def assign(jobs):
    # Create new jobs to be processed
    jobs.put(randrange(10))
    reactor.callLater(randrange(10), assign, jobs)


def worker(jobs):
    while True:
        yield jobs.get().addCallback(async)


def main():
    jobs = DeferredQueue()

    for i in range(10):
        jobs.put(i)

    assign(jobs)

    for i in range(3):
        cooperate(worker(jobs))

    reactor.run()


if __name__ == '__main__':
    main()
