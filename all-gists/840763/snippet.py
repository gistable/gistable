import sys
import re
from code import InteractiveInterpreter

import znc

class pyeval(znc.Module, InteractiveInterpreter):
    module_types = [znc.CModInfo.UserModule, znc.CModInfo.NetworkModule]
    description = 'Evaluates python code'

    def write(self, data):
        for line in data.split('\n'):
            if len(line):
                self.PutModule(line)

    def resetbuffer(self):
        """Reset the input buffer."""
        self.buffer = []

    def push(self, line):
        self.buffer.append(line)
        source = "\n".join(self.buffer)
        more = self.runsource(source, self.filename)
        if not more:
            self.resetbuffer()
        return more

    def OnLoad(self, args, message):
        if not self.GetUser().IsAdmin():
            message.s = 'You must have admin privileges to load this module.'
            return False

        self.filename = "<console>"
        self.resetbuffer()
        self.locals['znc'] = znc
        self.locals['module'] = self
        self.locals['user'] = self.GetUser()
        self.locals['network'] = self.GetNetwork()
        self.indent = re.compile(r'^>+')

        return True

    def OnModCommand(self, line):
        self.locals['client'] = self.GetClient()

        # Hijack sys.stdout.write
        stdout_write = sys.stdout.write
        sys.stdout.write = self.write

        m = self.indent.match(line)
        if m:
            self.push(('    ' * len(m.group())) + line[len(m.group()):])
        elif line == ' ' or line == '<':
            self.push('')
        else:
            self.push(line)

        # Revert sys.stdout.write
        sys.stdout.write = stdout_write
        del self.locals['client']

