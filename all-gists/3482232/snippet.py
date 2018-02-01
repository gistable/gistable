#!/usr/bin/env python
"""
Lint python files before commit with flake8 and pep8 lint tools.

You can define lint settings in '.pep8' file in the project root.
Section '[pep8]' if for pep8 linter, and section '[flake8]' is for flake8.

INSTALL:
1. sudo pip install flake8 pep8
2. Save this file to '.git/hooks/pre-commit' file in your git repository
3. Enjoy

TODO:
- Remove pep8 lint after flake8 will be updated (E127, E128 not recognized now)
"""
import os
import sys
import subprocess
import ConfigParser


# available settings list
AVAILABLE_SETTINGS = (
    'exclude', 'filename', 'select', 'ignore', 'max-line-length', 'count',
    'quiet', 'show-pep8', 'show-source', 'statistics', 'verbose'
)
SETTINGS_WITH_PARAMS = (
    'exclude', 'filename', 'select', 'ignore', 'max-line-length', 'format'
)
# colorize output
COLOR = {
    'red': '\033[1;31m',
    'green': '\033[1;32m',
    'yellow': '\033[1;33m',
    'off': '\033[1;m'
}


def parse_settings(config_file):
    """
    Get pep8 and flake8 lint settings from config file.
    Useful for define per-project lint options.
    """
    settings = {'pep8': list(), 'flake8': list()}

    # read project settings
    if not os.path.exists(config_file) or not os.path.isfile(config_file):
        return settings

    try:
        config = ConfigParser.ConfigParser()
        config.read(config_file)
    except ConfigParser.MissingSectionHeaderError, e:
        print "ERROR: project lint config file is broken:\n"
        print repr(e)
        sys.exit(1)

    # read project lint settings for pep8 and flake8
    for linter in settings.keys():
        try:
            for key, value in config.items(linter):
                if key in AVAILABLE_SETTINGS:
                    if key in SETTINGS_WITH_PARAMS:
                        settings[linter].append("--%s=%s" % (key, value))
                    else:
                        settings[linter].append("--%s" % key)
                else:
                    print "WARNING: unknown %s linter config: %s" % (
                        linter, key)
        except ConfigParser.NoSectionError:
            pass

    return settings


def system(*args, **kwargs):
    """
    Run system command.
    """
    kwargs.setdefault('stdout', subprocess.PIPE)
    proc = subprocess.Popen(args, **kwargs)
    out, err = proc.communicate()
    return out


def get_changed_files():
    """
    Get python files from 'files to commit' git cache list.
    """
    files = []
    filelist = system('git', 'diff', '--cached', '--name-status').strip()
    for line in filelist.split('\n'):
        action, filename = line.strip().split()
        if filename.endswith('.py') and action != 'D':
            files.append(filename)
    return files


def lint(cmd, files, settings):
    """
    Run pep8 or flake8 lint.
    """
    if cmd not in ('pep8', 'flake8'):
        raise Exception("Unknown lint command: %s" % cmd)
    args = settings[:]
    args.insert(0, cmd)
    args.extend(files)
    return filter(None, system(*args).strip().split('\n'))


def main():
    """
    Do work
    """
    files = get_changed_files()
    if not files:
        print "Python lint: %(yellow)sSKIP%(off)s" % COLOR
        return

    config_file = os.path.join(os.path.abspath(os.curdir), '.pep8')
    settings = parse_settings(config_file)

    errors = lint('flake8', files, settings['flake8'])

    # TODO: remove pep8 lint when flake8 will be updated (see E127, E128)
    for err in lint('pep8', files, settings['pep8']):
        divider = err.find(' ', err.find(' ') + 1)
        pep8_error = err[0:divider]
        if not any(error[0:divider] == pep8_error for error in errors):
            errors.append(err)

    if not errors:
        print "Python lint: %(green)sOK%(off)s" % COLOR
        return

    print "Python lint: %(red)sFAIL%(off)s" % COLOR
    print
    print "\n".join(sorted(errors))
    print
    print "Aborting commit due to python lint errors."
    sys.exit(1)


if __name__ == '__main__':
    main()
