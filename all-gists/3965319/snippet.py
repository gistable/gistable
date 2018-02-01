#!/usr/bin/env python

import sys, os, termios, select

TIMEOUT=2

stdin_fileno = sys.stdin.fileno()
backup = termios.tcgetattr(stdin_fileno)
new = termios.tcgetattr(stdin_fileno)
new[3] = new[3] &~ (termios.ECHO | termios.ICANON)
termios.tcsetattr(stdin_fileno, termios.TCSANOW, new)
try:
    rfds = [stdin_fileno]
    wfds = []
    xfds = []
    
    sys.stdout.write("\x1b[c")
    sys.stdout.flush()
    
    rfd, wfd, xfd = select.select(rfds, wfds, xfds, TIMEOUT)
    if rfd:
        data = os.read(stdin_fileno, 1024)
        print "reply: ESC %s" % data[1:]
finally:
    termios.tcsetattr(stdin_fileno, termios.TCSANOW, backup)

