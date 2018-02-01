#!/usr/bin/env python
# wol.py

# based on http://code.activestate.com/recipes/358449-wake-on-lan/
# added for loop to use arpwatch's MAC address list instead of manually having to maintain a list of MAC addresses
#  there could be potential security problems with using the arpwatch list so use at your own risk.

# [DZ]: Original Version by Jeremy Z (10Bitworks SA, Tx) <zunkworks@gmail.com> 
# [DZ](Change Log): Added Command Line Option Parsing, regex parsing to wake_on_lan()

import socket
import struct
import time
import re
from optparse import OptParse


# Use macaddresses with or without seperators.
#    wake_on_lan('0F:0F:DF:0F:BF:EF')
#    wake_on_lan('0F-0F-DF-0F-BF-EF')
#    wake_on_lan('0F0FDF0FBFEF')

def wake_on_lan(macaddress):
    """ Switches on remote computers using WOL. """

    # Check macaddress format and try to compensate.
    if len(macaddress) == 12:
        pass
    elif len(macaddress) == 17:
        macaddress = re.compile('[:-]', re.MULTILINE).sub('', macaddress)
    else:
        raise ValueError('Incorrect MAC address format')
 
    # Pad the synchronization stream.
    data = ''.join(['FFFFFFFFFFFF', macaddress * 20])
    send_data = ''

    # Split up the hex values and pack.
    for i in range(0, len(data), 2):
        send_data = ''.join([send_data,
                             struct.pack('B', int(data[i: i + 2], 16))])

    # Broadcast it to the LAN.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(send_data, ('<broadcast>', 5000)) # udp port 7, 9 are most common, I'm using 5000

def main():
    parser = OptionParser(usage="usage: %prog [options] <filename>",
                          version="%prog 1.0")
    parser.add_option("-m", "--mac",
                      action="store",
                      dest="macaddr",
                      default="00:ff:de:ad:be:ef",
                      help="MAC address to send to, valid usage is with or without separators")
    parser.add_option("-f", "--arpfile",
                      action="store", # optional because action defaults to "store"
                      dest="arpwatch",
                      default="/var/lib/arpwatch/eth3.dat",
                      help="path to match the appropriate arpwatch file on your system")
    parser.add_option("-d", "--delay",
                      action="store",
                      dest="delay",
                      default="0.5",
                      help="Works much better with a small delay to avoid large power surges")
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("wrong number of arguments")

    f = open(options['arpwatch'],'r')

    i = 0
    for line in f:
        info = line.split('\t')
        print 'waking - ' + str(i) + ' - ' + str(info[0])
        i += 1
        # FIXME: include options['macaddress'] || info[0]
        wake_on_lan(info[0])
	time.sleep(options['delay'])
    f.close()

if __name__ == '__main__':
    main()