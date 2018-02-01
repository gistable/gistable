#!/usr/bin/python3
import os, time, shutil, sys

dir = sys.argv[1]
os.chdir(dir)
for f in os.listdir('.'):
    ftime = time.gmtime(os.path.getmtime(f))
    ctime_dir = str(ftime.tm_year) '-' str(ftime.tm_mon) '-' str(ftime.tm_mday)
    if not os.path.isdir(ctime_dir):
        os.mkdir(ctime_dir)
    dst = ctime_dir '/' f
    shutil.move(f, dst);
    print('File' f 'has been moved to' dst)