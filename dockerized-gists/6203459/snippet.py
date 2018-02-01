#!/usr/bin/env python

# For details, in Mac OS X Terminal type: man pbcopy

import subprocess, sys

def getClipboardData(): # Only works for data types: {txt | rtf | ps}
    p = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE)
    retcode = p.wait()
    data = p.stdout.read()
    return data

def setClipboardData(data):
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.stdin.write(data)
    p.stdin.close()
    retcode = p.wait()

def sendTextToiOS(inText):
    pass  # Your Prowl code goes here!!!

def main(argv):
    theText = getClipboardData()
    if not theText:
        print('No text found on the Mac OS X Pasteboard.')
        return -1 # signal error
    print('Got: ' + theText)
    sendTextToiOS(theText)
    return 0      # noError

if __name__ == '__main__':
    sys.exit(main(sys.argv))