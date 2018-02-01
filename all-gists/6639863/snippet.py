from functools import partial
from greenlet import greenlet


BREAK_IT = True
coordinator = greenlet.getcurrent()


class EvilObject(object):

    def __init__(self, container):
        self.container = container

    def __repr__(self):
        if BREAK_IT:
            coordinator.switch(True)
        return 'EvilObject(%s)' % self.container


outstanding = set([-1])
container = []
for x in xrange(20):
    container.append(EvilObject(container))


def printer(num):
    outstanding.add(num)
    coordinator.switch(True)
    print repr(container)
    outstanding.discard(num)


printers = []
for x in xrange(10):
    printers.append(greenlet(partial(printer, x)))


while outstanding:
    outstanding.discard(-1)
    for printer in printers:
        printer.switch()
