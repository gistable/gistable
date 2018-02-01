import os
import os.path
import re

import fabric.api
import fabric.tasks


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
SUDO_PREFIX = re.compile(r'/(root|sudo)_?', re.I)


class ScriptTask(fabric.tasks.Task):
    def __init__(self, script_path, name=None, sudo=False):
        super(ScriptTask, self).__init__()
        self.script_path = script_path
        self.script_name = os.path.basename(script_path)
        self.name = name or os.path.splitext(self.script_name)[0]
        self.sudo = sudo
        if sudo:
            self.remote_path = '/root/{}'.format(self.script_name)
        else:
            self.remote_path = '/tmp/{}'.format(self.script_name)

    def run(self):
        fabric.api.put(
                self.script_path,
                self.remote_path,
                mirror_local_mode=True,
                use_sudo=self.sudo
        )
        if self.sudo:
            fabric.api.sudo(self.remote_path)
        else:
            fabric.api.run(self.remote_path)


__all__ = []
tasks = {}

for filename in os.listdir(SCRIPT_DIR):
    if filename in ["__init__.py", ]:
        continue
    filename = os.path.join(SCRIPT_DIR, filename)
    if os.path.isfile(filename) and os.access(filename, os.X_OK):
        task_is_sudo = bool(SUDO_PREFIX.search(filename))
        task = ScriptTask(filename, sudo=task_is_sudo)
        tasks[task.name] = task

for task_name, task in tasks.iteritems():
    globals()[task_name] = task
    __all__.append(task_name)