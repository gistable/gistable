#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 
# Hashsync
# Hash-based synchronization over FTP.
# http://thb.lt/blog/2013/fast-ftp-sync-for-jekyll.html
# 
# Copyright (c) 2012-2013 Thibault Polge <http://thb.lt>. All rights reserved.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse, ftplib, hashlib, os, re, subprocess, sys, tempfile

python3 = sys.version_info[0] >= 3

if python3:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

parser = argparse.ArgumentParser(description="Mirrors a directory over ftp using file hashes cache instead of timestamps.",
formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('source', metavar='Source', type=str,
                   help='Source directory')

parser.add_argument('dest', metavar='Destination', type=str,
                   help='Destination')

parser.add_argument('-d', '--delete', dest='delete', action='store_true',
                   help='Synchronize deletions')

parser.add_argument('-f', dest='file', action='store',
                    help='Cache file name', default=".sync_hashes")

parser.add_argument('-H', '--hash', metavar='command', dest='command', action='store',
                    help='Hash command to execute (must be in path). The last sequence matching[a-fA-F0-9]+ in the output will be used as a hash.', default=["openssl", "sha1", '-hex'])

if python3:
    parser.add_argument('--ftp-encoding', dest='ftp_encoding', action='store',
                   help='Encoding to use for FTP connection', default='utf-8')

parser.add_argument('--ignore-remote-hashes', dest='ignore_hashes', action='store_true',
                   help='Ignore remote hash cache and push everything.')

args = parser.parse_args()    
        
source = args.source
    
if not os.path.isdir(source):
    print("No such directory ‘{0}.’".format(source))
    exit(-1)
    
dest = args.dest
    
try:
    print("Connecting:\t"+dest)
    loc = urlparse(dest)
    if loc.scheme in ('ftp'):
        dest = ftplib.FTP()
        if python3:
            dest.encoding=args.ftp_encoding
        if loc.port:
            dest.connect(loc.hostname, loc.port)
        else:
            dest.connect(loc.hostname)
        if loc.username:
            print("Logging in...")
            dest.login(loc.username, loc.password)
        dest.cwd(loc.path)
except Exception as e:
    print("! Failed:\t"+str(e))
    exit(-2)
    
# Load remote hashes

print("Loading remote hash cache.")

if not args.ignore_hashes:
    try:
        destHashes = list()
        dest.retrlines("RETR {0}".format(args.file), lambda l: destHashes.append(l)) 
        destHashes = {x.split('\t')[0]: x.split('\t')[1] for x in destHashes}
    except Exception as e:
        print("Can't load remote hash file:\t"+str(e))
        print("Everything will be pushed.")
        destHashes = {}
else:
    destHashes = {}

# Build local hashes database

hexre = re.compile('([0-9A-Fa-f]+)')

print("Computing local hashes.")

def fullpath(path, path2=None):
    if path2:
        path = os.path.join(path, path2)
    return os.path.join(source, path)

def hashdir(path):
    ret = {}
    for file in os.listdir(fullpath(path)):
        if os.path.isdir(fullpath(path,file)):
            ret.update(hashdir(os.path.join(path, file)))
        else:
            try:
                out=subprocess.Popen(args.command+[fullpath(path, file)],stdout=subprocess.PIPE)
                (sout,serr)=out.communicate()
                sout = sout.decode('utf-8')            
                ret[os.path.join(path, file)] = hexre.findall(sout)[-1]
            except Exception as e:
                print("Can't compute hash for {0}:\t{1}".format(fullpath(path, file), e))
    return ret
sourceHashes = hashdir('')

# Compute difference

added = [x for x in sourceHashes if not x in destHashes.keys()]
modified = [x for x in sourceHashes if x in destHashes.keys() and not sourceHashes[x] == destHashes[x]]
deleted = [x for x in destHashes if not x in sourceHashes.keys()]

def pl(list):
    count = len(list)
    noun ='file'
    if count>1:
        noun = 'files'
    return "{0} {1}".format(count, noun)
    
print("{0} added, {1} modified and {2} removed.".format(pl(added), pl(modified), pl(deleted)))

for f in added+modified:
    print("Send:\t"+f)
    command = "STOR " + f
    dest.storbinary(command, open(fullpath(f), 'rb'))
    
if args.delete:
    for f in deleted:
        print("Delete:\t"+f)
        dest.delete(f)
else:
    if deleted:
        print("{0} deleted locally but kept on server, invoke with -d to delete remote copies.".format(pl(deleted)))

print("Sending hashes...")

hashes = tempfile.NamedTemporaryFile('w')

for h in sourceHashes.items():
    hashes.write("{0}\t{1}\n".format(h[0], h[1]))

if not args.delete:
    for h in {f: h for f, h in destHashes.items() if f in deleted }.items():
        hashes.write("{0}\t{1}\n".format(h[0], h[1]))
        
hashes.flush()

dest.storbinary("STOR "+args.file, open(hashes.name, 'rb'))