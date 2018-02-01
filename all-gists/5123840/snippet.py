#!/usr/bin/env python
"""
$ chmod +x player.py
$ python player.py /Users/user/Music/Directory
"""
import os
import subprocess
import sys

path = sys.argv[1]
files = os.listdir(path)

print("*** afplayer ***")
print("Loaded: {}, {} files".format(os.path.abspath(path), len(files)))

try:
    for filename in files:
        filepath = os.path.join(path, filename)
        print("Playing: {}".format(filepath))
        subprocess.Popen(['afplay', filepath]).communicate()
except KeyboardInterrupt:
    print('Exit')