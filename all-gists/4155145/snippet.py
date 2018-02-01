#!/usr/bin/env python
#-----------------------------------------------------------------------------
# 
#-----------------------------------------------------------------------------

import xml.etree.ElementTree
import sys
import re
import os.path

def usage():
    print("nessus_web_servers.py nessus_file")
    sys.exit()

def open_nessus_file(filename):
    if not os.path.exists(filename):
        print("{0} does not exist.".format(filename))
        sys.exit()

    if not os.path.isfile(filename):
        print("{0} is not a file.".format(filename))
        sys.exit()

    nf = xml.etree.ElementTree.ElementTree(file=filename)
    root = nf.getroot()

    if root.tag == 'NessusClientData_v2':
        return filename, root
    else:
        print("{0} is not a Nessus version 2 file.".format(filename))
        sys.exit()

#-------------------------#
# Begin the main program. #
#-------------------------#

if (len(sys.argv) != 2) or (sys.argv[1] == '-h'):
    usage()
else:
    file_name, nessus = open_nessus_file(sys.argv[1])

reports = nessus.findall('Report')

for report in reports:

    for host in report.findall('ReportHost'):
        ip = ''
        for tag in host_properties.findall('tag'):
            if tag.attrib['name'] == 'host-ip':
                ip = tag.text

        report_items = host.findall('ReportItem')
        for item in report_items:
            if plugin == '22964':
                m = re.search(r'web server', item.find('plugin_output').text)
                if m is not None:
                    print '{0} {1}'.format(ip, item.attrib['port'])
