#!/usr/bin/env python
import sys
import subprocess
import tempfile
import time

# Emacs is in the Cellar, installed by Homebrew
emacspath="/usr/local/Cellar/emacs/24.3/Emacs.app/Contents/MacOS/Emacs"

def run(cmd, args):
    args[:0] = [cmd]
    subprocess.call(args)
 
wait_for_exit = False
interactive = False
args = []

for arg in sys.argv[1:]:
    if arg == "-w" or arg == "--wait":
        wait_for_exit = True
    elif arg == "-h" or arg == "--help":
        run(emacspath, ["--help"])
        print """

Emacs wrapper options:

--wait, -w           wait for emacs to finish
-                    read standard input into a new buffer

"""
        sys.exit()
    elif arg == "-":
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            tmpfile.write(sys.stdin.read())
            args.append(tmpfile.name)
    elif arg == "-nw":
        interactive = True
    else:
        args.append(arg)

if interactive:
    args.append("-nw")
    ret = run(emacspath, args)
    sys.exit(ret)
 
# spawn off an emacs process
args[:0] = [emacspath]
emacs_process = subprocess.Popen(args, stdout=None, stderr=None)

# Wait for the emacs window to become active so we can mess with it
time.sleep(1)
 
# Execute some applescript to make emacs activate
run("osascript", ["-e",  "tell application \"Emacs\" to activate"])
 
if wait_for_exit:
    # Wait for it if we need to
    emacs_process.wait()
