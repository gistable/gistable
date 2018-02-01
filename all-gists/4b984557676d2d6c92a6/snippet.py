# Interpret the Ansible log for humans. In particular, we
# look for command executions and format their content
#
#     - name: list files
#       shell: "ls -lrt *e*"
#
# Might produce
#
#       TASK: [1] ***********************************************************
#       changed: [localhost]
#       2015-07-25 09:41:03: ls -lrt *e*
#           -rw-r--r--  1 dave  staff  1696 Jul 11 11:54 ansible.pem
#           -rw-r--r--  1 dave  staff   106 Jul 22 10:10 fix-sudoers.sh
#           -rw-r--r--  1 dave  staff    20 Jul 22 20:06 fred.yml
#           -rw-r--r--  1 dave  staff   345 Jul 23 14:48 ansible.cfg
#           -rw-r--r--  1 dave  staff    68 Jul 25 09:35 site.yml
#
#           filter_plugins:
#           total 16
#           -rw-r--r--  1 dave  staff  247 Jul 24 18:06 to_instance_tags.py
#           -rw-r--r--  1 dave  staff  859 Jul 24 20:55 to_instance_tags.pyc
#           (took .008240s)
#
# The start time appears as the prompt for the command, and the result
# is shown indented. The output ends with the elapsed time.
#
#
# This is an adaptation of Cliffano Subagio's "human_logging" gist
# described at http://bit.ly/1KqozNe

import re
from ansible.color import stringc

FIELDS = ['cmd', 'command', 'start', 'end', 'delta', 'msg', 'stdout', 'stderr']


# Display output indented by 4 spaces and in yellow

def display_output(output, color='yellow'):
    if output:
        output = "\n    ".join(output.split("\n"))
        print(stringc("    " + output, color))

# Given a command execution, extract the start time, command, and output
# colorizing them, appropriately

def format_command(res):
    cmd = "".join(res['cmd']).encode('utf-8')
    start = res.get('start', 'failed command')
    duration = res.get('delta', False)
    print("{0}: {1}".format(stringc(start[0:19], 'cyan'), cmd))
    display_output(res.get('stdout', False), 'yellow')
    display_output(res.get('stderr', False), 'bright red')
    if duration:
        duration = re.sub(r'^[0:]+', '', duration)
        print(stringc("    (took {0}s)".format(duration), 'cyan'))

# Handle any type of ansible callback. We treat `cmd` and `msg`
# specially, as we know their content and can format it neatly.
#
# Otherwise we just output key/value pairs

def human_log(res):
    if type(res) == type(dict()):
        keys = res.keys()
        if 'cmd' in keys:
            format_command(res)
        elif 'msg' in keys:
            msg = res['msg']
            if msg:
                print ' >> {0}'.format(stringc(msg, 'cyan'))
        else:
            for field in FIELDS:
                if field in keys:
                    val = res[field]
                    if isinstance(val, list):
                        val = " ".join(val)
                        encoded_field = val.encode('utf-8')
                        print '\n{0}:\n{1}'.format(field, encoded_field)


# and the callback itself

class CallbackModule(object):

	def on_any(self, *args, **kwargs):
            pass

	def runner_on_failed(self, host, res, ignore_errors=False):
            human_log(res)

        def runner_on_ok(self, host, res):
            human_log(res)

	def runner_on_error(self, host, msg):
            pass

	def runner_on_skipped(self, host, item=None):
            pass

	def runner_on_unreachable(self, host, res):
            human_log(res)

	def runner_on_no_hosts(self):
            pass

	def runner_on_async_poll(self, host, res, jid, clock):
            human_log(res)

	def runner_on_async_ok(self, host, res, jid):
            human_log(res)

	def runner_on_async_failed(self, host, res, jid):
            human_log(res)

	def playbook_on_start(self):
            pass

	def playbook_on_notify(self, host, handler):
            pass

	def playbook_on_no_hosts_matched(self):
            pass

	def playbook_on_no_hosts_remaining(self):
            pass

	def playbook_on_task_start(self, name, is_conditional):
            pass

        def playbook_on_vars_prompt(self, varname, private=True, prompt=None,
                                    encrypt=None, confirm=False, salt_size=None,
                                    salt=None, default=None):
            pass

	def playbook_on_setup(self):
            pass

        def playbook_on_import_for_host(self, host, imported_file):
            pass

	def playbook_on_not_import_for_host(self, host, missing_file):
            pass

	def playbook_on_play_start(self, pattern):
            pass

	def playbook_on_stats(self, stats):
            pass
