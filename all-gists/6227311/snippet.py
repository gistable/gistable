#!/usr/bin/python

import collections
import optparse
import os
import sys
import urllib

ROOT_WSDL_FILE = 'vimService.wsdl'
WSDL_FILES = frozenset([
    'vimService.wsdl',
    'vim.wsdl',
    'core-types.xsd',
    'query-messagetypes.xsd',
    'query-types.xsd',
    'reflect-messagetypes.xsd',
    'reflect-types.xsd',
    'vim-messagetypes.xsd'])

XSD_WITH_404 = """<?xml version="1.0" encoding="UTF-8"?>
<schema
   targetNamespace="urn:reflect"
   xmlns="http://www.w3.org/2001/XMLSchema"
   xmlns:xsd="http://www.w3.org/2001/XMLSchema"
   elementFormDefault="qualified">
</schema>
"""

parser = optparse.OptionParser("usage: %prog [options]")

parser.add_option("-H", "--host", 
                  dest="hostname", 
                  default=None,
                  type="string", 
                  help="specify hostname extract WSDL from")

parser.add_option("-D", "--dest", 
                  dest="dest_directory", 
                  default="/opt/stack/wsdl", 
                  type="string", 
                  help="specify destination directory for WSDL files")

(options, args) = parser.parse_args()

if not( options.hostname and options.dest_directory ):
    parser.print_help()
    sys.exit()

for wsdl_file in WSDL_FILES:
    remote_file_path = "https://%s/sdk/%s" % (options.hostname, wsdl_file)
    local_file_path = os.path.join(options.dest_directory, wsdl_file)
    local_file = open(local_file_path, 'w')
    remote_file = None
    
    try:
        remote_file = urllib.urlopen(remote_file_path)
    except IOError as e:
        print e.message
        print "Could not open %s" % remote_file_path
        os.sys.exit(1)

    code = remote_file.getcode() 
    if code == 200:
        print "%d: downloading %s" % (code, wsdl_file)
        local_file.write(remote_file.read())
    elif code == 404:
        print "fixing missing %s" % wsdl_file
        local_file.write(XSD_WITH_404)
    else:
        print "%s returned code %d" % (remote_file_path, code)

    remote_file.close()
    local_file.close()

local_file = open(os.path.join( options.dest_directory, ROOT_WSDL_FILE ), 'r')
local_file_name = os.path.abspath(local_file.name)
local_file.close()
print "# use the following location for your driver"
print "VMWAREAPI_WSDL_LOC=file://%s" % local_file_name