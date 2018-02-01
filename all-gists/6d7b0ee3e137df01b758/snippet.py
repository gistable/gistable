# Not extensively tested
# Put this script in the action_plugins directory of your playbook directory 
# If you have issues, please report it in the comments (or fork and fix)

# Usage:
# - name: "Ask the user if we should continue."
#   action: ask_key prompt="Continue? Yes / No / Random (y/n/r)?" accepted_keys="['y', 'n', 'r']"
#   register: answer
#
# The pressed key is now in answer.key

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import termios
import tty
from os import isatty

from ansible.plugins.action import ActionBase

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

class ActionModule(ActionBase):
    ''' Ask the user to input a key '''

    VALID_ARGS = set(["prompt", "accepted_keys"])
    REQUIRED_ARGS = set(["prompt", "accepted_keys"])

    BYPASS_HOST_LOOP = True

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        for arg in self._task.args:
            if arg not in self.VALID_ARGS:
                return {"failed": True, "msg": "'%s' is not a valid option in ask" % arg}

        for arg in self.REQUIRED_ARGS:
            if arg not in self._task.args:
                return {"failed": True, "msg": "'%s' is required in ask" % arg}

        result = super(ActionModule, self).run(tmp, task_vars)

        fd = None
        old_settings = None

        try:
            fd = self._connection._new_stdin.fileno()
        except ValueError:
            pass

        if fd is not None:
            if isatty(fd):
                old_settings = termios.tcgetattr(fd)
                tty.setraw(fd)

                termios.tcflush(self._connection._new_stdin, termios.TCIFLUSH)
        else:
            return {"failed": True, "msg": "For some reason, we couldn't access the connection tty."}

        display.display(self._task.args["prompt"] + "\r")

        while True:
            key = self._connection._new_stdin.read(1)
            if key == '\x03':
                result["failed"] = True
                result["msg"] = "User requested to cancel."
                break
            elif key in self._task.args["accepted_keys"]:
                result["key"] = key
                break

        if old_settings != None and isatty(fd):
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return result
