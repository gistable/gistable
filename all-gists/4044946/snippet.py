"""Speed up os.walk() significantly by using file attributes that
FindFirst/Next give us instead of doing an extra stat(). Can also do the same
thing with opendir/readdir on Linux.

This is doubly useful when the user (caller of os.walk) is doing *another*
stat() to get say the file sizes.

On my tests (Windows 64-bit) our walk() is about 5x as fast as os.walk() for
large directory trees, and 9x as fast if you're doing the file size thing.
Note that these timings are "once it's in the cache", not first-time timings.

Other advantages to using FindFirst/Next:

* You can write a version of listdir() which yield results rather than getting
  all filenames at once -- better for "streaming" large directories.

* You can use its built-in wildcard matching (globbing), which is presumably
  faster than getting all filenames and calling fnmatch on the result. (This one
  you couldn't do with opendir/readdir.)

This isn't just me who noticed these were issues. See also:

http://stackoverflow.com/questions/2485719/very-quickly-getting-total-size-of-folder
http://stackoverflow.com/questions/4403598/list-files-in-a-folder-as-a-stream-to-begin-process-immediately
http://bugs.python.org/issue15200 -- Titled "Faster os.walk", but actually unrelated

"""


import ctypes
import os
import stat

if os.name == 'nt':
    from ctypes import wintypes

    INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
    ERROR_FILE_NOT_FOUND = 2
    ERROR_NO_MORE_FILES = 18
    FILE_ATTRIBUTE_DIRECTORY = 16
    FILE_ATTRIBUTE_READONLY = 1
    SECONDS_BETWEEN_EPOCHS = 11644473600  # seconds between 1601-01-01 and 1970-01-01

    kernel32 = ctypes.windll.kernel32

    _FindFirstFile = kernel32.FindFirstFileW
    _FindFirstFile.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(wintypes.WIN32_FIND_DATAW)]
    _FindFirstFile.restype = wintypes.HANDLE

    _FindNextFile = kernel32.FindNextFileW
    _FindNextFile.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.WIN32_FIND_DATAW)]
    _FindNextFile.restype = wintypes.BOOL

    _FindClose = kernel32.FindClose
    _FindClose.argtypes = [wintypes.HANDLE]
    _FindClose.restype = wintypes.BOOL

    def _attributes_to_mode(attributes):
        """Convert Win32 dwFileAttributes to st_mode. Taken from CPython's
        Modules/posixmodule.c.
        """
        mode = 0
        if attributes & FILE_ATTRIBUTE_DIRECTORY:
            mode |= stat.S_IFDIR | 0111
        else:
            mode |= stat.S_IFREG
        if attributes & FILE_ATTRIBUTE_READONLY:
            mode |= 0444
        else:
            mode |= 0666
        return mode

    def _filetime_to_time(filetime):
        total = filetime.dwHighDateTime << 32 | filetime.dwLowDateTime
        return total / 10000000.0 - SECONDS_BETWEEN_EPOCHS

    def _find_data_to_stat(data):
        st_mode = _attributes_to_mode(data.dwFileAttributes)
        st_ino = 0
        st_dev = 0
        st_nlink = 0
        st_uid = 0
        st_gid = 0
        st_size = data.nFileSizeHigh << 32 | data.nFileSizeLow
        st_atime = _filetime_to_time(data.ftLastAccessTime)
        st_mtime = _filetime_to_time(data.ftLastWriteTime)
        st_ctime = _filetime_to_time(data.ftCreationTime)
        st = os.stat_result((st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid,
                             st_size, st_atime, st_mtime, st_ctime))
        return st

    def listdir_stat(dirname='.', glob=None):
        dirname = os.path.abspath(dirname)
        filename = os.path.join(dirname, glob or '*')

        data = wintypes.WIN32_FIND_DATAW()
        data_p = ctypes.byref(data)
        handle = _FindFirstFile(filename, data_p)
        if handle == INVALID_HANDLE_VALUE:
            error = ctypes.GetLastError()
            if error == ERROR_FILE_NOT_FOUND:
                return
            raise ctypes.WinError()

        try:
            while True:
                if data.cFileName not in ('.', '..'):
                    st = _find_data_to_stat(data)
                    yield (data.cFileName, st)
                success = _FindNextFile(handle, data_p)
                if not success:
                    error = ctypes.GetLastError()
                    if error == ERROR_NO_MORE_FILES:
                        break
                    raise ctypes.WinError()
        finally:
            if not _FindClose(handle):
                raise ctypes.WinError()


# Linux/posix -- this is only half-tested and doesn't work at the moment, but
# leaving here for future use
else:
    import ctypes
    import ctypes.util

    class DIR(ctypes.Structure):
        pass
    DIR_p = ctypes.POINTER(DIR)

    class dirent(ctypes.Structure):
        _fields_ = (
            ('d_ino', ctypes.c_long),
            ('d_off', ctypes.c_long),
            ('d_reclen', ctypes.c_ushort),
            ('d_type', ctypes.c_byte),
            ('d_name', ctypes.c_char * 256)
        )
    dirent_p = ctypes.POINTER(dirent)

    _libc = ctypes.CDLL(ctypes.util.find_library('c'))
    _opendir = _libc.opendir
    _opendir.argtypes = [ctypes.c_char_p]
    _opendir.restype = DIR_p

    _readdir = _libc.readdir
    _readdir.argtypes = [DIR_p]
    _readdir.restype = dirent_p

    _closedir = _libc.closedir
    _closedir.argtypes = [DIR_p]
    _closedir.restype = ctypes.c_int

    DT_DIR = 4

    def _type_to_stat(d_type):
        if d_type == DT_DIR:
            st_mode = stat.S_IFDIR | 0111
        else:
            st_mode = stat.S_IFREG
        st = os.stat_result((st_mode, None, None, None, None, None,
                             None, None, None, None))
        return st

    def listdir_stat(dirname='.', glob=None):
        dir_p = _opendir(dirname)
        try:
            while True:
                p = _readdir(dir_p)
                if not p:
                    break
                name = p.contents.d_name
                if name not in ('.', '..'):
                    st = _type_to_stat(p.contents.d_type)
                    yield (name, st)
        finally:
            _closedir(dir_p)


def walk(top):
    try:
        names_stats = list(listdir_stat(top))
    except OSError:
        return

    dirs, nondirs = [], []
    for name, st in names_stats:
        if stat.S_ISDIR(st.st_mode):
            dirs.append((name, st))
        else:
            nondirs.append((name, st))

    yield top, dirs, nondirs

    for name, st in dirs:
        new_path = os.path.join(top, name)
        for x in walk(new_path):
            yield x

if __name__ == '__main__':
    import datetime
    import sys
    import time

    size = 0
    time0 = time.clock()
    for root, dirs, files in walk('.'):
        for file, st in files:
            size += st.st_size
            pass
    elapsed1 = time.clock() - time0
    print 'our walk', elapsed1, size

    time0 = time.clock()
    size = 0
    for root, dirs, files in os.walk('.'):
        for file in files:
            size += os.path.getsize(os.path.join(root, file))
            pass
    elapsed2 = time.clock() - time0
    print 'os.walk', elapsed2, size

    print 'ours was', elapsed2 / elapsed1, 'times faster'
