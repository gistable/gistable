#!/usr/bin/env python

# Print out a list of board-id to model mappings from a munkiwebadmin/munkireport
# database. Requires the machine's board-id to be present at the admin-provided condition
# called 'machine_board_id'. A custom condition script to populate this can be found at:
# https://github.com/timsutton/munki-conditions/blob/master/hardware_id

# Hardcoded assumptions:
# - script is being run from a working directory where 'munkiadmin.db' can be found
# - if a virtualenv is being used, it is already activated  (ie. 'source /path/to/env/bin/activate')

import sqlite3
import plistlib
import sys
from django.utils.encoding import smart_str
from pprint import pprint

DB = 'munkiadmin.db'
conn = sqlite3.connect(DB)
c = conn.cursor()
reports = c.execute('''SELECT report from reports_munkireport''')
boards_populated = 0
boards = {}
for r in reports.fetchall():
    smrt = smart_str(r[0])
    p = plistlib.readPlistFromString(smrt)

    if 'Conditions' in p.keys():
        if 'machine_board_id' in p['Conditions']:
            if p['Conditions']['machine_board_id'] and p['Conditions']['machine_board_id'] != '440BX':
                boards_populated += 1
                boards[p['Conditions']['machine_board_id']] = p['Conditions']['machine_model']

conn.close()
print "%s clients with board-id configs." % str(boards_populated)
print "%s board-id values populated." % len(boards.keys())
pprint(boards)