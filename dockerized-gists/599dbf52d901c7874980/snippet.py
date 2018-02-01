'''
Python scanner for first line eval() based infection on php script (ex: Wordpress infection)
Information: http://somewebgeek.com/2014/wordpress-remote-code-execution-base64_decode/
hugokernel, 09/2014

Usage:
python scan.py directory
'''

import sys
import os

VARIANT = 'PCT4BA6ODSE'

# Remove file if empty after patch
REMOVE_IF_EMPTY = True

def patch(filename):
    with open(filename, 'r+') as f:
        lines = f.readlines()
        lines[0] = '<?php'
        f.seek(0)
        f.write(str(''.join(lines)).strip())
        f.truncate()

def scan(directory):
    
    for item in os.listdir(directory):
        line = os.path.join(directory, item)
        if os.path.isdir(line):
            scan(line)
        else:
            if item.split('.')[-1] == 'php':
                with open(line, "rb") as f:
                    first = f.readline()
                    if 'eval' in first:
                        print 'Found in %s' % line,
                        if VARIANT:
                            if VARIANT in first:
                                print 'variant ok !',
                            else:
                                print
                                raise Exception('Bad variant !')
                        else:
                            print 'no variant',

                        print ', patching',
                        patch(line)
                        print 'ok !',

                        if REMOVE_IF_EMPTY and os.path.getsize(line) == 0:
                            os.remove(line)
                            print 'empty file ! Removed !',

                        print

if __name__ == '__main__':
    scan(sys.argv[1])
    #patch(sys.argv[1])