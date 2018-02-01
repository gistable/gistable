#!/usr/bin/env python

def encodeZigZag32(n): return (n << 1) ^ (n >> 31)
def encodeZigZag64(n): return (n << 1) ^ (n >> 63)
def decodeZigZag32(n): return (n >> 1) ^ -(n & 1)
def decodeZigZag64(n): return (n >> 1) ^ -(n & 1)

def encodeVInt(n):
    data = ''
    while n >= 0x80:
        data += chr((n & 0x7f) | 0x80)
        n >>= 7
    data += chr(n)
    return data

def decodeVInt(data):
    shift = 0
    result = 0
    for c in data:
        b = ord(c)
        result |= ((b & 0x7f) << shift)
        if not (b & 0x80):
            break
        shift += 7
    return result

def lengthVInt(n):
    length = 1
    while n >= 0x80:
        length += 1
        n >>= 7
    return length
