import ctypes
import sys
import os
import errno

FUNC = ctypes.CFUNCTYPE(None)

PROT_NONE = 0
PROT_READ = 1
PROT_WRITE = 2
PROT_EXEC = 4

if __name__ == "__main__":
    # Get the system page size
    pagesize = os.sysconf("SC_PAGESIZE")
    print("Pagesize: %d"%pagesize)

    # Get a libc handle
    libc = ctypes.CDLL('libc.so.6', use_errno=True)

    # Create our code
    #    0:   55                      push   %ebp
    #    1:   89 e5                   mov    %esp,%ebp
    #    3:   5d                      pop    %ebp
    #    4:   c3                      ret
    buf = ctypes.create_string_buffer("\x55\x89\xe5\x5d\xc3")
    buf_addr = ctypes.addressof(buf)
    buf_addr_rounded = (buf_addr / pagesize)*pagesize
    print("Buffer addr: %s"%hex(buf_addr))

    # Mark the memory executable
    result = libc.mprotect(buf_addr_rounded, 1*pagesize, PROT_READ|PROT_WRITE|PROT_EXEC)
    if result == -1:
        print errno.errorcode[ctypes.get_errno()]

    sys.stdout.flush()

    # Turn this into a callable function
    f = FUNC(buf_addr)
    f() # please don't SIGSEGV...
