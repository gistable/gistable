#!/usr/bin/env python
"""
Netsarang backdoor DNS payload decrypter

file:     decode_shadowpad_dns.py
author:   Fox-IT Security Research Team <srt@fox-it.com>

 Usage: 
   $ cat dns.txt
   sajajlyoogrmkllmuoqiyaxlymwlvajdkouhkdyiyolamdjivho.cjpybuhwnjgkhllm.nylalobghyhirgh.com
 
   $ python decode_shadowpad_dns.py dns.txt 
   Year=17 Month=8 Day=17 Host=Admin-PC Domain= User=Admin
"""
import sys


def keybyte(c, v):
    cl = c
    cl ^= (v & 0xff)
    cl += ((v >> 8) & 0xff)
    cl ^= ((v >> 16) & 0xff)
    cl -= ((v >> 24) & 0xff)
    return cl & 0xff

def xcrypt(data):
    kb = 0
    keys = [0x9F248E8A, 0xBFD7681A, 0xE03A30FA, 0xB1BF5581]
    keys_2 = [0x2F8FCE7E, 0x7DB1F70F, 0x3035D0D6, 0x11C208F]
    ksum = [0,0,0,0]
    for i in xrange(len(data)):
        key = (keys[i % len(keys)] - (keys_2[i % len(keys_2)] * ksum[i % len(keys)])) & 0xffffffff
        ksum[i % len(keys)] = key
        kb = keybyte(kb, key)
        data[i] ^= kb
    return data

def xencode(data):
    r = ''
    for i in xrange(len(data)):
        c = data[i] & 0x0F
        r += chr((c + 0x61))
        c = data[i] >> 4
        r += chr((c + 0x6a))
    return r


def xdecode(data):
    r = ''
    if len(data) % 2 != 0:
        raise Exception("incorrect data size")
    for i in xrange(len(data) / 2):
        a = ord(data[(i * 2)]) - 0x61
        b = (ord(data[(i * 2) + 1]) - 0x6a) << 4
        r += chr(a | b)
    return r


def DecodeDNS(dns):
    data = ''
    r = dns.split('.')
    for i in range(len(r) - 2):
        data += r[i]
    d = bytearray(xdecode(data[1:]))
    dc = xcrypt(d)
    t = dc[14:17]
    tt = dc[17:-1].split(chr(0))
    print 'Year=%d Month=%d Day=%d' % (t[0], t[1], t[2]), 'Host=%s Domain=%s User=%s' % (tt[0], tt[1], tt[2])


if __name__ == '__main__':
    f = open(sys.argv[1], 'r')
    for l in f.readlines():
        dns = l.strip()
        DecodeDNS(dns)