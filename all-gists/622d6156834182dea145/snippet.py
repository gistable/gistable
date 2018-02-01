#!/usr/bin/python
###############################################################################
# IMPORTANT:
#   Place this script in $JOHN/run/ directory.
#
# USAGE:
#   $ python <scriptname>.py <passwdfile> <outfile>
#   Where -
#       scriptname = name of this script.
#       passwdfile = passwd file cracked by JtR.
#       outfile = file name/destination of the output file.
#
# OUTPUT:
#   The output file generated containt a combination of [user:password] on
#   every line for every pair of username and pasword cracked.
#   Example -
#       alice:alice
#       bob:bob
###############################################################################

import sys
import subprocess
import re
import os


def formatJohnShow(johnShowString):
    # Split the string into lines
    linesArr = johnShowString.splitlines(True)
    # Sorts the lines in order
    linesArr.sort()
    formattedShow = ""
    for line in linesArr:
        # Compile and run a regex on every line to get the formatted line
        m = re.search('(^\w+[:]+\w+)', line)
        # If regex match
        if m:
            # Add the formatted line to a string
            formattedShow += m.group(1)
            # Add a new line to seprate pairs
            formattedShow += '\n'
    return formattedShow


def johnShow(passwdfile):
    # You know nothing John Sh(n)ow ;)
    # Command to run in bash
    johnCrackedPassCMD = "./john --show " + passwdfile
    process = subprocess.Popen(
        johnCrackedPassCMD.split(), stdout=subprocess.PIPE)
    # Get the output of the command execution
    output = process.communicate()[0]
    return output

if __name__ == '__main__':

    # Get the name of this script
    script = sys.argv[0]

    # Check the no. of arguments passed
    if len(sys.argv) == 3:
        # Get the passwd file
        passwdfile = sys.argv[1]
        # Name of the output file
        outfile = sys.argv[2]

        # Get string generated from using john --show <passwdfile>
        johnShowString = johnShow(passwdfile)
        # Get formated string for writing to file
        userpass = formatJohnShow(johnShowString)
        try:
            # Open the proper file
            f = open(outfile, 'w')
            # Write the formatted string to file
            f.write(userpass)
        except IOError as e:
            print """
            Failed to open output file.
            I/O error(%d): %s" % (e.errno, e.strerror)
            """
        finally:
            try:
                # Close file
                f.close
            except IOError as e:
                print """
                Failed to close output file.
                I/O error(%d): %s" % (e.errno, e.strerror)
                """
        # Display a confirmation message
        print "Created: %s" % os.path.abspath(outfile)
    else:
        print """
        Error: Missing arguments!
        USAGE: $ python %s <passwdfile> <outfile>
        """ % script
