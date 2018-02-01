#!/usr/bin/env python
import socket
import struct


class ArtNet(object):
    PORT = 6454  # 0x1936

    def __init__(self, port=PORT):
        self._socket = None
        self.port = port

    @property
    def socket(self):
        if self._socket is None:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return self._socket

    def _make_message(self, data, port=None):
        signature = struct.pack("!cccccccx", *list("Art-Net"))
        opcode = struct.pack("<H", 0x5000)  # low byte first
        protocol = struct.pack("!H", 14)  # high byte first
        head = signature + opcode + protocol

        sequence = struct.pack("!x")  # 0x00 to disable
        pyhsical = struct.pack("!x")  # for information only

        # 15 bit port address:
        # - a universe 0-3 (16 universes in 1 subnet, 256 universes in 1 net)
        # - b subnet 4-7 (16 subnets in 1 net)
        # - c net 8-14 (128 nets)
        # - d 0 15
        #
        # total of 16*16*128 = 32768 universes/port addresses
        if port is None:
            #                          aaaabbbbcccccccd
            port = struct.pack("!H", 0b0000000000000000)

        length = struct.pack("!H", len(data))

        return head + sequence + pyhsical + port + length + data

    @staticmethod
    def encode_channels(*args):
        channels = [0] * 512
        for index, value in args:
            channels[index] = value
        fmt = "!" + "B" * len(channels)
        return struct.pack(fmt, *channels)

    def sendArtDMX(self, ip, data):
        msg = self._make_message(data)
        return self.socket.sendto(msg, (ip, self.port))


def main(ip, channels):
    a = ArtNet()
    d = ArtNet.encode_channels(*channels)
    c = a.sendArtDMX(ip, d)

    print "%s bytes sent to %s" % (c, ip)
    for x, y in channels:
        print "channel %s: %s" % (x, y)


if __name__ == "__main__":
    main("2.255.255.255", (
        ## color
        # blue
        (11, 255),
        # green 
        (12, 128),
        # red 
        (13, 255),
        # dim 
        (15, 4), 
        ## white
        # dim
        (14, 2), 
        # flash
        (16, 0), 
    ))
