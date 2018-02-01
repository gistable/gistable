#!/usr/bin/python
"""
Python script for automated compilation of .less files

Author: Jesse the Game 

Usage: python autolessc.py <infile> <outfile>

Parse infile for dependencies, then compile less code into the outfile.
From then on, the script periodically check for modifications on dependencies
and recompile when necessary. On error, display it's message but keep running.
"""

import os
import sys
import re
import time
import datetime
import subprocess

class chdir_stack(object):
    """
    Remember current directory, move to a new one, do something,
    then return to the old.
    """
    def __init__(self, path):
        self.target = path
    def __enter__(self):
        self.orig = os.getcwd()
        os.chdir(self.target)
    def __exit__(self, type, value, traceback):
        os.chdir(self.orig)

def parse_imports(less):
    """
    Return a list of all imported paths in given less string
    """
    #TODO: Ignore '/* */' commented sections
    pattern = re.compile(r"""
            ^                                # Don't allow leading characters
            \s*                         
            @import                     
            \s*                         
            ("(?:[^"\\]*(?:\\.[^"\\]*)*)"    # Double quoted string
            |'(?:[^'\\]*(?:\\.[^'\\]*)*)')   # Single quoted string
            \s*                         
            ;                                """,
            re.VERBOSE | re.MULTILINE)
    # Strip quotes from the string
    return [match[1:-1] for match in pattern.findall(less)]
    

# A global dict containing the timestamps of dependency files
WATCHLIST = dict()

def parse(path, is_less=True):
    """
    Add a file, and all files imported by that file to the global
    watchlist.
    """
    path = os.path.realpath(path)

    if path in WATCHLIST:
        return 

    WATCHLIST[path] = None

    if not is_less:
        return 

    with open(path, 'r') as f:
        imports = parse_imports(f.read())

    with chdir_stack(os.path.dirname(path)):
        for rel in imports:
            # Add .css files to watchlist, but don't parse them
            if rel.endswith('.css'):
                file(rel, False)
                continue
            # Append '.less' to paths without that extension
            elif not rel.endswith('.less'):
                rel += '.less' 
            parse(rel)

def dict_diff(d1, d2):
    return dict(set(d1.iteritems()) - set(d2.iteritems()))

def lessc(infile, outfile):
    """
    Compile infile into outfile.
    Errors are reported but don't break the loop.
    """
    print '[%s]' % str(datetime.datetime.now())[:-7],
    try:
        output = subprocess.check_output(['lessc', infile])
    except subprocess.CalledProcessError:
        print 'ERROR'
    else:
        with open(outfile, 'w') as f:
            f.write(output)
        print 'lessc %s > %s' % (os.path.relpath(infile),
                                 os.path.relpath(outfile))

def check_files_modified():
    """
    Return a dict of path, timestamp pairs of all files
    that were modified since last check.
    """
    global WATCHLIST
    snapshot = dict(((path, os.stat(path).st_mtime) for path in WATCHLIST))
    diff = dict_diff(WATCHLIST, snapshot)
    WATCHLIST = snapshot
    return diff

def main():
    #TODO: parameters like --interval
    try:
        infile = os.path.realpath(sys.argv[1])
        outfile = os.path.realpath(sys.argv[2])
    except IndexError:
        exit("Usage: python autolessc <infile> <outfile>")

    parse(infile)

    print 32 * "=" + "[Less do this!]" + "=" * 32
    while 1:
        try:
            if check_files_modified():
                lessc(infile, outfile)
                parse(infile)
            time.sleep(1)
        except KeyboardInterrupt:
            break

    print 39 * "^C"
    print 32 * "=" + "[My plessure!!]" + "="  * 32


if __name__ == '__main__':
    main()

