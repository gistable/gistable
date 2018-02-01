#Call this inside ~/.ipython/ipy_user_conf.py main()

import sys
import subprocess
from os import environ

if 'VIRTUAL_ENV' in environ:
    #This is kludgy but it works; grab the right sys.path from the virtualenv python install:
    path = subprocess.Popen(['python', '-c','import sys;print(repr(sys.path))'],
                            stdout=subprocess.PIPE).communicate()[0]
    sys.path = eval(path)
    del path

del sys, subprocess, environ