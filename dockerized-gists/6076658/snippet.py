#!/usr/bin/python
###############################################################################
#
# file:     gmail-count
#
# Purpose:  generates a string value representing the Gmail unread email count.
#
# Usage:    pipe the i3status with this script (see i3status manpage)
#           or use conky.
#
###############################################################################
#
# Copyright 2013 Bruno Braga
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
###############################################################################
#
# Soft Dependencies:
#               * python-gnomekeyring
#               (if you do not want to use it, just remove the keyring import
#               and place the plain password - read below)
#
#               * python-lxml
#               (if not available, will try to parse the hard way)
#
###############################################################################

__NAME__ = 'gmail-count'
"""
Defines the name of this script. Used as the service name of keyring store,
if applicable.
"""

__VERSION__ = 0.1
"""
Defines the version of this script.
"""


#
# Built-in Libraries
#
import urllib2
import sys
import os
import datetime
import optparse
import traceback

# #############################
# CONFIGURABLE SETTINGS: BEGIN
# #############################

#
# First time? Add password to keyring
# keyring.set_password('Gmail', 'bruno.braga@gmail.com', '{password}')
#
# Don't want to use keyring (or don't have it)?
# Just remove the keyring import and replace this password line for your
# raw password (do not recommend doing this, but if you choose to do so,
# remember to change the file permissions to 700 to ensure you alone can
# access it).
#
password  = ''

#
# A cache file to avoid making repetitive queries (which take long) in same
# frequency as i3 status (usually every 5 seconds)
# The expiration is defined in seconds (2 minutes by default).
#
cacheFile = '/tmp/gmail-count.cache'
cacheExpiresNSec = 120

# #############################
# CONFIGURABLE SETTINGS: END
# #############################

verbose = False
username = ''
useCache = True


def dieGracefully(message):
    """
    Exits in error, but outputs a question mark instead of the expected number,
    to inform the user something is wrong. Message will only be printed out if
    in verbose mode.
    """
    if verbose:
        print >> sys.stderr, message
    else:
        print '?'
    sys.exit(1)

def setKeyringPassword():
    """
    Prompts and stores a user password in Gnome Keyring.
    """
    import getpass
    kPassword = getpass.getpass(prompt='Type in password for user [%s]: ' % username)
    if not kPassword or len(kPassword) == 0:
        print 'Must set a valid password'
        sys.exit(1)
    else:
        try:
            import keyring
            keyring.set_password(__NAME__, username, kPassword)
            print "Done."
            sys.exit(0)
        except Exception, e:
            dieGracefully('keyring module not found. See --help for details.')


def parseArgs():

    # override the default parser to allow new lines
    class Parser(optparse.OptionParser):
        def format_epilog(self, formatter):
            return self.epilog

    global username, password, verbose, cacheExpiresNSec, useCache
    parser = Parser(usage="usage: %prog [options]",
        description="A simple Gmail unread count script for i3status or conky \
bars, using simple caching (avoid overhead in simplistic approaches such as \
i3status).",
        version="%%prog %s" % __VERSION__,
        epilog="""
Notes:

This script will attempt to access the account's password in the following manner:
  - if --password is informed, will use it
  - if not, will see if it has been hard-coded within the script (some people
    may prefer that)
  - lastly, if none of the above satisfies, it will retrieve it from keyring,
    if available. To add your password to the keyring, use option --add-keyring

""")
    parser.add_option("-u", "--username", dest="username", action="store",
                      help="The Gmail username (without the gmail.com). \
If Google Apps account, need to inform the complete email address.")

    parser.add_option("-p", "--password", dest="password", action="store",
                      help="The plain text password associated with the \
username. If not informed, this script will try to retrieve it from keyring. \
Alternatively, you can set the password by hand in this script source, if you \
don't want to send it as option. See source code for details.")

    parser.add_option("-r", "--refresh", dest="refresh", action="store",
                      help="minimum period, in seconds, to allow another call \
to Google (this is just to avoid HTTP overhead). Default value is %d. If using \
conky, you can use --no-cache option if you define execution time rules in \
conkyrc." % cacheExpiresNSec)

    parser.add_option("-v", "--verbose", dest="verbose", default=False,
                      action="store_true",
                      help="Used for troubleshooting problems (do not use this \
with output bars, which are usually expecting very few chars).")

    parser.add_option("-a", "--add-keyring", dest="add", default=False,
                      action="store_true",
                      help="Prompts for the password to store it in Gnome \
Keyring. Useful if it is the first time using this script.")

    parser.add_option("-n", "--no-cache", dest="cache", default=True,
                      action="store_false",
                      help="Does not use cache (overrides --refresh option). \
Only use this if you are controlling the calls to this script by yourself or \
another program (such as conky, etc).")

    (options, args) = parser.parse_args()
    verbose = options.verbose
    username = options.username
    useCache = options.cache

    # validate username
    if not username or len(username) == 0:
        dieGracefully("The --username option is required!")

    if options.add:
        setKeyringPassword()

    # validate password
    if not password or len(password) == 0:
        # no passwords stored locally, try to get from options
        password = options.password
        if not password:
            # still nothing, try from keyring
            try:
                import keyring
                password  = keyring.get_password(__NAME__, username)
                if not password:
                    dieGracefully("""Password not available (not in keyring).
Try to either:
    a) use option --password;
    b) add your password to keyring (see --help for details); or
    c) hard-code your password in this script (see password variable).
""")
            except Exception, e:
                dieGracefully("keyring module not found. See --help for details.")

    # validate refresh
    refresh = options.refresh
    if refresh:
        try:
            cacheExpiresNSec = int(refresh)
            if cacheExpiresNSec <= 0:
                dieGracefully("--refresh must be higher than zero!")
        except Exception, e:
            dieGracefully("--refresh must be an integer value, higher than zero.")


def main():
    """
    Executes the main code of this script
    """

    parseArgs()

    # validate settings
    if not username or not password:
        dieGracefully()

    if os.path.exists(cacheFile):
        if datetime.datetime.now() - \
            datetime.datetime.fromtimestamp(os.path.getmtime(cacheFile)) > \
                datetime.timedelta(seconds=cacheExpiresNSec):
            # remove if old enough
            os.remove(cacheFile)
        else:
            if verbose:
                print 'Accessing cache file.'
            # still looks good
            with open(cacheFile, 'r') as f:
                print f.read()
            sys.exit(0)

    url = 'https://mail.google.com/mail/feed/atom'
    try:
        if verbose:
            print 'Refreshing data from Google.'

        ah = urllib2.HTTPBasicAuthHandler()
        ah.add_password('New mail feed', 'https://mail.google.com', username, password)
        op = urllib2.build_opener(ah)
        urllib2.install_opener(op)
        response = urllib2.urlopen('https://mail.google.com/mail/feed/atom')
        contents = response.read().decode('utf-8')
        unread = '?'
        try:
            from  xml.etree.ElementTree import fromstring
            e = fromstring(contents)
            fc = e.find('{http://purl.org/atom/ns#}fullcount')
            unread = fc.text
        except Exception, e:
            # XML parsing failed, do it the hard-way (ugly, but works)
            ifrom = contents.index('<fullcount>') + 11
            ito   = contents.index('</fullcount>')
            unread = contents[ifrom:ito]

        print unread
        # save to cache, if applicable
        if useCache:
            with open(cacheFile, 'w') as f:
                f.write(unread)
            sys.exit(0)
    except Exception, e:
        dieGracefully("Unexpected error has occurred. %s" % traceback.format_exc())


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print # just to avoid password input interruption.
        sys.exit(0)