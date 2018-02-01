#!/usr/bin/env python
# coding: utf-8
"""
This script implements a server which listens in UDP port 9999 (by default)
waiting for an incoming datagram.

If the incoming datagram is empty, the script answers with the current content
of the clipboard (in utf8), otherwise it sets the content of the clipboard
to the contents received in the datagram, interpreted as plain text in utf8

The clipboard is limited to 64K.

Requires xerox module.
"""

# HOWTO use it in conjunction with iOS Editorial App ##################
# 
# In your Linux/OSX/Windows machine:
# 
# 1) Be sure that you have xerox module installed (ej: pip install xerox)
# 2) Run current script: python copypaste.py &
# 3) Select any text and copy it to system clipboard (Ctrl-C)
#
# In Editorial
#
# 1) Install Editorial workflow "Paste from remote" (http://www.editorial-workflows.com/workflow/5249408887160832/j3cX2R5bFp0)
# 2) Optionally assign it an abbreviation (I use rpp)
# 3) Edit the workflow and configure the first action, putting the IP and port of your server
# 4) Run the workflow and see how the text copied in the server appears in the editor
#
# You can also i nstall Editorial workflow "Copy to remote", and then the contents of
# iPad's clipboard can be uploaded to the Linux/OSX/Windows server, where they can be pasted 
# into any other application

import socket
import sys,locale
import xerox

if len(sys.argv)==1:
    port = 9999
else:
    port = int(sys.argv[1])

# find our own IP (this will show the private IP if behind a NAT)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 53))
my_ip = s.getsockname()[0]
s.close()
print "Listening in IP=%s, port=%d" % (my_ip, port)


# Find the encoding used by the system clipboard
encoding = locale.getpreferredencoding()

# Now create the listening socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", port))


# Infinite loop
while True:
    data, origin = s.recvfrom(65535)
    if len(data) == 0:  # Empty datagram
        # Get clipboard and send it
        p = xerox.paste()
        if type(p)!=unicode:
            p=unicode(p,encoding)
        data = p.encode("utf-8")
        s.sendto(data, origin)
    else:
        # Set the clipboard with the content of the datagram
        data = unicode(data, "utf-8")
        if encoding=="cp1252":
            data = data.encode(encoding)
        xerox.copy(data)
        
