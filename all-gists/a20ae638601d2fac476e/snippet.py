#!/usr/bin/env python

try:
    import gdb
    inside_gdb = True
except ImportError:
    inside_gdb = False


if inside_gdb:
    import re

    class FunctionEnterBreakpoint(gdb.Breakpoint):
        def __init__(self, spec):
            self._function_name = spec
            super(FunctionEnterBreakpoint, self).__init__(spec, internal=True)

        @staticmethod
        def stack_depth():
            depth = -1
            frame = gdb.newest_frame()
            while frame:
                frame = frame.older()
                depth += 1
            return depth

        def stop(self):
            info_args = gdb.execute(
                'info args', from_tty=False, to_string=True)
            if info_args == 'No arguments.\n':
                args_str = ''
            else:
                args_str = ', '.join(info_args.splitlines())
            gdb.write('%s%s (%s)\n' % ('  ' * self.stack_depth(),
                                       self._function_name,
                                       args_str),
                      gdb.STDLOG)
            return False  # continue immediately

    class TraceFunctionCommand(gdb.Command):
        def __init__(self):
            super(TraceFunctionCommand, self).__init__(
                'trace-functions',
                gdb.COMMAND_SUPPORT,
                gdb.COMPLETE_NONE,
                True)

        @staticmethod
        def extract_function_names():
            info_functions = gdb.execute(
                'info functions', from_tty=False, to_string=True)
            result = []
            current_file = None
            for line in info_functions.splitlines():
                if line.startswith('File '):
                    current_file = line[5:-1]
                elif line.startswith('Non-debugging'):
                    break
                elif current_file:
                    match = re.search('[\s*]([^\s*]+)\(', line)
                    if match and current_file.find('/usr/include') == -1:
                        function_name = match.group(1)
                        result.append(function_name)
            return result

        def invoke(self, arg, from_tty):
            # arg: quick name filter
            function_names = self.extract_function_names()
            if arg:
                function_names = [n for n in function_names
                                  if n.find(arg) >= 0]
            count = 0
            verbose = (len(function_names) > 1000)
            for name in function_names:
                FunctionEnterBreakpoint(name)
                count += 1
                if verbose and count % 128 == 0:
                    gdb.write('\r%d / %d breakpoints set' %
                              (count, len(function_names)),
                              gdb.STDERR)
            if verbose:
                gdb.write('\r%(n)d / %(n)d breakpoints set\n' %
                          {'n': len(function_names)}, gdb.STDERR)

    TraceFunctionCommand()

else:  # outside gdb
    import os
    import subprocess
    import sys
    import tempfile

    if len(sys.argv) < 2:
        arg0 = os.path.basename(__file__)
        print('Usage: [NAME=name] %s binary [args]' % arg0)
        sys.exit(0)

    self_path = os.path.realpath(__file__)
    command_path = os.path.join(tempfile.gettempdir(),
                                'gdb-trace.%d.cmd' % os.getpid())
    with open(command_path, 'w') as f:
        f.write('source %s\n'
                'trace-functions %s\n'
                'run\n'
                'quit\n'
                % (self_path,  os.getenv('NAME', '')))

    gdb_cmd = ['gdb', '--batch', '--command=%s' % command_path,
               '--args'] + sys.argv[1:]
    subprocess.call(gdb_cmd)
    os.unlink(command_path)
