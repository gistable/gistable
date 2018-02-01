import os, shlex

from twisted.internet import defer, utils, reactor, threads
from twisted.python import log, failure
from buildbot.buildslave import AbstractBuildSlave, AbstractLatentBuildSlave
from buildbot import config


class ScriptedLatedBuildSlave(AbstractLatentBuildSlave):

    def __init__(self, name, password, start_script, stop_script, max_builds=None, notify_on_missing=[],
                 missing_timeout=60*20, build_wait_timeout=60*10, properties={}, locks=None):
        AbstractLatentBuildSlave.__init__(self, name, password, max_builds, notify_on_missing,
                                          missing_timeout, build_wait_timeout, properties, locks)

        self.name = name
        self.start_script = shlex.split(start_script)
        self.stop_script = shlex.split(stop_script)

    @defer.inlineCallbacks
    def start_instance(self, build):
        log.msg("Attempting to start '%s'" % self.name)
        retval = yield utils.getProcessValue(self.start_script[0], self.start_script[1:])
        defer.returnValue(retval == 0)

    @defer.inlineCallbacks
    def stop_instance(self, fast=False):
        log.msg("Attempting to stop '%s'" % self.name)
        retval = yield utils.getProcessValue(self.stop_script[0], self.stop_script[1:])

        log.msg("slave destroyed (%s): Forcing its connection closed." % self.name)
        yield AbstractBuildSlave.disconnect(self)

        log.msg("We forced disconnection (%s), cleaning up and triggering new build" % self.name)
        self.botmaster.maybeStartBuildsForSlave(self.name)

        defer.returnValue(retval == 0)
