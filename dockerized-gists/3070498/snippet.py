#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, subprocess

def getAttachedDeviceIds():
    deviceIds = []
    cmd = "adb devices | sed -n 's/^\(.*\)\s\+device$/\1/p'"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, close_fds=True)
    stdo = p.stdout
    while True:
        line = stdo.readline()
        if not line:
            break
        deviceIds.append(line.rstrip())
    return deviceIds

def getSpecificModelDeviceId(modelName):
    deviceIds = getAttachedDeviceIds()
    if modelName is not None:
        tmp = []
        for deviceId in deviceIds:
            cmd = "adb -s %s shell getprop 'ro.product.model'" % (deviceId)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, close_fds=True)
            stdo = p.stdout
            while True:
                line = stdo.readline()
                if not line:
                    break
                if line.rstrip() == modelName:
                    tmp.append(deviceId)
        deviceIds = tmp
    return deviceIds

def getTargetDeviceIds(switch = None, serial = None):
    deviceIds = getAttachedDeviceIds()
    if switch is not None:
        p = re.compile('^emulator-[0-9]{4}$')
        tmp = []
        for deviceId in deviceIds:
            if p.match(deviceId) == None:
                if switch == '-d':
                    tmp.append(deviceId)
            else:
                if switch == '-e':
                    tmp.append(deviceId)
        deviceIds = tmp
    if serial is not None:
        tmp = []
        for deviceId in deviceIds:
            if deviceId == a:
                tmp.append(deviceId)
                break
        deviceIds = tmp
    return deviceIds

if __name__ == '__main__':
    import getopt, sys
    args = sys.argv[1:]
    switch = None
    serial = None
    try:
        opts, args = getopt.getopt(args, 'des:', ['device', 'emulator', 'serial='])
        for o, a in opts:
            if o in ('-d', '--device'):
                switch = '-d'
            if o in ('-e', '--emulator'):
                switch = '-e'
            if o in ('-s', '--serial'):
                serial = a
    except:
        pass
    deviceIds = getTargetDeviceIds(switch, serial)
    numberOfDevices = len(deviceIds)
    if numberOfDevices == 0:
        print 'device not found'
        sys.exit(1)
    if numberOfDevices > 1:
        print 'more than one device and emulator'
        sys.exit(numberOfDevices)
    print deviceIds[0]
#EOF