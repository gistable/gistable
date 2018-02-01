#!/usr/bin/python

import subprocess
import os

def adbshell(command, serial=None, adbpath='adb'):
    args = [adbpath]
    if serial is not None:
        args.append('-s')
        args.append(serial)
    args.append('shell')
    args.append(command)
    return os.linesep.join(subprocess.check_output(args).split('\r\n')[0:-1])

def adbdevices(adbpath='adb'):
    return [dev.split('\t')[0] for dev in subprocess.check_output([adbpath, 'devices']).splitlines() if dev.endswith('\tdevice')]

def touchscreen_devices(serial=None, adbpath='adb'):
    return [dev.splitlines()[0].split()[-1] for dev in adbshell('getevent -il', serial, adbpath).split('add device ') if dev.find('ABS_MT_POSITION_X') > -1]

def tap(devicename, x, y, serial=None, adbpath='adb'):
    adbshell('S="sendevent {}";$S 3 57 0;$S 3 53 {};$S 3 54 {};$S 3 58 50;$S 3 50 5;$S 0 2 0;$S 0 0 0;'.format(devicename, x, y), serial, adbpath)
    adbshell('S="sendevent {}";$S 3 57 -1;$S 0 2 0;$S 0 0 0;'.format(devicename), serial, adbpath)

serial = adbdevices()[0]
touchdev = touchscreen_devices(serial)[0]
tap(touchdev, 100, 100, serial)





