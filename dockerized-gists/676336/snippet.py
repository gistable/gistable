#!/course/cs053/bin/python3
import os, time
import sys

"""
reruns the given file whenever it changes. 
usage: python3 run.py myfile.py
"""

def stat(f):
  return os.stat(f).st_mtime

def monitor(f):
  a = stat(f)
  while True:
    time.sleep(1.0)
    b = stat(f)
    if a != b:
      a = b
      run(f)
      
def run(f):
  os.system('python3 '+f)

if __name__ == '__main__':


  if len(sys.argv) != 2:
    print("ERROR: Specify a file to watch!")
    print('args:',sys.argv)
    sys.exit()
  
  f = sys.argv[1]
  print('\nrunning and will rerun on change: ',f,'\n')
  run(f)
  monitor(f)