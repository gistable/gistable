from __future__ import print_function

import ctypes

DLL_KERNEL32 = ctypes.windll.kernel32
DLL_WININET = ctypes.windll.wininet

handle_inet = DLL_WININET.InternetOpenA(None, 1, None, None, None)
response = DLL_WININET.InternetOpenUrlA(
    handle_inet,
    'http://iuqerfsodp9ifjaposdfjhgosurijfaewrwergwea.com/',
    None,
    None,
    0x84000000,
    None)

if response:
    print('SinkHole reachable')
    DLL_WININET.InternetCloseHandle(response)
else:
    print('SinkHole NOT reachable!!')

DLL_WININET.InternetCloseHandle(handle_inet)
