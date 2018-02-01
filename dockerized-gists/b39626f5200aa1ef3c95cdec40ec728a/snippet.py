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

def dump_file(name, offset, size):
    global archive, out_dir
    path = os.path.join(out_dir, name[1:])
    print 'Dumping %s (%012X-%012X) to %s...' % (name, offset, offset+size, path)
    archive.seek(offset)
    with open(path, 'wb') as f:
        ofs = 0
        sz = 0x800000
        while ofs < size:
            if size - ofs < sz:
                sz = size - ofs
            f.write(archive.read(sz))
            ofs += sz
    print 'Dumped!'

def parse_file(off, path = ''):
    global archive, dirs_off, files_off, fdata_off
    sibling = 0
    while sibling != 0xFFFFFFFF:
        archive.seek(files_off + off)
        (parent, sibling, ofs, size, hsh, namelen) = up('<IIQQII', archive.read(0x20))
        name = read_filename(archive, files_off + off + 0x20, namelen)
        filepath = '%s%s' % (path, name)
        dump_file(filepath, fdata_off+ofs, size)
        off = sibling

def parse_dir(off, path = ''):
    global archive, dirs_off, files_off, fdata_off, out_dir
    archive.seek(dirs_off + off)
    (sibling, child, file, hsh, namelen) = up('<IIIII', archive.read(0x14))
    name = read_filename(archive, dirs_off + off + 0x14, namelen)
    if path:
        newpath = '%s%s/' % (path, name)
    else:
        newpath = '%s/' % name
    dirp = os.path.dirname(os.path.join(out_dir, newpath[1:])).replace('/', os.path.sep)
    if not os.path.exists(dirp):
        os.mkdir(dirp)
    if file != 0xFFFFFFFF:
        parse_file(file, newpath)
    if sibling != 0xFFFFFFFF:
        parse_dir(sibling, path)
    if child != 0xFFFFFFFF:
        parse_dir(child, newpath)

def main(argc, argv):
    if argc != 3:
        print 'Usage: %s in_file out_dir' % argv[0]
        return
    global archive, dirs_off, files_off, fdata_off
    try:
        archive = open(argv[1], 'rb')
        if read_u64(archive, 0) != 0x50:
            print 'Error: Invalid archive.'
            return
        dirs_off = read_u64(archive, 0x18)+4
        files_off = read_u64(archive, 0x38)
        fdata_off = read_u64(archive, 0x48)
        print 'Directory Metadata at %08X' % dirs_off
        print 'File Metadata at %08X' % files_off
    except:
        print 'Failed to open %s.' % argv[1]
        return

    global out_dir
    out_dir = argv[2]

    sys.setrecursionlimit(100000)
    parse_dir(0)

if __name__ == '__main__':
    main(len(sys.argv), sys.argv)