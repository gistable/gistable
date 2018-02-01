print 'maya.py is running!'

print 'importing pymel.core'

from pymel.core import *

import sys
sys.path.append('c:\\py')

def get (file):
  file=str(file)
	return 'c:/py/maya_scripts/'+file+'.py'

print 'embedding ipython'

import pyreadline

import IPython
IPython.embed()