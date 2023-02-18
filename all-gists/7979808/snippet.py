from subprocess import Popen, PIPE
import pty
import os
from select import select
import sys
import tty

main, subordinate = pty.openpty()
p = Popen(['python'], stdin=subordinate, stdout=PIPE, stderr=PIPE)
pin = os.fdopen(main, 'w')
tty.setcbreak(sys.stdin)

msg = ''
errmsg = ''

while True:
    rs, ws, es = select([sys.stdin, p.stdout, p.stderr], [], [])
    for r in rs:
        if r is sys.stdin:
            c = r.read(1)
            if c == '':
                msg = msg[:-1]
            elif c == '\n':
                pin.write(msg+'\n')
                print '\r>>> %s' % msg
                msg = ''
            else:
                msg += c
                print '\r    '+ ' '*(len(msg)+1),
                print '\r>>> %s' % msg,
                sys.stdout.flush()
        elif r is p.stdout:
            print p.stdout.readline(),
            sys.stderr.flush()
        elif r is p.stderr:
            errmsg += p.stderr.read(1)
            if errmsg.endswith('>>> '):
                errmsg = errmsg[:-4]
            if errmsg.endswith('\n'):
                print 'ERR~%s' % (errmsg,),
                errmsg = ''
