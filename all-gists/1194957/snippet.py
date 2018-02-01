import ctypes
import ctypes.util

c_off_t = ctypes.c_int64

def make_fallocate():
    libc_name = ctypes.util.find_library('c')
    libc = ctypes.CDLL(libc_name)

    _fallocate = libc.fallocate
    _fallocate.restype = ctypes.c_int
    _fallocate.argtypes = [ctypes.c_int, ctypes.c_int, c_off_t, c_off_t]

    del libc
    del libc_name

    def fallocate(fd, mode, offset, len_):
        res = _fallocate(fd.fileno(), mode, offset, len_)
        if res != 0:
            raise IOError(res, 'fallocate')

    return fallocate

fallocate = make_fallocate()
del make_fallocate

FALLOC_FL_KEEP_SIZE = 0x01
FALLOC_FL_PUNCH_HOLE = 0x02


def main(db):
    orig_data = ''.join(chr(i) for i in xrange(10))
    format_ = lambda s: [ord(c) for c in s]

    with open(db, 'w') as fd:
        fd.write(orig_data)

    with open(db, 'r') as fd:
        data = fd.read()
        print 'Original value:', format_(data)

    print 'Punching hole at offset 2, length 3'
    with open(db, 'a') as fd:
        fallocate(fd, FALLOC_FL_KEEP_SIZE | FALLOC_FL_PUNCH_HOLE, 2, 3)

    print 'Reading file'
    with open(db, 'r') as fd:
        data = fd.read()
        print 'New value:', format_(data)

if __name__ == '__main__':
    main('punch.db')