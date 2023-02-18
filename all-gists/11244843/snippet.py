##
## "Manage Subordinates" builder for buildbot:
##  - a buildbot builder that can start/stop/restart any buildsubordinate
##  - runs simple shell script on subordinate to do the action
##
##  ### INSTRUCTIONS ###
##
## On each subordinate, install the buildmain's public SSH key so the buildmain can SSH in.
## Then, add a script like the one below to each buildsubordinate. A few notes on this script:
##  - "bash -l" seems to be important in order to get the virtualenv to take correctly
##  - I wasnt able to get a full one-liner ("ssh subordinate1 '...one-liner...'") that could run directly via
##    ssh, so I had to create this redirection through a local script file.
##
##  ### THE BASE SCRIPT : ~/run_buildsubordinate.sh ###
##
##    #! /bin/bash -l
##  
##    # Fail the script on any error.
##    set -e
##  
##    # Start the virtualenv, then run 'buildsubordinate' with whatever arg is passed to this script.
##    cd ~/buildsubordinate-base
##    source sandbox/bin/activate
##    cd subordinate
##    buildsubordinate $1

from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.forcesched import ChoiceStringParameter, CodebaseParameter
from buildbot.process import properties
from buildbot.process.properties import Interpolate
from buildbot.steps.shell import ShellCommand

# Fill these in:
BUILD_SLAVES = []  # The subordinates that can be managed via this builder
MAIN_SLAVE = ''    # The subordinate that is able to ssh into all other subordinates to run the comman

def create_subordinate_management(subordinates):
    # Check if any action will be taken on a given subordinate (or whether it should be skipped).
    def skip_if_no_action(subordinate):
        def must_do_step(step):
            action = step.getProperty('%s_action' % subordinate, None)

            if not isinstance(action, basestring):
                return False

            action = action.lower()
            if action in ['start', 'restart', 'stop']:
                return True

            return False

        return must_do_step

    # Get the command line parameter that should be taken on a given subordinate.
    def get_action(subordinate):
        @properties.renderer
        def pick_buildbot_action(props):
            action = props.getProperty('%s_action' % subordinate, None)

            if not isinstance(action, basestring):
                return '--version'  # dummy action

            action = action.lower()
            if action in ['start', 'restart', 'stop']:
                return action

            return '--version'  # dummy action

        return pick_buildbot_action

    steps = []

    for subordinate in subordinates:
        steps.append(
             ShellCommand(
                name="Act-%s" % subordinate,
                command = ["ssh", subordinate, Interpolate("~/run_buildsubordinate.sh %(kw:action)s", action=get_action(subordinate))],
                doStepIf=skip_if_no_action(subordinate))
             )

    return {
            'factory': BuildFactory(steps),
            'name': "ManageSubordinates",
            'subordinatenames': [ MAIN_SLAVE ],
    }

c['builders'].append(create_subordinate_management(BUILD_SLAVES))
c['schedulers'].append(
    ForceScheduler(name="Force-ManageSubordinates", builderNames=['ManageSubordinates'],
                   codebases=[CodebaseParameter(codebase='', hide=True)],
                   reason=StringParameter(name="reason", default="Manage Subordinates", length=20, hide=True),
                   reasonString="%(reason)s",
                   properties=[
                        ChoiceStringParameter(label=subordinate, name='%s_action' % subordinate, choices=['None', 'Start', 'Restart', 'Stop'])
                        for subordinate in BUILD_SLAVES
                   ]),