"""
A trivial utility that I needed and you might find useful. 

It reads lines from STDIN and writes them to STDOUT. But if the line
it sees is the same as the last line it saw, rather than writing a fresh
line it updates a counter at the end of the current line.

So e.g. 

echo -e 'foo\nfoor\nbar' | python linecounter.py 

will give the output:

foo (2)
bar

Importantly this happens on a line by line basis, so if you've got something
spewing lots of duplicated crap to stdout then this will turn it into
an updating counter instead of a buffer full of nonsense.
"""


import sys

last_l = None
counter = 0

while True:
    l = sys.stdin.readline()
    if not l: break
    if l[-1] == '\n': l = l[0:-1]
    if l == last_l:
        sys.stdout.write("\r")
        sys.stdout.write(l)
        counter += 1
        sys.stdout.write(" (%s)" % counter)
    else:
        if last_l != None: sys.stdout.write("\n")
        counter = 0
        last_l = l
        sys.stdout.write(l)
        
    sys.stdout.flush()
