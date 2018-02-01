#!/usr/bin/python
import sys
import os

if len(sys.argv) <= 1:
        print os.path.realpath(os.getcwd())
else:
        print os.path.realpath(sys.argv[1])
