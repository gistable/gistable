#!/usr/bin/env python
"""
Synchronise block devices over the network
 
Copyright 2006-2008 Justin Azoff <justin@bouncybouncy.net>
Copyright 2011 Robert Coup <robert@coup.net.nz>
License: GPL
 
Getting started:
 
* Copy blocksync.py to the home directory on the remote host
* Make sure your remote user can either sudo or is root itself.
* Make sure your local user can ssh to the remote host
* Invoke:
    sudo python blocksync.py /dev/source user@remotehost /dev/dest
"""
 
import sys
from sha import sha
import subprocess
import time
 
SAME = "same\n"
DIFF = "diff\n"
 
 
def do_open(f, mode):
    f = open(f, mode)
    f.seek(0, 2)
    size = f.tell()
    f.seek(0)
    return f, size
 
 
def getblocks(f, blocksize):
    while 1:
        block = f.read(blocksize)
        if not block:
            break
        yield block
 
 
def server(dev, blocksize):
    print dev, blocksize
    f, size = do_open(dev, 'r+')
    print size
    sys.stdout.flush()
 
    for block in getblocks(f, blocksize):
        print sha(block).hexdigest()
        sys.stdout.flush()
        res = sys.stdin.readline()
        if res != SAME:
            newblock = sys.stdin.read(blocksize)
            f.seek(-len(newblock), 1)
            f.write(newblock)
 
 
def sync(srcdev, dsthost, dstdev=None, blocksize=1024 * 1024):
 
    if not dstdev:
        dstdev = srcdev
 
    print "Block size is %0.1f MB" % (float(blocksize) / (1024 * 1024))
    # cmd = ['ssh', '-c', 'blowfish', dsthost, 'sudo', 'python', 'blocksync.py', 'server', dstdev, '-b', str(blocksize)]
    cmd = ['ssh', '-c', 'blowfish', dsthost, 'python', 'blocksync.py', 'server', dstdev, '-b', str(blocksize)]
    print "Running: %s" % " ".join(cmd)
 
    p = subprocess.Popen(cmd, bufsize=0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
    p_in, p_out = p.stdin, p.stdout
 
    line = p_out.readline()
    p.poll()
    if p.returncode is not None:
        print "Error connecting to or invoking blocksync on the remote host!"
        sys.exit(1)
 
    a, b = line.split()
    if a != dstdev:
        print "Dest device (%s) doesn't match with the remote host (%s)!" % (dstdev, a)
        sys.exit(1)
    if int(b) != blocksize:
        print "Source block size (%d) doesn't match with the remote host (%d)!" % (blocksize, int(b))
        sys.exit(1)
 
    try:
        f, size = do_open(srcdev, 'r')
    except Exception, e:
        print "Error accessing source device! %s" % e
        sys.exit(1)
 
    line = p_out.readline()
    p.poll()
    if p.returncode is not None:
        print "Error accessing device on remote host!"
        sys.exit(1)
    remote_size = int(line)
    if size != remote_size:
        print "Source device size (%d) doesn't match remote device size (%d)!" % (size, remote_size)
        sys.exit(1)
 
    same_blocks = diff_blocks = 0
 
    print "Starting sync..."
    t0 = time.time()
    t_last = t0
    size_blocks = size / blocksize
    for i, l_block in enumerate(getblocks(f, blocksize)):
        l_sum = sha(l_block).hexdigest()
        r_sum = p_out.readline().strip()
 
        if l_sum == r_sum:
            p_in.write(SAME)
            p_in.flush()
            same_blocks += 1
        else:
            p_in.write(DIFF)
            p_in.flush()
            p_in.write(l_block)
            p_in.flush()
            diff_blocks += 1
 
        t1 = time.time()
        if t1 - t_last > 1 or (same_blocks + diff_blocks) >= size_blocks:
            rate = (i + 1.0) * blocksize / (1024.0 * 1024.0) / (t1 - t0)
            print "\rsame: %d, diff: %d, %d/%d, %5.1f MB/s" % (same_blocks, diff_blocks, same_blocks + diff_blocks, size_blocks, rate),
            t_last = t1
 
    print "\n\nCompleted in %d seconds" % (time.time() - t0)
 
    return same_blocks, diff_blocks
 
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] /dev/source user@remotehost [/dev/dest]")
    parser.add_option("-b", "--blocksize", dest="blocksize", action="store", type="int", help="block size (bytes)", default=1024 * 1024)
    (options, args) = parser.parse_args()
 
    if len(args) < 2:
        parser.print_help()
        print __doc__
        sys.exit(1)
 
    if args[0] == 'server':
        dstdev = args[1]
        server(dstdev, options.blocksize)
    else:
        srcdev = args[0]
        dsthost = args[1]
        if len(args) > 2:
            dstdev = args[2]
        else:
            dstdev = None
        sync(srcdev, dsthost, dstdev, options.blocksize)