#! /usr/bin/env/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys

# This code gets the major, minor, and patch version and displays it
# You can change this to sys.version[0:4] if you do not want the patch version
print("You are running {0}".format(sys.version[0:5]))

# This code shows off a conditional version check
if sys.version_info > (3, 3, 0):
    print("\nYou need at least Python 3.3.0 to run this.")

# Can be changed to use major and minor only
if sys.version_info > (2, 5):
    print("\nYou need at least Python 2.5 to run this.")

# They can be combined
if sys.version_info != (2, 7, 3):
    print('''
You are running Python {0}. You need to get Python 2.7.3 to run this script.'''
                     .format(sys.version[0:5]))

# Close the script
sys.exit(0)
