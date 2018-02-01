# -*- coding: utf-8 -*-

import csv

fp = open('oui.txt', 'rb')

entries = [{'oui_hex': 'oui_hex',
            'oui_base16': 'oui_base16',
            'lower_mac_bound': 'lower_mac_bound',
            'upper_mac_bound': 'upper_mac_bound',
            'vendor': 'vendor',
            'address': 'address'
            }]

for item in fp.read().split('\n\n')[1:-1]:
    parts = item.split('\n')
    
    hex_oui = parts[0].strip().split()[0]
    base16_oui = parts[1].strip().split()[0]
    lower_bound = base16_oui + '0'*6
    upper_bound = base16_oui + 'F'*6
    
    vendor = parts[0].split('\t')[-1]
    address = ', '.join([s.strip().strip('\t') for s in parts[2:]])
    
#     print parts
#    print 'hex:\t' + hex_oui
#    print 'base16:\t' + base16_oui + '\tupper: ' + upper_bound + '\tlower: ' + lower_bound
#    print 'vendor:\t' + vendor
#    print 'addr:\t' + address
#    print
    
    entries.append({'oui_hex': hex_oui,
                    'oui_base16': base16_oui,
                    'lower_mac_bound': lower_bound,
                    'upper_mac_bound': upper_bound,
                    'vendor': vendor,
                    'address': address
                    })

fields = ['vendor', 'oui_hex', 'oui_base16', 'lower_mac_bound', 'upper_mac_bound', 'address']
writer = csv.DictWriter(open('oui.csv', 'wb+'), fields)
# writer = csv.DictWriter(open('oui_tab.csv', 'wb+'), fields, delimiter='\t')

for entry in entries:
    writer.writerow(entry)

fp.close()
