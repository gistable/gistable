# Don't use this.
import zmq
import os

class Worker:
    def __init__(self):
        print "parent: %d, pid: %d" % (os.getppid(), os.getpid())
        self.pid = os.getppid()
        self.context = zmq.Context()
        self.sub = self.context.socket(zmq.SUB)
        self.sub.connect("ipc://workers-" + str(self.pid))
        self.sub.setsockopt(zmq.SUBSCRIBE, "")
        self.running = True

    def run(self):
        print 'A new worker ', os.getpid()
        while True:
            msg = self.sub.recv()
            print "Worker: " + msg
            if msg == 'quit':
                self.stop()
            if not self.running:
                break
        self.sub.close()
        self.context.destroy()
        os._exit(0)

    def stop(self):
        self.running = False

class Master:
    def __init__(self):
        self.pid = os.getpid()
        self.context = zmq.Context()
        self.rep = self.context.socket(zmq.REP)
        self.pub = self.context.socket(zmq.PUB)
        self.rep.bind("ipc://master-" + str(self.pid))
        self.pub.bind("ipc://workers-" + str(self.pid))
        self.workers = []

    def run(self):
        print 'A new master ', os.getpid()
        while True:
            lst = self.rep.recv_multipart()
            print "Master: " + ", ".join(lst)
            if lst[0] == 'fork':
                self.fork()
                self.rep.send("ok: " + str(self.workers))
            elif lst[0] == 'workers':
                self.rep.send("ok: " + str(self.workers))
            elif lst[0] == 'quit_workers':
                self.quit_workers()
            else:
                self.rep.send("invalid")

    def quit_workers(self):
        self.pub.send("quit")
        self.rep.send("OK")

    def fork(self):
        newpid = os.fork()
        if newpid == 0:
            worker = Worker()
            worker.run()
        else:
            self.workers.append(newpid)

master = Master()
master.run()
