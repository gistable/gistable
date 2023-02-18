#!/usr/bin/env python

"""
    Find host - decode hashed known_hosts files

    Using an unhashed known_hosts file as reference, compare by host
    key.
"""

import logging
import argparse
import fileinput
import os.path

logger = logging.getLogger(__name__)

def _parse_known_hosts(decoder):
    known_keys = {}
    for line in decoder.readlines():
        fields = line.split()
        try:
            hostname, key_format, keyhash = fields
        except ValueError:
            logger.error("Got %d fields: %s" % (len(fields),
                '|'.join(fields)))
            raise
        l = known_keys.get(keyhash, [])
        l.append(hostname)
        known_keys[keyhash] = l
    return known_keys


def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    def_decoder = '~/.ssh/known_hosts'
    parser.add_argument("--decoder",
            help='unhashed known_hosts file (default is %s)' % def_decoder,
            type=argparse.FileType('r'),
            default=os.path.expanduser(def_decoder))
    parser.add_argument("--generate", "-g", default=False,
            action='store_true', help="generate decoded file")
    parser.add_argument("file", nargs='*',
            help="known_host file(s) to decode")
    args = parser.parse_args()
    return args


def _main():
    context = _parse_args()
    main_hosts = _parse_known_hosts(context.decoder)
    exit_code = 0
    for l in fileinput.input(context.file):
        h, key_format, key_in_question = l.split()
        try:
            matches = main_hosts[key_in_question]
            if context.generate:
                print("%s %s %s" % (','.join(matches), key_format,
                    key_in_question))
            else:
                print("%s is %s" % (h, ' '.join(matches)))
        except KeyError:
            logger.info("%s not found", h)
            exit_code = 1
    return exit_code

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    raise SystemExit(_main())
