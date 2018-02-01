#!/usr/bin/env python3

import sys
import os
import re
import subprocess

def get_files_subs(file):
  file = file.rstrip('\n')
  qfile = quote(file)
  process = os.popen("mkvmerge -i " + qfile)
  lines = process.readlines()
  process.close()
  for arg in lines:
    res = re.match("Track ID ([0-9]): subtitles.*", arg)
    if res:
      print("Subtitle track %s found." % res.groups()[0])
      extract_srt(file, res.groups()[0])
      subs = prase_srt(file + ".srt")
      create_vtt(subs, file + ".vtt")

def extract_srt(file, track_num):
  a = "mkvextract tracks " + quote(file) + " " + track_num + ":" + quote(file + ".srt")
  os.system(a)

def prase_srt(file):
  f=open(file,'r')
  subs = []
  for line in f.readlines():
    ##              subStart         time start                           time end                        
    res = re.match("Dialogue: [0-9],([^,]*),([^,]*),([^,]*),([^,]*),[^,]*,[^,]*,[^,]*,[^,.]*,(.*)", line)
    if res:
      subs.append(res.groups())
  return subs

def create_vtt(subs, file):
  content = 'WEBVTT\n\n';
  i = 0;
  for line in subs:
    start, end, what, actor, text = line
    content += "%i\n" % i
    content += "0%s0 --> 0%s0\n" % (start, end)
    content += "<v %s>%s\n" % (what + " " + actor, text.replace('\\N','\n'))
    content += "\n"
    i = i + 1;
  f=open(file, 'w')
  f.write(content)
  f.close()

_find_unsafe = re.compile(r'[^\w@%+=:,./-]', re.ASCII).search
 
def quote(s):
    """Return a shell-escaped version of the string *s*."""
    if not s:
        return "''"
    if _find_unsafe(s) is None:
        return s

    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + s.replace("'", "'\"'\"'") + "'"

if __name__ == '__main__':
  files = sys.argv[1:]
  if not files:
    files = sys.stdin.readlines();
  for file in files:
    get_files_subs(file)
   
