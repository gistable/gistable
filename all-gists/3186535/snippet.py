#!/usr/bin/env python

"""
Saves URL(s) to a user's Pocket queue.
It accepts either command line arguments or a URL from the OS X clipboard.
For information about Pocket see http://getpocket.com/
"""

import optparse
import subprocess
import urllib
import urllib2


# Fill these variable in with your own Pocket credentials.
POCKET_APIKEY = '<apikey>'
POCKET_USERNAME = '<username>'
POCKET_PASSWORD = '<password>'


def save_url(url, username=POCKET_USERNAME, password=POCKET_PASSWORD,
             apikey=POCKET_APIKEY, verbose=False):
    """Saves a URL to a user's Pocket queue."""
    params = dict(url=url, username=username, password=password, apikey=apikey)
    payload = urllib.urlencode(params)
    urllib2.urlopen('https://readitlaterlist.com/v2/add', payload)

    if verbose:
        print 'Saved URL: %s' % url


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-c', action='store_true', dest='clipboard',
                      help='save a URL from the clipboard')
    parser.add_option('-v', action='store_true', dest='verbose', default=True,
                      help='show status of URL save')
    (options, args) = parser.parse_args()

    # Save URLs supplied as command line arguments.
    for arg in args:
        save_url(arg, verbose=options.verbose)

    # Save URL from clipboard, if specified.
    if options.clipboard:
        clipboard = subprocess.check_output('pbpaste')
        save_url(clipboard, verbose=options.verbose)