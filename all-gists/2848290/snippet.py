import sys
import shlex
from subprocess import Popen, PIPE
from IPython.utils.py3compat import unicode_to_str

def shebang(line, cell):
    cmd = shlex.split(unicode_to_str(line))
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    out,err = p.communicate(cell)
    if err:
        print >> sys.stderr, err
    print out
    
get_ipython().register_magic_function(shebang, 'cell')

"""
From now, you can do:

%%shebang bash
uname -a
echo "foo $(hostname)"

"""