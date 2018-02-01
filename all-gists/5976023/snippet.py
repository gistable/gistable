#!/usr/bin/env python
import shlex
import subprocess
import datetime as dt
from sys import argv, exit
from os import fork
import time


def usage():
    print('Usage: %s HH:MM [custom message]' % argv[0])


def sleep(seconds):
    '''Wait!!!'''
    print('Sending alert in %s seconds' % seconds)
    time.sleep(seconds)


def send_message():
    '''Send message to i3-nagbar'''
    message = ' '.join(argv[2:]) if len(argv) > 2 else 'Reminder'
    subprocess.Popen(shlex.split("i3-nagbar -m '%s'" % message), stderr=subprocess.STDOUT, stdout=open('/dev/null'))


def calculate_sleep(hour, minute):
    '''Calculate seconds'''
    now = dt.datetime.now()
    t0 = dt.datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=hour,
        minute=minute
    )
    return (t0 - now).seconds


def get_seconds_from_input():
    return argv[1].split(':')


def main():
    if fork():
        exit()
    hour, minute = get_seconds_from_input()
    sleep(calculate_sleep(int(hour), int(minute)))
    send_message()


if __name__ == '__main__':
    try:
        main()
    except Exception, err:
        print(err)
        usage()
