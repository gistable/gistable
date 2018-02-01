#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import os
import time
import select
import socket

import pycares

RETRIES = 3
TIMEOUT = 3
CONCURRENT = 1000
FORCED_TIMEOUT = 60

class Resolver(object):
    def __init__(self):
        self.chan = pycares.Channel(timeout=TIMEOUT, tries=RETRIES)
        self.sent_count = 0
        self.recv_count = 0
        self.active_count = 0
        self.error_count = 0
        self.last_answer = time.time()

    def process(self, ip):
        self.chan.gethostbyname(ip, socket.AF_INET, self.result_cb)
        self.active_count += 1
        self.sent_count += 1

    def result_cb(self, res, error):
        self.last_answer = time.time()
        self.active_count -= 1
        self.recv_count += 1
        if res:
            try: addr = res.addresses[0]
            except: addr = "UNKNOWN"
            print "{0},{1}".format(res.name, addr)
        else:
            self.error_count += 1

    def select(self):
        readfds, writefds = self.chan.getsock()
        canreadfds, canwritefds, _ = select.select(readfds, writefds, [], 0.001)
        for rfd in canreadfds:
            self.chan.process_fd(rfd, -1)
        for wfd in canwritefds:
            self.chan.process_fd(-1, wfd)

    def close(self):
        self.chan.destroy()


def main():
    r = Resolver()

    while True:
        if r.active_count < CONCURRENT:
            rfds, _, _ = select.select([sys.stdin,],[],[],0.001)
            if rfds:
                line = sys.stdin.readline()
                if not line: break
                line = line.strip()
                if not line: continue

                try:
                    r.process(line)
                except Exception as e:
                    print >>sys.stderr, "exception gethostbyaddr", e, line

        r.select()

    input_done = time.time()
    wait_time = TIMEOUT * (RETRIES + 1) + 1
    while time.time() < r.last_answer + wait_time and r.active_count > 0 and time.time() < input_done + FORCED_TIMEOUT:
        r.select()

    print >>sys.stderr, "EXIT sent: {0} | recv: {1} | fail: {2} | active: {3}".format(r.sent_count, r.recv_count, r.error_count, r.active_count)
    return 0

if __name__ == '__main__':
    try: sys.exit(main())
    except KeyboardInterrupt: pass
