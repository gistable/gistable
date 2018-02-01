#!/usr/bin/env python
#coding: utf-8

import os
import imp
import time
import signal
import argparse
import commands

# !!! You must specify this !!!
CONFIG_PATH = '{SOME-PATH-TO}/gunicorn_conf.py'


config = imp.load_source('config', CONFIG_PATH)

def get_pid():
    if os.path.exists(config.pidfile):
        with open(config.pidfile, 'r') as f:
            return int(f.read())
    else:
        print '[Error]: pid file not exists!'
        return None


def rm_pidfile():
    if os.path.exists(config.pidfile):
        print '[Remove File]: %s' % config.pidfile
        os.remove(config.pidfile)


def status():
    if os.path.exists(config.pidfile):
        output = commands.getoutput('ls -l %s' % config.pidfile)
        print '[Pid File]: %s' % output
        pid = get_pid()
        try:
            os.kill(pid, 0)
            print '[OK]: <pid: %d> is alive.' % pid
        except OSError, e:
            print '[Error]: <pid: %d> has gone!' % pid
            rm_pidfile()
    else:
        print '[Pid File]: NOT exists!'

    status_cmd = 'ps aux | grep gunicorn.*%s' % config.app
    print '[Process List]:  %s' % status_cmd
    output = commands.getoutput(status_cmd)
    lines = [line for line in output.split('\n') if line.find('grep') == -1]
    print '''--------------------------------------------------
%s
--------------------------------------------------''' % '\n'.join(lines)


def Quit():
    pid = get_pid()
    if pid:
        print '>>> Quiting ......'
        try:
            os.kill(pid, signal.SIGQUIT)
        except OSError, e:
            print '[Failed]: Server haven\'t start yet!'
        finally:
            time.sleep(1)
            rm_pidfile()


def Stop():
    pid = get_pid()
    if pid:
        print '>>> Stoping ......'
        try:
            os.kill(pid, signal.SIGTERM)
            print '[Successed]: ok!'
        except OSError, e:
            print '[Failed]: <pid: %d> has gone!' % pid
        finally:
            rm_pidfile()


def Reload():
    pid = get_pid()
    if pid:
        print '>>> Reloading ......'
        try:
            os.kill(pid, signal.SIGHUP)
        except OSError, e:
            print '[Failed]: Server haven\'t start yet!'


def start(bind):
    if os.path.exists(config.pidfile):
        pid = get_pid()
        print '<< Server already started! >>'
    else:
        print '>>> Starting server ......'
        if bind is None:
            bind = config.bind
        run_cmd = 'gunicorn  -c %(config)s  -b %(bind)s  %(app)s ' % {
            'config' : CONFIG_PATH,
            'bind' : bind,
            'app': config.app,
        }
        print '[Run Command]: %s' % run_cmd
        code, output = commands.getstatusoutput(run_cmd)

        if code == 0:
            time.sleep(8)
            pid = get_pid()
            try:
                os.kill(pid, 0)
                print '''
[Successed]:
===========
    pid      =  %d
    pidfile  =  %s
    address  =  %s
                ''' % (pid, config.pidfile, bind)
            except OSError, e:
                print '''
[Failed]:
========
    Process start failed.
    Permission denied? You may run this script as `root'.
                '''
                rm_pidfile()
        else:
            print '[Failed]: status=[%d], output=[%s]' % (code, output)


def restart():
    Quit()
    start()


def main():
    parser = argparse.ArgumentParser(description='Manage the gunicorn(just like apache) server.')
    parser.add_argument('--start', action='store_true', help='Start your wsgi application. (config = %s, app = %s)' % (CONFIG_PATH, config.app))
    parser.add_argument('--quit', action='store_true', help='[Unrecomanded!] Quick shutdown. ')
    parser.add_argument('--stop', action='store_true', help='Graceful shutdown. Waits for workers to finish their current requests up to the graceful timeout.')
    parser.add_argument('--reload', action='store_true', help='Reload the configuration, start the new worker processes with a new configuration and gracefully shutdown older workers.')
    parser.add_argument('--restart', action='store_true', help='[Unrecomanded!] Simply `quit\' the server then `start\' it')
    parser.add_argument('--status', action='store_true', help='Show gunicorn processes.')
    parser.add_argument('-b', '--bind', metavar='ADDRESS', help='The socket to bind. [[\'127.0.0.1:8000\']]')
    args = parser.parse_args()

    # `start' and `restart' are special.
    if args.start:
        start(args.bind)
        return
    elif args.restart:
        restart()
        return

    for label, func in {'status': status,
                        'quit': Quit,
                        'stop': Stop,
                        'reload': Reload }.iteritems():
        if getattr(args, label):
            func()
            break
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
