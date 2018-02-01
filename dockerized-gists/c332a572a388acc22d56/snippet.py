#!/usr/bin/env python

""" Converts a directory full of .eml files to a single Unix "mbox" file.

Accepts as input either an individual .eml file or a directory containing one
or more .eml files.

The output mbox will be created if it doesn't already exist.  If it exists,
it will be appended to.  There is no checking for duplicates, so use caution.
If duplicate filtering is desired, it could be added to addFileToMbox().
Inspired by http://www.cosmicsoft.net/emlxconvert.html

Usage:
$ ./emlToMbox.py inputdir/ output.mbox
$ ./emlToMbox.py input.eml output.mbox

Requires Python 2.5 or later

STATUS:  Tested and appears to work.
"""

import os
import sys
import mailbox

global debug
debug = True

def main( arguments ):
    infile_name = arguments[1]
    dest_name = arguments[2]
    
    if debug:
        print "Input is:  " + infile_name
        print "Output is: " + dest_name
    
    dest_mbox = mailbox.mbox(dest_name, create=True) # if dest doesn't exist create it
    dest_mbox.lock() # lock the mbox file
    
    if os.path.isdir(infile_name):
        if debug:
            print "Detected directory as input, using directory mode"
        count = 0
        for filename in os.listdir(infile_name):
            if filename.split('.')[-1] == "eml":
                try:
                    fi = open(os.path.join(infile_name, filename), 'r')
                except:
                    sys.stderr.write("Error while opening " + filename + "\n")
                    dest_mbox.close()
                    raise
                addFileToMbox( fi, dest_mbox )
                count += 1
                fi.close()
        if debug:
            print "Processed " + str(count) + " total files."
    
    if infile_name.split('.')[-1] == "eml":
        if debug:
            print "Detected .eml file as input, using single file mode"
        try:
            fi = open(infile_name, 'r')
        except:
            sys.stderr.write("Error while opening " + infile_name + "\n")
            dest_mbox.close()
            raise
        addFileToMbox( fi, dest_mbox )
        fi.close()
    
    dest_mbox.close() # close/unlock the mbox file
    return 0

def addFileToMbox( fi, dest_mbox ):
    # Any additional preprocessing logic goes here, e.g. duplicate filter
    try:
        dest_mbox.add( fi )
    except:
        dest_mbox.close()
        raise

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write("Usage: ./emlToMbox.py input outbox.mbox\n")
        sys.exit(1)
    sys.exit( main( sys.argv ) )
