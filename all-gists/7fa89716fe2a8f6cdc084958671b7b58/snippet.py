from ctypes import CDLL, Structure, POINTER, c_int64, c_int32, c_int16, c_char, c_uint32
from ctypes.util import find_library
import time

c = CDLL(find_library("System"))

# https://opensource.apple.com/source/Libc/Libc-1158.50.2/include/NetBSD/utmpx.h.auto.html
# https://developer.apple.com/legacy/library/documentation/Darwin/Reference/ManPages/man3/endutxent.3.html#//apple_ref/doc/man/3/endutxent

BOOT_TIME     =  2
USER_PROCESS  =  7
DEAD_PROCESS  =  8
SHUTDOWN_TIME = 11

class timeval(Structure):
    _fields_ = [
                ("tv_sec",  c_int64),
                ("tv_usec", c_int32),
               ]

class utmpx(Structure):
    _fields_ = [
                ("ut_user", c_char*256),
                ("ut_id",   c_char*4),
                ("ut_line", c_char*32),
                ("ut_pid",  c_int32),
                ("ut_type", c_int16),
                ("ut_tv",   timeval),
                ("ut_host", c_char*256),
                ("ut_pad",  c_uint32*16),
               ]

setutxent_wtmp = c.setutxent_wtmp
setutxent_wtmp.restype = None

getutxent_wtmp = c.getutxent_wtmp
getutxent_wtmp.restype = POINTER(utmpx)

endutxent_wtmp = c.setutxent_wtmp
endutxent_wtmp.restype = None

# This is an example implementation of parsing the utmpx records
# You have to:
# - initialize a session with setutxent_wtmp
# - iterate through getutxent_wtmp until a NULL record, indicating no more
# - finalize session with endutxent_wtmp

def fast_last(gui_only=True):
    # initialize
    setutxent_wtmp(0)
    entry = getutxent_wtmp()
    while entry:
        e = entry.contents
        entry = getutxent_wtmp()
        if e.ut_type   == BOOT_TIME:
            # reboot/startup
            print "reboot:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e.ut_tv.tv_sec))
        elif e.ut_type == SHUTDOWN_TIME:
            # shutdown
            print "shutdown:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e.ut_tv.tv_sec))
        elif e.ut_type == USER_PROCESS:
            # login
            if gui_only and e.ut_line != "console":
                continue
            print "login:", e.ut_user, e.ut_line, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e.ut_tv.tv_sec))
        elif e.ut_type == DEAD_PROCESS:
            # logout
            if gui_only and e.ut_line != "console":
                continue
            print "logout:", e.ut_user, e.ut_line, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e.ut_tv.tv_sec))
    # finish
    endutxent_wtmp()
