#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
import subprocess
from threading import Thread
import signal

def getPath(dir, prefix = None):
    files = sorted(filter(lambda f: os.path.isfile(dir + f), os.listdir(dir)))
    if None != prefix:
        files = filter(lambda f: f.startswith(prefix), files)
    return dir + files[-1]

class Tailer:
    proc = None

    def __call__(self, path):
        self.proc = subprocess.Popen('tail -f ' + path, shell=True)

argv = sys.argv
if 1 == len(argv):
    print(u'第一引数に監視対象のディレクトリを指定してください')
    print(u'第二引数にファイルの接頭語を指定することが任意でできます')
    sys.exit()
dir = argv[1] if '/' == argv[1][-1] else argv[1] + '/'
prefix = None if 3 != len(argv) else argv[2]
print('watching: ' + dir)
last = ''
tailer = None
while(True):
    path = getPath(dir, prefix)
    if path != last:
        print path
        if None != tailer:
            os.kill(tailer.proc.pid, signal.SIGUSR1)
        last = path
        tailer = Tailer()
        thread = Thread(target=tailer, args=(path, ))
        thread.start()
    time.sleep(1)
