#!/usr/bin/env python
# coding: utf-8
import os
import time
import zmq


name = "main"
#endpoint = "ipc://test-pub-sub-double-bind.ipc"
endpoint = "tcp://127.0.0.1:5004"


def log(s, **kw):
    print ("{name}> " + s).format(name=name, **kw)


def publisher():
    time.sleep(1)
    log("started")
    ctx = zmq.Context()
    sock = ctx.socket(zmq.PUB)
    sock.connect(endpoint)
    time.sleep(1)
    sock.send("test from " + name)
    log("sent")
    return 0


def subscriber():
    time.sleep(1)
    log("started")
    ctx = zmq.Context()
    sock = ctx.socket(zmq.SUB)
    sock.connect(endpoint)
    sock.setsockopt(zmq.SUBSCRIBE, "")
    # Expect one message from each publisher.
    for _ in range(2):
        events = sock.poll(timeout=3000)
        if events:
            msg = sock.recv()
            log("received: " + msg)
        else:
            log("no messages in 3 seconds")
            return 1
    return 0


def main():
    global name

    if os.fork() == 0:
        name = "pub1"
        return publisher()
    if os.fork() == 0:
        name = "pub2"
        return publisher()
    if os.fork() == 0:
        name = "sub1"
        return subscriber()
    if os.fork() == 0:
        name = "sub2"
        return subscriber()

    ctx = zmq.Context()
    sock = ctx.socket(zmq.PUB) # or SUB - does not make any difference
    sock.bind(endpoint)

    exit_codes = [os.wait3(0)[1] for _ in range(4)]
    if any(exit_codes):
        log("TEST FAIL: some child processes returned non-zero")
        return 1

    log("TEST PASS")
    return 0

if __name__ == "__main__":
    exit(main())