import subprocess
import time
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        exit("need an argument")
    to_run = sys.argv[1]
    proc = subprocess.Popen(to_run)
    print "start process with pid %s" % proc.pid
    time.sleep(50)
    # kill after 50 seconds if process didn't finish
    if proc.poll() is None:
        print "Killing process %s with pid %s " % (to_run,proc.pid)
        proc.kill()