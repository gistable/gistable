#!/usr/bin/env python

#ZPL docs can be found at https://support.zebra.com/cpws/docs/zpl/zpl_manual.pdf
#This works with Python 3, change the bytes to str if you are using Python 2

import socket

#One easy way to find the IP address is with this nmap command
# nmap  192.168.0.* -p T:9100 --open

TCP_IP = '192.168.0.140'
TCP_PORT = 9100
BUFFER_SIZE = 1024

#this will print a code 128 barcode 
zpl = """
^XA
^FO150,40^BY3
^BCN,110,Y,N,N
^FD123456^FS
^XZ 
"""

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(bytes(zpl, "utf-8"))
s.close()
