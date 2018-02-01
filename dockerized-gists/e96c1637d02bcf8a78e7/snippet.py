#!/usr/bin/env python

# File: log_exec.py
# Author: McKay Davis
# Date: Jun 23, 2014
# Non-blocking stdout and stderr read from a
# Popen process

import os
import subprocess
import select

def log_exec(args, env = None, log = None):
  '''
  execute command and log process stdout and stderr
  to file-object 'log' while simultaneously logging to stdout
  '''
  exec_env = {}
  exec_env.update(os.environ)

  # copy the OS environment into our local environment
  if env is not None:
    exec_env.update(env)

  # create a pipe to receive stdout and stderr from process
  (pipe_r, pipe_w) = os.pipe()

  p = subprocess.Popen(args,
                       shell = False,
                       env = exec_env,
                       stdout = pipe_w,
                       stderr = pipe_w)

  # Loop while the process is executing
  while p.poll() is None:
    # Loop long as the selct mechanism indicates there
    # is data to be read from the buffer
    while len(select.select([pipe_r], [], [], 0)[0]) == 1:
      # Read up to a 1 KB chunk of data
      buf = os.read(pipe_r, 1024)
      # Stream data to our stdout's fd of 0
      os.write(0, buf)
      if log is not None:
        log.write(buf)

  # cleanup
  os.close(pipe_r)
  os.close(pipe_w)

  # return the result of the process
  return p.returncode


# Test by running 'log_exec.py log.txt <cmd>'
if __name__ == "__main__":
  import sys
  log_exec(sys.argv[2:], log=open(sys.argv[1], "wb"))
