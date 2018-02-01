#!/usr/bin/env python
import sys
import subprocess
import re
import logging
import argparse

# https://github.com/wooster/biplist (pip install biplist)
import biplist


KEY_TYPES = ['generic', 'internet']

logger = logging.getLogger(__name__)


def decode_hex(hex_string):
    if hex_string == '':
        return hex_string
    else:
        return chr(int(hex_string[:2], base=16)) + decode_hex(hex_string[2:])


def getpass(service, acct=None, key_type='generic'):
    '''Return the password stored in the Mac OS X user keychain for given service and account names.'''
    assert key_type in KEY_TYPES

    cmd_parts = ['/usr/bin/security', 'find-{0}-password'.format(key_type)]

    cmd_parts.append('-g')  # display password

    cmd_parts.extend(('-s', service))

    if acct:
        cmd_parts.extend(('-a', acct))

    logging.debug(cmd_parts)
    proc = subprocess.Popen(cmd_parts, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = proc.communicate()
    logger.debug(' => %s', result)

    match = re.match(r'password: (?:0x([0-9A-F]+)\s*)?"(.*)"$', result[1])
    if match:
        logging.debug('Matches: %s', match.groups())
        hexform, stringform = match.groups()

        if hexform:
            decoded_pass = decode_hex(hexform)

            if decoded_pass.startswith('bplist'):
                plist_data = biplist.readPlistFromString(decode_hex(hexform))
                assert 'password' in plist_data
                return plist_data['password']

            else:
                return decoded_pass

        else:
            return stringform
    else:
        logger.warn("No match for output: '%s'", result[1])
        raise Exception("No match for output: '%s'", result[1])


def main(argv):
    # Parse arguments
    parser = argparse.ArgumentParser(description="Get password from Mac OS X Keychain")

    # Global options
    parser.add_argument('-v', '--verbose', help='Show DEBUG messages',
                        action='store_true', default=False)
    parser.add_argument('-i', '--internet', help='Look up "internet" keychain entries',
                        action='store_const', const='internet', default='generic', dest='type')
    parser.add_argument('-g', '--generic', help='Look up "generic" keychain entries',
                        action='store_const', const='generic', default='generic', dest='type')
    parser.add_argument('service', help='Keychain entry service name (or URL)')
    parser.add_argument('account', help='Keychain entry account (user name)')

    args = parser.parse_args(argv[1:])

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    password = getpass(args.service, args.account, args.type)
    print password
    return 0

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN, stream=sys.stderr)
    sys.exit(main(sys.argv))
