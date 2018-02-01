'''
Save this file and add the following line to your ~/.bashrc"

export PYTHONSTARTUP="$HOME/.pythonrc"
'''
import os
import readline
import rlcompleter
import atexit

history_file = os.path.join(os.environ['HOME'], '.python_history')
try:
    readline.read_history_file(history_file)
except IOError:
    pass
readline.parse_and_bind("tab: complete")
readline.set_history_length(1000)
atexit.register(readline.write_history_file, history_file)

del readline, rlcompleter, atexit, history_file


# In addition to os, import some useful things:
import re
from collections import *
from itertools import *
