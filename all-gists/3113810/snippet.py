#!/usr/bin/python
# -*- coding: utf-8 -*-

# BBErrors: Script to display compiler output messages in BBEdit browser window
# Copyright Jay Lieske Jr.
# 2 May 2016

import sys, re, os
import struct
from Foundation import NSAppleEventDescriptor
from ScriptingBridge import SBApplication

if sys.stdin.isatty():
    print "usage: ... | bberrors 'Window Title'"
    print "Filters standard input for compiler error messages, "
    print "and tells BBEdit to display the messages in an error browser window."
    sys.exit(1)

def fourCharCode(string):
  "Convert a four-char code string into a 32-bit int."
  return struct.unpack('>I', string)[0]

def processMessages():
    # Matches just the error messages from the compiler:
    # a file name, followed by a colon and line number, an optional column number,
    # and then the error message.
    # Since BBEdit doesn't accept column numbers, it doesn't try to parse
    # other positional feedback from the compiler.
    # To avoid false matches, this version doesn't allow spaces in file names.
    pat = re.compile(r"^([^: ]+):(\d+)(?:[.:-]\d+)*[:\s]+(.+)$")

    # Distinguish warning from errors.
    warning = re.compile(r"warning", re.IGNORECASE)
    warning_kind = NSAppleEventDescriptor.descriptorWithEnumCode_(
        fourCharCode('Wrng'))
    error_kind = NSAppleEventDescriptor.descriptorWithEnumCode_(
        fourCharCode('Err '))

    # Accumulate the set of errors found on stdin.
    entries = []
    for line in sys.stdin:
        sys.stdout.write(line) # echo everything
        match = pat.match(line)
        if match:
            file, line, message = match.groups()
            kind = warning_kind if warning.match(message) else error_kind
            file = os.path.abspath(file)
            # BBEdit returns error -1701 for nonexistent files.
            if os.path.exists(file):
                entries.append(dict(result_kind=kind,
                                    result_file=file,
                                    result_line=int(line),
                                    message=message))
    return entries

def showResultsBrowser(name, entries):
    BBEdit = SBApplication.applicationWithBundleIdentifier_(
      "com.barebones.BBEdit")
    ResultsBrowser = BBEdit.classForScriptingClass_("results browser")
    properties = {'name': name}
    browserSpecifier = ResultsBrowser.alloc().initWithElementCode_properties_data_(
      fourCharCode('RslW'), properties, entries)
    BBEdit.windows().addObject_(browserSpecifier)

entries = processMessages()
if not entries: sys.exit(0)
name = sys.argv[1] if len(sys.argv) > 1 else "Browser"
showResultsBrowser(name, entries)


# MIT License
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
