#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
AWS S3 Gzip compression utility

Author: Dmitriy Sukharev
Modified: 2013-09-11
-------

Synchronizes directory with gzipped content of Amazon S3 bucket with local
one to avoid redundant synchronization requests when files were not changed,
but MD5 sums of Gzipped files are different. This script is part of article
http://sukharevd.net/gzipping-website-in-amazon-s3-bucket.html
'''

'''
Algorithm:
  Precondition: last compressed publication is in the last_publication
                directory, sha512sum is in file sha512.digest
  1. Read sha512.digest into dictionary
  2. For each file in output directory:
     -- If sha512 differ or dictionary doesn't contain hash sum, update
        last_publication directory with gzipped version of the file.
  3. Rewrite sha512.digest
'''

import os, sys, gzip, hashlib, shutil

if len(sys.argv) != 3:
    print 'Command should have 2 arguments: output dir and publication dir'
    sys.exit(0)
    
OUTPUT_DIR = sys.argv[1]
PUBLICATION_DIR = sys.argv[2]
HASH_SUM_FILE = sys.argv[2] + '/SHA512SUM'
GZIPPED_EXTENSIONS = ('html', 'js', 'css', 'xml')

def read_hash_codes(filename):
    hashes = {}
    try:
        with open(filename) as file:
            lines = file.readlines()
            for line in lines:
                split = line.split()
                assert(len(split) == 2)
                hashes[split[1]] = split[0]
            file.close()
            return hashes
    except:
        return {}

def update_gzipped_publications(output_dir, publication_dir):
    for root, subs, files in os.walk(output_dir):
        for f in files:
            filename = os.path.join(root, f)
            relpath = os.path.relpath(filename, output_dir);
            
            if (relpath.endswith(GZIPPED_EXTENSIONS)):
                # can be a problem if files are big:
                current_hash = hashlib.sha512(open(filename).read()).hexdigest()
                if not (relpath in hashes and hashes[relpath] == current_hash):
                    publicatedFile = os.path.join(publication_dir, relpath);
                    directoryOfFile = os.path.dirname(publicatedFile)
                    if not os.path.exists(directoryOfFile):
                        os.makedirs(directoryOfFile)
                    with gzip.open(publicatedFile, 'w') as fw:
                        with open(filename) as fr:
                            blocksize = 65536
                            buf = fr.read(blocksize)
                            while len(buf) > 0:
                                fw.write(buf)
                                buf = fr.read(blocksize)
                    hashes[relpath] = current_hash
                    print filename + ' renewed'
            else:
                 publicated_file = os.path.join(publication_dir, relpath);
                 directory_of_file = os.path.dirname(publicated_file)
                 if not os.path.exists(directory_of_file):
                     os.makedirs(directory_of_file)
                 shutil.copy(filename, directory_of_file)

def rewrite_hash_codes(hash_sum_file, hashes):
    with open(hash_sum_file, 'w') as fw:
        for key in hashes:
            fw.write(hashes[key] + '  ' + key + '\n')


hashes = read_hash_codes(os.path.abspath(HASH_SUM_FILE))
update_gzipped_publications(os.path.abspath(OUTPUT_DIR), os.path.abspath(PUBLICATION_DIR))
rewrite_hash_codes(os.path.abspath(HASH_SUM_FILE), hashes)
