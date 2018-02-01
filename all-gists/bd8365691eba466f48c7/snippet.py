#!/usr/bin/env python

import subprocess
import plistlib
import sys

# Our read and write commands to the authorizationdb
readcmd = ['/usr/bin/security', 'authorizationdb', 'read', 'system.login.console']
writecmd = ['/usr/bin/security', 'authorizationdb', 'write', 'system.login.console']

# Run the read task, get the contents of system.login.console
task = subprocess.Popen(readcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(out, err) = task.communicate()
formatted = plistlib.readPlistFromString(out)

# Pop the first item in the list, this should be builtin:policy-banner
banner = formatted['mechanisms'].pop(0)

# If the popped item is not the policy-banner we bail, something is not right
if 'builtin:policy-banner' in banner:
    print "NOTICE: Changing policy-banner to be last item in system-login-console."
    formatted['mechanisms'].append(banner)
    input_plist = plistlib.writePlistToString(formatted)

    # Write the plist back to the authorizationdb
    task = subprocess.Popen(writecmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = task.communicate(input=input_plist)
else:
    print "WARNING: Policy banner was not first item, not making changes."
    sys.exit(-1)
