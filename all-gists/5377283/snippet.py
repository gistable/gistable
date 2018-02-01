#!/usr/bin/python -E
# -*- coding: UTF-8 -*-

# Usage:  In ~/.tmuxrc,
#    set default-command /Users/chirayu/ck/vcs/ck5/scripts/for_os_x/tmux_shell_with_clipboard_support.sh

import ctypes
import os
import platform


# Fix clipboard access under Mac OS X.
# I think with vim 7.3 and later with the +clipboard option, this won't be
# needed anymore so add a check for that.
#
# For details, see https://github.com/ChrisJohnsen/tmux-MacOSX-pasteboard/blob/master/reattach-to-user-namespace.c


def fixup_clipboard_on_mac_os_x():
  if platform.system() != "Darwin":
    return
  mac_ver = platform.mac_ver()  # e.g. ('10.7.3', ('', '', ''), 'x86_64')
  mac_ver = tuple(map(int, mac_ver[0].split(".")))[:2]
  if mac_ver < (10, 5) or mac_ver >= (11, 0):
    return
  libsystem = ctypes.cdll.LoadLibrary("libSystem.dylib")
  if mac_ver == (10, 5):
    r = libsystem._vprocmgr_move_subset_to_user(os.getuid(), "Background")
  else:
    r = libsystem._vprocmgr_move_subset_to_user(os.getuid(), "Background", 0)
  if r:
    print "fixup_clipboard_on_mac_os_x(): Failed. Error code: ", r


def run_login_shell():
  os.execv(os.getenv("SHELL", "/usr/bin/zsh"), ["-l"])


fixup_clipboard_on_mac_os_x()
run_login_shell()