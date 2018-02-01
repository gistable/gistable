#!/usr/bin/env python
import time

import nose
from nose.plugins.base import Plugin

class NoseTimer(Plugin):
    """
    Times each individual test and outputs them in reverse order of
    speed (highest first)

    Usage: nosetimer.py --time [optional nose arguments]
    """
    name = "Nose Timer"
    results = {}

    def options(self, parser, env):
        super(NoseTimer, self).options(parser, env)
        parser.add_option(
            '--time',
            dest='nosetimer_time',
            action='store_true',
            default=False,
            help="Time each test."
        )

    def configure(self, options, conf):
        super(NoseTimer, self).configure(options, conf)
        self.enabled = options.nosetimer_time

    def startTest(self, *args, **kwargs):
        self.start_time = time.time()

    def stopTest(self, test):
        end_time = time.time() - self.start_time
        self.results[str(test)] = end_time

    def report(self, stream):
        results = self.results.items()
        results.sort(key=lambda x: x[1], reverse=True)
        for test, time in results:
            stream.write("%0.4fs: %s\n" % (time, test))


if __name__ == '__main__':
    nose.main(addplugins=[NoseTimer()])
