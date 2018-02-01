from struct import unpack as up
import sys, os

dirs, files = None, None

def read_at(fp, off, len):
    fp.seek(off)
    return fp.read(len)

def read_u8(fp, off):
    return up('<B', read_at(fp, off, 1))[0]

def read_u16(fp, off):
    return up('<H', read_at(fp, off, 2))[0]

def read_u32(fp, off):
    return up('<I', read_at(fp, off, 4))[0]

def read_u64(fp, off):
    return up('<Q', read_at(fp, off, 8))[0]

def read_filename(fp, off, l):
    if l == 0:
        return ''
    s = read_at(fp, off, l)
    if '\0' in s:
        s = s[:s.index('\0')]
    return s

def parse_file(off, path = ''):
    global dirs, files
    files.seek(off)
    (parent, sibling, ofs, size, hsh, namelen) = up('<IIQQII', files.read(0x20))
    name = read_filename(files, off + 0x20, namelen)
    filepath = '%s%s' % (path, name)
    print filepath
    if sibling != 0xFFFFFFFF:
        parse_file(sibling, path)

def parse_dir(off, path = ''):
    global dirs, files
    dirs.seek(off)
    (sibling, child, file, hsh, namelen) = up('<IIIII', dirs.read(0x14))
    name = read_filename(dirs, off + 0x14, namelen)
    if path:
        newpath = '%s%s/' % (path, name)
    else:
        newpath = '%s/' % name
    if file != 0xFFFFFFFF:
        parse_file(file, newpath)
    if sibling != 0xFFFFFFFF:
        parse_dir(sibling, path)
    if child != 0xFFFFFFFF:
        parse_dir(child, newpath)

def main(argc, argv):
    if argc != 3:
        print 'Usage: %s dirinfo fileinfo' % argv[0]
        return
    global dirs, files
    try:
        dirs = open(argv[1], 'rb')
    except:
        print 'Failed to open %s.' % argv[1]
        return
    try:
        files = open(argv[2], 'rb')
    except:
        print 'Failed to open %s.' % argv[2]
    sys.setrecursionlimit(10000)
    parse_dir(0)
    dirs.close()
    files.close()

if __name__ == '__main__':
    main(len(sys.argv), sys.argv)