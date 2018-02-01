#!/usr/bin/env python
#
# Script to check who of your Facebook friends were removed from FB or unfriend
# you.
#
# Requirements
# ============
#
# * Linux / Mac OS X / other Unix
# * `Python <http://www.python.org/>`_ 2.6 or 2.7
# * `xmpppy <http://xmpppy.sourceforge.net/>`_ 0.5.0rc1 or later
#
# Installation
# ============
#
# Just store script somewhere in your ``$PATH``, and give necessary rights to
# execute, like::
#
#     $ chmod +x ~/bin/fb-friends-diff.py
#
# Usage
# =====
#
# ::
#
#     $ fb-friends-diff.py
#     $ fb-friends-diff.py -u FACEBOOK_USERNAME -p FACEBOOK_PASSWORD
#     $ fb-friends-diff.py -d /path/to/database.file
#
# Configuration
# =============
#
# The easiest way to configure script is storing all available options in
# ``~/.config/fb-friends-diff/fb-friends-diff.conf`` file in ini format which
# later would be read with ``ConfigParser`` library. This should looks
# something next::
#
#     [DEFAULT]
#     username = FACEBOOK_USERNAME
#     password = FACEBOOK_PASSWORD
#     database = /path/to/database.file
#
# .. note:: Don't forget to wrap configuration in ``[DEFAULT]`` section, cause
#    ``ConfigParser`` doesn't understand files without any sections.
#
# By default, ``~/.config/fb-friends-diff/fb-friends-diff.db`` path would be
# used for database file.
#
# Also as password would be stored as raw text its good idea to disable all
# other users to read ``~/.config/fb-friends-diff/fb-friends-diff.conf`` file.
#
# Changelog
# =========
#
# 0.2
# ---
#
# + Do not diff when friend changed name on Facebook
#
# 0.1
# ---
#
# * Initial release
#

import getpass
import json
import os
import socket
import sys

try:
    import argparse
except ImportError:
    import optparse
    ArgumentParser = optparse.OptionParser
    add_argument = lambda parser, *args, **kwargs: \
                       parser.add_option(*args, **kwargs)
else:
    ArgumentParser = argparse.ArgumentParser
    add_argument = lambda parser, *args, **kwargs: \
                       parser.add_argument(*args, **kwargs)

from ConfigParser import Error as ConfigParserError, RawConfigParser

try:
    import xmpp
except ImportError:
    print('Python xmpp library is required! You can install it with pip ' \
          'as:\n\n    $ pip install xmpp\n')
    sys.exit(1)


__author__ = 'Igor Davydenko'
__license__ = 'MIT License'
__script__ = 'fb-friends-diff'
__version__ = (0, 2)

DIRNAME = os.path.expanduser('~/.config/%s' % __script__)
rel = lambda *parts: os.path.abspath(os.path.join(DIRNAME, *parts))
sort_by_name = lambda x, y: cmp(x[1], y[1])


class Database(object):
    """
    Simple class to operate with json key-value store, where friends would be
    stored.
    """
    __slots__ = ('handler', 'name')

    def __init__(self, name):
        """
        Setup database name.
        """
        self.handler, self.name = None, name

    def connect(self):
        """
        Try to initiate connection to the database using defined name.

        If cannot connect to database (maybe cause of IO error) - exit from the
        script.
        """
        try:
            self.handler = open(self.name, 'r+')
        except (IOError, OSError):
            try:
                handler = open(self.name, 'w+')
            except (IOError, OSError):
                print('Cannot open database file at %r. Please, check your ' \
                      'permissions there. Exit...')
                sys.exit(1)
            else:
                self.handler = open(self.name, 'r+')
        finally:
            self.handler.seek(0)

    def get_friends(self):
        """
        Read all available friends from database.
        """
        assert self.handler, 'Please, connect to database first.'
        self.handler.seek(0)
        content = self.handler.read()
        return json.loads(content.strip() or '[]')

    def save_friends(self, friends):
        """
        Save friends list to database.
        """
        assert self.handler, 'Please, connect to database first.'
        self.handler.close()

        handler = open(self.name, 'w+')
        handler.write(json.dumps(friends))
        handler.close()

        self.connect()


class Facebook(object):
    """
    Simple class to work with Facebook over XMPP protocol.
    """
    __slots__ = ('_jid_cache', 'client', 'password', 'server', 'username')

    server = 'chat.facebook.com'

    def __init__(self, username, password):
        """
        Remember your Facebook username and password as instance attributes.
        """
        self.client = None
        self.username = username
        self.password = password

    def connect(self):
        """
        Tries to connect to the Facebook using stored credentials.

        If cannot - exit from the script.
        """
        hostname = socket.gethostname()
        client = xmpp.Client(self.jid.getDomain(), debug=[])
        server = (self.server, 5222)

        if not client.connect(server):
            print('Cannot connect to %s server. Please, check your internet ' \
                  'connection. Exit...' % self.server)
            sys.exit(1)

        if not client.auth(self.jid.getNode(), self.password, hostname):
            print('Cannot authenticate %s user. Please, check your ' \
                  'credentials. Exit...' % self.username)
            sys.exit(1)

        self.client = client

    @property
    def jid(self):
        """
        Combine username and password into the JID.
        """
        if not hasattr(self, '_jid_cache'):
            jid = self.username + '@' + self.server
            setattr(self, '_jid_cache', xmpp.JID(jid))
        return getattr(self, '_jid_cache')

    def get_friends(self):
        """
        Read all possible friends from existed Facebook connection.
        """
        assert self.client, 'Please, connect to Facebook first.'

        friends = []
        roster = self.client.getRoster()
        keys = roster.keys()

        for key in keys:
            item = roster[key]

            if not item['name']:
                continue

            friends.append((key, item['name']))

        return friends


def get_options():
    """
    Read options from command line or from configuration file.
    """
    default_database = rel('%s.db' % __script__)
    names = ('database', 'password', 'username')
    result = {}

    # At first, read options from command line
    args = sys.argv[1:]
    description = 'Script to check who of your Facebook friends were removed '\
                  'from FB or unfriend you.'

    parser = ArgumentParser(description=description)
    add_argument(parser, '-u', '--username', default=None, dest='username',
        metavar='FACEBOOK_USERNAME')
    add_argument(parser, '-p', '--password', default=None, dest='password',
        metavar='FACEBOOK_PASSWORD')
    add_argument(parser, '-d', '--database', default=None, dest='database',
        help='Path to database. By default: %s' % default_database)

    try:
        options, _ = parser.parse_args(args)
    except TypeError:
        options = parser.parse_args(args)

    for name in names:
        result.update({name: getattr(options, name, None)})

    # Next, check for configuration file values
    if not result['password'] or not result['username']:
        config_file = rel('%s.conf' % __script__)
        config_parser = RawConfigParser()

        try:
            config_parser.read(config_file)
        except ConfigParserError:
            pass
        else:
            values = config_parser.defaults()

            for name in names:
                if name == 'database' and result['database']:
                    continue
                result.update({name: values.get(name)})

    # Finally, get ability to input configuration
    for name in ('username', 'password'):
        if result[name]:
            continue
        func = getpass.getpass if name == 'password' else raw_input
        result.update({name: func('Facebook %s: ' % name)})

    if not result['database']:
        result['database'] = default_database

    return result.copy()


def main():
    """
    Read script settings from command line or from configuration file, initiate
    connection to Facebook, read fresh list of friends and compare with
    existed friends and show diff.
    """
    options = get_options()

    facebook = Facebook(options['username'], options['password'])
    facebook.connect()

    database = Database(options['database'])
    database.connect()

    fb_friends = set(facebook.get_friends())
    db_friends = set(map(tuple, database.get_friends()))

    fb_jids = set(map(lambda item: item[0], fb_friends))
    db_jids = set(map(lambda item: item[0], db_friends))

    diff_jids = list(db_jids.symmetric_difference(fb_jids))
    raw_diff_jids = list(db_jids.difference(fb_jids))
    union = list(db_friends.union(fb_friends))

    db_friends, fb_friends = dict(db_friends), dict(fb_friends)
    diff = []

    for friend_jid in diff_jids:
        friend_name = fb_friends.get(friend_jid, db_friends.get(friend_jid))

        if not friend_name:
            continue

        diff.append((friend_jid, friend_name))

    if diff and db_friends:
        diff.sort(sort_by_name)
        print('Difference between last sync are %d friends:\n' % len(diff))

        for friend_jid, friend_name in diff:
            label = '-' if friend_jid in raw_diff_jids else '+'

            friend_id, _ = friend_jid.split('@')
            friend_id = abs(int(friend_id))

            url = 'https://www.facebook.com/profile.php?id=%d' % friend_id
            print(u'%s | %55s | %s' % (label, url, friend_name))

        print('\nAll OK!')
    elif not db_friends:
        print('Initiate friends database...')
    else:
        print('No difference between last sync...')

    database.save_friends(sorted(union, sort_by_name))


if __name__ == '__main__':
    main()
