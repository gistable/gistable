#!/usr/bin/env python

""" A pre-commit git hook that gunzips the .als file and adds the resulting xml file to the git staging index.  

Caveat:
   It doesn't work perfectly to do a `git add` in a pre-commit hook - if nothing else in the repo has changed, 
the pre-commit won't even be fired so nothing happens.  If something else has changed, the pre-commit hook 
doesn't get fired in time for the files it creates to show up in the list of files to be committed but the 
files it creates do actually go into the commit.  So it works, but that's kind of weird.

   In any case it's probably better to just run this manually before committing.
"""

import os
import sys
import subprocess
import gzip

ABLETON_FILE_EXT = '.als'
CONVERTED_XML_EXT = ABLETON_FILE_EXT + '.xml'

###
### find path to the root project directory
###
try:
    _GIT_DIR = subprocess.check_output(['git', 'rev-parse', '--git-dir']).rstrip('\n').rstrip('\r') # returns the .git dir
except subprocess.CalledProcessError:
    # if not in a git repository, do nothing
    exit(0)
ROOT_DIR = os.path.join(_GIT_DIR, '../') # got one directory up 

###
### Convert live sets to xml files
###
converted_files = []
for filepath in filter(lambda x: x.endswith(ABLETON_FILE_EXT), os.listdir(ROOT_DIR)):
    outfile = filepath.rstrip(ABLETON_FILE_EXT) + CONVERTED_XML_EXT
    outpath = os.path.join(ROOT_DIR, outfile)
    #print "outfile :%s" % (outfile,)
    with gzip.open(filepath, 'r') as f_als:
        with open(outpath, 'w') as f_xml:
            f_xml.write(f_als.read())
            print "als file converted to xml: %s" % (outfile,)
    converted_files.append((outpath, outfile))

###
### uncomment to add all newly created xml files to the git index
###
#for file_tuple in converted_files:
#    result = subprocess.call(['git', 'update-index', '--add', file_tuple[0]])
#    if result == 0:
#        print "changes to %s were added to the git index" % (file_tuple[1],)
#    else:
#        print "ERROR: file %s not added to the git index" % (file_tuple[1],)
sys.exit(0)