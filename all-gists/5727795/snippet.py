#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    Example app using bottle and multiprocessing for queuing long jobs
    and using several workers.
"""

from multiprocessing import Process, Queue, cpu_count
from bottle import Bottle, run
import time

app = Bottle()
app.queue = Queue()
app.nb_workers = cpu_count()


def do_long_stuff(msg):
    print ">> Long stuff to do with :", msg
    time.sleep(3)
    print "<< Long stuff done with :", msg


def pull_msgs(queue):
    while True:
        msg = queue.get()
        if msg is None:
            break
        do_long_stuff(msg)


@app.route('/')
def index():
    return 'Hello !'


@app.route('/add/<msg>')
def add_message_to_queue(msg):
    app.queue.put(msg)
    return 'Hello ' + msg


@app.route('/exit')
def end(msg):
    for i in xrange(app.nb_workers):
        app.queue.put(None)


def main():
    for i in xrange(app.nb_workers):
        msg_puller_process = Process(target=pull_msgs, args=[app.queue])
        msg_puller_process.start()
    run(app, host='localhost', port=8080)


if __name__ == '__main__':
    main()
