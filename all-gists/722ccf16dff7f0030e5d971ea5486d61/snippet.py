#!/usr/bin/python3

"""
The idea is to take stdin, and write it to a new unique log file

php myscript.php | newlog filename
"""

import os
import sys
import datetime
import time

# Logs go to example /home/richard/logs
logdir = os.path.expanduser('~/logs')

# Set timezone for filename
os.environ['TZ'] = 'America/Los_Angeles'
time.tzset()

def parse_stream():
  now = datetime.datetime.now()
  filename = now.strftime("%Y-%m-%d_%I_%M_%p")
  if len(sys.argv) > 1:
    filename = filename + '_' + sys.argv[1]
  filename = logdir + '/' + filename + '.log'

  with open(filename, 'w') as outfile:
    for line in sys.stdin:
      print(line, end="")
      outfile.write(line)

  print(filename)
      
if __name__ == '__main__':
  parse_stream()