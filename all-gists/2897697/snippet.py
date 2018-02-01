#!/usr/bin/env python
# coding: utf-8

import os
import shlex
from subprocess import Popen, PIPE


def execute_in_virtualenv(virtualenv_name, commands):
    '''Execute Python code in a virtualenv, return its stdout and stderr.'''
    command_template = '/bin/bash -c "source {}/{}/bin/activate && python -"'
    command = shlex.split(command_template.format(os.environ['WORKON_HOME'],
                                                  virtualenv_name))
    process = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    return process.communicate(commands)


if __name__ == '__main__':
    from textwrap import dedent


    virtualenv_name = 'pypln'
    commands = dedent(r'''
        import sys

        try:
            import rdfextras
            print 'Imported successfully'
        except:
            print 'Cannot import'

        sys.stderr.write('testing stderr\n')
        ''')
    stdout, stderr = execute_in_virtualenv(virtualenv_name, commands)
    print 'stdout:'
    print stdout
    print '\nstderr:'
    print stderr