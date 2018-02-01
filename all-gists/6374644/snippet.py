#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import subprocess
import shutil
import tarfile
import tempfile
import argparse
import datetime
import boto
from boto.s3.key import Key

logging.basicConfig(level=logging.INFO, format="%(asctime)s;%(name)s;%(levelname)s;%(message)s")
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

def memoize(function):
    # Cache result of function call in dictionary, making subsequent
    # lookups cheap.
    memo = {}
    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper    

@memoize
def generate_key_name(collection=None):
    if collection:
        return datetime.datetime.utcnow().strftime('%Y/%m/%Y-%m-%dT%H:%M:%SZ-{0}.tgz'.format(collection))
    else:
        return datetime.datetime.utcnow().strftime('%Y/%m/%Y-%m-%dT%H:%M:%SZ.tgz')


class TemporaryDirectory(object):

    def __init__(self, base_dir, keep=False):
        self._base_dir = base_dir
        self._tmp_dir = None
        self._keep = keep
        assert os.path.exists(self._base_dir), \
            'Base directory {} does not exist'.format(self._base_dir)

    @property
    def path(self):
        return self._tmp_dir

    def __enter__(self):
        self._tmp_dir = tempfile.mkdtemp(dir=self._base_dir)
        return self

    def __exit__(self, type, value, tb):
        if not self._keep:
            try:
                shutil.rmtree(self._tmp_dir)
            except OSError, e:
                if e.errno != 2:
                    # The error isn't related to the dir not existing.
                    raise        

    def archive(self, files_or_dirs=['.'], filename='dump.tgz'):
        os.chdir(self._tmp_dir)

        path = os.path.join(self._tmp_dir, filename)
        with tarfile.open(path, 'w:gz') as tar:
            for f in files_or_dirs:
                tar.add(f, exclude=lambda f: f == os.path.join('.', filename))
        return path

    def unarchive(self, path):
        path = os.path.join(self._tmp_dir, path)        
        os.chdir(os.path.dirname(path))
        with tarfile.open(path, 'r:gz') as tar:
            tar.extractall(path=self._tmp_dir)
        return self._tmp_dir

    def remove(self, filename):
        path = os.path.join(self._tmp_dir, filename)        
        os.remove(path)

class S3Bucket(object):

    def __init__(self, bucket_name):
        self._bucket_name = bucket_name


    def upload(self, f, key_name):
        bucket = self.create_or_get_backup_bucket()
        k = Key(bucket)
        k.key = key_name
        logger.info('Uploading dump into bucket {0} with key {1}'.format(bucket.name, key_name))
        k.set_contents_from_filename(f)


    def download(self, directory, key_name, filename):
        os.chdir(directory)
        bucket = self.create_or_get_backup_bucket()
        k = Key(bucket)
        k.key = key_name
        logger.info('Getting file from bucket {0} and key {1} to directory {2}'.format(bucket.name, key_name, directory))
        k.get_contents_to_filename(filename)
        return os.path.join(directory, key_name)

    @memoize
    def connection(self):
        # Assumes Boto keys have already been configured on the system, see
        # http://code.google.com/p/boto/wiki/BotoConfig for details.
        return boto.connect_s3()


    def create_or_get_backup_bucket(self):
        c = self.connection()
        rs = c.get_all_buckets()

        logger.info('Looking for bucket {0} in S3'.format(self._bucket_name)) 
        for r in rs:
            if r.name == self._bucket_name:
                logger.info('Found bucket')  
                return r

        logger.info('Bucket not found, creating') 
        return c.create_bucket(self._bucket_name)


class MongoDumpRestore(object):

    MONGODUMP = 'mongodump'
    MONGORESTORE = 'mongorestore'

    def __init__(self, host=None, port=None):
        self._host = host
        self._port = port

    def _call(self, app, params=[]):
        if self._host:
            params += ['--host', self._host]
        if self._port:
            params += ['--port', self._port] 

        params.insert(0, app)

        return subprocess.check_call(params)

    def dump(self, directory, database=None, collection=None):
        args = ['-o', directory]
        if not database and not collection:
            args += ['--oplog'] 

        if database:
            args += ['--db', database]
        if collection:
            assert database is not None, 'Database name is missing'
            args += ['--collection', collection]

        return self._call(self.MONGODUMP, args)

    def restore(self, directory):
        args = [directory]
        return self._call(self.MONGORESTORE, args)


if __name__ == '__main__':
    '''
    Backup collection to S3:
    python mongobak.py --database test --collection foo --base-dir /tmp --bucket my-backups

    Restore collection from S3 backup:
    python mongobak.py --unarchive-from "2013/08/2013-08-29T05:01:20Z-test-foo.tgz" --base-dir /tmp --bucket my-backups
    '''

    parser = argparse.ArgumentParser(description='Dumps a mongo db')
    parser.add_argument('--database',
        help='A database name to dump, omitting dumps the entire db')
    parser.add_argument('--collection',
        help='A collection name to dump, omitting dumps the entire db')
    parser.add_argument('--local', action='store_true', default=False,
        help='Don\'t upload the dump to S3')
    parser.add_argument('--persist', action='store_true', default=False,
        help='Don\'t rm the dump dir when the script terminates')
    parser.add_argument('--port', default='27017',
        help='Mongo port number')
    parser.add_argument('--host', default='localhost',
        help='Mongo port number')
    parser.add_argument('--base-dir',
        help='Base directory to store temporary files in', required=True)
    parser.add_argument('--bucket',
        help='S3 bucket name', required=True)

    parser.add_argument('--unarchive-from',
        help='Unarchive by key', default=False)

    args = parser.parse_args()

    mongo = MongoDumpRestore(host=args.host, port=args.port)
    s3 = S3Bucket(args.bucket)

    if args.database:
        if args.collection:
            suffix = '{}-{}'.format(args.database, args.collection)
        else:
            suffix = args.database
    else:
        suffix = 'mongo'


    with TemporaryDirectory(args.base_dir, keep=args.persist) as tmpdir:
        if args.unarchive_from:
            key = args.unarchive_from
            filename = 'dump.tgz'
            s3.download(tmpdir.path, key, filename)
            tmpdir.unarchive(filename)
            tmpdir.remove(filename)
            mongo.restore(tmpdir.path)
        else:
            mongo.dump(tmpdir.path, args.database, args.collection)
            archive = tmpdir.archive('.')
            if not args.local:
                key = generate_key_name(suffix)
                s3.upload(archive, key)
            else:
                logger.info('Dump is in {}'.format(archive))
