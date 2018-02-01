#!/usr/bin/env python

# Author: Andrey Vlasovskikh
# License: MIT

import sys
import os
import subprocess

def main():
    if len(sys.argv) != 2:
        print('usage: pacnew FILE', file=sys.stderr)
        sys.exit(1)

    filename = sys.argv[1]
    pacnew = '{}.pacnew'.format(filename)
    subprocess.call(['meld', filename, pacnew])
    answer = input("delete '{}' [y/N]: ".format(pacnew))
    if answer == 'y':
        os.remove(pacnew)
    else:
        raise KeyboardInterrupt

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('interrupted', file=sys.stderr)
        sys.exit(1)
