#!/usr/bin/python
# ========================================================================================
# Check System
#
# Written by    : Ryan Fisher  rfisher@cyberpointllc.com
# Release       : 1.0
# Creation date : 13 Jan 2016
# ========================================================================================

import psutil
import sys
import traceback

STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3

try:
    action = sys.argv[1]
    warn = int(sys.argv[2])
    crit = int(sys.argv[3])

    # This is a status check for disk
    if action == 'disk':
        path = sys.argv[4]

        disk = psutil.disk_usage(path)
        if disk.percent >= crit:
            print("DISK CRITICAL: %s%% used" % disk.percent)
            sys.exit(STATE_CRITICAL)
        if disk.percent >= warn:
            print("DISK WARNING: %s%% used" % disk.percent)
            sys.exit(STATE_CRITICAL)

        print("DISK OK: %s%% used" % disk.percent)
        sys.exit(STATE_OK)

    # This is a memory check for a service
    if action == 'mem':
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        if mem.percent >= crit or swap.percent >= crit:
            print("MEM CRITICAL: %s%% memory used -- %s%% swap used" % (mem.percent, swap.percent))
            sys.exit(STATE_CRITICAL)
        if mem.percent >= warn or swap.percent >= warn:
            print("MEM WARNING: %s%% memory used -- %s%% swap used" % (mem.percent, swap.percent))
            sys.exit(STATE_WARNING)

        print("MEM OK: %s%% memory used -- %s%% swap used" % (mem.percent, swap.percent))
        sys.exit(STATE_OK)

    # This is a cpu check for a service
    if action == 'cpu':

        cpu_p = psutil.cpu_percent(interval=1)
        if cpu_p >= crit:
            print("CPU CRITICAL: %s%%" % cpu_p)
            sys.exit(STATE_CRITICAL)
        if cpu_p >= warn:
            print("CPU WARNING: %s%%" % cpu_p)
            sys.exit(STATE_WARNING)

        print("CPU OK: %s%%" % cpu_p)
        sys.exit(STATE_OK)

except Exception as e:
    print(traceback.format_exc())
    sys.exit(STATE_CRITICAL)
