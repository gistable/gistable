#!/usr/bin/python
"""
Usage: watchpos {filename|pid fd}

Watches the file pointer of an opened file on Linux.  Use it to provide a
progress bar to a command that doesn't have one, assuming the program reads
this file from start to end without jumping around.

Copyright (c) 2011 Marius Gedminas <marius@gedmin.as>

Licence: GPL v2 or later
"""
import os
import time
import optparse
import sys
import subprocess
import string


def lsof(filename):
    pid = fd = None
    pipe = subprocess.Popen(['lsof', '-Fpf', filename], stdout=subprocess.PIPE)
    for line in pipe.stdout:
        if line.startswith('p'):
            pid = int(line[1:])
        elif line.startswith('f'):
            fd = int(line[1:])
    return pid, fd


def getpos(pid, fd):
    with open('/proc/%d/fdinfo/%d' % (pid, fd)) as f:
        for line in f:
            if line.startswith('pos:'):
                return int(line.split()[1])
    return None


def getsize(pid, fd):
    return os.stat('/proc/%d/fd/%d' % (pid, fd)).st_size


def getname(pid, fd):
    return os.readlink('/proc/%d/fd/%d' % (pid, fd))


def getargv(pid):
    with open('/proc/%d/cmdline' % pid) as f:
        return f.read().split('\0')


def format_arg(arg):
    safe_chars = string.ascii_letters + string.digits + '-=+,./:@^_~'
    if all(c in safe_chars for c in arg):
        return arg
    else:
        return "'%s'" % arg.encode('string-escape')


def format_argv(argv):
    return ' '.join(map(format_arg, argv))


def fmtsize(size):
    unit = "B"
    if size >= 1024:
       size /= 1024.0
       unit = "KiB"
    if size >= 1024:
       size /= 1024.0
       unit = "MiB"
    if size >= 1024:
       size /= 1024.0
       unit = "GiB"
    if size >= 1024:
       size /= 1024.0
       unit = "TiB"
    return "%.1f %s" % (size, unit)


def fmttime(secs):
    days, secs = divmod(secs, 24*60*60)
    return (("%sd" % days if days else "") +
            "%d:%02d:%02d" % (secs // 3600, secs % 3600 // 60, secs % 60))


def fmtspeed(speed):
    return fmtsize(speed) + "/s"


LAST_STR_LEN = 0


def do_print(str):
    global LAST_STR_LEN
    padding = " "  * (LAST_STR_LEN - len(str))
    sys.stdout.write("\r%s%s" % (str, padding))
    sys.stdout.flush()
    LAST_STR_LEN = len(str)


def do_main():
    parser = optparse.OptionParser(usage='%prog {pid fd|filename}')
    opts, args = parser.parse_args()
    if len(args) < 1:
        parser.error("not enough arguments")
    if len(args) > 2:
        parser.error("too many arguments")
    if len(args) == 1:
        filename = args[0]
        pid, fd = lsof(filename)
        if pid is None:
            sys.exit("no process has %s open" % filename)
    else:
        try:
            pid = int(args[0])
        except ValueError:
            parser.error("pid is not an integer: %s" % pid)
        try:
            fd = int(args[1])
        except ValueError:
            parser.error("fd is not an integer: %s" % fd)

    argv = getargv(pid)
    filename = getname(pid, fd)
    size = getsize(pid, fd)
    lastpos = firstpos = getpos(pid, fd)
    lasttime = firsttime = time.time()

    print "%s is file descriptor %d of pid %d" % (filename, fd, pid)
    print format_argv(argv)
    perc = ("%.1f%% " % (lastpos * 100.0 / size) if size and lastpos is not None
            else "")
    do_print("%s%s/%s" % (perc, fmtsize(lastpos), fmtsize(size)))
    while True:
        curpos = getpos(pid, fd)
        if curpos is None:
            print "\n/proc/%d/fd/%d does not exist" % (pid, fd)
            break
        curtime = time.time()
        delta_t = curtime - lasttime
        delta = curpos - lastpos
        if delta != 0 and delta_t != 0 or delta_t > 30:
            sp_cur = max(0, delta / delta_t)
            sp_avg = max(0, (curpos - firstpos) / (curtime - firsttime))
            size = getsize(pid, fd) # file may have grown since we last checked
            perc = ("%.1f%% " % (lastpos * 100.0 / size)
                    if size and lastpos is not None else "")
            eta = (" ETA: %s" % fmttime((size - curpos) / sp_avg)
                   if size and sp_avg else "")
            do_print("%s%s/%s (%s cur, %s avg)%s" % (
                perc, fmtsize(lastpos), fmtsize(size),
                fmtspeed(sp_cur), fmtspeed(sp_avg), eta))
            lastpos = curpos
            lasttime = curtime
        time.sleep(2)


def main():
    try:
        do_main()
    except KeyboardInterrupt:
        print

if __name__ == '__main__':
    main()