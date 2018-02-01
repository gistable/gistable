import logging
import os

from twisted.internet import defer

from buildbot.schedulers.triggerable import Triggerable
from buildbot.status.results import EXCEPTION
from buildbot.status.results import FAILURE
from buildbot.status.results import SKIPPED
from buildbot.status.results import SUCCESS
from cactus.parameters.properties import BuildProperties

from cactus.steps.trigger_steps import SafeTrigger


cactusLog = logging.getLogger(__name__)


class SimpleTriggerStep(SafeTrigger, StepUtilMixin):

    '''
    I am a step which goal is to ease the writing of trigger step. A Trigger is a special buildbot
    step that received a list of Buildbot "Scheduler Names" and trigger them, which in turn will
    launch new builds.

    The main differences with the buildbot Trigger are:

    - accept empty schedulerName in the __init__ function. Use addRuntimeSchedulerNames to add
      scheduler name just before executing the trigger
    - accept scheduler name to be directly underneath the class initialization, like "description"
      and descriptionDone
    - if an empty list of trigger is given, the step will ends in "SKIPPED" statement
    - postExecute allows you to add nice status messages and logs for the user
    - preExecute allows you to perform some actions before executing the main trigger.

    It will automatically set the step status to self.description on start, and to
    self.descriptionDone on SUCCESS. You also have self.descriptionSkipped in the case of empty
    scheduler name list.

    Samples
    -------

    This executes a deferred and set the result according to this returned value.

    .. code-block:: python

        class ASimpleTiggerStep(SimpleTriggerStep):

            @defer.inlineCallbacks
            def preExecute(self):
                # do many stuff

                yield oneDeffered()

                self.importantData = stuff

            def addRuntimeSchedulerNames(self):
                return ["scheduler-{}".format(self.importantData)]

            def postExecute(self, res):
                if res = FAILURE and the_right_condition:
                    res = SUCCESS
                return res
    '''
    name = "SimpleTrigger"
    description = None
    descriptionDone = None
    descriptionSkipped = None
    updateSourceStamp = None

    def __init__(self, *args, **kwargs):
        # Trigger.__init__ wont accept empty schedulerNames. So we cheat it and we will remove the
        # "dummy" trigger afterwards.
        #
        # We also need to handle the case where schedulerNames was intentionnally set to None in the
        # kwargs
        default_scheduler_names = kwargs.pop("schedulerNames", None)
        scheduler_names = (getattr(self, 'schedulerNames', None) or
                           default_scheduler_names) or ['dummy']
        update_source_stamp = kwargs.pop("updateSourceStamp", self.updateSourceStamp)
        SafeTrigger.__init__(self, *args,
                             schedulerNames=scheduler_names,
                             updateSourceStamp=update_source_stamp,
                             **kwargs)
        self.wanted_results = None

    def start(self):
        # Do not use inlineCallback to have the more complete callback when an exception occurs.

        # Ensure the stdio log is created at the beginning of the step
        self.createLogStdio()

        # don't use inlineCallbacks to ensure displaying the full traceback in the error message
        if self.description is not None:
            self.updateStepAndBuildStatus(self.description)
        d = defer.maybeDeferred(self.preExecute)

        def cbPreExecute(res):
            if res in (FAILURE, EXCEPTION, SKIPPED):
                if res == SKIPPED and self.descriptionSkipped is not None:
                    self.updateStepAndBuildStatus(self.descriptionSkipped)
                self.end(res)
                return
            return defer.maybeDeferred(self.addRuntimeSchedulerNames)

        def cbAddRuntimeTriggerables(res):
            if self.ended:
                return

            # Handle the case where one scheduler name is None here, since it corrupts the pickles
            # when Trigger (buildbot's) update its status with:
            #
            #   self.step_status.setText(['no scheduler:'] + unknown_schedulers)
            #
            # and so when unknown_schedulers == [None]
            #
            # => This causes the following error:
            #
            #   exceptions.TypeError: sequence item 3: expected string, NoneType found
            #
            # in builbot.status.web.base, so the UI is blowed.
            if any(sched is None for sched in self.schedulerNames):
                raise ValueError("One of the scheduler name is None. "
                                 "All provided schedulers name are: {!r}"
                                 .format(self.schedulerNames))

            runtime_scheduler_names = res
            if runtime_scheduler_names and not isinstance(runtime_scheduler_names, list):
                runtime_scheduler_names = [runtime_scheduler_names]

            if self.schedulerNames == ["dummy"]:
                self.schedulerNames = []

            # Don't test only against "None", empty list has no sense here
            if runtime_scheduler_names:
                self.schedulerNames.extend(runtime_scheduler_names)

            if not self.schedulerNames:
                if self.descriptionSkipped is not None:
                    self.updateStepAndBuildStatus(self.descriptionSkipped)
                else:
                    self.updateStepAndBuildStatus("No build to trigger")
                self.end(SKIPPED)
                return

            cactusLog.debug("Create a Simple trigger with: %r", self.schedulerNames)

            self._printErrorOutputOnUnknownScheduler()
            return defer.maybeDeferred(self.setBuildProperties)

        def cbSetBuildProperties(new_properties):
            if self.ended:
                return

            if new_properties is not None:
                if not isinstance(new_properties, BuildProperties):
                    raise TypeError("setBuildProperties shall return an instance of "
                                    "BuildProperties")
                self.set_properties = new_properties
                # Rendering properties into a dictionary will be automatically done within
                # SafeTrigger.start when needed.
                self.set_properties.getRenderingFor(self)

            # Let Trigger.start fails if required
            SafeTrigger.start(self)

        def cbStart(_):
            if not self.ended:
                # If the trigger.start returned without call to self.end, it is a case of success
                self.end(SUCCESS)

            # self.ended should have been called once here
            return defer.maybeDeferred(self.postExecute, self.wanted_results)

        def cbPostExecute(res):
            if res is not None:
                # Overwriting result
                self.wanted_results = res

        def cbAfterAll(_):
            # Set description to descriptionDone if present, otherwize let the default
            # "triggered a, triggered b"
            if self.descriptionDone is not None:
                # we test against None to allow empty string if the user wants so
                self.updateStepAndBuildStatus(self.descriptionDone)
            self.finished(self.wanted_results)

        def errback(failure):
            cactusLog.exception("exception received during step execution:")
            self.addLogError(indent(str(failure), indent="    ").rstrip(),
                             stdio=True, writeToLog=True)
            # Call fail safe cleanup function
            self.failSafeCleanup()

            # Fails the build
            self.failed(failure)

            # override status set in self.failed with the text of the exception
            #
            self.updateStepAndBuildStatus(failure.getErrorMessage())

        # First execute ``preExecute``,
        #  then execute ``addRuntimeTriggerables``,
        #  then execute ``start``,
        #  then execute ``postExecute``,

        d.addCallbacks(cbPreExecute, errback)
        d.addCallbacks(cbAddRuntimeTriggerables, errback)
        d.addCallbacks(cbSetBuildProperties, errback)
        d.addCallbacks(cbStart, errback)
        d.addCallbacks(cbPostExecute, errback)
        d.addCallbacks(cbAfterAll, errback)
        return d

    def failSafeCleanup(self):
        '''
        I am called when an exception or an failure occurs. I should be used in order to clean some
        stuff that cannot be automatically deleted.

        I am a normal routine and NOT a inlineCallbacks.

        I am NOT called during nominal operations.

        Override me in order to implement your clean up procedure. Ignore if you don't have any.

        For instance:
          - pending txrequests
          - timeout mixin
        '''
        pass

    def preExecute(self):
        '''
        I am called BEFORE the execution of the triggers.

        I can be a deferred or not.

        Return value: SUCCESS and WARNING are both allowed and provoke the continuation of the
                      step. EXCEPTION, FAILURE and SKIPPED both stop the execution.
        '''
        return SUCCESS

    def postExecute(self, res):
        '''
        I am called AFTER the execution of the trigger.

        You are reasponsible for acting accordingly in every case. The "res" parameter holds the
        return status (SUCCES/FAILURE/EXCEPTION) of the step up to now.

        You typically want to propagate the "res" value, overriding it eventually, so you can turn a
        FAILURE into WARNINGS under some conditions, for instance.

        I can be a deferred or not.

        Return value: SUCCESS and SKIPPED are both allowed and provoke the continuation of the step.
        EXCEPTION and FAILURE both stop the execution. If None is returned, the initial res is used.

        Note: It's important to understand that the return value of the postExecute method will be
        used to set the result of the step. If you don't want to change the execution state after
        postExecute, simply propagate "res".
        '''
        return res

    def addRuntimeSchedulerNames(self):
        '''
        Override me for adding scheduler when "start" is executed.

        I can be a normal function or a deferred (maybeDeferred is used to call me)

        I can return either a simple scheduler name string or a list of scheduler name strings.
        '''
        return []

    def setBuildProperties(self):
        '''
        Override me to set the trigger properties just after "start" has been called.

        I can be a normal function or a deferred (maybeDeferred is used to call me)

        I shall return None or an instance of BuildProperties with the properties to transfer
        from the current build
        '''
        return None

    def end(self, results):
        '''
        This function is an override of the Trigger.end function. Do not use it directly.
        '''
        # self.ended has been created in Trigger.__init__
        if not self.ended:
            self.ended = True
            self.wanted_results = results

    def _getTriggerableSchedulerName(self):
        '''
        Return list of available triggerable scheduler name.
        '''
        return sorted([x.name for x in self.build.builder.botmaster.parent.allSchedulers()
                       if isinstance(x, Triggerable)])

    def _printErrorOutputOnUnknownScheduler(self):
        '''
            This check is also done in Trigger.start, but we do it here in order to catch the "bad
            scheduler name" error earlier and dump a more developer-friendly output.

            Testing that the name of the scheduler is valid in the system is not possible right now
            in unit tests, so we need fail and retry once the step is integrated.

            This ensure the developer has all the information right in front of his eyes when it
            fails.
        '''
        all_scheduler_names = self._getTriggerableSchedulerName()
        error = False
        for schname in self.schedulerNames:
            if schname not in all_scheduler_names:
                self.addLogError("Invalid scheduler name: {!r}".format(schname))
                error = True
        if error:
            self.addLogError("List of all available triggerable schedulers: ", stdio=False)
            for scheduler_name in all_scheduler_names:
                self.addLogError(" - {!r}".format(scheduler_name), stdio=False)

    def getWorkdir(self):
        '''
        Method needed to be able to use some method from StepUtilMixin such as uploadFileFromSlave
        '''
        return os.path.join(self.getProperty("workdir"), self.build.workdir)
