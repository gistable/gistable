#!/usr/bin/env python
import sys
import json

from boto.s3.connection import S3Connection
from boto.s3.prefix import Prefix
from boto.s3.key import Key

bucketname = sys.argv[1]
delimiter = '/'
prefix = '/'

conn = S3Connection()

bucket = conn.get_bucket(bucketname)


def list_dir(prefix='', max_keys=10):
    """Get all items in a directory.

    Returns a dictionary with keys: 'files' and 'directories'
    """
    # strip leading '/' from the prefix
    prefix = prefix.lstrip('/')
    if prefix != '' and prefix[-1] != '/':
        prefix = prefix + '/'

    # a list of keys/prefixes
    all_keys = bucket.get_all_keys(
        max_keys=10, delimiter=delimiter, prefix=prefix
    )

    out = {
        'prefix': prefix,
        'files': [],
        'directories': []
    }

    for key in all_keys:
        if isinstance(key, Prefix):
            out['directories'].append(key.name)
        elif isinstance(key, Key) and key.name != prefix:
            out['files'].append(key.name)

    return out


def list_recursive(prefix='', max_keys=10):
    o = list_dir(prefix, max_keys)

    for i, d in enumerate(o['directories']):
        if i > max_keys:
            break
        o['directories'][i] = list_recursive(d, max_keys)

    if not len(o['files']):
        o.pop('files')

    if not len(o['directories']):
        o.pop('directories')

    return o


def tree(o, padding=' ', print_files=True):
    s = [padding[:-1] + '+-' + o['prefix'].strip('/').split('/')[-1] + '/']
    padding = padding + ' '

    count = 0
    for d in o.get('directories', []):
        count += 1
        # s.append(padding + '|')
        if count != len(o['directories']):
            s.extend(tree(d, padding + '|', print_files))
        else:
            s.extend(tree(d, padding + ' ', print_files))

    if print_files:
        for f in o.get('files', []):
            # s.append(padding + '|')
            s.append(padding + '+-' + f.split('/')[-1])
    return s
#    for file in o['files']:
#        count += 1
#        s.append(padding + '|')
#        path = dir + sep + file
#        if isdir(path):
#            if count == len(files):
#                tree(path, padding + ' ')
#            else:
#                tree(path, padding + '|')
#        else:
#            s.append(padding + '+-' + file)
    return s

if __name__ == '__main__':
    prefix = ['']
    if len(sys.argv) > 2:
        prefix = sys.argv[2:]

    for p in prefix:
        o = list_recursive(p)
        print(json.dumps(o, indent=2))
        print('')
