#!/usr/bin/env python

"""Small app to read nrf uart RX port"""

#sudo gatttool -b F3:5F:71:83:EE:2D -t random --char-write-req -a 0x000c -n 0100 --listen

import subprocess
import time
import sys
import signal
import os
import re
from ctypes.util import find_library
from datetime import datetime

class BleUartScanner:

    def __init__(self, bleMacAddr):
        self.bleMacAddr = bleMacAddr
        self.rxCommand = "gatttool -b %s -t random --char-write-req -a 0x000c -n 0100 --listen" % self.bleMacAddr
        self.dataRe = re.compile("Notification handle = 0x[0-9a-f]{4} value:(( [0-9a-f]{2})+)")
        self.p = None
    
    def readTxOutput(self):
        p = subprocess.Popen(self.rxCommand, stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE, shell=True, bufsize=0)
        try:
            output = ""
            lchar = None
            while p.poll() is None:
                line = p.stdout.readline()
                match = self.dataRe.match(line)
                if match:
                    l = "".join(match.group(1).split()).decode("hex")
                    # State machine
                    for c in l:
                        if ord(c) == 0x0d:
                            lchar = c
                        elif ord(c) == 0x0a and lchar is not None and ord(lchar) == 0x0d:
                            lchar = None
                            self.echo(output)
                            output = ""
                        elif lchar is not None:
                            output += lchar + c
                            lchar = None
                        else:
                            output += c
                else:
                    print("<shell output>: %s" % line )
        except KeyboardInterrupt:
            if p is not None:
                p.terminate()
                print("Terminated gatttool")

    def readHexStr(self, string):
        return "".join([chr(int(h, 16)) for h in string.strip().split(' ')])

    def echo(self, string):
        d = datetime.now().strftime("[%Y-%m-%d %I:%M:%S %p]")
        print("%s%s" % (d, string))
                
def main(args):

    # Check for root
    if not os.geteuid() == 0:
        sys.exit("Must be root to run this application")

    # Check for bluetooth libraries
    btlib = find_library("bluetooth")
    if not btlib:
        sys.exit("Unable to find required bluetooth libraries")

    if len(args) < 2:
        sys.exit("Missing BLE MAC address")

    b = BleUartScanner(args[1])
    b.readTxOutput()
    

if __name__ == "__main__":
    main(sys.argv)