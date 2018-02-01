import socket
import struct
import zlib

def get_checksum(cs):
    return struct.pack("i", zlib.crc32(cs))

class RconClient:
    MSG_LOGIN   = 0x00
    MSG_COMMAND = 0x01
    MSG_SERVER  = 0x02
    seq = 0x00
    send_queue = []
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        
    def connect (self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.challenge = None
        self.sock.connect ((self.host, self.port))

    def send(self, msg_type, msg):
        if msg_type == self.MSG_LOGIN:
            # login to server
            msg_packet = "%s%s" % (chr(self.MSG_LOGIN), msg)
        elif msg_type == self.MSG_COMMAND:
            # send command to server
            msg_packet = "%s%s%s" % (chr(self.MSG_COMMAND), self.seq, msg)
        elif msg_type == self.MSG_SERVER:
            # ack a server message
            msg_packet = "%s%s" % (chr(self.MSG_SERVER), msg)
        
        std_head = chr(0x42)+chr(0x45) # BE
        msg_packet = chr(0xFF)+msg_packet
        checksum = get_checksum(msg_packet)
        
        bundle_of_joy = "%s%s%s" % (std_head, checksum, msg_packet)
        hexmsg = " ".join([hex(ord(c)) for c in bundle_of_joy])
        
        print "SEND".rjust(16), hexmsg
        print "SEND".rjust(16), "".join(i for i in bundle_of_joy if ord(i)<128)
        self.sock.send(bundle_of_joy)
        self.seq += 0x01
    
    def ack(self, i):
        return self.send(self.MSG_SERVER, i)

    def invoke (self, orig_cmd):
        self.send(self.MSG_COMMAND, orig_cmd)
        return self.getResponse()

    def login(self, pwd):
        self.send(self.MSG_LOGIN, pwd)
        return self.getResponse()

    def getResponse (self):
        result = ""
        done = False
        while not done:
            data = self.sock.recv(4096)
            
            hexmsg = " ".join([hex(ord(c)) for c in data])
            print "RECV".rjust(16), hexmsg
            print "RECV".rjust(16), "".join(i for i in data if ord(i)<128)
            if "%s%s" % (chr(0xFF), chr(0x02)) in data:
                # Message that should be acked
                wut = data.split(chr(0xFF))[1]
                if wut[:1] == chr(0x02):
                    self.ack(wut[1:2])
                    continue
            elif "%s%s%s" % (chr(0xFF), chr(0x00), chr(0x01)) in data:
                print "Successfully logged in.".rjust(16)
                continue
            else:
                print "..."
            
            if "Unknown command" in data:
                print "Unknown command."
                done = True
                break
            done = True
        return result



if __name__ == '__main__':
    from getopt import getopt
    import sys

    host = 
    port =  

    opts, args = getopt(sys.argv[1:], 'h:p:')
    for k, v in opts:
        if k == '-h': host = v
        elif k == '-p': port = int(v)

    print 'Connecting to %s, port %d..' % (host, port)

    try:
        conn = RconClient(host, port)
        conn.connect()
        conn.login(...)
        while 1:
            cmd = raw_input('rcon> ')
            if cmd == 'quit': break
            result = conn.invoke(cmd)
            print result

    except socket.error, detail:
        print 'Network error:', detail[1]

    except EOFError:
        pass
