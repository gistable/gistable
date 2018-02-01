"""
===========
Description
===========

Simple script to copy and gzip static web files to an AWS S3 bucket. S3 is great for cheap hosting of static web content, but by default it does not gzip CSS and JavaScript, which results in much larger data transfer and longer load times for many applications

When using this script CSS and JavaScript files are gzipped in transition, and appropriate headers set as per the technique described here: http://www.jamiebegin.com/serving-compressed-gzipped-static-files-from-amazon-s3-or-cloudfront/

* Files overwrite old versions
* Orphaned files are not deleted
* S3 will not negotiate with clients and will always serve the gzipped version, so user agents must be able to understand the Content-Encoding:gzip header (all modern web browsers can)

=============
Prerequisites
=============

Python >= v2.7
boto

install with pip:
    pip install boto
or with apt-get
    apt-get install python-boto

=====
Usage
=====

From the command line

    python deploy_to_s3.py --directory source-dir --bucket bucket-name

The standard boto environment variables AWS_SECRET_ACCESS_KEY and AWS_ACCESS_KEY_ID are used for authentication - see boto for details

For help:

    python deploy_to_s3.py --help

"""

#!/usr/bin/python
__author__ = 'rob@redanorak.co.uk'

import os, sys, argparse, tempfile, gzip
from boto.s3.connection import S3Connection
from boto.s3.key import Key

def add_file(source_file, s3_key):
    """write a file to an s3 key"""
    if source_file.endswith(".js") or source_file.endswith(".css"):
        print("gzipping %s to %s" %(source_file, s3_key.key))
        gzip_to_key(source_file, s3_key)
    else:
        print("uploading %s to %s" %(source_file, s3_key.key))
        s3_key.set_contents_from_filename(source_file)

def gzip_to_key(source_file, key):
    tmp_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".gz", delete=False)
    with open(source_file, 'rb') as f_in:
        with gzip.open(tmp_file.name, 'wb') as gz_out:
            gz_out.writelines(f_in)
    key.set_metadata('Content-Type', 'application/x-javascript' if source_file.endswith(".js") else 'text/css')
    key.set_metadata('Content-Encoding', 'gzip')
    key.set_contents_from_filename(tmp_file.name)
    os.unlink(tmp_file.name) #clean up the temp file

def dir_to_bucket(src_directory, bucket):
    """recursively copy files from source directory to boto bucket"""
    for root, sub_folders, files in os.walk(src_directory):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, src_directory)
            #get S3 key for this file
            k = Key(bucket)
            k.key = rel_path
            add_file(abs_path, k)

def main():
    #get arguments
    arg_parser = argparse.ArgumentParser(description='Deploy static web resources to an S3 bucket, gzipping JavaScript and CSS files in the process')
    arg_parser.add_argument('-d','--directory', help='The source directory containing your static website files', required=True)
    arg_parser.add_argument('-b','--bucket', help='The name of the bucket you wish to copy files to, the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables are used for your credentials', required=True)
    args = arg_parser.parse_args()

    #connect to S3
    conn = S3Connection()
    target_bucket = conn.get_bucket(args.bucket, validate=False)
    dir_to_bucket(args.directory, target_bucket)

if __name__ == '__main__':
    main()
