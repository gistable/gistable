#!/usr/bin/env python
#coding:utf-8

import sys

def base64_encode_(in_data, padding=False):
    in_len = len(in_data)
    out_data = []
    for i in range(0, in_len, 3):
        out_data.append(in_data[i] >> 2)
        if i+1 < in_len:
            out_data.append(((in_data[i] << 4) | (in_data[i+1] >> 4)) & 63)
            if i+2 < in_len:
                out_data.append(((in_data[i+1] << 2) | (in_data[i+2] >> 6)) & 63)
                out_data.append(in_data[i+2] & 63)
            else:
                out_data.append((in_data[i+1] << 2) & 63)
                if padding:
                    out_data.append(-1)
        else:
            out_data.append((in_data[i] << 4) & 63)
            if padding:
                out_data.append(-1)
                out_data.append(-1)

    return out_data

def base64_decode_(in_data, padding=False):
    in_len = len(in_data)
    if not padding:
        in_data.append(-1)
        in_data.append(-1)
    out_data = []
    for i in range(0, in_len, 4):
        o = (in_data[i] << 18) | (in_data[i+1] << 12)
        r = 1
        if in_data[i+2] >= 0:
            o |= (in_data[i+2] << 6)
            r = 2
            if in_data[i+3] >= 0:
                o |= in_data[i+3]
                r = 3
        out_data.append(o >> 16)
        if r >= 2:
            out_data.append((o >> 8) & 255)
            if r >= 3:
                out_data.append(o & 255)
    return out_data

def ord64(s):
    if s == '=': return -1
    elif s == '+': return 62
    elif s == '/': return 63
    c = ord(s)
    if c < 0x30: return -1
    elif c <= 0x39: return c - 0x30 + 52
    elif c < 0x41: return -1
    elif c <= 0x5A: return c - 0x41
    elif c < 0x61: return -1
    elif c <= 0x7A: return c - 0x61 + 26
    return -1

BASE64_TABLE = "=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
def base64_encode(text):
    b64 = base64_encode_(map(ord, text), padding=True)
    return ''.join(map(lambda x:BASE64_TABLE[1+x], b64))

def base64_decode(text):
    data = base64_decode_(map(ord64, text), padding=True)
    return ''.join(map(chr, data))

def base64t_encode(text):
    b64 = base64_encode_(map(ord, text), padding=False)
    return ''.join(map(lambda x:unichr(0x2800+x), b64)).encode('utf-8')

def base64t_decode(text):
    data = base64_decode_(map(lambda c:ord(c)-0x2800, text.decode('utf-8')), padding=False)
    return ''.join(map(chr, data))


assert("QUJDREVGRw==" == base64_encode("ABCDEFG"))
assert("ABCDEFG" == base64_decode("QUJDREVGRw=="))

assert("⠐⠔⠉⠃⠑⠄⠕⠆⠑⠰" == base64t_encode("ABCDEFG"))
assert("ABCDEFG" == base64t_decode("⠐⠔⠉⠃⠑⠄⠕⠆⠑⠰"))

if __name__ == '__main__':
    for line in sys.stdin:
        enc = base64t_encode(line.rstrip())
        dec = base64t_decode(enc)
        print enc, dec

