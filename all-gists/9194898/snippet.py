#!/usr/bin/python
#-*- coding: iso-8859-15 -*-

###################################################################
# macinfo by unixtrem                                             #
#                                                                 #
# this script shows the vendor of a mac address                   #
# you can use different syntaxes to get the result and the script #
# automatically parses your entered MAC for more speed.           #
#                                                                 #
# examples:                                                       #
#     macinfo 00:0a:F8                                            #
#     macinfo 00-0A-F8                                            #
#     macinfo 000af8                                              #
#     macinfo 00:0A:F8:B2:55:C0                                   #
###################################################################

import sys
import string
import urllib

# variables globales
class Default:
    def __init__(self):
        self.file   = sys.path[0]+'/.oui.txt'
        self.upTest = 'http://www.google.com'
        self.upFile = 'http://standards.ieee.org/regauth/oui/oui.txt'
        self.limit  = [':','-']
        self.hex    = ['A','B','C','D','E','F',
                      '1','2','3','4','5','6',
                      '7','8','9','0']
d = Default()

help = '\n'
help+= 'macinfo (vendor ascociation)\n'
help+= 'Usage : macinfo <mac-address>\n'
help+= '        macinfo upgrade\n'

try:open(d.file)
except:
    open(d.file,'w')
    print 'First you have to upgrade .oui.txt file with "upgrade" option.'

if len(sys.argv) != 2: sys.exit(help)

if sys.argv[1] == 'upgrade':
    try:
        urllib.urlopen(d.upTest)
    except:
        sys.exit('Not connected')
    try:
        oui=urllib.urlopen(d.upFile).read()
    except:
        sys.exit('Error: "'+d.upfile+'" is offline')
    try:
        oldOui=open(d.file,'r').read()
    except:
        sys.exit('Error: failed to read "'+d.file+'"')
    if oui == oldOui:
        sys.exit('Your actual oui file is already the newest')
    try:
        open(d.file,'w').write(oui)
    except:
        sys.exit('Error: failed to write on "'+d.file+'"')
    sys.exit('macinfo was correctly upgraded')

mac = sys.argv[1]
mac = string.upper(mac) # convert min en maj

if len(mac) > 18:
    sys.exit(help)
if len(mac) < 6 :
    sys.exit(help)
if mac[2] in d.limit and mac[5] in d.limit and len(mac) > 7:
    mac = mac[0:2]+mac[3:5]+mac[6:8]
for x in mac:
    if x not in d.hex:
        sys.exit(help)
mac = mac[0:2]+'-'+mac[2:4]+'-'+mac[4:6]

try:
    file = open(d.file,'r').read()
except:
    sys.exit('error opening '+d.file)

file = file.split('\n\n')

for i in file:
    if mac in i:
        sys.exit('\n'+i+'\n')

print '\nmac not found\n'