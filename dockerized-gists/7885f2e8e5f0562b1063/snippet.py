#!/usr/bin/env python

from __future__ import print_function

from sys import stderr

from pip import get_installed_distributions
from pip.commands import install
from pip.exceptions import InstallationError

print_error = lambda error: print(
    '{0}: {1}'.format(error.__class__.__name__, error.message),
    file=stderr
)

if __name__ == '__main__':
    print('Trying to upgrade all python packages (using pip)')

    install_cmd = install.InstallCommand()
    for package in get_installed_distributions():
        options, args = install_cmd.parse_args([package.project_name])
        options.upgrade = True
        print('Attempting to upgrade: {project_name!r}'.format(project_name=package.project_name))
        try:
            install_cmd.run(options, args)
        except OSError as e:
            if e.errno == 13:  # permissions error
                raise
            print_error(e)
        except (InstallationError, IOError) as e:
            print_error(e)
