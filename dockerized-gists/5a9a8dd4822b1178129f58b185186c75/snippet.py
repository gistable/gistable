##
## Quick & dirty python toolz
## Copyright (c) 2016 YouniS Bensalah [:younishd] <younis.bensalah@gmail.com>
##

import os

def ex(cmd):
    """
    Execute a command and return True on success or False on failure.
    """
    return os.system(cmd + ' >/dev/null 2>&1') == 0

def ex_in(cmd, path):
    """
    Execute a command in a path and return True on success or False on failure.
    """
    return os.system('cd \'{}\' && {} >/dev/null 2>&1'.format(path, cmd)) == 0
    
def ex_ll(cmd):
    """
    Execute a command and return the last line of output.
    """
    p = os.popen(cmd)
    s = p.readline()
    p.close()
    return s

def ex_in_ll(cmd, path):
    """
    Execute a command in a path and return the last line of output.
    """
    p = os.popen('cd \'{}\' && {}'.format(path, cmd))
    s = p.readline()
    p.close()
    return s
    
GREEN           = '\033[92m'
YELLOW          = '\033[93m'
RED             = '\033[91m'
BOLD            = '\033[1m'
ENDC            = '\033[0m'
TICK            = u'\u2713'
CROSS           = u'\u2718'

def green(msg):
    return GREEN + msg + ENDC

def yellow(msg):
    return YELLOW + msg + ENDC

def red(msg):
    return RED + msg + ENDC

def bold(msg):
    return BOLD + msg + ENDC
