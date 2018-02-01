#!/usr/bin/env python

import re
import sys
import os
import pprint
import types

defines = {}

def parse_define_arg(arg):
    """
    Looks for command-line provided defines of the form:
        -DDEBUG
        -DVERBOSE=2
    etc... and returns a defines-compatible dictionary of
    any found.
    """
    if arg[:2] == "-D":
        parts = arg[2:].split("=")
        if len(parts) == 2:
            return {parts[0]: parts[1]}
        else:
            return {parts[0]: True}
    else:
        return {}


class SyntaxError(Exception):
    def __init__(self, filename, line_no, message):
        super(SyntaxError, self).__init__("File \"%s\", line %s:\n    %s" % (filename, line_no+1, message))

def expression(expr):
    raise(NotImplementedError("Evaluating expressions used in #if or #elif isn't implemented yet."))

def resolve(value):
    return defines.get(value, value)


def strip_comments(line):
    """
    Returns the part of the line that is code. Excludes any parts
    that are comments. Keeps some state to handle block comments that
    span lines.
    """
    if not strip_comments.in_block_comment:
        # Looking for simple single-line comments:
        comment_start_index = line.find("//")
        if comment_start_index != -1:
            code_part = line[:comment_start_index]
        else:
            code_part = line

        # Looking for the start of a block comment:
        block_comment_start_index = code_part.find("/*")
        if block_comment_start_index != -1:
            strip_comments.in_block_comment = True
            return code_part[:block_comment_start_index] + strip_comments(code_part[block_comment_start_index:])
        else:
            return code_part
    else:
        # We're already in a block comment, so just looking for the end:
        block_comment_end_index = line.find("*/")
        if block_comment_end_index != -1:
            strip_comments.in_block_comment = False
            return strip_comments(line[block_comment_end_index+2:])
        else:
            return ""
strip_comments.in_block_comment = False

def load(filename):
    """
    Open and parse the specified file.
    """
    with open(filename) as f:
        continued_line = ""
        if_state = [] # Entries are either "doing", "skipping", or "done".
        for line_no, line in enumerate(f.readlines()):
            line = (continued_line + line).strip()
            continued_line = ""
            if not line:
                continue
            if line[-1] == "\\":
                continued_line = line[:-1]
                continue
            line = strip_comments(line)

            # Looking for #endif:
            match = re.search("#endif", line)
            if match:
                if not if_state:
                    raise(SyntaxError(filename, line_no, "Found #endif with no matching #if, #ifdef, etc..."))
                else:
                    if_state.pop()

            # Looking for #else:
            match = re.search("#(else|elif ) *(.*)", line)
            if match:
                if not if_state:
                    raise(SyntaxError(filename, line_no, "Found %s with no matching #if, #ifdef, etc..." % match.group(1)))
                if if_state[-1] == "doing":
                    if_state[-1] = "done"
                elif if_state[-1] == "skipping":
                    if match.group(1) == "else" or expression(match.group(2)):
                        if_state[-1] = "doing"
                else:
                    pass
                continue

            # Skipping appropriate parts of an #if, #else, #elif, etc...:
            if if_state and if_state[-1] != "doing":
                continue

            # Looking for the various forms of if:
            match = re.search("#(if|ifdef|ifndef) (.*)", line)
            if match:
                if (match.group(1) == "if" and expression(match.group(2))) or (match.group(1) == "ifdef" and match.group(2) in defines) or (match.group(1) == "ifndef" and match.group(2) not in defines):
                    if_state.append("doing")
                else:
                    if_state.append("skipping")
                continue

            # Looking for function-like macros:
            match = re.search("#define +([^ ]+)\(([^)]*)\)(?: +(.*))?", line)
            if match:
                def func(*args, **kwargs):
                    raise NotImplementedError("Evaluating function-like macros isn't supported yet.")
                defines[match.group(1)] = func
                continue

            # Looking for empty macros and macros with a value:
            match = re.search("#define +([^ ]+)(?: +(.*))?", line)
            if match:
                defines[match.group(1)] = resolve(match.group(2)) or True
                continue

            # Looking for undefines:
            match = re.search("#undef +([^ ]+)", line)
            if match:
                defines.pop(match.group(1), None)
                continue

            # Looking for includes:
            match = re.search('#include +(.*)', line)
            if match:
                load(match.group(1).strip("").strip('"<>')) # Recursively loading the include file
                continue


# Parsing command line arguments and preparing help text:
# First, determining both the executable name and the module name, whether this
# file was run as an executable or imported as a module: not straightforward.
if __name__ == "__main__":
    executable_name = sys.argv[0]
    filename = os.path.basename(executable_name)
    if filename[-3:] != ".py":
        module_name = None # Can't be imported as a module (normaly at least) if the filename doesn't end in .py
        input_file = filename + ".h"
    else:
        module_name = filename[:-3]
        input_file = module_name + ".h"
else:
    filename = os.path.basename(__file__)
    if filename[-4:] == ".pyc":
        executable_name = filename[:-1]
    else:
        executable_name = filename
    module_name = __name__
    input_file = module_name + ".h"


help = """Command line usage:
    {executable_name} [input_file] [-h] [--help] [-Dname] [-Dname=value]

Python usage:
    import {module_name}

Parses macros out of a C/C++ source file. When called from the command line,
prints them to stdout. When imported as a Python module, makes them available
as module attributes.

optional arguments:
  input_file        path to the file to use as input (defaults to the name of
                    this module + .h: {input_file})
  -h, --help        show this help message and exit
  -Dname            define an empty macro named "name". Can be specified
                    multiple times for different names.
  -Dname=value      define a macro with name "name" and value "value". Can
                    be specified multiple times for different names.

Arguments can be provided even when importing by setting them manually. Ex:

import sys
sys.argv[1:] = ["-DDEBUG", "-DVERBOSE=2]
import {module_name}

Alternatively, a special form is available for easily specifying multiple
defines:

import sys
sys.argv[1:] = [{{"DEBUG": True, "VERBOSE":2}}]
import {module_name}

""".format(executable_name=executable_name, module_name=module_name if module_name else "<module_name> # must rename file to end in .py to be a module", input_file=input_file)

for arg in sys.argv[1:]:
    if arg == "-h" or arg == "--help":
        print(help)
        sys.exit(0)
    else:
        if isinstance(arg, dict):
            # Handling the case where a complete dictionary of defines is provided
            # by an importing module. This dictionary of course didn't come from
            # the command line.
            defines.update(arg)
        elif arg.find("-") != 0:
            input_file = arg
        else:
            defines.update(parse_define_arg(arg))

load(input_file)

if __name__ == "__main__":
    # If we're running this file as a script, just print the defines:
    pprint.pprint(defines)
else:
    # If this module is being imported, we replace everything defined above with a class to get the defines.
    # This is what allows the defines to appear as module attributes.
    class DefinesModule(types.ModuleType):
        __defines = defines
        def __getattr__(self, name):
            return self.__defines.get(name)

    sys.modules[__name__] = DefinesModule(__name__)