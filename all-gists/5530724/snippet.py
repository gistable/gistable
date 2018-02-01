#! /usr/bin/env python
import subprocess
import re

# Settings
diskPath = '/dev/sda'
mountPath = '/media/drobo'

# Get status
command = "/usr/sbin/drobom status"
process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
status = process.communicate()[0]

# Validate status
# Expected response:
# /dev/sda /media/drobo Drobo disk pack 72% full - ([], 0)
regex = '(\/.*?\/.*?)\ (-|.*?)\ Drobo\ disk\ pack\ (\d{1,2})%\ full\ -\ \(\[(.*?)\],\ (\d)\)'
errors = []

if re.match(regex, status) is None:
    errors.append('status did not match')
else:
    check = re.search(regex, status)

    if check.group(1) != diskPath:
        errors.append('unexpected disk path')

    if check.group(2) != mountPath:
        errors.append('unexpected mount path')

    if int(check.group(3)) > 90:
        errors.append('not enough room')

    if check.group(4) != '':
        errors.append(check.group(4))

    if check.group(5) != '0':
        errors.append('something should be 0')

if len(errors) > 0:
    print "Drobo in danger!!"
    print status
    for error in errors:
        print error
else:
    print "Drobo seems ok: "
    print status

# Get firmware
command = "/usr/sbin/drobom fwcheck"
process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
status = process.communicate()[0]

# Expected response:
# looking for firmware for: armmarvell 1.254.50341 hw version: 2.00
# no matching firmware found, must be the latest and greatest!
regex = 'no\ matching\ firmware\ found'

# Validate firmware
if re.search(regex, status) is None:
    print 'FW not up to date:'
    print status
else:
    print 'FW is up to date.'
