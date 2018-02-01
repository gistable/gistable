from ctypes import CDLL, c_uint, byref, create_string_buffer
libc = CDLL('/usr/lib/libc.dylib')

def sysctl(name):
    size = c_uint(0)
    libc.sysctlbyname(name, None, byref(size), None, 0)
    buf = create_string_buffer(size.value)
    libc.sysctlbyname(name, buf, byref(size), None, 0)
    return buf.value

def is_mac_vm():
  return 'VMM' in sysctl('machdep.cpu.features').split(' ')
