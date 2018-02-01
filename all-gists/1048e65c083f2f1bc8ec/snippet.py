#!/usr/bin/env python
#######################################################################
##
## Extract the disk serial number from the SOFTWARE hive
##
#######################################################################

__AUTHOR__ = '@herrcore'

import datetime
import struct
import operator
import sys
import argparse

try:
    import hivex
except:
    print >>sys.stderr, 'Error - Please ensure you install the Hivex library, part of libguestfs, before running this script (http://libguestfs.org/).'
    sys.exit(1)

def get_sus_client_validation(hive_location):
    h = hivex.Hivex(hive_location)
    key = h.root()
    key = h.node_get_child(key,"Microsoft")
    key = h.node_get_child(key,"Windows")
    key = h.node_get_child(key,"CurrentVersion")
    key = h.node_get_child(key,"WindowsUpdate")
    val = h.node_get_value(key,'SusClientIdValidation')
    return h.value_value(val)[1]

def get_disk_serial(hive_location):
    data = get_sus_client_validation(hive_location)
    #the serial is stored as little endian DWORDS
    #each serial byte is interspaced with a null (like a wide string)
    #instead of using struct we just parse it ourselves
    wide_data_serial = data[6:46]
    data_serial = wide_data_serial[0::2]
    out_data=[]
    for i in range(0,len(data_serial)-1,2):
        out_data.append(data_serial[i+1])
        out_data.append(data_serial[i])
    out_str = "".join("{:02x}".format(ord(c)) for c in out_data)
    return out_str.lower()

def main():
    desc='''
    This script can be used to parse the disk serial number from the SOFTWARE hive.
    Note: the disk serial number is not the same as the volume serial number.
    '''
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("software_hive", help="The SOFTWARE hive location.")
    args = parser.parse_args()
    software_hive = args.software_hive
    
    str_serial_number = get_disk_serial(software_hive)

    print "\n\n============ Disk Serial Number Extractor ============\n"
    print "Disk serial number: " + str_serial_number + "\n\n"



if __name__ == '__main__':
    main()



