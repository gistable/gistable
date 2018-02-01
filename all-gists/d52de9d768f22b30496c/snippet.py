#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Cliff sample app
    ~~~~~~~~~~~~~~~~
"""

import os
import sys
import logging
from cliff.app import App
from cliff.commandmanager import CommandManager
from cliff.command import Command
from cliff.show import ShowOne
from cliff.lister import Lister


class AWS(Command):
    "A simple command that prints a message."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(AWS, self).get_parser(prog_name)
        subparser1 = parser.add_subparsers(help='sub-command help')

        # add a subcommand
        parser_a = subparser1.add_parser('dns', help='dns help')
        #parser_a.add_argument('value', type=str, help='value help')


        # add a subcommand of a subcommand
        subparser2 = parser_a.add_subparsers(help='child sub-command help')
        parser_b = subparser2.add_parser('ipv4', help='ipv4 help')
        parser_b.add_argument('ipval', type=str, help='value help')

        return parser

    def take_action(self, parsed_args):
        self.log.info('sending greeting')
        self.log.debug('debugging')
        self.app.stdout.write('AWS FILED \n')


class LibcloudCLI(App):
    log = logging.getLogger(__name__)

    def __init__(self):
        command = CommandManager('libcloudcli.app')
        super(LibcloudCLI, self).__init__(
            description='sample app',
            version='0.1',
            command_manager=command,
        )
        commands = {
            'aws': AWS,
        }
        for k, v in commands.iteritems():
            command.add_command(k, v)


    def initialize_app(self, argv):
        self.log.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    app = LibcloudCLI()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))


output:

(manage) aws dns ipv4 -h
usage: aws dns ipv4 [-h]

optional arguments:
  -h, --help  show this help message and exit
