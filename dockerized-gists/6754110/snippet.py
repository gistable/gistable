#!/usr/bin/env python
'''
Little script to set timestamps based on filenames for files uploaded to
Dropbox by CameraSync.

:author: Dan Blanchard
:date: September, 2013
'''

from __future__ import print_function, unicode_literals

import argparse
import logging
import os
import re
from datetime import datetime
from time import mktime, strftime
from stat import ST_ATIME


def main():
    '''
    Handles command line arguments and gets things started.
    '''
    # Get command line arguments
    parser = argparse.ArgumentParser(
        description="Fixes timestamps for files that are named in the format\
                     'YYYY-MM-DD at HH.mm.ss.*'. If given a file that does\
                     not fit the format, it is just skipped.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('target_file', help='File to fix timestamp for.',
                        nargs='+')
    parser.add_argument('-t', '--timestamp_re',
                        help='Regular expression to use to find timestamp in \
                              filename. Must define year, month, day, hour, \
                              minute, and second capture groups.',
                        default=(r'^(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-' +
                                 r'(?P<day>[0-9]{2}) at (?P<hour>[0-9]{2}).' +
                                 r'(?P<minute>[0-9]{2}).(?P<second>[0-9]{2})'))
    args = parser.parse_args()

    # initialize the logger
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    timestamp_re = re.compile(args.timestamp_re)

    # Loop through given files
    for f in args.target_file:
        # Check if the filename starts with a CameraSync-formatted timestamp
        match = timestamp_re.search(os.path.basename(f))
        if match:
            # Get current access time
            st = os.stat(f)
            atime = st[ST_ATIME]

            # Create new struct_time out of regex match
            new_mtime = datetime(int(match.group('year')),
                                 int(match.group('month')),
                                 int(match.group('day')),
                                 int(match.group('hour')),
                                 int(match.group('minute')),
                                 int(match.group('second'))).timetuple()

            # Modify the file timestamp
            os.utime(f, (atime, mktime(new_mtime)))

            logging.info('Set timestamp for {0} to '.format(f) +
                         strftime("%a, %d %b %Y %H:%M:%S", new_mtime))
        else:
            logging.warn(('Skipping {0} because it did not match timestamp ' +
                          'regex {1}').format(f, args.timestamp_re))


if __name__ == '__main__':
    main()
