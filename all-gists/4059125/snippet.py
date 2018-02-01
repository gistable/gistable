#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime
import time
import os
from stat import *
import commands

def watch(dir, command):
    timestamp = time.mktime(datetime.datetime.now().utctimetuple())
    while True:
        for file in  os.listdir(dir):
            # 隠しファイルは無視
            if 0 is file.find('.'):
                continue
            file_timestamp = os.stat(file)[ST_MTIME]
            if timestamp < file_timestamp:
                timestamp = file_timestamp
                print(commands.getoutput(command))
                break
        # 100ミリ秒待機
        time.sleep(0.1)

def help():
    print(u'第一引数が監視対象のディレクトリです．')
    print(u'第二匹数が監視下のファイルに変更があった場合に実行するコマンドです．')
    print(u'例: % dirwatch . \'echo "hello"\'')
    print(u'例ではカレントディレクトリ内のファイルに変更があった場合にhelloと表示します．')

if __name__ == '__main__':
    # 引数足りない場合にヘルプを表示する．
    if 3 > len(sys.argv):
        help()
    else:
        watch(sys.argv[1], sys.argv[2])
