#!/usr/bin/env python
import socket, shutil, os.path, struct, sys

def usage():
    print "For FBI 2.0+ only!   https://github.com/Steveice10/FBI"
    print "If you need 1.0 compatibility, check: https://gist.github.com/pudquick/66ae2238367ae76528e1"
    print "Usage: informant2.py ip.address.here filename.cia [second.cia third.cia ...]"
    sys.exit(1)

def main():
    args = sys.argv
    if len(args) < 3:
        usage()
    ip_address = args[1]
    filenames   = args[2:]
    port = 5000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print "Connecting to %s on TCP port 5000" % ip_address
    try:
        s.connect((ip_address,port))
    except:
        print "ERROR: Couldn't connect!"
        sys.exit(1)
    print "Connected"
    # With FBI 2.0+, the first 4 bytes sent are the
    # number of files you're sending, written as an
    # unsigned integer, 4 bytes long, big endian
    filecount = len(filenames)
    # Lazy here, just loop through all the files and
    # get sizes first - if we can't get the size of
    # one file, assume there's an error and ditch
    filepairs = []
    for f in filenames:
        print "Getting file size of file: %s" % f
        try:
            fsize = os.path.getsize(f)
        except:
            print "ERROR: Could not get size of file: %s" % f
            s.close()
            sys.exit(1)
        filepairs.append([f, fsize])
    # Build our count message
    cmsg = struct.pack('>L', filecount)
    print "Sending file count of %s ..." % (filecount)
    s.sendall(cmsg)
    # Now we loop for each file we want to send
    for i, x in enumerate(filepairs):
        fname, fsize = x
        # Also new in FBI 2.0, there is a single byte ack
        # sent by FBI back to the sender you must wait for
        # before sending the file data
        print "Waiting for ack from FBI ..."
        ack = s.recv(1)
        print "... ack received!"
        # For a file, the first 8 bytes sent to FBI have to
        # be the size of the file you're sending, written
        # as an unsigned integer, 8 bytes long, big endian
        print "* File %s of %s : %s" % (i+1, filecount, fname)
        smsg = struct.pack('>Q', fsize)
        print "Sending file size ..."
        s.sendall(smsg)
        print "Opening file for sending ..."
        f = open(fname, 'rb')
        sfile = s.makefile('wb')
        print "Sending ..."
        shutil.copyfileobj(f, sfile)
        print "Sent!"
        sfile.close()
        f.close()
    s.close()

if __name__ == '__main__':
    main()
