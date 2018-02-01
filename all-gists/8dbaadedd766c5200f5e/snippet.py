#!/usr/bin/env python
import zipfile
import argparse
import re
import os
from time import strftime

"""
Attempt to extract zip archive with password
"""
def extractFile(zip, password, opath):
    try:
        zip.extractall(path=opath, pwd=password)
        return True
    except KeyboardInterrupt:
        exit(0)
    except Exception, e:
        pass

"""
Begin brute forcing passwords
"""
def run(zip, batchList, batchCount, opath):
    for x in range(0, batchCount):
        try:
            tid = x+1
            print '[*] Entering batch %d/%d with %s passwords (%s)'%(tid, batchCount, '{0:,}'.format(len(batchList[x])), strftime('%H:%M:%S'))
            for password in batchList[x]:
                if extractFile(zip, password, opath):
                    print '\n[+] Found Password: %s'%(password)
                    print '[*] Content has been extracted to \'%s\'\n'%(opath)
                    print '[*] Process ended %s\n'%(strftime('%c'))
                    exit(0)
        except KeyboardInterrupt:
            print '[*] Process ended %s\n'%(strftime('%c'))
            exit(0)

    print '[*] Process ended %s\n'%(strftime('%c'))

"""
Split dictionary file into batches
"""
def splitFile(filename, size):
    try:
        batchList = []
        batch = []
        num_lines = sum(1 for line in open(filename))
        batchSize = num_lines if size is None else int(size)
        with open(filename) as fileList:
            print '[*] Building dictionary batch list'
            for line in fileList.readlines():
                password = line.strip('\n')
                batch.append(password)
                if len(batch) == batchSize:
                    batchList.append(batch)
                    batch = []
        if len(batch) is not 0:
            batchList.append(batch)

        print '[+] Successfully created %d %s from %s passwords.\n'%(len(batchList), 'batch' if len(batchList) == 1 else 'batchess', '{0:,}'.format(num_lines))
        return batchList
    except KeyboardInterrupt:
        exit(1)

"""
Throw error messages
"""
def error(message, fatal = False):
    errmsg = str(message)
    errmsg = re.sub('\[[^\]]+\] ', '', errmsg)
    errmsg = errmsg.strip()
    prefix = '[!] Error: ' if not fatal else '[!!] Fatal Error: '
    print '%s%s\n'%(prefix, errmsg)
    if fatal:
        exit(1)

"""
Main function
"""
def main(args):
    print """
================================================
=                                              =
= BruteZip - Zip archive password brute forcer =
= by Ole Aass (@oleaass)                       =
=                                              =
================================================
    """

    zfile = args.z
    if os.path.isfile(zfile) is False:
        error('Zip file does not exist', True)
    if os.access(zfile, os.R_OK) is False:
        error('You do not have permission to read the zip archive file', True)

    dfile = args.d
    if os.path.isfile(dfile) is False:
        error('Dictionary file does not exist', True)
    if os.access(dfile, os.R_OK) is False:
        error('You do not have permission to read the dictionary file', True)

    opath = os.getcwd() if args.o is None else args.o
    if os.path.isdir(opath) is False:
        error('Output path does not exit', True)
    if os.access(opath, os.W_OK) is False:
        error('You do not have write permissions in output path', True)

    bsize = args.b

    batchList = splitFile(dfile, bsize)
    batchCount = len(batchList)

    zip = zipfile.ZipFile(zfile)

    print '[*] Process started %s\n'%(strftime('%c'))
    run(zip, batchList, batchCount, opath)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BruteZip - by Ole Aass (@oleaass)')
    parser.add_argument('-z', metavar='zipfile',  help='zip file', required=True)
    parser.add_argument('-d', metavar='dictionary', help='dictionary file', required=True)
    parser.add_argument('-o', metavar='path', help='extract to this path')
    parser.add_argument('-b', metavar='size', help='batch size (default: size of dictionary)')
    args = parser.parse_args()

    main(args)
