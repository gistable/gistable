#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helpers for automating the process of setting up ported Linux/UNIX
applications which were designed with expectations like being in $PATH.

@note: Basic functionality requires only the Python standard library.
       Some functions and methods also require the PyWin32 package.

@note: A much more verbose "sudo for Windows" implementation (BSD-licensed)
       which requires only Python stdlib (uses ctypes) can be found in esky:
       https://github.com/cloudmatrix/esky/blob/master/esky/sudo/sudo_win32.py

@todo: Wrap the Windows API for looking up an associated application so
       elevate() without arguments can be made to work on non-frozen apps.

@todo: Decide if other things like C{DisableReflectionKey} are necessary.
"""

__author__  = "Stephan Sokolow (deitarion/SSokolow)"
__version__ = "0.2"
__license__ = "MIT"

# Dodge the case-sensitivity issue
KEY_PATH = 'Path'

# Constants which seem to not be defined in PyWin32
HWND_BROADCAST   = 0xFFFF # http://msdn.microsoft.com/en-us/library/ms644950%28VS.85%29.aspx
WM_SETTINGCHANGE = 0x001A # http://msdn.microsoft.com/en-us/library/ms725497%28VS.85%29.aspx

import os, sys, _winreg as winreg

def elevate(argv=None, cwd=None, use_arguments=True, show=True):
    """Run a subprocess with elevated privileges.

    (Should work with both UAC and Guest accounts)

    @param argv: Command to run. C{None} for self.
    @param cwd: Working directory or C{None} for C{os.getcwd()}
    @param use_arguments: If False, PyWin32 is not required.
    @param show: See bShow in C{win32api.ShellExecute} docs.
                        (Ignored if use_arguments = C{False})

    @note: This assumes that sys.argv[0] is absolute or relative to cwd.
    @todo: Get access to something newer than XP to test on.
    """
    argv = argv or sys.argv
    cwd = cwd or os.getcwd()

    if isinstance(argv, basestring):
        argv = [argv]
    cmd = os.path.normpath(argv[0])

    if use_arguments:
        from win32api import ShellExecute
        from subprocess import list2cmdline

        args = list2cmdline(argv[1:])
        ShellExecute(0, 'runas', cmd, args, cwd, show)
    else:
        os.chdir(cwd)
        os.startfile(os.path.normpath(cmd), 'runas')

def self_is_elevated():
    """Returns a boolean indicating whether the current process has full
    administrator rights. (eg. whether a UAC elevation needs to be performed)

    @note: Requires PyWin32.
    @todo: Get access to something newer than XP to test on.
    """
    from win32security import (
        CheckTokenMembership,
        CreateWellKnownSid,
        WinBuiltinAdministratorsSid
        )

    sid = CreateWellKnownSid(WinBuiltinAdministratorsSid, None)
    return CheckTokenMembership(None, sid)

class WinEnv(object):
    """
    Convenience class for permanently modifying Windows system environment
    variables from within a Python program or script.

    @note: This bypasses Python's C{os.environ} and directly modifies the
           registry keys Windows uses to persistently store environment
           variables.

    @note: This only supports modern Windows (2K/XP/etc.) which store their
           environment in the registry. C{AUTOEXEC.BAT} is unsupported.

    @note: People writing batch files probably want the SetEnv tool instead.
           (It's more featureful, but it's under a non-libre license so I
           haven't touched it. Binaries, code, and instructions available at
           http://www.codeproject.com/KB/applications/SetEnv.aspx )
    """
    PATH_ENV = r"System\CurrentControlSet\Control\Session Manager\Environment\\"
    DEFAULT_SEP = os.pathsep
    DEFAULT_NORM = lambda x: os.path.normpath(os.path.normcase(x))

    def __init__(self):
        self.env = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            self.PATH_ENV,
            0,
            winreg.KEY_READ|winreg.KEY_WRITE)
        self.val_type_cache = {}

    def _in_val_list(self, val_list, component, norm):
        val_match_list = [norm(x) for x in val_list]
        return norm(component) in val_match_list

    def add(self, key, value, sep=DEFAULT_SEP, norm=DEFAULT_NORM):
        """Append a component to a variable like C{PATH}.

        Wraps L{read_list} and L{write_list}.

        @note: If C{value} is already present in C{key}, no
               modification will take place.
        @param norm: A normalization function for "x in y" checks.
        """
        val_list = self.read_list(key, sep=sep)

        if not self._in_val_list(val_list, value, norm):
            val_list.append(value)

        self.write_list(key, val_list, sep=sep)

    def announce(self):
        """Attempt to update the environment for running applications.

        @note: Requires PyWin32 (Unlike the rest of this class)
        @todo: Confirm this actually does something
        """
        winreg.FlushKey(self.env) # TODO: Is this necessary?

        import win32api
        win32api.SendMessage(HWND_BROADCAST, WM_SETTINGCHANGE, None, 'Environment')
        # (..., None, 'Environment') as specified at http://msdn.microsoft.com/en-us/library/ms725497%28VS.85%29.aspx

    def remove(self, key, value, sep=DEFAULT_SEP, norm=DEFAULT_NORM):
        """Remove a component from a variable like C{PATH}.

        Wraps L{read_list} and L{write_list}.

        @note: If multiple instances of C{value} are found, all will be removed.
        @param norm: A normalization function for "x in y" checks.
        """
        val_list = self.read_list(key, sep=sep)

        while self._in_val_list(val_list, value, norm):
            val_list.remove(value)

        self.write_list(key, val_list, sep=sep)

    def read(self, key):
        """Read and return the given environment variable from the registry.

        Caches the key's type for use with L{write}.
        """
        key_val, key_type = winreg.QueryValueEx(self.env, key)
        self.val_type_cache[key] = key_type
        return key_val

    def read_list(self, key, sep=DEFAULT_SEP):
        """Call L{read} and process its output into a list.

        Defaults to sep=C{os.pathsep}

        @raises TypeError: Returned value is not C{REG_SZ} or C{REG_EXPAND_SZ}
        """
        key_val = self.read(key)

        if self.val_type_cache[key] not in (winreg.REG_EXPAND_SZ, winreg.REG_SZ):
            raise TypeError("Environment variable not a string: %s" % key)

        return key_val.split(sep)

    def write(self, key, value, type=None):
        """Write the given value to the registry.

        Will use the cached value type if not provided.

        @raises KeyError: type=C{None} and key not in cache.
        """
        type = type or self.val_type_cache[key]
        winreg.SetValueEx(self.env, key, 0, type, value)

    def write_list(self, key, value, type=None, sep=DEFAULT_SEP):
        """Convenience wrapper for L{write} which mirrors L{read_list}."""
        self.write(key, sep.join(value), type)

if __name__ == '__main__':
    #NOTE: Example usage only. Command-line syntax will change.
    from optparse import OptionParser
    parser = OptionParser(
        usage="%prog <Path to add to %PATH%>",
        version="%%prog v%s" % __version__)

    opts, args = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        sys.exit(1)

    try:
        if not self_is_elevated():
            elevate()
            sys.exit(0)
    except ImportError:
        print("Unable to import PyWin32. Skipping privilege elevation.")

    env = WinEnv()
    env.add(KEY_PATH, args[0])

    try:
        env.announce()
    except ImportError:
        print("Unable to import PyWin32. Skipping announce()")

