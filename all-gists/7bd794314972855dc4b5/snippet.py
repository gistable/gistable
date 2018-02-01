__author__ = 'dhcdht'

import os
import re

plugin_path = os.path.expanduser('~/Library/Application Support/Developer/Shared/Xcode/Plug-ins')
#for Xcode 6.3
#plugin_uuid = '9F75337B-21B4-4ADC-B558-F9CADF7073A7'
#for Xcode 6.3.2
#plugin_uuid = 'E969541F-E6F9-4D25-8158-72DC3545A6C6'
#for Xcode 6.4
# plugin_uuid = '7FDF5C7A-131F-4ABB-9EDC-8C5F8F0B8A90'
#for Xcode 7.0 beta 6
# plugin_uuid = 'AABB7188-E14E-4433-AD3B-5CD791EAD9A3'
#for Xcode 7.0 GM
# plugin_uuid = '0420B86A-AA43-4792-9ED0-6FE0F2B16A13'
#for Xcode 7.1
# plugin_uuid = '7265231C-39B4-402C-89E1-16167C4CC990'
#fro Xcode 7.2
# plugin_uuid = 'F41BD31E-2683-44B8-AE7F-5F09E919790E'
#fro Xcode 7.3
plugin_uuid = 'ACA8656B-FEA8-4B6D-8E4A-93F4C95C362C'

for root, dirs, files in os.walk(plugin_path):
    for file in files:
        if file == 'Info.plist' and root.endswith('xcplugin/Contents'):
            plist_path = os.path.join(root, file)
            # print(plist_path)
            fp = open(plist_path, 'r')
            plist_content = fp.read()
            fp.close()
            if re.search('DVTPlugInCompatibilityUUIDs', plist_content):
                if not re.search(plugin_uuid, plist_content):
                    fp = open(plist_path, 'w')

                    plist_replaced = re.sub('<key>DVTPlugInCompatibilityUUIDs</key>\s*<array>',
                                            '<key>DVTPlugInCompatibilityUUIDs</key>\n'
                                            '	<array>\n'
                                            '		<string>%s</string>' % plugin_uuid,
                                           plist_content)
                    fp.write(plist_replaced)
                    fp.close()
                    print('add : ' + plist_path)
                else:
                    print('Dont need add : ' + plist_path)
