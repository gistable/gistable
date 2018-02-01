#! /usr/bin/python2.7
# coding: utf-8

# ref: http://unixhelp.ed.ac.uk/CGI/man-cgi?xargs

"""
create .bat file below as xargs.bat and run this script 
@echo off
C:\Python27\python.exe %~dp0xargs.py %*

"""

import sys
import os
import argparse
import multiprocessing
import Queue

__version__ = '0.0.1'
__author__ = 'yatt/brainfs'

def worker_fn(no, cmd, queue, lock, verbose, show_only):
    #with lock:print '[%d] start' % no
    
    while True:
        try:
            args = queue.get(timeout = 1)
            
            # build commandline
            cmd_folded = ''
            if any('{}' in c for c in cmd):
                cmd_folded = ' '.join(c.replace('{}', ' '.join(args)) for c in cmd)
            else:
                cmd_folded = ' '.join(cmd + args)

            if verbose or show_only:
                with lock:
                    print '[%d] %s ' % (no, cmd_folded)

            if not show_only:
                os.system(cmd_folded)

        except Queue.Empty, e:
            #with lock: print '[%d] %s' % (no,e)
            break
    
        except Exception, e:
            with lock: print '[%d] %s' % (no,e)


def main():
    parser = argparse.ArgumentParser(description='build and execute command lines from standard input')

    parser.add_argument('--max-args', '-n'
        , type = int
        , dest = 'maxargs'
        , action = 'store'
        , default = 1
        , help = """Use  at  most  max-args  arguments per command line.  Fewer than
max-args arguments will be used if the size (see the -s  option)
is  exceeded, unless the -x option is given, in which case xargs
will exit."""
        )

    parser.add_argument('--max-procs', '-P'
        , type = int
        , dest = 'maxprocs'
        , action = 'store'
        , default = 1
        , help = """Run up to max-procs processes at a time; the default is  1.   If
max-procs is 0, xargs will run as many processes as possible at
a time.  Use the -n option with -P; otherwise chances  are  that
only one exec will be done."""
        )

    parser.add_argument('--version'
        , dest = 'version'
        , action = 'store_true'
        , default = False
        , help = 'Print the version number of xargs and exit.'
        )

    parser.add_argument('--verbose', '-t'
        , dest = 'verbose'
        , action = 'store_true'
        , default = False
        , help = """Print  the command line on the standard error output before exe-
cuting it."""
        )

    parser.add_argument('--show'
        , dest = 'show'
        , action = 'store_true'
        , default = False
        , help = 'Print  the command line only.'
        )

    parser.add_argument('remaining', nargs=argparse.REMAINDER)

    args = parser.parse_args()
    
    cmd = args.remaining
    
    
    if args.version:
        print __version__
        return
    
    if cmd == []:
        print >> sys.stderr, 'specify command to apply argments'
        return
    
    # chunking stdin and initialize job queue
    cmdargs = sys.stdin.read().splitlines()
    queue = multiprocessing.Queue()
    lock = multiprocessing.Lock()

    jobs = []
    n = args.maxargs
    d,m = divmod(len(cmdargs), n)
    for i in xrange(d):
        jobs.append(cmdargs[i*n: i*n+n])
    if m != 0:
        jobs.append(cmdargs[-m:])
    for j in jobs:
        queue.put(j)

    workers = [multiprocessing.Process(target=worker_fn, args=(i+1, cmd, queue,lock,args.verbose,args.show)) for i in xrange(args.maxprocs)]
    for w in workers:
        w.start()

    for w in workers:
        w.join()


if __name__ == '__main__':
    main()

