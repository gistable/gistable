# snippet is placed into public domain by
# anatoly techtonik <techtonik@gmail.com>

# http://stackoverflow.com/questions/8151300/ignore-case-in-glob-on-linux

import fnmatch
import os
import re

def findfiles(which, where='.'):
    '''Returns list of filenames from `where` path matched by 'which'
       shell pattern. Matching is case-insensitive.'''
    
    # TODO: recursive param with walk() filtering
    rule = re.compile(fnmatch.translate(which), re.IGNORECASE)
    return [name for name in os.listdir(where) if rule.match(name)]

# findfiles('*.ogg')