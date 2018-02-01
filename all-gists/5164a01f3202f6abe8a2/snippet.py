#!/usr/bin/env python

import optparse
from subprocess import Popen, PIPE
import time

def prepare_options():
    """Define optparse options."""
    optp = optparse.OptionParser(
        usage = 'Usage: %prog OUT1 [OUT2 OUT3...]\n\tOUT[n] are devices taken from left to right.',
    )

    return optp

def main():
    optp = prepare_options()
    (options, args) = optp.parse_args()

    if len(args) == 0:
        print "Incorrect number of arguments!"
        return 1

    modes = {}

    command = ['xrandr']
    fallback_command_enable = ['xrandr'] # enable back current settings
    fallback_command_disable = ['xrandr'] # but first disable wanted ones!
    out, err = Popen(command, stdout=PIPE, stderr=PIPE).communicate()
    print err

    # gather available modes and the best resolution for each one
    current_out = None
    for line in out.splitlines():
        line = line.strip().split()
        if line[1] == 'connected':
            current_out = line[0]
            if line[0] not in args:
                command.extend(['--output', line[0], '--off'])
        else:
            if "*" in ' '.join(line):
                fallback_command_enable.extend(['--output', current_out, '--auto'])
            if current_out is not None:
                try:
                    if current_out not in modes:
                        mode = line[0]
                        if int(mode.split('x')[0]) > 0:
                            modes[current_out] = mode
                    else:
                        mode = line[0]
                        if int(line[0].split('x')[0]) > int(modes[current_out].split('x')[0]):
                            modes[current_out] = mode
                except ValueError:
                    pass

    # Disable current mode(s)
    print ' '.join(command)
    out, err = Popen(command, stdout=PIPE, stderr=PIPE).communicate()

    command = ['xrandr']
    for arg_no, arg in enumerate(args):
        if arg in modes:
            command.extend(['--output', arg, '--mode', modes[arg]])
            fallback_command_disable.extend(['--output', arg, '--off'])
            if arg_no > 0:
                command.extend(['--right-of', args[arg_no - 1]])

    # Enable new mode(s)
    print ' '.join(command)
    out, err = Popen(command, stdout=PIPE, stderr=PIPE).communicate()
    print err

    # check if any output is connected after operation. Otherwise fallback
    out_connected = False
    out, err = Popen(['xrandr'], stdout=PIPE, stderr=PIPE).communicate()
    for line in out.splitlines():
        if "*" in line:
            out_connected = True
            break

    # fallback if nothing is connected
    if out_connected is False:
        print 'Falling back!'
        print ' '.join(fallback_command_disable)
        out, err = Popen(fallback_command_disable, stdout=PIPE, stderr=PIPE).communicate()
        print ' '.join(fallback_command_enable)
        out, err = Popen(fallback_command_enable, stdout=PIPE, stderr=PIPE).communicate()
        print err

try:
    main()
except KeyboardInterrupt:
    raise SystemExit(0)