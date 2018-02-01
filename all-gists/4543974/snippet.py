# commanduo.py - Running multiple Commando's in the same script

from trigger.cmds import Commando as CommandoBase
from twisted.internet import defer, task, reactor
from twisted.python import log
import sys

# Uncomment me for verbose logging.
#log.startLogging(sys.stdout, setStdout=False)

class ReactorlessCommando(CommandoBase):
    """
    A reactor-less Commando subclass.
   
    This allows multiple instances to coexist, with the side-effect that you
    have to manage the reactor start/stop manually.
    """
    def _start(self):
        """Initializes ``all_done`` instead of starting the reactor"""
        log.msg("._start() called")
        self.all_done = False

    def _stop(self):
        """Sets ``all_done`` to True instead of stopping the reactor"""
        log.msg("._stop() called")
        self.all_done = True

    def run(self):
        """
        We've overloaded the run method to return a Deferred task object.
        """
        log.msg(".run() called")

        # This is the default behavior
        super(ReactorlessCommando, self).run()

        # Setup a deferred to hold the delayed result and not return it until
        # it's done. This object will be populated with the value of the
        # results once all commands have been executed on all devices.
        d = defer.Deferred()
            
        # Add monitor_result as a callback
        d.addCallback(self.monitor_result, reactor)

        # Tell the reactor to call the callback above when it starts
        reactor.callWhenRunning(d.callback, reactor)

        return d

    def monitor_result(self, result, reactor):
        """
        Loop periodically or until the factory stops to check if we're
        ``all_done`` and then return the results.
        """
        # Once we're done, return the results
        if self.all_done:
            return self.results

        # Otherwise tell the reactor to call me again after 0.5 seconds.
        return task.deferLater(reactor, 0.5, self.monitor_result, result, reactor)

class ShowClock(ReactorlessCommando):
    commands = ['show clock']

class ShowUsers(ReactorlessCommando):
    commands = ['show users']

def stop_reactor(result):
    if reactor.running:
        log.msg('STOPPING REACTOR!')
        reactor.stop()
    return result

if __name__ == '__main__':
    devices = ['dev1', 'dev2']

    # Our Commando instances. This is an example  to show we have two instances
    # co-existing under the same reactor.
    c1 = ShowClock(devices)
    c2 = ShowUsers(devices)
    instances = [c1, c2]

    # Call the run method for each instance to get a list of Deferred task objects.
    deferreds = []
    for i in instances:
        deferreds.append(i.run())

    # Here we use a DeferredList to track a list of Deferred tasks that only 
    # returns once they've all completed.
    d = defer.DeferredList(deferreds)

    # Once every task has returned a result, stop the reactor
    d.addBoth(stop_reactor)

    # And... finally, start the reactor to kick things off.
    reactor.run()
