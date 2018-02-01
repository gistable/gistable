#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   zhangxiaolin
#   E-mail  :   petelin1120@gmail.com
#   Date    :   16/11/3 16:03
#   Desc    :   ...
import queue
from queue import Queue
import socket
import select
from collections import defaultdict
import heapq
import datetime
import types


class Task(object):
    task_count = 0

    def __init__(self, target):
        """
        :param target: 一个协程.
        """
        Task.task_count += 1
        self.tid = Task.task_count
        self.target = target
        self.sendval = None

    def run(self):
        return self.target.send(self.sendval)

    def kill(self):
        self.target.close()

    def __repr__(self):
        return 'task %s, %s' % (self.tid, str(self.target))


class Sleeper(Task):
    def __init__(self, seconds):
        now = datetime.datetime.now()
        self.sec = seconds
        self.wait = now + datetime.timedelta(seconds=seconds)
        self.stop = False

    def __repr__(self):
        return 'Sleeper <{}><{}>'.format(self.sec, self.wait)

    def run(self):
        self.stop = True
        now = datetime.datetime.now()
        self.result = now
        return now

    def __iter__(self):
        while not self.stop:
            yield self
        return self.result

    def __lt__(self, other):
        return self.wait < other.wait

    def __le__(self, other):
        if self.wait < other.wait:
            return True
        return self.__eq__(other)

    def __ge__(self, other):
        if self.wait > other.wait:
            return True
        return self.__eq__(other)

    def __eq__(self, other):
        return self.wait == other.wait


## system call
class SystemCall(object):
    def handle(self, scheduler, task):
        pass


class SystemSleeper(SystemCall):
    def __init__(self, t):
        self.sleeper = Sleeper(t)

    def handle(self, scheduler, task):
        heapq.heappush(scheduler.sleepqueue, (self.sleeper, task))


class GETPID(SystemCall):
    def handle(self, s, t):
        t.sendval = t.tid
        s.schedu(t)


class FORK(SystemCall):
    def __init__(self, target):
        self.target = target

    def handle(self, scheduler, task):
        new_task = scheduler.new(self.target)
        # 设置用户task,得到系统创建出来的task的id
        task.sendval = new_task.tid
        scheduler.schedu(task)


class KILL(SystemCall):
    def __init__(self, tid):
        self.tid = tid

    def handle(self, scheduler, task):
        kt = scheduler.runmap.get(self.tid, None)
        if kt:
            kt.kill()
            task.sendval = True
        else:
            task.sendval = False


class WAIT(SystemCall):
    def __init__(self, tid):
        self.tid = tid

    def handle(self, scheduler, current_tas):
        scheduler.add_to_wait(self.tid, current_tas.tid)


class READ(SystemCall):
    def __init__(self, connect):
        self.connect = connect

    def handle(self, scheduler, task):
        scheduler.add_to_read(self.connect, task)


class WRITE(SystemCall):
    def __init__(self, connect):
        self.connect = connect

    def handle(self, scheduler, task):
        scheduler.add_to_write(self.connect, task)


class Scheduler(object):
    def __init__(self):
        self.ready = Queue()
        self.runmap = {}
        self.waitmap = defaultdict(list)
        self.write_wait = {}
        self.read_wait = {}
        self.sleepqueue = []

    def new(self, target):
        """target is a generator"""
        t = Task(target)
        self.runmap[t.tid] = t
        self.schedu(t)
        return t

    def schedu(self, task):
        self.ready.put(task)

    def exit(self, task):
        print("--*- tid:{tid}, {t} exit-*--".format(tid=task.tid, t=task.target.__name__))
        del self.runmap[task.tid]
        if task.tid in self.waitmap:
            for task in self.waitmap[task.tid]:
                self.runmap[task.tid] = task
                task.sendval = True
                self.schedu(task)

    def add_to_wait(self, run_tid, wait_tid):
        return self.waitmap[run_tid].append(self.runmap.pop(wait_tid))

    def add_to_read(self, connect, task):
        self.read_wait[connect] = task

    def add_to_write(self, connect, task):
        self.write_wait[connect] = task

    def ioloop(self):
        if self.read_wait or self.write_wait:
            rs, ws, e = select.select(self.read_wait.keys(), self.write_wait.keys(), [], 0)
            for r in rs:
                self.schedu(self.read_wait.pop(r))
            for w in ws:
                self.schedu(self.write_wait.pop(w))

    def sleeploop(self):
        while self.sleepqueue:
            sleeper, task = self.sleepqueue[0]
            now = datetime.datetime.now()
            if now < sleeper.wait:
                break
            self.sleepqueue.pop(0)
            task.sendval = datetime.datetime.now()
            self.schedu(task)

    def loop(self):
        while self.runmap or self.sleepqueue:
            self.ioloop()
            self.sleeploop()
            try:
                t = self.ready.get_nowait()
                result = t.run()
                if isinstance(result, SystemCall):
                    result.handle(self, t)
                    continue
            except queue.Empty:
                pass
            except StopIteration as e:
                self.exit(t)
            except Exception as e:
                print(e)
            else:
                self.schedu(t)


@types.coroutine
def sleep(t):
    result = yield SystemSleeper(t)
    return result
    # sper = Sleeper(t)
    # heapq.heappush(s.sleepqueue, sper)
    # result = (yield from sper)
    # return result


def foo():
    pid = yield GETPID()
    sid = yield FORK(bar)
    for i in range(1):
        print("part foo: %d" % pid)
        yield
    a = yield KILL(sid)
    print(a)


def bar():
    pid = yield GETPID()
    for i in range(100):
        print("part bar: %d" % pid)
        yield


def child():
    pid = yield GETPID()
    for i in range(10):
        print("i am child: %d" % pid)
        yield


def father():
    cid = yield FORK(child)
    print("wait for child")
    yield WAIT(cid)
    print("child done")


def server(port):
    print("start server at ", port)
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("", port))
    srv.listen(5)
    while True:
        result = yield READ(srv)
        client, addr = srv.accept()
        result = yield FORK(handle_client(client, addr))
        print("fork result", result)


def handle_client(client, addr):
    print("Connection from", addr)
    yield READ(client)
    # print(client.getpeername(), "\t接受数据")
    # data = client.recv(65536)
    # if not data:
    #     break
    yield from sleep(2)
    from web import servicess
    yield WRITE(client)
    servicess.send(client, False)
    client.close()


def heartbeat(t, sysmbol='.'):
    print('heartbeat')
    while 1:
        # 这个sleep的时候确实阻塞的只是通过yield暂时交出了执行权利.
        result = yield from sleep(t)
        print(result)
        # print(result, end=' ')
        print(sysmbol, end='\n')
        # import sys
        # sys.stdout.flush()


s = Scheduler()
# 因为 new 里面的东西是一个iter...所以呢, 并不会被直接执行
s.new(heartbeat(1, '-'))
# s.new(heartbeat(1.5, '+'))
# s.new(server(8080))
s.loop()
