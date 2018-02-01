import os.path
import sys

def main(pid):
    f = open(os.path.join('/proc', pid, 'maps'))
    for l in f.readlines():
        col = l.split()
        if len(col) == 5:
            address, perms, offset, device, inode = col
            pathname = ''
            comment = ''
        elif len(col) == 6:
            address, perms, offset, device, inode, pathname = col
            comment = ''
        elif len(col) == 7:
            address, perms, offset, device, inode, pathname, comment = col
        else:
            raise RuntimeError('unrecognized line format: \n' + l)
        start_address, end_address = address.split('-')
        if not pathname.strip() or pathname[0] == '[' or comment:
            print 'dump memory %s 0x%s 0x%s' % (start_address, start_address, end_address)
    print '\n\nRun the commands above with `gdb --pid %s`' % pid

if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print "Usage: dumpmaps.py <pid>"
        sys.exit(1)
    pid = sys.argv[1]
    main(pid)