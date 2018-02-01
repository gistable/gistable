#!/usr/bin/env python

import argparse
import fileinput
import grp
import json
import urllib.request
import os
import subprocess
import tarfile

# Config
HOME_DIR = os.environ.get('HOME')
ACCOUNT_NAME = grp.getgrgid(os.getgid()).gr_name
WALLABAG_ARCHIVE_URL = 'https://wllbg.org/latest-v2-package'
WALLABAG_ARCHIVE_NAME = 'release-2.2.2'
ALWAYSDATA_API_URL = 'https://api.alwaysdata.com/v1/'


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Install Wallabag on alwaysdata."
    )
    parser.add_argument('destination',
                        help='The destination directory (absolute path)')
    parser.add_argument('apikey',
                        help='alwaysdata API key (see your Profile section)')
    parser.add_argument('database_type',
                        choices=['MYSQL', 'POSTGRESQL'],
                        help='The database type')
    parser.add_argument('database',
                        help='The database name')
    parser.add_argument('database_user',
                        help='The database user name')
    parser.add_argument('database_password',
                        help='The database user password')
    parser.add_argument('url',
                        help='The URL to join your Wallabag app')

    args = parser.parse_args()
    apikey = '%s account=%s' % (args.apikey, ACCOUNT_NAME)
    relative_destination_dir = '/' + args.destination.strip(HOME_DIR)

    # Download archive
    print('Downloading/extracting archive to %s... (eta: 30 seconds)' %
          args.destination)
    # Without this header, wallabag servers send a 403
    headers = {'User-Agent': 'alwaysdata'}
    request = urllib.request.Request(WALLABAG_ARCHIVE_URL, None, headers)
    response = urllib.request.urlopen(request)
    tar = tarfile.open(mode="r|gz", fileobj=response)
    tar.extractall(args.destination)
    tar.close()

    # Initialize API connection
    passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, ALWAYSDATA_API_URL, apikey, '')
    auth_handler = urllib.request.HTTPBasicAuthHandler(passman)
    opener = urllib.request.build_opener(auth_handler)
    urllib.request.install_opener(opener)

    # Create database user
    print('Creating database user...')
    data = {
        'type': args.database_type,
        'name': args.database_user,
        'password': args.database_password
    }
    data = json.dumps(data).encode('ascii')
    request = urllib.request.Request(
        ALWAYSDATA_API_URL + 'database/user/',
        data,
        headers={'Content-Type': 'application/json'})
    response = urllib.request.urlopen(request)

    # Create database
    print('Creating database...')
    data = {
        'type': args.database_type,
        'name': args.database,
        'permissions': {args.database_user: 'FULL'}
    }
    data = json.dumps(data).encode('ascii')
    request = urllib.request.Request(
        ALWAYSDATA_API_URL + 'database/',
        data,
        headers={'Content-Type': 'application/json'})
    response = urllib.request.urlopen(request)

    # Create site
    print('Creating site...')
    data = {
        'name': 'Wallabag',
        'httpd': 'apache',
        'type': 'apache_standard',
        'path': os.path.join(relative_destination_dir, WALLABAG_ARCHIVE_NAME, 'web'),
        'addresses': [args.url],
        'vhost_additional_directives': """
    <Directory {0}>
        AllowOverride None
        Order Allow,Deny
        Allow from All

        <IfModule mod_rewrite.c>
            Options -MultiViews
            RewriteEngine On
            RewriteCond %{{REQUEST_FILENAME}} !-f
            RewriteRule ^(.*)$ app.php [QSA,L]
        </IfModule>
    </Directory>
    """.format(os.path.join(args.destination, WALLABAG_ARCHIVE_NAME, 'web'))
    }
    data = json.dumps(data).encode('ascii')
    request = urllib.request.Request(
        ALWAYSDATA_API_URL + 'site/',
        data,
        headers={'Content-Type': 'application/json'})
    response = urllib.request.urlopen(request)

    # Update wallabag parameters.yml
    print('Update parameters.yml...')
    for line in fileinput.input(os.path.join(
                                args.destination,
                                WALLABAG_ARCHIVE_NAME, 'app', 'config',
                                'parameters.yml'), inplace=True):
        if line.strip():
            if 'database_driver:' in line:
                print('    database_driver: %s' % (
                    'pdo_mysql' if args.database_type == 'MYSQL'
                    else 'pdo_pgsql'))
            elif 'database_host:' in line:
                print('    database_host: %s' % '%s-%s.alwaysdata.net' % (
                    args.database_type.lower(),
                    ACCOUNT_NAME))
            elif 'database_name:' in line:
                print('    database_name: %s' % args.database)
            elif 'database_user:' in line:
                print('    database_user: %s' % args.database_user)
            elif 'database_password:' in line:
                print('    database_password: %s' % args.database_password)
            elif 'database_path:' in line:
                print('    database_path: null')
            else:
                print(line)

    # Execute wallabag installer
    print('Launch wallabag installer...')
    subprocess.run("%s/bin/console wallabag:install -e=prod" % (
        os.path.join(args.destination, WALLABAG_ARCHIVE_NAME)), shell=True)
