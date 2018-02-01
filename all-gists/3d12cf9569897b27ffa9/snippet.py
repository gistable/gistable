import socket
import struct
import os
 
# Create UDP socket.
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 
# Bind to LFS.
sock.bind(('127.0.0.1', 20777))
 
while True:
    # Receive data.
    data = sock.recv(512)
 
    if not data:
        break # Lost connection
      
    outsim_pack = struct.unpack('64f', data[0:256])
    os.system('cls')
 
    for id, value in enumerate(outsim_pack):
        print "%d : %s" % (id, value)
 
print 'lost connection'
# Release the socket.
sock.close()