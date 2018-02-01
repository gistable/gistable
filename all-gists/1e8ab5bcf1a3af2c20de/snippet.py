"""dbox_sync.py
One-way sync of local directory to Dropbox using Dropbox API V2 and python3.

Dependencies:

- dropbox (`pip3 install dropbox`)

Minimal modifications from:
https://github.com/dropbox/dropbox-sdk-python/blob/master/example/updown.py

Example config.ini:

```
[DBOX_SYNC]
DROPBOX_TOKEN = asdf
SOURCE_DIR = /home/user/scans
DBOX_DIR = stuff/scans
CLEAN_OLD = true
```

"""

import argparse
import contextlib
import datetime
import os
import sys
import time
import unicodedata
import dropbox
import configparser
import logging

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s %(name)-12s %(lineno)d %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
    )

logger_name = str(__file__) + " :: " + str(__name__)
logger = logging.getLogger(logger_name)
logging.getLogger("requests").setLevel(logging.WARNING)


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Config file')
    parser.add_argument('--source', help='Local directory to upload')
    parser.add_argument('--dest', help='Destination folder in your Dropbox')
    parser.add_argument('--token', help='Access token (see '
                        'https://www.dropbox.com/developers/apps)')
    parser.add_argument('--yes', '-y', action='store_true',
                        help='Answer yes to all questions')
    parser.add_argument('--no', '-n', action='store_true',
                        help='Answer no to all questions')
    parser.add_argument('--clean', action='store_true',
                        help='Delete files that have been successfully '
                        'uploaded')
    parser.add_argument('--default', '-d', action='store_true',
                        help='Take default answer on all questions')

    args = parser.parse_args()
    main(args=args)


def main(args=None):
    """Main program.

    Parse command line, then iterate over files and directories under
    rootdir and upload all files.  Skips some temporary files and
    directories, and avoids duplicate uploads by comparing size and
    mtime with the server.
    """

    if args is None:
        args = {}

    if args.config:
        config_locs = args.config
    else:
        config_locs = [
                'config.ini',
                '/etc/dbox_sync/config.ini',
                'instance/config.ini',
                os.path.join(os.path.expanduser('~'), '.dbox_sync_config.ini')
                ]
    config = configparser.ConfigParser()
    config.read(config_locs)
    if not config.has_section('DBOX_SYNC'):
        config['DBOX_SYNC'] = {}

    config = config['DBOX_SYNC']
    logger.debug(config)

    # args.foo should never be inappropriately falsey; even if directory named
    # `0`; bool("0") == True
    token = args.token or config.get('DROPBOX_TOKEN')
    source_dir = args.source or config.get('SOURCE_DIR')

    # Use empty string instead of None to avoid getting cast to string which
    # results in extra folders named "None", e.g. `"{}".format(None) == "None"`
    dbox_dir = args.dest or config.get('DBOX_DIR') or ""

    # An option to delete files that are confirmed to already be uploaded
    # (matching metadata)
    #
    # FIXME -- if args.clean == False, this doesn't respect that due to or
    clean_old = args.clean or config.getboolean('CLEAN_OLD')

    if sum([bool(b) for b in (args.yes, args.no, args.default)]) > 1:
        logger.error('At most one of --yes, --no, --default is allowed')
        sys.exit(2)
    if not token:
        logger.error('--token is mandatory')
        sys.exit(2)

    logger.debug('Dropbox folder name: {}'.format(dbox_dir))
    logger.debug('Local directory: {}'.format(source_dir))
    if not os.path.isdir(source_dir):
        logger.error('{} does not exist or is not a folder'.format(source_dir))
        sys.exit(1)

    dbx = dropbox.Dropbox(token)

    for dirname, dirs, files in os.walk(source_dir):
        subfolder = dirname[len(source_dir):].strip(os.path.sep)
        listing = list_folder(dbx, dbox_dir, subfolder)
        logger.debug('Descending into {}...'.format(subfolder))

        # First do all the files.
        for name in files:
            fullname = os.path.join(dirname, name)
            nname = unicodedata.normalize('NFC', name)
            if name.startswith('.'):
                logger.debug('Skipping dot file: {}'.format(name))
            elif name.startswith('@') or name.endswith('~'):
                logger.debug('Skipping temporary file: {}'.format(name))
            elif name.endswith('.pyc') or name.endswith('.pyo'):
                logger.debug('Skipping generated file: {}'.format(name))
            elif nname in listing:
                md = listing[nname]
                mtime = os.path.getmtime(fullname)
                mtime_dt = datetime.datetime(*time.gmtime(mtime)[:6])
                size = os.path.getsize(fullname)
                if (isinstance(md, dropbox.files.FileMetadata) and
                        mtime_dt == md.client_modified and size == md.size):
                    logger.debug('{} is already synced [stats '
                                 'match]'.format(name))
                    if clean_old:
                        os.remove(fullname)
                else:
                    logger.debug('{} exists with different stats, '
                                 'downloading'.format(name))
                    res = download(dbx, dbox_dir, subfolder, name)
                    with open(fullname, 'rb') as f:
                        data = f.read()
                    if res == data:
                        logger.debug('{} is already synced [content '
                                     'match]'.format(name))
                        if clean_old:
                            os.remove(fullname)
                    else:
                        logger.debug('{} has changed since last '
                                     'sync'.format(name))
                        if yesno('Refresh {}'.format(name), False, args):
                            upload(dbx, fullname, dbox_dir, subfolder, name,
                                   overwrite=True)
            elif yesno('Upload {}'.format(name), True, args):
                upload(dbx, fullname, dbox_dir, subfolder, name)

        # Then choose which subdirectories to traverse.
        keep = []
        for name in dirs:
            if name.startswith('.'):
                logger.debug('Skipping dot directory: {}'.format(name))
            elif name.startswith('@') or name.endswith('~'):
                logger.debug('Skipping temporary directory: {}'.format(name))
            elif name == '__pycache__':
                logger.debug('Skipping generated directory: {}'.format(name))
            elif yesno('Descend into {}'.format(name), True, args):
                logger.debug('Keeping directory: {}'.format(name))
                keep.append(name)
            else:
                logger.debug('OK, skipping directory: {}'.format(name))
        dirs[:] = keep


def list_folder(dbx, dbox_dir, subfolder):
    """List a folder.

    Return a dict mapping unicode filenames to FileMetadata|FolderMetadata
    entries.
    """
    path = '/{}/{}'.format(dbox_dir, subfolder.replace(os.path.sep, '/'))
    while '//' in path:
        path = path.replace('//', '/')
    path = path.rstrip('/')
    try:
        with stopwatch('list_folder'):
            res = dbx.files_list_folder(path)
    except dropbox.exceptions.ApiError:
        logger.warning('Folder listing failed for {} -- assumed empty'
                       .format(path))
        return {}
    else:
        return {entry.name: entry for entry in res.entries}


def download(dbx, dbox_dir, subfolder, name):
    """Download a file.

    Return the bytes of the file, or None if it doesn't exist.
    """
    path = '/{}/{}/{}'.format(dbox_dir, subfolder.replace(os.path.sep, '/'),
                              name)
    while '//' in path:
        path = path.replace('//', '/')
    with stopwatch('download'):
        try:
            md, res = dbx.files_download(path)
        except dropbox.exceptions.HttpError:
            logger.exception("*** Dropbox HTTP Error")
            return None
    data = res.content
    logger.debug('{} bytes; md: {}'.format(len(data), md))
    return data


def upload(dbx, fullname, dbox_dir, subfolder, name, overwrite=False):
    """Upload a file.

    Return the request response, or None in case of error.
    """
    path = '/{}/{}/{}'.format(dbox_dir, subfolder.replace(os.path.sep, '/'),
                              name)
    while '//' in path:
        path = path.replace('//', '/')
    mode = (dropbox.files.WriteMode.overwrite
            if overwrite
            else dropbox.files.WriteMode.add)
    mtime = os.path.getmtime(fullname)
    with open(fullname, 'rb') as f:
        data = f.read()
    with stopwatch('upload %d bytes' % len(data)):
        try:
            res = dbx.files_upload(
                data, path, mode,
                client_modified=datetime.datetime(*time.gmtime(mtime)[:6]),
                mute=True)
        except dropbox.exceptions.ApiError:
            logger.exception('*** API error')
            return None
    logger.debug('Uploaded as {}'.format(res.name))
    return res


def yesno(message, default, args):
    """Handy helper function to ask a yes/no question.

    Command line arguments --yes or --no force the answer;
    --default to force the default answer.

    Otherwise a blank line returns the default, and answering
    y/yes or n/no returns True or False.

    Retry on unrecognized answer.

    Special answers:
    - q or quit exits the program
    - p or pdb invokes the debugger
    """
    if args.default:
        logger.debug('{} ? [auto] {}'.format(message, 'Y' if default else 'N'))
        return default
    if args.yes:
        logger.debug('{} ? [auto] YES'.format(message))
        return True
    if args.no:
        logger.debug('{} ? [auto] NO'.format(message))
        return False
    if default:
        message += '? [Y/n] '
    else:
        message += '? [N/y] '
    while True:
        answer = input(message).strip().lower()
        if not answer:
            return default
        if answer in ('y', 'yes'):
            return True
        if answer in ('n', 'no'):
            return False
        if answer in ('q', 'quit'):
            logger.warning('Exit')
            raise SystemExit(0)
        if answer in ('p', 'pdb'):
            import pdb
            pdb.set_trace()
        logger.debug('Please answer YES or NO.')


@contextlib.contextmanager
def stopwatch(message):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        logger.debug('Total elapsed time for {}: '
                     '{:.3f}'.format(message, t1 - t0))

if __name__ == '__main__':
    cli()
