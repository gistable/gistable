#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Copyright 2015 François Charlier <francois.charlier@enovance.com>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

#
# This is a simple script to call the TargetProcess REST API to get time
# entries for the authenticated user for the current day from a configured
# targetprocess instance (use `-h` to get more options).
#

from datetime import date, timedelta
import os
import os.path
from prettytable import PrettyTable
import requests
import shlex
import subprocess
import sys
import yaml


DAYSMAP = {
    'mon': 0,
    'tue': 1,
    'wed': 2,
    'thu': 3,
    'fri': 4
}


class TPConfig(object):
    def __init__(self):
        if not os.path.exists(TPConfig.config_path()):
            print("No configuration file found! Will exit now.\n")
            do_help()
            exit(1)

        with open(TPConfig.config_path()) as config_file:
            self.conf = yaml.load(config_file)

    def __getattr__(self, item):
        return self.conf[item]

    @classmethod
    def config_path(cls):
        xdg_config_home = os.environ.get('XDG_CONFIG_HOME', '~/.config')
        config_path = os.path.join(xdg_config_home, 'targetprocess.yaml')
        config_path = os.path.expandvars(os.path.expanduser(config_path))
        return config_path

    @property
    def auth_password(self):
        if self.auth_provider == 'command':
            return self.auth_password_command()
        elif self.auth_provider == 'yaml':
            return self.conf['auth_password']

    def auth_password_command(self):
        # The command should return the password on one line
        password = subprocess.check_output(shlex.split(self.auth_command))
        return password.decode('utf-8').strip()


class TPClient(object):
    def __init__(self):
        self.conf = TPConfig()

    def time_entries(self, date, user=None, span='day'):
        if user is None:
            user = self.conf.auth_user

        if span == 'day':
            PAYLOAD = {
                'format': 'json',
                'where': "(User.Email eq '%s') and (Date eq '%s')" % (
                    user,
                    date.isoformat()
                )
            }
        elif span == 'week':
            PAYLOAD = {
                'format': 'json',
                'orderby': 'Date',
                'where': "(User.Email eq '%s') and (Date gte '%s') "
                         "and (Date lt '%s')" % (
                             user,
                             date.isoformat(),
                             (date + timedelta(5)).isoformat()
                         )
            }

        r = requests.get(
            'https://%s/api/v1/Times' % (self.conf.tp_instance),
            auth=(self.conf.auth_user, self.conf.auth_password),
            params=PAYLOAD
        )

        return r.json()['Items']


def relativedays(diff):
    """Returns the previous named day or diff days from now"""
    if diff in DAYSMAP:
        previous = -7
        if DAYSMAP[diff] < date.today().weekday():
            previous = 0
        return date.today() + timedelta(DAYSMAP[diff]
                                        - date.today().weekday()
                                        + previous)
    else:
        return date.today() + timedelta(int(diff))


def startofweek(diff):
    """Returns the start of the week starting diff weeks from now"""
    return date.today() - timedelta(date.today().weekday() - 7 * int(diff))


def to_date(json_date):
    str_ts = json_date.replace('/Date(', '').replace(')/', '')
    (ts, tz) = str_ts.split('-')
    return date.fromtimestamp(int(ts)/1000)


def do_conf():
    if os.path.exists(TPConfig.config_path()):
        print("ERROR: configuration file exists in %s. Won't overwrite"
              % TPConfig.config_path())
    else:
        with open(TPConfig.config_path(), 'w') as config:
            config.writelines([
                'tp_instance: <instance>.tpondemand.com\n',
                'auth_user: <email@example.com>\n',
                'auth_provider: <embedded|command>\n',
                '# use auth_command with "command" auth_provider\n',
                '# auth_command: <some command that returns the password on '
                'one line>\n',
                '# use auth_password with "embedded" auth_provider\n',
                '# auth_password: <tpondemand password>\n'
            ])
            print("Skeleton configuration file created in %s. Please edit "
                  "before running again." % TPConfig.config_path())


def do_help():
    print("Usage: %s [<-X>|<day name>]" % sys.argv[0])
    print(" - <X> being an integer, will return time entries for X days ago")
    print(" - <day name> in 'mon' 'tue' 'wed' 'thu' 'fri', returns time "
          "entries for the previous named-day")
    print(" - default to returning the current day time entries")
    print("")
    print("Usage: %s -w [<-X>]" % sys.argv[0])
    print(" - <X> being an integer, will return time entries for X weeks ago")
    print(" - default to returning the current week time entries")
    print("")
    print("Usage: %s --make-config" % sys.argv[0])
    print(" - creates a configuration template in $XDG_HOME or ~/.config/"
          "targetprocess.yml")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', 'help']:
            do_help()
            exit(1)
        if sys.argv[1] in ['--make-config']:
            do_conf()
            exit(1)
        if sys.argv[1] in ['-w', '--week']:
            span = 'week'
            if len(sys.argv) > 2:
                dt = startofweek(sys.argv[2])
            else:
                dt = startofweek('0')
            label = ' week starting '
        else:
            span = 'day'
            dt = relativedays(sys.argv[1])
            label = ''
    else:
        span = 'day'
        dt = date.today()
        label = ''

    client = TPClient()
    entries = client.time_entries(dt, user=None, span=span)

    table = PrettyTable(['Date', 'Project', 'Description', 'Spent'])
    table.float_format = '.1'
    date_prev = None
    for entry in entries:
        if date_prev is not None and date_prev != entry['Date']:
            table.add_row(['-----']*4)
        date_prev = entry['Date']
        table.add_row([
            to_date(entry['Date']),
            entry['Project']['Name'],
            entry['Description'],
            entry['Spent']
        ])

    total_time = sum(entry['Spent'] for entry in entries)

    print("Time entries for%s: %s %s" % (label,
                                         dt.strftime('%A'),
                                         dt.isoformat()))
    print(table)
    print("Total spent time: %.1f" % total_time)
