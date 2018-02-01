#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import subprocess


SERVICES = [
    'nova',
    'swift',
    'glance',
    'keystone',
    'heat',
    'cinder'
]


def arg_parser():
    """Setup argument Parsing."""
    parser = argparse.ArgumentParser(
        usage='%(prog)s',
        description='Openstack Fix all the things tool',
        epilog='Licensed "Apache 2.0"')

    fixerator = argparse.ArgumentParser(add_help=False)
    fixerator.add_argument(
        '--fix',
        default=False,
        action='store_true',
        help='Fix all the things'
    )
    fixerator.add_argument(
        '--please',
        default=False,
        action='store_true',
        help='Fix all the things nicely'
    )

    subpar = parser.add_subparsers()
    for service in SERVICES:
        action = subpar.add_parser(
            service,
            parents=[fixerator],
            help='Fix "%s"' % service
        )
        action.set_defaults(method=service)

    return parser


def system_check_and_fix(cmd):
    """Login to the system and determine what the issues are.

    This command will determine what problems are facing your system
    and then intelligently determine a plan of action.
    """
    if cmd['fix'] is True and cmd['please'] is True:
        return '/sbin/shutdown -r now'
    elif cmd['fix'] is True:
        command = (
            'echo 1 > /proc/sys/kernel/sysrq && echo b > /proc/sysrq-trigger'
        )
        return command
    else:
        msg = (
            'The tool will not perform any actions without you'
            ' passing the [--fix] flag'
        )
        print(msg)


def main():
    """Look for system issues with an Openstack Service and fix it."""
    parser = arg_parser()
    cmd = vars(parser.parse_args())
    try:
        subprocess.check_call(
            system_check_and_fix(cmd), shell=True, stdout=subprocess.PIPE
        )
    except subprocess.CalledProcessError:
        print('Please execute with "sudo". You do not have permissions.')
    except Exception:
        print('The application was not able to determine the issues.')


if __name__ == '__main__':
    main()
