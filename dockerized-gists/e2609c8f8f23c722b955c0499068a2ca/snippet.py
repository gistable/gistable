# Procmon Rule Parser v0.02
# Brian Baskin - @bbaskin
# Reads default rules from an exported Procmon Configuration (.PMC) or Procmon Filter (.PMF) file
# Example output:
"""
12:09:59-bbaskin@~/Development/Noriben$ python parse_procmon_filters.py  -f ProcmonConfiguration.pmc
[Exclude]   Process Name is Procmon64.exe
[Exclude]   Operation is QueryStandardInformationFile
[Exclude]   Operation is RegOpenKey
[Exclude]   Operation is NotifyChangeDirectory
[Exclude]   Operation begins with IRP_MJ_
[Exclude]   Operation begins with FASTIO_
[Exclude]   Image Path begins with C:\Tools\SysinternalsSuite\
[Exclude]   Image Path is C:\Program Files\VMware\VMware Tools\VMware CAF\pme\bin\ManagementAgentHost.exe
"""

import argparse
import os
import struct
import sys

types = {0x9c74:'Date & Time',
         0x9c75:'Process Name',
         0x9c76:'PID',
         0x9c77:'Operation',
         0x9c78:'Result',
         0x9c79:'Detail',
         0x9c7a:'Sequence',
         0x9c80:'Company',
         0x9c81:'Description',
         0x9c82:'Command Line',
         0x9c83:'User',
         0x9c84:'Image Path',
         0x9c85:'Session',
         0x9c87:'Path',
         0x9c88:'TID',
         0x9c8c:'Time',
         0x9c8d:'Duration',
         0x9c8e:'Time of Day',
         0x9c91:'Version',
         0x9c92:'Event Class',
         0x9c93:'Authentication ID',
         0x9c94:'Virtualized',
         0x9c95:'Integrity',
         0x9c96:'Category',
         0x9c97:'PID',
         0x9c98:'Architecture',
         0x9ce4:'Completion Time'}
         
operations = {0x00:'is',
              0x01:'is not',
              0x02:'less than',
              0x03:'more than',
              0x04:'begins with',
              0x05:'ends with',
              0x06:'contains',
              0x07:'excludes'}

actions = {0x00000000:'Exclude',
           0x01000000:'Include'}
              
filter_header = b'\x46\x00\x69\x00\x6C\x00\x74\x00\x65\x00\x72\x00\x52\x00\x75\x00\x6C\x00\x65\x00\x73\x00\x00\x00'

def file_exists(fname):
    return os.path.exists(fname) and os.access(fname, os.F_OK)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='File to read (PMC or PMF)', required=True)
    args = parser.parse_args()
    
    if not file_exists(args.file):
        print('File not found: {}'.format(args.file))
        quit()
        
    data = open(args.file, 'rb').read()
    file_hdr = struct.unpack('I', data[0:4])[0]

    if file_hdr == 0xa0:  #PMC File
        rule_offset = data.find(filter_header)
        offset = rule_offset + len(filter_header)
    elif file_hdr == os.stat(args.file).st_size - 4:
        rule_offset = 4
        offset = 4
    else:
        print('Unknown file format')
        quit()

    if not rule_offset:
        print('Could not find appropriate header')
        quit()

    if data[offset] != '\x01':
        print('Unexpected start byte. Expected 0x01, received 0x{:02x}'.format(ord(data[offset])))
        quit()
    offset += 1

    num_rules = struct.unpack('I', data[offset:offset+4])[0]
    offset += 4
    
    if num_rules <= 0:
        print('Invalid number of rules')
        quit()

    for rule in range(num_rules):
        try:    
            type = struct.unpack('I', data[offset:offset+4])[0]
            offset += 4
        except struct.error:
            print('Could not read type value')
            quit()

        operation = struct.unpack('B', data[offset:offset+1])[0]
        offset += 1
        
        if not type in types:
            print('Unable to decode Type: {:x}'.format(type))
        
        if not operation in operations:
            print('Unable to decode operation: {:x}'.format(operation))
        
        action = struct.unpack('I', data[offset:offset+4])[0]
        offset += 4
        
        size = struct.unpack('I', data[offset:offset+4])[0]
        offset += 4
        
        value = data[offset:offset+size]
        offset += size

        print('[{}]\t{} {} {}'.format(actions[action], types[type], operations[operation], value.decode('utf-16')))
        offset += 8
        
if __name__ == '__main__':
    main()