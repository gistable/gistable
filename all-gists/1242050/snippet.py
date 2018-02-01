#!/usr/bin/env python

import sys, os.path

install_path = sys.argv[1]
target_platform = sys.argv[2]

if target_platform != "iPhone": sys.exit()

info_plist_path = os.path.join(install_path, 'Info.plist')

file = open(info_plist_path, 'r')
plist = file.read()
file.close()

elements_to_add = '''
<key>CFBundleURLTypes</key>
<array>
 <dict>
  <key>CFBundleURLSchemes</key>
  <array>
   <string>fbXXXXXXXXXXXXXXX</string>
  </array>
 </dict>
</array>
<key>CFBundleLocalizations</key>
<array>
 <string>en</string>
 <string>ja</string>
</array>                    
'''

plist = plist.replace('<key>', elements_to_add + '<key>', 1)

file = open(info_plist_path, 'w')
file.write(plist)
file.close()
