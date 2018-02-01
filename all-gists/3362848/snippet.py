#!/usr/bin/env python

import os
import re

os.system('git reset --hard HEAD')
os.system('git clean -fdx')

REs = [
  r'''\s+\*\n\s+\* @author[^\n]*''',
  r'''\s+-\s*\n\s+- @author[^\n]*''',
  r'''\s+- @author[^\n]*''',
  r'''\s+\* @author[^\n]*''',
  r'''\n/\*\* @author[^\n]*\*/''',
]

def authors():
  (stdin, stdout, stderr) = os.popen3('\grep -lrs "@author"')
  return stdout.read().split()

for RE in REs:
  for f in authors():
    with open(f) as infile:
      incontent = infile.read()
    outcontent = re.sub(RE, '', incontent, re.M)
    if (incontent != outcontent):
      with open(f, 'w') as outfile:
        outfile.write(outcontent)

remain = authors()
print(str(len(remain)) + " holdouts...")
if len(remain) > 0:
  print("Next victim: " + remain[0])
