#!/usr/bin/env python
# 
# A handy tool to compile and execute C source directly.
#
# @author Yecheng Fu <cofyc.jackson@gmail.com> 

import os
import sys
import tempfile
import subprocess

# This block ensures that ^C interrupts are handle quietly.
try:
    import signal

    def exithandle(signum, frame):
        signal.signal(signal.SIGINT, exithandle)
        signal.signal(signal.SIGTERM, exithandle)
        sys.exit(1)

    signal.signal(signal.SIGINT, exithandle)
    signal.signal(signal.SIGTERM, exithandle)
except KeyboardInterrupt:
    sys.exit(1)

def usage():
    print("""Usage: xrunc [COMPILER_OPTS] FILES [-- [ARGS]]

Options and arguments:
    COMPILER_OPTS   - any arguments that are not c files before '--'
    --              - stop handling COMPILER_OPTS & FILES
    FILES           - argument with '.c' suffix or '-' (stdin) before '--'
    ARGS            - arguments after '--', which are passed to compiled program

Environment variables:
    CC              - specify c compiler (default: cc)

Examples:
    xrunc                           - show this help info
    xrunc hello.c                   - compile and execute hello.c
    xrunc -lm hello.c --std=c99     - compile hello.c with "-lm --std=c99" then execute
    xrunc hello.c -- a b c          - compile hello.c then execute with args "a b c"
    xrunc -                         - read c source from stdin
""")
    sys.exit(0)

def compile_and_execute(c_src_files, c_args, cc_opts):
    fd, filepath = tempfile.mkstemp()
    try:
        status = 0
        # compile
        args = [os.getenv('CC', 'cc'), '-o', filepath] + c_src_files + cc_opts
        p = subprocess.Popen(args, cwd=os.getcwd())
        status = os.waitpid(p.pid, 0)[1]
        if status != 0:
            raise Exception("compiling failed, exit code: {}".format(status))
        # execute
        args = [filepath] + c_args
        p = subprocess.Popen(args, cwd=os.getcwd())
        status = os.waitpid(p.pid, 0)[1]
        if status != 0:
            raise Exception("executing failed, exit code: {}".format(status))
    finally:
        os.path.exists(filepath) and os.unlink(filepath)


class Completer:
    def __init__(self):
        keywords = [ 
            'auto', 'enum', 'restrict', 'break', 'extern', 'return',
            'case', 'float', 'short', 'char', 'for', 'signed', 'const',
            'goto', 'sizeof', 'continue', 'if', 'static', 'default',
            'inline', 'struct', 'do', 'int', 'switch', 'double', 'long',
            'typedef', 'else', 'register', 'union', 'unsigned', 'void',
            'volatile', 'while', '_Bool', '_Complex', '_Imaginary'
            ]
        preprocessing_directives = [
            '#if', '#ifdef', '#ifndef', '#elif', '#else', '#endif',
            '#include', '#define', '#undef', 'line', '#error', '#pragma',
            ]
        self.words = []
        self.words.extend(keywords)
        self.words.extend(preprocessing_directives);
        self.prefix = None
    def complete(self, prefix, index):
        if prefix != self.prefix:
            # we have a new prefix!
            # find all words that start with this prefix
            self.matching_words = [
                w for w in self.words if w.startswith(prefix)
                ]
            self.prefix = prefix
        try:
            return self.matching_words[index]
        except IndexError:
            return None

class CFile:
    header_lines = [
        "#include <assert.h>",
        "#include <complex.h>",
        "#include <ctype.h>",
        "#include <errno.h>",
        "#include <fenv.h>",
        "#include <float.h>",
        "#include <inttypes.h>",
        "#include <iso646.h>",
        "#include <limits.h>",
        "#include <locale.h>",
        "#include <math.h>",
        "#include <setjmp.h>",
        "#include <signal.h>",
        "#include <stdarg.h>",
        "#include <stdbool.h>",
        "#include <stddef.h>",
        "#include <stdint.h>",
        "#include <stdio.h>",
        "#include <stdlib.h>",
        "#include <string.h>",
        "#include <tgmath.h>",
        "#include <time.h>",
        "#include <wchar.h>",
        "#include <wctype.h>",
    ]
    body_lines = []
    @staticmethod
    def tmpfile():
        c_src_file = tempfile.NamedTemporaryFile(suffix=".c", delete=True)
        main_prefix = """
int
main(int argc, const char **argv)
{
"""
        main_postfix = """
}
"""
        c_src_file.write("\n".join(CFile.header_lines) + main_prefix + "\n".join(CFile.body_lines) + main_postfix)
        c_src_file.flush()
        return c_src_file

if __name__ == '__main__':
    args = sys.argv[1:]

    C_COMPILER_OPTS = []
    C_FILES = []
    C_ARGS = []
    C_ARGS_FLAG = False
    for arg in args:
        if not C_ARGS_FLAG:
            if arg == '-' or arg.endswith('.c'):
                C_FILES.append(arg)
            elif arg == '--':
                C_ARGS_FLAG = True
            else:
                C_COMPILER_OPTS.append(arg)
        else:
            C_ARGS.append(arg)

    # remove duplicates
    C_FILES = list(set(C_FILES))

    if not C_FILES:
        if args:
            print("Please specify c source file to run.\n")
        usage()
    
    if '-' in C_FILES:
        if os.isatty(sys.stdin.fileno()):
            """ Interatcive mode """
            import readline
            histfile = os.path.join(os.path.expanduser("~"), ".xrunc_history")
            try:
                readline.read_history_file(histfile)
            except IOError:
                pass
            import atexit
            atexit.register(readline.write_history_file, histfile)
            readline.set_completer(Completer().complete)
            if 'libedit' in readline.__doc__:
                readline.parse_and_bind("bind ^I rl_complete")
            else:
                readline.parse_and_bind("tab: complete")

            try:
                while 1:
                    line = raw_input(">>> ")
                    if line.startswith("#include"):
                        CFile.header_lines.append(line);
                    else:
                        CFile.body_lines.append(line)
                    c_src_file = CFile.tmpfile()
                    try:
                        compile_and_execute([c_src_file.name], C_ARGS, C_COMPILER_OPTS)
                    except Exception as e:
                        print("error: {}".format(e))
                        CFile.body_lines.pop()
            except EOFError:
                print("")
                sys.exit(0)

        c_src_file = tempfile.NamedTemporaryFile(suffix=".c", delete=True)
        c_src = ''
        while True:
            c = sys.stdin.read(1)
            if len(c) == 0:
                break
            c_src += c
        c_src_file.write(c_src.encode(sys.stdin.encoding))
        c_src_file.flush()
        # if '-' exists, ignore all other c files
        C_FILES = [c_src_file.name]

    compile_and_execute(C_FILES, C_ARGS, C_COMPILER_OPTS)