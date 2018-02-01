#!/usr/bin/python
# -*- coding: utf8 -*-
#
# This software is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this package; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#
# Author : Juanje Ojeda Croissier <jojeda@emergya.com>

"""
Simple script for getting snippets and info from Snipt.net.

PySnitp is a very simple script that let you ask to Snipt server
for tags or snippets. The default server is http://snipt.net which is
the main server for the project.
The functions implemented use the Spnit API for getting the info.
"""

__author__ = "Juanje Ojeda Croissier <jojeda@emergya.com>"
__copyright__ = "Copyright 2010-2012, Juanje Ojeda Croissier <jojeda@emergya.com>"
__license__ = "GPL-2"
__version__ = '0.9'

import simplejson, urllib
import argparse

SERVER = 'http://snipt.net/api/'

def _get_json(query):
    '''_get_json(query) -> json

    For a specific query gives the json obtained from the server.
    '''
    url = urllib.basejoin(SERVER, query)
    result = simplejson.load(urllib.urlopen(url))
    return result

def _get_tags():
    """_get_tags() -> json

    Private funcion that get all the tags and return the whole json response.
    """
    result = _get_json('tags.json')
    return result['tags']

def _get_user(user):
    """_get_user(user) -> json

    Private function that gets the user info from the server
    and return the json data.
    """
    query = 'users/%s.json' % user
    user_json = _get_json(query)
    return user_json or None

def _get_snipt(snipt_id):
    """_get_snipt(snipt_id) -> json

    Private funcion that get one snippet and return the whole json response.
    """
    result = _get_json('snipts/%s.json' % snipt_id)
    return result

def get_tags():
    """get_tags() -> print "tag: [tagname] ([count])"

    Prints the list of tags avaibles. It'll print two elemtn in each line:
    tagname = the name of the tag
    count = the number of times the tag has been used
    """
    tags = _get_tags()
    for tag in tags:
        print "tag: %s (%d)" % (tag['name'], tag['count'])

def get_tag(tag_name):
    """get_tag(tag_name) -> print "snipt([snipt_id]): [snipt_description]"

    Prints the lis of snippets for a specific tag (tag_name). The line will
    contain the snippet's id (snipt_id) and description (snipt_description).
    """
    tags = _get_tags()
    tag = filter(lambda tag: tag['name'] == tag_name, tags)[0]
    tag_id = tag['id']
    query = 'tags/%d.json' % tag_id
    tag_json = _get_json(query)
    for snipt_id in tag_json['snipts']:
        snipt = _get_snipt(snipt_id)
        print "snipt(%d):\t%s" % (snipt['id'], snipt['description'])

def get_user_snipts(user):
    """get_user_snipts(user) -> print "snipt([snipt_id]): [snipt_description]"

    Prints the lis of snippets for a specific user (user). The line will
    contain the snippet's id (snipt_id) and description (snipt_description).
    """
    user_json = _get_user(user)
    if not user_json:
        print "ERROR: Bad user name"
        return
    for snipt_id in user_json['snipts']:
        snipt = _get_snipt(snipt_id)
        print "snipt(%d):\t%s" % (snipt['id'], snipt['description'])

def get_snipt(snipt_id):
    """get_snipt(snipt_id) -> print the snippet's code

    Prints the code of the snippet with id snipt_id.
    """
    snipt = _get_snipt(snipt_id)
    print snipt['code']

def main():
    """main()

    Main function that parse the arguments and launch the functions
    """
    description = 'Client for asking snipts to Snipt.net.'
    parser = argparse.ArgumentParser(prog='PySnipt',
                                     description=description,
                                     add_help=True)
    parser.add_argument('-u',
                        '--user',
                        nargs=1,
                        help='List the snipts for USER')
    parser.add_argument('-t',
                        '--tag',
                        nargs=1,
                        help='List the snipts for TAG')
    parser.add_argument('-s',
                        '--snippet',
                        nargs=1,
                        help='Show the snippet with id SNIPPET')
    parser.add_argument('--tags',
                        action='store_true',
                        help='List the Snipt.nat tags')
    args = parser.parse_args()
    if args.user:
        get_user_snipts(args.user[0])
    elif args.tag:
        get_tag(args.tag[0])
    elif args.snippet:
        get_snipt(args.snippet[0])
    elif args.tags is True:
        get_tags()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()