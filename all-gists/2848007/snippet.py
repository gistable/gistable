import sys
import time
from subprocess import Popen, PIPE

def magic_pypy(line, cell):
    cmd = ['pypy', '-c', cell]
    tic = time.time()
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    p.wait()
    toc = time.time()
    out,err = p.communicate()
    if err:
        print >> sys.stderr, err
    print out
    if '-t' in line:
        print "time: %.3fs" % (toc - tic)
    
get_ipython().register_magic_function(magic_pypy, 'cell', 'pypy')
