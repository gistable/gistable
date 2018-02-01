#!/usr/bin/python
'''Converts a standard Wi-Fi configuration profile for iOS/macOS that uses
a user certificate, and converts it into a SystemConfiguration profile type
that can be used to connect to a Wi-Fi network at macOS login screen.
This is useful where you need a laptop to be able to bind to an AD or LDAP
server, or just want to have user credential free Wi-Fi connection at the
system level.'''

import os
import plistlib
import sys

try:
    infile = os.path.expanduser(os.path.expandvars(sys.argv[1]))
    outfile = os.path.expanduser(os.path.expandvars(sys.argv[2]))

    if all([infile.endswith('.mobileconfig'), outfile.endswith('.mobileconfig')]):  # NOQA
        try:
            config = plistlib.readPlist(infile)
            # This goes into the PayloadContent
            # (where 'AutoJoin' exists)
            for payload in config['PayloadContent']:
                # Target the payload with 'AutoJoin' in it
                if 'AutoJoin' in payload.keys():
                    payload['SetupModes'] = ['System']  # NOQA
                    payload['PayloadScope'] = 'System'  # NOQA

                    # Convert the profile from a standard Configuration
                    # type, to SystemConfiguration type
                    config['PayloadType'] = 'SystemConfiguration'

            plistlib.writePlist(config, outfile)
        except Exception as e:
            print '{} {}'.format(e, infile)
    else:
        print 'In/Out files must be \'.mobileconfig\' type.'
        sys.exit(1)
except:
    print 'Usage: {} infile outfile'.format(sys.argv[0])
    sys.exit(1)