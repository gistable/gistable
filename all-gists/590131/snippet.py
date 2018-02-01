#! /usr/bin/env python
 
from os import fork, chdir, setsid, umask
from sys import exit
 
def main():
  while 1:
    #main daemon process loop
 
# Dual fork hack to make process run as a daemon
if __name__ == "__main__":
  try:
    pid = fork()
    if pid > 0:
      exit(0)
  except OSError, e:
    exit(1)
 
  chdir("/")
  setsid()
  umask(0)
 
  try:
    pid = fork()
    if pid > 0:
      exit(0)
  except OSError, e:
    exit(1)
 
  main()