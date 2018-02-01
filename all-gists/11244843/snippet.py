##
## "Manage Slaves" builder for buildbot:
##  - a buildbot builder that can start/stop/restart any buildslave
##  - runs simple shell script on slave to do the action
##
##  ### INSTRUCTIONS ###
##
## On each slave, install the buildmaster's public SSH key so the buildmaster can SSH in.
## Then, add a script like the one below to each buildslave. A few notes on this script:
##  - "bash -l" seems to be important in order to get the virtualenv to take correctly
##  - I wasnt able to get a full one-liner ("ssh slave1 '...one-liner...'") that could run directly via
##    ssh, so I had to create this redirection through a local script file.
##
##  ### THE BASE SCRIPT : ~/run_buildslave.sh ###
##
##    #! /bin/bash -l
##  
##    # Fail the script on any error.
##    set -e
##  
##    # Start the virtualenv, then run 'buildslave' with whatever arg is passed to this script.
##    cd ~/buildslave-base
##    source sandbox/bin/activate
##    cd slave
##    buildslave $1

from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.forcesched import ChoiceStringParameter, CodebaseParameter
from buildbot.process import properties
from buildbot.process.properties import Interpolate
from buildbot.steps.shell import ShellCommand

# Fill these in:
BUILD_SLAVES = []  # The slaves that can be managed via this builder
MAIN_SLAVE = ''    # The slave that is able to ssh into all other slaves to run the comman

def create_slave_management(slaves):
    # Check if any action will be taken on a given slave (or whether it should be skipped).
    def skip_if_no_action(slave):
        def must_do_step(step):
            action = step.getProperty('%s_action' % slave, None)

            if not isinstance(action, basestring):
                return False

            action = action.lower()
            if action in ['start', 'restart', 'stop']:
                return True

            return False

        return must_do_step

    # Get the command line parameter that should be taken on a given slave.
    def get_action(slave):
        @properties.renderer
        def pick_buildbot_action(props):
            action = props.getProperty('%s_action' % slave, None)

            if not isinstance(action, basestring):
                return '--version'  # dummy action

            action = action.lower()
            if action in ['start', 'restart', 'stop']:
                return action

            return '--version'  # dummy action

        return pick_buildbot_action

    steps = []

    for slave in slaves:
        steps.append(
             ShellCommand(
                name="Act-%s" % slave,
                command = ["ssh", slave, Interpolate("~/run_buildslave.sh %(kw:action)s", action=get_action(slave))],
                doStepIf=skip_if_no_action(slave))
             )

    return {
            'factory': BuildFactory(steps),
            'name': "ManageSlaves",
            'slavenames': [ MAIN_SLAVE ],
    }

c['builders'].append(create_slave_management(BUILD_SLAVES))
c['schedulers'].append(
    ForceScheduler(name="Force-ManageSlaves", builderNames=['ManageSlaves'],
                   codebases=[CodebaseParameter(codebase='', hide=True)],
                   reason=StringParameter(name="reason", default="Manage Slaves", length=20, hide=True),
                   reasonString="%(reason)s",
                   properties=[
                        ChoiceStringParameter(label=slave, name='%s_action' % slave, choices=['None', 'Start', 'Restart', 'Stop'])
                        for slave in BUILD_SLAVES
                   ]),