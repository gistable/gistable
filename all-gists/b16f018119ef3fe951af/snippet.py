#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2013 deanishe@deanishe.net.
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2013-11-01
#

"""workflow-build [options] <workflow-dir>

Build Alfred Workflows.

Compile contents of <workflow-dir> to a ZIP file (with extension
`.alfredworkflow`).

The name of the output file is generated from the workflow name,
which is extracted from the workflow's `info.plist`. If a `version`
file is contained within the workflow directory, it's contents
will be appended to the compiled workflow's filename.

Usage:
    workflow-build [-v|-q|-d] [-f] [-n] [-o <outputdir>] <workflow-dir>...
    workflow-build (-h|--version)

Options:
    -o, --output=<outputdir>    Directory to save workflow(s) to.
                                Default is current working directory.
    -f, --force                 Overwrite existing files.
    -n, --dry-run               Only show files that would be included
                                in workflow. Don't build anything.
    -h, --help                  Show this message and exit.
    -V, --version               Show version number and exit.
    -q, --quiet                 Only show errors and above.
    -v, --verbose               Show info messages and above.
    -d, --debug                 Show debug messages.

"""

from __future__ import print_function

from contextlib import contextmanager
from fnmatch import fnmatch
import logging
import os
import plistlib
import re
from subprocess import check_call, CalledProcessError
import string
import sys
from unicodedata import normalize

from docopt import docopt

__version__ = "0.5"
__author__ = "Dean Jackson <deanishe@deanishe.net>"

DEFAULT_LOG_LEVEL = logging.WARNING

# Characters permitted in workflow filenames
OK_CHARS = set(string.ascii_letters + string.digits + '-.')

EXCLUDE_PATTERNS = [
    '.*',
    '*.pyc',
    '*.log',
    '*.acorn',
    '*.swp',
    '*.bak',
    '*.sublime-project',
    '*.sublime-workflow',
    '*.git',
    '*.dist-info',
    '*.egg-info',
]

log = logging.getLogger('')


@contextmanager
def chdir(dirpath):
    """Context-manager to change working directory."""
    startdir = os.path.abspath(os.curdir)
    os.chdir(dirpath)
    log.debug('cwd=%s', dirpath)

    yield

    os.chdir(startdir)
    log.debug('cwd=%s', startdir)


class TechnicolorFormatter(logging.Formatter):
    """Intelligent and pretty log formatting.

    Colourise output to a TTY and prepend logging level name to
    levels other than INFO.

    """

    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

    RESET = '\033[0m'
    COLOUR_BASE = '\033[1;{:d}m'
    BOLD = '\033[1m'

    LEVEL_COLOURS = {
        logging.DEBUG: BLUE,
        logging.INFO: WHITE,
        logging.WARNING: YELLOW,
        logging.ERROR: MAGENTA,
        logging.CRITICAL: RED
    }

    def __init__(self, fmt=None, datefmt=None, technicolor=True):
        """Create new Formatter.

        Args:
            fmt (str): A `logging.Formatter` format string.
            datefmt (str): `strftime` format string.
            technicolor (bool): Colourise TTY output?

        """
        logging.Formatter.__init__(self, fmt, datefmt)
        self.technicolor = technicolor
        self._isatty = sys.stderr.isatty()

    def format(self, record):
        """Format (and colourise) log record.

        Prepend log level for levels other than INFO.
        Colourise level names for TTY output.

        """
        # Output `INFO` messages without level name.
        # The idea is to treat them as normal status messages.
        if record.levelno == logging.INFO:
            msg = logging.Formatter.format(self, record)
            return msg

        # Other levels have their level name colourised if
        # the destination is a TTY.
        if self.technicolor and self._isatty:
            colour = self.LEVEL_COLOURS[record.levelno]
            bold = (False, True)[record.levelno > logging.INFO]
            levelname = self.colourise('{:9s}'.format(record.levelname),
                                       colour, bold)
        else:
            levelname = '{:9s}'.format(record.levelname)

        return (levelname + logging.Formatter.format(self, record))

    def colourise(self, text, colour, bold=False):
        """Surround `text` with terminal colours."""
        colour = self.COLOUR_BASE.format(colour + 30)
        output = []
        if bold:
            output.append(self.BOLD)
        output.append(colour)
        output.append(text)
        output.append(self.RESET)
        return ''.join(output)


def init_logging():
    """Set up logging handlers, add and configure global `log`."""
    # console output
    console = logging.StreamHandler()
    formatter = TechnicolorFormatter('%(message)s')
    console.setFormatter(formatter)
    console.setLevel(logging.DEBUG)

    log.addHandler(console)


def safename(name):
    """Make name filesystem and web-safe."""
    if isinstance(name, str):
        name = unicode(name, 'utf-8')

    # remove non-ASCII
    s = normalize('NFD', name)
    b = s.encode('us-ascii', 'ignore')

    clean = []
    for c in b:
        if c in OK_CHARS:
            clean.append(c)
        else:
            clean.append('-')

    return re.sub(r'-+', '-', ''.join(clean)).strip('-')


def get_workflow_files(dirpath):
    """Return all files to be included in the workflow."""
    paths = []
    for root, dirnames, filenames in os.walk('.'):

        # Remove directories that match EXCLUDE_PATTERNS.
        # Iterate through them in reverse, so as not to mess with
        # the indexing
        for i in range(len(dirnames) - 1, -1, -1):
            dn = dirnames[i]
            for pat in EXCLUDE_PATTERNS:
                if fnmatch(dn, pat):
                    log.debug('- [%s] %s', pat, dn)
                    del dirnames[i]

        # Process filenames within accepted directories
        for fn in filenames:
            p = os.path.join(root, fn)
            for pat in EXCLUDE_PATTERNS:
                if fnmatch(fn, pat):
                    log.debug('- [%s] %s', pat, fn)
                    break

            else:  # didn't match any patterns
                paths.append(p)

    return paths


def build_workflow(workflow_dir, outputdir, overwrite=False, verbose=False,
                   dry_run=False):
    """Create an .alfredworkflow file from the contents of `workflow_dir`."""
    with chdir(workflow_dir):
        # ------------------------------------------------------------
        # Read workflow metadata from info.plist
        info = plistlib.readPlist(u'info.plist')
        version = None
        if not os.path.exists(u'info.plist'):
            log.error(u'info.plist not found')
            return False

        if 'version' in info and info.get('version'):
            version = info['version']

        elif os.path.exists('version'):
            with open('version') as fp:
                version = fp.read().strip().decode('utf-8')

        name = safename(info['name'])
        zippath = os.path.join(outputdir, name)
        if version:
            zippath = '{}-{}'.format(zippath, version)

        zippath += '.alfredworkflow'

        # ------------------------------------------------------------
        # Workflow files
        wffiles = get_workflow_files('.')
        if dry_run:
            print('workflow directory: ' + os.path.abspath(os.curdir))
            print('workflow file: ' + zippath)
            print('contents:')
            for p in wffiles:
                print(p)
            return

        # ------------------------------------------------------------
        # Build workflow
        if os.path.exists(zippath):
            if overwrite:
                log.info('overwriting existing workflow')
                os.unlink(zippath)
            else:
                log.error('File "%s" exists. Use -f to overwrite', zippath)
                return False

        # build workflow
        command = ['zip']
        if not verbose:
            command.append(u'-q')

        command.append(zippath)

        for p in wffiles:
            command.append(p)

        log.debug('command=%r', command)

        try:
            check_call(command)
        except CalledProcessError as err:
            log.error('zip exited with %d', err.returncode)
            return False

        log.info('wrote %s', zippath)

    return True


def main(args=None):
    """Run CLI."""
    # ------------------------------------------------------------
    # CLI flags
    args = docopt(__doc__, version=__version__)
    init_logging()

    if args.get('--verbose'):
        log.setLevel(logging.INFO)
    elif args.get('--quiet'):
        log.setLevel(logging.ERROR)
    elif args.get('--debug'):
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(DEFAULT_LOG_LEVEL)

    log.debug('log level=%s', logging.getLevelName(log.level))
    log.debug('args=%r', args)

    # Build options
    dry_run = args['--dry-run']
    force = args['--force']
    outputdir = os.path.abspath(args['--output'] or os.curdir)
    workflow_dirs = [os.path.abspath(p) for p in args['<workflow-dir>']]
    verbose = log.level == logging.DEBUG

    log.debug(u'outputdir=%r, workflow_dirs=%r', outputdir, workflow_dirs)

    # ------------------------------------------------------------
    # Build workflow(s)
    errors = False
    for path in workflow_dirs:
        ok = build_workflow(path, outputdir, force, verbose, dry_run)
        if not ok:
            errors = True

    if errors:
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
