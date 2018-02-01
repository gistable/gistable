""" USEAGE: xclip -o | python chrome_xxd.py | xxd -r - [destination]
To access chrome's cache, go to about:cache in the address bar.
Make sure you copy the second section of the hex dump (the first section is the header).
"""

import sys
for line in sys.stdin.readlines():
  sys.stdout.write(line[1:].replace("  ", " "))