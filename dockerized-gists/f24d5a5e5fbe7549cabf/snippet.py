#!/usr/bin/env python
# coding:utf-8 

import pykka
import threading
import signal
import time
import sys


class PeriodicTimer:
    def __init__(self, actor_classes):
        self._stop_pending = False
        self._actor_classes = actor_classes

    def start(self):
        self._periodic()

    def stop(self):
        self._stop_pending = True

    def _periodic(self):
        if self._stop_pending:
            return

        reg = pykka.ActorRegistry()
        for cls in self._actor_classes:
            for act in reg.get_by_class(cls):
                act.proxy().tick()

        threading.Timer(.3, self._periodic).start()


class HiActor(pykka.ThreadingActor):
    def __init__(self):
        super(HiActor, self).__init__()

    def tick(self):
        try:
            print('hi')
            reg = pykka.ActorRegistry()
            for act in reg.get_by_class(YoActor):
                act.proxy().reply()
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise


class YoActor(pykka.ThreadingActor):
    def __init__(self):
        super(YoActor, self).__init__()

    def reply(self):
        try:
            print('yo')
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise


timer = PeriodicTimer([HiActor])

def sigterm_handler(_signo, _stack_frame):
    timer.stop()

    reg = pykka.ActorRegistry()
    for act in reg.get_all():
        act.stop(block=True)

    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, sigterm_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)

    ya = YoActor.start()
    ha = HiActor.start()
    timer.start()

    # wait until all actor stop
    reg = pykka.ActorRegistry()
    while True:
        time.sleep(.5)
        if len(reg.get_all()) == 0:
            break


if __name__ == '__main__':
    main()


# http://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
# http://stackoverflow.com/questions/19790570/python-global-variable-with-thread
# http://stackoverflow.com/questions/11822879/python-threading-timer-on-a-class-method
