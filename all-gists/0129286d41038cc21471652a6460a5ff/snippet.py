import memcache
import signal
import sys
import shutil
import os
import threading
import time

mc = memcache.Client(['127.0.0.1:5551'], debug=0)
cwd = os.getcwd()
error = 0
processed = 0

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print("Ctrl-C exits")

def create_files():
    for fname in range(1,11):
        touch(str(fname) + ".txt")

def move_files_get_set():
    global error
    global processed
    files = [file for file in os.listdir(".") if file.endswith(".txt")]
    for file in files:
        if os.path.isfile(file) and not mc.get(file):
            processed = processed + 1 
            mc.set(file, int(round(time.time() * 1000)))
            try:
                shutil.move(os.path.join(cwd, file), os.path.join(cwd, "archive", "%s" % file))
            except Exception as e:
                print(e)
                processed = processed - 1
                error = error + 1
                print("%s errors happened with %s" % (error, processed))
            mc.set(file, None)

def move_files_add():
    global error
    global processed
    files = [file for file in os.listdir(".") if file.endswith(".txt")]
    for file in files:
        if os.path.isfile(file) and mc.add(file, int(round(time.time() * 1000))):
            processed = processed + 1 
            try:
                shutil.move(os.path.join(cwd, file), os.path.join(cwd, "archive", "%s" % file))
            except Exception as e:
                print(e)
                processed = processed - 1
                error = error + 1
                print("%s errors happened with %s" % (error, processed))
            mc.set(file, None)

class myThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        print "Starting " + self.name
        move_files_get_set()
        print "Exiting " + self.name

def trigger():
    while True:
        create_files()
        t1 = myThread("1", "Thread 1", "1")
        t2 = myThread("2", "Thread 2", "2")
        t1.start()
        t2.start()
        t1.join()
        t2.join(