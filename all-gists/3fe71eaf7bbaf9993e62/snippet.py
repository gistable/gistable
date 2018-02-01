#!/usr/bin/env python

'''
    Extremely simple Bill Of Materials creator for KiCad.
    Creates a MarkDown output from KiCad .xml netlist files.
    It's a fast and dirty approach that just works, if you need a good BoM creator, forget this.
'''
__author__ = "Ekaitz Zarraga"
__license__= "WTFPL"

import xml.etree.ElementTree as ET
import sys

component_list = {}

# Doesn't check input, use it at your own risk ;)
inputFile = sys.argv[1]
outputFile = sys.argv[2]

tree = ET.parse(inputFile)
root = tree.getroot()

components = root.find('components')

for component in components.iter('comp'):
    try:
        component_list [ component.find('libsource').attrib['part'] ].append(component.find('value').text)
    except KeyError:
        component_list [ component.find('libsource').attrib['part'] ] = []    
        component_list [ component.find('libsource').attrib['part'] ].append(component.find('value').text)

with open( outputFile, 'w') as f:
    f.write('BILL OF MATERIALS \n')
    f.write('------------------\n\n')
    for key, items in component_list.iteritems():
        f.write('- [ ] ' + key.replace('_', ' ') + ":\n\n")
        items.sort()
        lastItem = items[0]
        count = 0
        for item in items:
            if count == 0:
                count = 1
                continue
            if lastItem != item:
                f.write('  - [ ] ' + str(count) + 'x ' +  lastItem.replace('_', ' ') + '\n\n')
                count = 1
            else:
                count += 1

            lastItem = item
        f.write('  - [ ] ' + str(count) + 'x ' +  lastItem.replace('_', ' ') + '\n\n')

    f.close()
