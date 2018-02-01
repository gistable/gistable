#!/usr/bin/env python
import os
import argparse
import logging
import datetime
import urlparse
import subprocess

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description='Backup Mongolab DBs')
parser.add_argument('-u', '--url',
        type=str,
        required=False,
        default=None,
        help='Mongo DB URL for Backups')
parser.add_argument('-o', '--output_dir',
        type=str,
        required=False,
        default='./',
        help='Output directory for the backup.')

def backup(args):
    today = datetime.datetime.now()

    url = args.url

    if url is None:
        logging.info('Fetching MONGOLAB_URI using heroku config:get')

        url = subprocess.check_output([
                'heroku',
                'config:get',
                'MONGOLAB_URI'
                ]).strip()

    url = urlparse.urlparse(url)
    assert url.scheme == 'mongodb', 'URL must be a MongoDB URL'

    netloc = url.netloc
    username = url.username
    password = url.password
    hostname = url.hostname
    port = url.port
    db = url.path[1:]

    output_dir = os.path.abspath(os.path.join(
            os.path.curdir,
            args.output_dir))

    assert os.path.isdir(output_dir), 'Directory %s can\'t be found.' % output_dir

    output_dir = os.path.abspath(os.path.join(output_dir,
            '%s__%s'% ( db, today.strftime('%Y_%m_%d_%H%M%S'))
            ))

    logging.info('Backing up %s from %s to %s' % (db, hostname, output_dir))

    backup_output = subprocess.check_output(
            [
                'mongodump',
                '-host', '%s' % hostname,
                '-u', '%s' % username,
                '-p', '%s' % password,
                '-d', '%s' % db,
                '--port', '%s' % port,
                '-o', '%s' % output_dir
            ])

    logging.info(backup_output)


if __name__ == '__main__':
    args = parser.parse_args()
   
    try:
        backup(args)
    except AssertionError, msg:
        logging.error(msg)



