#!/usr/bin/python

# Script for generating a software version code(hex) from a version string.
# 
# Usage e.g $ python CreateVersionNumber.py 1.4.2"
#
# Peter Vasil
# Date: 2011-02-15

from optparse import OptionParser
import sys

try:
    import pygtk
    pygtk.require('2.0')
    import gtk
    with_clipboard = True
except ImportError:
    with_clipboard = False
    

def str_to_hex_version(version_string):
    """
    
    Arguments:
    - `version`:
    """
    if version_string.count(".") == 2:
        versions = version_string.split(".")
        value = (int(versions[0]) << 16) + (int(versions[1]) << 8) + (int(versions[2]))
    else:
        value = None

    return value

def main():
    usage = "usage: %prog 'version number (e.g. 1.0.0)'"
    parser = OptionParser(usage, version="%prog 0.1")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("\nplease enter a version number!")
    
    version_string = args[0]

    version_hex = str_to_hex_version(version_string)

    if not version_hex == None: 
        print("version number %s => 0x%x" % (version_string, version_hex))

        if with_clipboard:
            clipboard = gtk.clipboard_get()
            clipboard.set_text("0x%x" % version_hex)
            clipboard.store()
    else:
        print("Not valid version number.")
    
if __name__ == '__main__':
    sys.exit(main())
