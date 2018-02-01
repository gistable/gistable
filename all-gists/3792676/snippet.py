#! /usr/bin/env python2
# Small test client for rtl_tcp
# Simeon Miteff <simeon.miteff@gmail.com>
# Thu Sep 27 09:28:55 SAST 2012
import socket
import struct
import time

SET_FREQUENCY = 0x01
SET_SAMPLERATE = 0x02
SET_GAINMODE = 0x03
SET_GAIN = 0x04
SET_FREQENCYCORRECTION = 0x05

class RtlTCP(object):
    def __init__(self):
        self.remote_host = "localhost"
        self.remote_port = 1234
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.remote_host, self.remote_port))
        self.__send_command(SET_SAMPLERATE, 2048000)
    def tune(self, freq):
        self.__send_command(SET_FREQUENCY, freq)
    def __send_command(self, command, parameter):
        cmd = struct.pack(">BI", command, parameter)
        self.conn.send(cmd)

if __name__=="__main__":
    sdr = RtlTCP()
    start = time.time()
    for i in range(0,10):
        time.sleep(0.1)
        sdr.tune(88e6+i*1e6)
    elapsed = time.time() - start
    print "Took %f seconds." % elapsed
