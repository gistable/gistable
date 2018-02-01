'''
Created on May 8, 2013

@author: Victor J. Reventos

Copies the preferences from the src workspace to the dest workspace.
If the dest  workspace doesn't exist it will be created.
Enjoy!
'''

import sys,os
from distutils.dir_util import copy_tree

if len(sys.argv) <3:
    print 'Usage: <src workspace to copy settings from> <dest workspace>'

PATH = os.path.join(".metadata",".plugins","org.eclipse.core.runtime")
args = map(lambda p: os.path.join(p.strip(),PATH),sys.argv[1:])
copy_tree(args[0], args[1])