#!/usr/bin/env python

import sys
import string
import commands
import subprocess

true = True
false = False

def main(argv):
    argc = len(argv)

    if argc != 2:
        print '[*] gdbwaitforproc.py by argp at domain census-labs.com'
        print '[*] usage: %s <process name>' % (argv[0])
        sys.exit(1)

    pname = argv[1]
    pstr = ''

    while true:
        pstr = commands.getoutput('ps aux | grep %s | grep -v grep | grep -v %s' % (pname, argv[0]))

        if pstr == '':
            print '[+] waiting for process: %s' % (pname)
        else:
            break

    pid = string.split(pstr)[1]

    if pid == '':
        print '[!] error finding the PID of process %s' % (pname)
        sys.exit(1)

    gdb_proc = subprocess.Popen(['gdb', '--command=~/.gdbinit', '--pid=%d' % (int(pid))])
    gdb_proc.wait()
 
if __name__ == '__main__':
    main(sys.argv)
    sys.exit(0)

# EOF