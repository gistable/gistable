import os
import pty

pair = pty.fork()
if not pair[0]:
    os.execvp('python', ['python'])

s = os.fdopen(pair[1], 'w+')

while True:
    c = s.read(1)
    if c == '>':
        c = s.read(1)
        if c == '>':
            c = s.read(1)
            if c == '>':
                break

s.write('1 + 1\r\n')
assert s.readline().strip() == '1 + 1'

print s.readline()
