import json
import socket

### Helper functions

# Read n bytes from the socket
def read(sock, n):
    o = ""
    while len(o) < n:
        o += sock.recv(n-len(o))
    return o

# Read a varint from the socket
def read_varint(sock, remaining=0):
    o = 0
    for i in range(5):
        b = ord(sock.recv(1))
        o |= (b & 0x7F) << 7*i
        if not b & 0x80:
           return remaining-(i+1), o

# Read a packet header from the socket
def read_header(sock, compression=False):
    # Packet length
    _, length = read_varint(sock)

    # Compression (1.8+, only if enabled)
    if compression:
        length, _ = read_varint(sock, length)

    # Packet ident
    length, packet_ident = read_varint(sock, length)

    return length, packet_ident

### Main code

def get_status(addr, port=25565):

    ### 1st pass - get the protocol version
    sock = socket.create_connection((addr, port), 10)  # Connect to the server
    sock.send("\x06\x00\x00\x00\x00\x00\x01")          # Send handshake packet
    sock.send("\x01\x00")                              # Send req packet

    length, _  = read_header(sock)                     # Read res packet header
    length, _  = read_varint(sock, length)             # Read res json length
    status = json.loads(read(sock, length))            # Read res json
    ver = int(status["version"]["protocol"])           # Set protocol ver for 2nd pass

    ### 2nd pass - check online mode
    sock = socket.create_connection((addr, port), 10)  # Connect to server
    sock.send("\x06\x00%s\x00\x00\x00\x02" % chr(ver)) # Send handshake
    sock.send("\x03\x00\x01\x5f")                      # Send login start

    compression = False                                # Compression is off by default
    while True:                                        # Start packet loop
        length, ident = read_header(sock, compression) # Read packet header
        read(sock, length)                             # Read packet body
        if ident == 0x01:                              # Packet: Encryption request
            status["online-mode"] = True               #  --> we're in online mode
            break                                      #  --> close the connection
        elif ident == 0x02:                            # Packet: Login success
            status["online-mode"] = False              #  --> we're in offline mode
            break                                      #  --> close the connection
        elif ident == 0x03:                            # Packet: Set compression
            compression = True                         #  --> enable compression
        else:                                          # Packet: ???
            raise Exception("Unknown packet")          #  --> throw an exception
    
    return status                                      # Return the status
