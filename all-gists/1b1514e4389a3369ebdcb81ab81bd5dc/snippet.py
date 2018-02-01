import os, sys
from time import sleep

## We could update this to all files in all subdirectories
watching = [__file__]
watched_mtimes = [(f, os.path.getmtime(f)) for f in watching]

while True:
    print("Idle...")
    sleep(2) ## So not to kill our CPU cycles
    for f, mtime in watched_mtimes:
        if os.path.getmtime(f) != mtime:
            print("SOmehtign changed sucka reloading and exploding!!")
            os.execv(sys.executable, ['python'] + sys.argv)