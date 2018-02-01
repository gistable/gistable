#!/usr/bin/python
# From http://stackoverflow.com/questions/352098/how-to-pretty-print-json-script
# To install paste this into a file named prettyjson that lives in your PATH
# e.g. 
# sudo touch /usr/bin/prettyjson
# sudo open -t /usr/bin/prettyjson 
# paste this file and save
# sudo chmod +x /usr/bin/prettyjson

"""
Convert JSON data to human-readable form.

Usage:
  prettyJSON.py inputFile [outputFile]
"""

import sys
import simplejson as json


def main(args):
    try:
        inputFile = open(args[1])
        input = json.load(inputFile)
        inputFile.close()
    except IndexError:
        usage()
        return False
    if len(args) < 3:
        print json.dumps(input, sort_keys = False, indent = 4)
    else:
        outputFile = open(args[2], "w")
        json.dump(input, outputFile, sort_keys = False, indent = 4)
        outputFile.close()
    return True


def usage():
    print __doc__


if __name__ == "__main__":
    sys.exit(not main(sys.argv))