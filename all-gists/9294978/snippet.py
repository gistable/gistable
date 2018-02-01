#!/usr/bin/env python
"""
- read subprocess output without threads using Tkinter
- show the output in the GUI
- stop subprocess on a button press
"""
import logging
import os
import sys
from subprocess import Popen, PIPE, STDOUT

try:
    import Tkinter as tk
except ImportError: # Python 3
    import tkinter as tk

info = logging.getLogger(__name__).info

# define dummy subprocess to generate some output
cmd = [sys.executable or "python", "-u", "-c", """
import itertools, time

for i in itertools.count():
    print(i)
    time.sleep(0.5)
"""]

class ShowProcessOutputDemo:
    def __init__(self, root):
        """Start subprocess, make GUI widgets."""
        self.root = root

        # start subprocess
        self.proc = Popen(cmd, stdout=PIPE, stderr=STDOUT)

        # show subprocess' stdout in GUI
        self.root.createfilehandler(
            self.proc.stdout, tk.READABLE, self.read_output)
        self._var = tk.StringVar() # put subprocess output here
        tk.Label(root, textvariable=self._var).pack()

        # stop subprocess using a button
        tk.Button(root, text="Stop subprocess", command=self.stop).pack()

    def read_output(self, pipe, mask):
        """Read subprocess' output, pass it to the GUI."""
        data = os.read(pipe.fileno(), 1 << 20)
        if not data:  # clean up
            info("eof")
            self.root.deletefilehandler(self.proc.stdout)
            self.root.after(5000, self.stop) # stop in 5 seconds
            return
        info("got: %r", data)
        self._var.set(data.strip(b'\n').decode())

    def stop(self, stopping=[]):
        """Stop subprocess and quit GUI."""
        if stopping:
            return # avoid killing subprocess more than once
        stopping.append(True)

        info('stopping')
        self.proc.terminate() # tell the subprocess to exit

        # kill subprocess if it hasn't exited after a countdown
        def kill_after(countdown):
            if self.proc.poll() is None: # subprocess hasn't exited yet
                countdown -= 1
                if countdown < 0: # do kill
                    info('killing')
                    self.proc.kill() # more likely to kill on *nix
                else:
                    self.root.after(1000, kill_after, countdown)
                    return # continue countdown in a second

            self.proc.stdout.close()  # close fd
            self.proc.wait()          # wait for the subprocess' exit
            self.root.destroy()       # exit GUI
        kill_after(countdown=5)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
root = tk.Tk()
app = ShowProcessOutputDemo(root)
root.protocol("WM_DELETE_WINDOW", app.stop) # exit subprocess if GUI is closed
root.mainloop()
info('exited')
