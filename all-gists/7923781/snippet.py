""" File: reveal.py

Add to ~/.lldbinit:
    command script import ~/.lldb-scripts/reveal.py

Q: Want to automatically load the Reveal lib on launch while debugging from Xcode?
A: In Xcode:
    Add a Symbolic Breakpoint
    Symbol: "UIApplicationMain"
    Action: Debugger Command with value "reveal"
    Tick "Automatically continue after evaluating"
"""

__author__ = 'Chris Miles'
__copyright__ = 'Copyright (c) Chris Miles 2013'
__license__ = 'MIT'


import lldb


def auto_load_reveal(debugger, command, result, dict):
    lldb.debugger.HandleCommand('call (void*)dlopen("/Applications/Reveal.app/Contents/SharedSupport/iOS-Libraries/libReveal.dylib", 0x2)')


def __lldb_init_module(debugger, internal_dict):
  debugger.HandleCommand('command script add -f reveal.auto_load_reveal reveal')
