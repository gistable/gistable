#!/usr/bin/env python
# coding=utf8

# Copyright (C) 2010 Saúl ibarra Corretgé <saghul@gmail.com>
#

"""
pydmesg: dmesg with human-readable timestamps
"""

from __future__ import with_statement

import re
import subprocess
import sys

from datetime import datetime, timedelta


_datetime_format = "%Y-%m-%d %H:%M:%S"
_dmesg_line_regex = re.compile("^\[\s*(?P<time>\d+\.\d+)\](?P<line>.*)$")

def exec_process(cmdline, silent, input=None, **kwargs):
    """Execute a subprocess and returns the returncode, stdout buffer and stderr buffer.
       Optionally prints stdout and stderr while running."""
    try:
        sub = subprocess.Popen(cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        stdout, stderr = sub.communicate(input=input)
        returncode = sub.returncode
        if not silent:
            sys.stdout.write(stdout)
            sys.stderr.write(stderr)
    except OSError,e:
        if e.errno == 2:
            raise RuntimeError('"%s" is not present on this system' % cmdline[0])
        else:
            raise
    if returncode != 0:
        raise RuntimeError('Got return value %d while executing "%s", stderr output was:\n%s' % (returncode, " ".join(cmdline), stderr.rstrip("\n")))
    return stdout

def human_dmesg():
    now = datetime.now()
    uptime_diff = None
    try:
        with open('/proc/uptime') as f:
            uptime_diff = f.read().strip().split()[0]
    except IndexError:
        return
    else:
        try:
            uptime = now - timedelta(seconds=int(uptime_diff.split('.')[0]), microseconds=int(uptime_diff.split('.')[1]))
        except IndexError:
            return

    dmesg_data = exec_process(['dmesg'], True)
    for line in dmesg_data.split('\n'):
        if not line:
            continue
        match = _dmesg_line_regex.match(line)
        if match:
            try:
                seconds = int(match.groupdict().get('time', '').split('.')[0])
                nanoseconds = int(match.groupdict().get('time', '').split('.')[1])
                microseconds = int(round(nanoseconds * 0.001))
                line = match.groupdict().get('line', '')
                t = uptime + timedelta(seconds=seconds, microseconds=microseconds)
            except IndexError:
                pass
            else:
                print "[%s]%s" % (t.strftime(_datetime_format), line)


if __name__ == '__main__':
    human_dmesg()