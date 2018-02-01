#!/usr/bin/env python

import subprocess, sys, os, zipfile

try:
    import boto
except ImportError:
    print 'requires boto. `pip install boto`'
    sys.exit(os.EX_UNAVAILABLE)
try:
    import argparse
except ImportError:
    print 'requires argpars. `pip install argparse`'
    sys.exit(os.EX_UNAVAILABLE)

# from http://stackoverflow.com/questions/4814970/subprocess-check-output-doesnt-seem-to-exist-python-2-6-5
if "check_output" not in dir( subprocess ): # duck punch it in!
    def f(*popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise subprocess.CalledProcessError(retcode, cmd)
        return output
    subprocess.check_output = f

from datetime import datetime

DATE_FORMAT =   '%Y%m%d%H%M%S'

parser      =   argparse.ArgumentParser()
parser.add_argument('name', help = 'The name of the site to backup. Used as folder name for S3 files.')
parser.add_argument('--database', help ='The database name to backup.')
parser.add_argument('--database-user', help ='The database user to use.')
parser.add_argument('--database-password', help = 'The database password to use.')
parser.add_argument('--bucket', help = 'The S3 bucket to upload to.', required = True)
parser.add_argument('--aws-key', help = 'The AWS Access Key ID to use for S3. Uses boto\'s default config if not present.')
parser.add_argument('--aws-secret', help = 'The AWS Access Key Secret to use for S3. Uses boto\'s default config if not present.')
parser.add_argument('--files', help = 'The absolute path to a folder to backup.')
args        =   parser.parse_args()

def zipdir(path, zip_file):
    relroot = os.path.abspath(os.path.join(path, ".."))
    for root, dirs, files in os.walk(path):
        zip_file.write(root, os.path.relpath(root, relroot))
        for f in files:
            filename = os.path.join(root, f)
            if os.path.isfile(filename):
                zip_file.write(filename, os.path.join(os.path.relpath(root, relroot), f))

# cleanup old backups
def cleanup(prefix = None, current_filename = ''):
    for key in bucket.list(prefix = prefix):
        created =   datetime.strptime(os.path.splitext(key.name.split('/')[-1])[0], DATE_FORMAT)
        if created.year == now.year and created.month == now.month and created.day == now.day and not key.name == current_filename.replace('-', '/'):
            # this was made earlier today so delete it
            key.delete()
        if created.year == now.year and created.month == now.month:
            # leave the current month alone
            pass
        elif created.day == 1:
            # leave the first backup of the month alone
            pass
        else:
            # this is from a previous month and isn't the first backup of the month so delete it
            key.delete()

now                 =   datetime.now()
db_filename         =   'databases-%s-%s.sql' % (args.name, now.strftime(DATE_FORMAT))
files_filename      =   'files-%s-%s.zip' % (args.name, now.strftime(DATE_FORMAT))

# setup the s3 connection
if args.aws_key and args.aws_secret:
    s3  =   boto.connect_s3(args.aws_key, args.aws_secret)
else:
    s3  =   boto.connect_s3()
bucket      =   s3.get_bucket(args.bucket)

# dump the data to a var
if args.database:
    mysqldump_args  =   [
        subprocess.check_output(['which', 'mysqldump']).strip(),
        '--add-drop-database', 
        '--databases', 
        args.database
    ]
    if args.database_user:
        mysqldump_args.append('-u')
        mysqldump_args.append(args.database_user)
    if args.database_password:
        mysqldump_args.append('-p%s' % args.database_password)
    data        =   subprocess.check_output(mysqldump_args)

    # create the new key
    key         =   bucket.get_key(db_filename.replace('-', '/'))
    if key is None:
        key =   bucket.new_key(db_filename.replace('-', '/'))
    key.set_contents_from_string(data)
    key.set_acl('private')
    cleanup('databases', db_filename)

if args.files and os.path.exists(args.files):
    # backup the files
    zip_file    =   zipfile.ZipFile(files_filename, 'w', zipfile.ZIP_DEFLATED)
    zipdir(args.files, zip_file)
    zip_file.close()

    # create the new key
    key     =   bucket.get_key(files_filename.replace('-', '/'))
    if key is None:
        key     =   bucket.new_key(files_filename.replace('-', '/'))
    key.set_contents_from_filename(files_filename)
    key.set_acl('private')
    os.unlink(files_filename)
    cleanup('files', files_filename)
elif args.files:
    print '%s does not exist' % args.files
    sys.exit(os.EX_CONFIG)

sys.exit(os.EX_OK)

