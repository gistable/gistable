#!/usr/bin/python3
# mysapsso.py - Decoding MYSAPSSO2 cookies

import sys
import fileinput
import urllib.parse
import base64
import binascii
import re
import struct

def hexdump(data):
    while len(data) > 0:
        (cur, data) = (data[:16],data[16:])
        print("| {:<48}| {:<16} |".format(str(re.sub(b'(.{2})', b'\\1 ', binascii.hexlify(cur)), 'ascii'), str(re.sub(b'[\x00-\x1f\x80-\xff]', b'.', cur), 'ascii')))

def decodeSAPToken(token, format=False):
    (v, id, token) = (token[0], token[1:5], token[5:])
    if format:
        print("Version = " + str(v))
        print("ID      = " + str(id, 'ascii'))
    else:
        print(str(v) + ":" + str(id, 'ascii'))
        
    while len(token) > 0:
        ((type, length), token) = (struct.unpack('!BH', token[:3]), token[3:])
        (value, token) = (token[:length], token[length:])

        if format:
            print("Type={:02x} Length={:d}".format(type, length))
            if type == 0x01 or type == 0x0a:
                print("Username = " + str(value, 'ascii'))
            elif type == 0x02:
                print("Client = " + str(value, 'ascii'))
            elif type == 0x03:
                print("System = " + str(value, 'ascii'))
            elif type == 0x04:
                print("Toke issued at = " + str(value, 'ascii'))
            elif type == 0x88:
                print("Authentication type = " + str(value, 'ascii'))
            elif type == 0xff:
                print("Signature:")
                hexdump(value)
            else:      
                hexdump(value)
                print()
        else:
            print(str(type) + ":" + str(value)[2:-1])

def usage():
    print("Usage:\n" + sys.argv[0] + " decode|decode2 <token>\n - OR -\n" + sys.argv[0] + " encode [<decode-formatted-files> ...]")
    sys.exit()

### Main ###
if len(sys.argv) < 2:
    usage()

if sys.argv[1] in ('decode', 'decode2'):
    if len(sys.argv) != 3:
        usage()
        
    try:
        token = base64.b64decode(bytes(urllib.parse.unquote(sys.argv[2], 'ascii'), 'ascii'))
    except binascii.Error:
        try:
            token = base64.b64decode(bytes(urllib.parse.unquote(sys.argv[2] + '=', 'ascii'), 'ascii'))
        except binascii.Error:
            try:
                token = base64.b64decode(bytes(urllib.parse.unquote(sys.argv[2] + '==', 'ascii'), 'ascii'))
            except:
                print("Failed to complete missing padding - giving up!")
                sys.exit()

    if sys.argv[1] == 'decode':
        decodeSAPToken(token)
    else:
        print("=== Raw ===")
        hexdump(token)
        print("=== Decoded ===")
        decodeSAPToken(token, True)
elif sys.argv[1] == 'encode':
    firstline = True
    for line in fileinput.input(sys.argv[2:]):
        line = line.rstrip("\n")
        if firstline:
            (v, id) = line.split(":")
            ssotoken = struct.pack('!B4s', int(v), bytes(id, 'ascii'))
            firstline = False
        else:
            (type, value) = line.split(":", 1)
            value = eval("b'''" + value + "'''")
            length = len(value)
            ssotoken += struct.pack('!BH', int(type), int(length)) + value
    print(urllib.parse.quote(str(base64.b64encode(ssotoken), 'ascii')))
